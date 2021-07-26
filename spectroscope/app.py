import click
import grpc
import importlib
import os
import sys
import spectroscope
import toml
import asyncio
from motor import motor_asyncio
from click_default_group import DefaultGroup
from ethereumapis.v1alpha1 import beacon_chain_pb2_grpc
from ethereumapis.v1alpha1 import validator_pb2_grpc
from pkg_resources import load_entry_point
from spectroscope.clients.beacon_client import BeaconChainStreamer
from spectroscope.clients.validator_client import ValidatorClientStreamer
from spectroscope.service.spectroscope_server import SpectroscopeServer
from spectroscope.clients.mongodb_client import MongodbClientStreamer

from spectroscope.config import DefaultConfigBuilder
from spectroscope.module import ConfigOption, ENABLED_BY_DEFAULT
from spectroscope.module import Plugin, Subscriber
from spectroscope.streaming import StreamingClient
from typing import List
from spectroscope.exceptions import Invalid, ValidatorInvalid, ValidatorActivated
from functools import wraps

# System modules should be considered separate; they are for configuration purposes only.
SYSTEM_MODULES: List[str] = ["spectroscope", "database"]

DEFAULT_CONFIG_PATH: str = "config.toml"


log = spectroscope.log()


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


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
    help="Config file path, ([::])",
)
@click.option(
    "--host",
    "server_host",
    type=click.STRING,
    default="[::]",
    help="server host ip (51001)",
)
@click.option(
    "--port",
    "server_port",
    type=click.INT,
    default=50051,
    help="server port number",
)
@coro
async def run(
    config_file: click.utils.LazyFile, server_host: click.STRING, server_port: click.INT
):
    """Run the Spectroscope monitoring agent."""

    log.info("Spectroscope starting up")

    log.info("Loading configuration")
    config_root = toml.loads(config_file.read())

    try:
        scope_config = config_root.get("spectroscope", dict())
        grpc_endpoint = scope_config["eth2_endpoint"]
        validator_set = set(scope_config["pubkeys"])
        database_config = config_root.get("database", dict())
        db_uri = database_config["database_uri"]
        db_name = database_config["database_name"]
        db_col = database_config["database_collection"]

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
                m = load_entry_point("spectroscope", "spectroscope.module", module)
            except ImportError:
                raise click.ClickException("Couldn't import module {}".format(module))
            modules.append((m, config))

    log.info("Loaded {} modules".format(len(modules)))

    log.info("Opening gRPC channel")

    async with grpc.aio.insecure_channel(grpc_endpoint) as channel:
        validator_stub = validator_pb2_grpc.BeaconNodeValidatorStub(channel)
        beacon_stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
        val_streamer = ValidatorClientStreamer(validator_stub, [x for x in modules])
        beacon_streamer = BeaconChainStreamer(beacon_stub, [x for x in modules])
        mongo_streamer = MongodbClientStreamer(
            db_uri=db_uri, db_name=db_name, col_name=db_col, modules=modules
        )
        spectro_server = SpectroscopeServer(
            server_host, server_port, [x for x in modules]
        )
        streamer = StreamingClient(
            val_streamer, beacon_streamer, mongo_streamer, spectro_server, validator_set
        )
        streamer.setup()
        await streamer.loop()


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
    log.info("Found {} modules".format(len(config_data.items())))
    for module, configs in config_data.items():
        log.info(
            "Writing configuration for{system}module {module}".format(
                system=" system " if module in SYSTEM_MODULES else " ", module=module
            )
        )
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
