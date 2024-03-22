import yaml
import jack
import click
from time import sleep
from dataclasses import dataclass
import logging
from pathlib import Path
import sys
import signal

logFormat = "%(asctime)s [%(levelname)-5.5s]: %(message)s"
timeFormat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=logFormat, datefmt=timeFormat)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

base_path = Path(__file__).parent


def add_to_dict_of_sets(d: dict, key, value):
    if key in d:
        d[key].add(value)
    else:
        d[key] = set((value,))


class ConnectionManager:
    def __init__(self, config_path: Path) -> None:
        self.c = jack.Client("jack_conneeect", no_start_server=True)
        self.source_ports: dict[str, set[str]] = {}
        self.all_ports: dict[str, set[str]] = {}

        self.build_connection_dict(config_path)
        self.set_initial_connections()
        self.c.set_port_registration_callback(self.set_connection_for_port, False)
        self.c.activate()

    def build_connection_dict(self, config_path: Path):
        with open(config_path) as f:
            conf = yaml.load(f, yaml.Loader)

        for source_client in conf:
            source_base = source_client["client"]
            n_channels = source_client["n_channels"]
            source_start_index = (
                source_client["start_index"] if "start_index" in source_client else 1
            )

            for sink_client in source_client["connections"]:
                sink_base = sink_client["client"]
                sink_start_index = (
                    sink_client["start_index"] if "start_index" in sink_client else 1
                )

                for i in range(n_channels):
                    source_port = f"{source_base}{source_start_index+i}"
                    sink_port = f"{sink_base}{sink_start_index+i}"
                    log.debug(f"parsing connection {source_port} -> {sink_port}")
                    add_to_dict_of_sets(self.source_ports, source_port, sink_port)
                    add_to_dict_of_sets(self.all_ports, sink_port, source_port)
                    add_to_dict_of_sets(self.all_ports, source_port, sink_port)

    def set_initial_connections(self):
        for source in self.source_ports:
            try:
                source_port = self.c.get_port_by_name(source)
            except jack.JackError:
                continue

            self.set_connection_for_port(source_port)

    def set_connection_for_port(self, port: jack.Port, registered: bool = True):
        if not registered:
            log.debug("callback unregister port")
            return

        if not port.name in self.all_ports:
            return

        sinks = self.all_ports[port.name]
        connections = self.c.get_all_connections(port)

        for sink in sinks:
            try:
                sink_port = self.c.get_port_by_name(sink)
            except jack.JackError:
                continue

            if sink_port not in connections:
                if port.is_output:
                    self.c.connect(port, sink_port)
                else:
                    self.c.connect(sink_port, port)

    def deactivate(self, *args):
        self.c.deactivate()


def remove_connections(exclude: list[str]):
    c = jack.Client("jack_disconneeect", no_start_server=True)
    log.info(f"Removing all connections, skipping clients: {', '.join(exclude)}")

    out_ports: list[jack.Port] = c.get_ports(is_audio=True, is_output=True)
    for p in out_ports:
        connected_ports = c.get_all_connections(p)
        if p.name.startswith(exclude):
            continue
        for c_p in connected_ports:
            if c_p.name.startswith(exclude):
                continue

            c.disconnect(p, c_p)


@click.command(help="Set Jack Connections")
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    default=base_path / "connections.yml",
    help="path to configfile",
)
@click.option(
    "-r",
    "--remove-connections",
    "disconnect",
    is_flag=True,
    default=False,
    help="remove all connections",
)
@click.option("-e", "--exclude", multiple=True, default=[])
def main(config_path, disconnect, exclude):

    # TODO handle jack server not existing

    if disconnect:
        remove_connections(exclude)
        log.info("exiting...")
        sys.exit(0)

    cm = ConnectionManager(config_path)

    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, cm.deactivate)
    signal.pause()


if __name__ == "__main__":

    main()
