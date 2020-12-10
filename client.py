import argparse
import grpc
import importlib
import logging
import os
import sys

from alert_sink.alert_sink import AlertSink
from configparser import ConfigParser
from eth.v1alpha1 import beacon_chain_pb2, beacon_chain_pb2_grpc
from typing import List


class BalanceWatcher:
    def __init__(
        self,
        stub: beacon_chain_pb2_grpc.BeaconChainStub,
        alerter: AlertSink,
        validator_set: List[str],
    ):
        self.stub = stub
        self.alerter = alerter
        self.validator_set = validator_set
        self.validator_data = {}
        self.alerting_validators = set()

    def _generate_messages(self):
        public_keys = map(bytes.fromhex, self.validator_set)
        yield beacon_chain_pb2.ValidatorChangeSet(
            action=beacon_chain_pb2.SET_VALIDATOR_KEYS,
            public_keys=public_keys,
        )

    def stream_validators(self):
        responses = self.stub.StreamValidatorsInfo(self._generate_messages())
        for response in responses:
            if response.public_key in self.validator_data:
                if (
                    self.validator_data[response.public_key]["status"]
                    in [
                        2,
                        3,
                    ]
                    and response.status not in [2, 3]
                ):
                    self.alerter.alert(
                        response.index,
                        response.public_key,
                        "ValidatorBadState",
                        "{} -> {}".format(
                            self.validator_data[response.public_key]["status"],
                            response.status,
                        ),
                    )
                if (
                    self.validator_data[response.public_key]["status"] == 3
                    and response.status == 2
                ):
                    self.alerter.alert(
                        response.index,
                        response.public_key,
                        "ValidatorBadState",
                        "{} -> {}".format(
                            self.validator_data[response.public_key]["status"],
                            response.status,
                        ),
                    )
                if (
                    self.validator_data[response.public_key]["balance"]
                    > response.balance
                ):
                    self.alerter.alert(
                        response.index,
                        response.public_key,
                        "ValidatorEthLoss",
                        (
                            self.validator_data[response.public_key]["balance"]
                            - response.balance
                        )
                        * 0.000000001,
                    )
                    self.alerting_validators.add(response.public_key)
                if (
                    response.public_key in self.alerting_validators
                    and self.validator_data[response.public_key]["balance"]
                    < response.balance
                ):
                    self.alerter.clear(
                        response.index, response.public_key, "ValidatorEthLoss"
                    )
                    self.alerting_validators.remove(response.public_key)
            self.validator_data[response.public_key] = {
                "status": response.status,
                "balance": response.balance,
            }


if __name__ == "__main__":
    logging.basicConfig()

    parser = argparse.ArgumentParser(description="Ethereum 2.0 monitoring client.")
    parser.add_argument("--pubkeys", help="file containing public keys", required=True)
    parser.add_argument("--config", help="config file", default="config.ini")
    args = parser.parse_args()
    validator_set = [line.rstrip("\n") for line in open(args.pubkeys)]

    alert_module = None
    config = ConfigParser()
    with open(args.config, "r") as config_file:
        config.read_file(config_file)
        alert_sink_class = config.get("alert", "sink", raw=True, fallback="alerta")
        try:
            alert_module = importlib.import_module(
                "alert_sink.{}".format(alert_sink_class)
            )
        except ImportError:
            logging.error("Couldn't import alert class {}".format(alert_sink_class))
    api_key = config.get("alert", "api_key", raw=True)
    alerter = alert_module.Alerter(api_key)

    grpc_endpoint = config.get("rpc", "endpoint", raw=True)
    with grpc.insecure_channel(grpc_endpoint) as channel:
        stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
        bw = BalanceWatcher(stub, alerter, validator_set)
        bw.stream_validators()
