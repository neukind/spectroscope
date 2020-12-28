import click
import grpc
import importlib
import os
import sys
import spectroscope
import toml

from click_default_group import DefaultGroup
from ethereumapis.v1alpha1 import beacon_chain_pb2_grpc
from pkg_resources import load_entry_point
from spectroscope.beacon_client import BeaconChainStreamer
from spectroscope.config import DefaultConfigBuilder
from spectroscope.module import ConfigOption, ENABLED_BY_DEFAULT
from typing import List

# System modules should be considered separate; they are for configuration purposes only.
SYSTEM_MODULES: List[str] = ["spectroscope"]

DEFAULT_CONFIG_PATH: str = "config.toml"


log = spectroscope.log()


@click.group(cls=DefaultGroup, default="run", default_if_no_args=True)
def cli():
    """
    The Spectroscope CLI program. By default, it will run `spectroscope run` if
    no command is given.
    """
    pass


@cli.command()
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.File("r"),
    default=DEFAULT_CONFIG_PATH,
    help="Config file path",
)
def run(config_file: click.utils.LazyFile):
    """Run the Spectroscope monitoring agent."""

    log.info("Spectroscope starting up")

    log.info("Loading configuration")
    config_root = toml.loads(config_file.read())

    try:
        scope_config = config_root.get("spectroscope", dict())
        grpc_endpoint = scope_config["eth2_endpoint"]
        validator_set = set(scope_config["pubkeys"])
    except KeyError as e:
        raise click.ClickException(
            "{} expected but not found in config file. Exiting.".format(e)
        )

    log.info("gRPC ETH2 endpoint is {}".format(grpc_endpoint))
    log.info("Found {} unique validator keys to watch".format(len(validator_set)))

    modules = list()
    for module, config in config_root.items():
        if module not in SYSTEM_MODULES and config.get("enabled", False):
            try:
                log.info("Loading module {} with {} args".format(module, len(config)))
                m = load_entry_point("spectroscope", "spectroscope.module", module)
            except ImportError:
                raise click.ClickException("Couldn't import module {}".format(module))
            modules.append((m, config))
    log.info("Loaded {} modules".format(len(modules)))

    log.info("Opening gRPC channel")
    with grpc.insecure_channel(grpc_endpoint) as channel:
        stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
        bw = BeaconChainStreamer(stub, modules)
        bw.add_validators(set(map(bytes.fromhex, validator_set)))
        bw.stream()


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force overwriting the destination file.",
)
@click.argument("destination_file", default=DEFAULT_CONFIG_PATH, type=click.File("w"))
def init(destination_file: click.utils.LazyFile, force: bool):
    """Initialize a config file into DESTINATION_FILE."""

    dst_path = destination_file.name
    if dst_path != "<stdout>" and os.path.exists(dst_path) and force != True:
        raise click.ClickException(
            "Can't overwrite {} without --force. Exiting.".format(dst_path)
        )

    config_data = DefaultConfigBuilder.build()
    for module, configs in config_data.items():
        destination_file.write("[{section}]\n".format(section=module))
        if module not in SYSTEM_MODULES:
            destination_file.write("# enable or disable the module\n")
            destination_file.write(
                "enabled = {auto}\n".format(
                    auto="true" if module in ENABLED_BY_DEFAULT else "false"
                )
            )

        for opt in filter(lambda o: not o.hide, configs):
            if opt.param_type == list:
                default = '[\n    "{}"\n    ]'.format('",\n    "'.join(opt.default))
            elif opt.default:
                default = toml.TomlEncoder().dump_value(opt.default)
            else:
                default = '""'

            destination_file.write("# {comment}\n".format(comment=opt.description))
            destination_file.write(
                "{key} = {value}\n".format(key=opt.name, value=default)
            )
        destination_file.write("\n")


if __name__ == "__main__":
    cli()
