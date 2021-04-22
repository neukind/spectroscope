import click
import grpc
import importlib
import os
import sys
import spectroscope
import toml

from click_default_group import DefaultGroup
from ethereumapis.v1alpha1 import beacon_chain_pb2_grpc
from ethereumapis.v1alpha1 import validator_pb2_grpc
from pkg_resources import load_entry_point
from spectroscope.beacon_client import BeaconChainStreamer
from spectroscope.validator_client import ValidatorClientStreamer
from spectroscope.config import DefaultConfigBuilder
from spectroscope.module import ConfigOption, ENABLED_BY_DEFAULT
from spectroscope.module import Plugin, Subscriber
from typing import List
import multiprocessing

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
    special_module = tuple()
    for module, config in config_root.items():
        if module not in SYSTEM_MODULES and config.get("enabled", False):
            try:
                log.info("Loading module {} with {} args".format(module, len(config)))
                m = load_entry_point("spectroscope", "spectroscope.module", module)
            except ImportError:
                raise click.ClickException("Couldn't import module {}".format(module))
            if module == "activation_alert": 
                special_module = (m,config)
            modules.append((m, config))
    log.info("Loaded {} modules".format(len(modules)))
    log.info("Opening gRPC channel")
    with grpc.insecure_channel(grpc_endpoint) as channel:
        validator_stub = validator_pb2_grpc.BeaconNodeValidatorStub(channel)
        log.debug("this should print True: {}".format(issubclass(modules[-1][0], Plugin)))
        log.debug("this is the list of modules for validator client : {}".format([x for x in modules if x == special_module or issubclass(x[0],Plugin)]))
        vw = ValidatorClientStreamer(validator_stub, [x for x in modules if x == special_module or issubclass(x[0],Plugin)])
        vw.add_validators(set(map(bytes.fromhex, validator_set)))
        activated_validators = vw.stream()
        log.info("received {} new active validators of {} type".format(len(activated_validators),type(activated_validators[0])))

        # processes = []
        # result_queue = multiprocessing.Queue()
        # while vw.get_validators():
        #     validator_process = multiprocessing.Process(target=vw.stream, args=[result_queue])
        #     beacon_process = multiprocessing.Process(target=bw.stream, args=[result_queue])
        #     validator_process.start()
        #     beacon_process.start()
        #     processes.append(validator_process)
        #     processes.append(beacon_process)
        #     #wait until the validator process ends
        #     active_validators = result_queue.get()
        #     for process in processes:
        #         process.terminate()
            
        #     vw.remove_validators(active_validators)
        #     bw.add_validators(active_validators)
        


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
