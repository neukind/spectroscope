import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

import click
from ethereumapis.v1alpha1 import beacon_chain_pb2_grpc
import grpc
import importlib
from spectroscope.beacon_client import BeaconChainStreamer
import toml

SYSTEM_MODULES = ["spectroscope"]


log = logging.getLogger("spectroscope")
logging.basicConfig(level=logging.DEBUG)


@click.command()
@click.option(
    "-c",
    "--config",
    "config_file",
    type=str,
    default="config.toml",
    help="Config file path",
)
def cli(config_file: str):
    log.info("Spectroscope starting up")

    log.info("Loading configuration")
    config_root = toml.load(config_file)

    scope_config = config_root.get("spectroscope", dict())
    grpc_endpoint = scope_config["eth2_endpoint"]
    log.info("gRPC ETH2 endpoint is {}".format(grpc_endpoint))
    validator_set = set(scope_config["pubkeys"])
    log.info("Found {} unique validator keys to watch".format(len(validator_set)))

    modules = list()
    for module, config in config_root.items():
        if module not in SYSTEM_MODULES and config.get("enabled", False):
            try:
                log.info("Loading module {} with {} args".format(module, len(config)))
                m = importlib.import_module("spectroscope.module", module)
            except ImportError:
                log.error("Couldn't import module {}".format(alert_sink_class))
            modules.append(tuple(m.SPECTROSCOPE_MODULE, config))
    log.info("Loaded {} modules".format(len(modules)))

    with grpc.insecure_channel(grpc_endpoint) as channel:
        stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
        bw = BeaconChainStreamer(stub, modules)
        bw.add_validators(set(map(bytes.fromhex, validator_set)))
        bw.stream()


if __name__ == "__main__":
    cli()
