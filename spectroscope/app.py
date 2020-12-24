import click
import grpc
import importlib
import sys
import spectroscope
import toml

from ethereumapis.v1alpha1 import beacon_chain_pb2_grpc
from spectroscope.beacon_client import BeaconChainStreamer

SYSTEM_MODULES = ["spectroscope"]


log = spectroscope.log()


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
    for top_level, module_type in config_root.items():
        if top_level not in SYSTEM_MODULES:
            for module, config in module_type.items():
                if config.get("enabled", False):
                    try:
                        log.info(
                            "Loading module {}.{} with {} args".format(
                                top_level, module, len(config)
                            )
                        )
                        m = importlib.import_module(
                            "spectroscope.module.{}.{}".format(top_level, module)
                        )
                    except ImportError:
                        log.error("Couldn't import module {}".format(module))
                        sys.exit(1)
                    modules.append((m.SPECTROSCOPE_MODULE, config))
    log.info("Loaded {} modules".format(len(modules)))

    log.info("Opening gRPC channel")
    with grpc.insecure_channel(grpc_endpoint) as channel:
        stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
        bw = BeaconChainStreamer(stub, modules)
        bw.add_validators(set(map(bytes.fromhex, validator_set)))
        bw.stream()


if __name__ == "__main__":
    cli()
