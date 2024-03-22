import yaml
import jack

from pathlib import Path

import logging

log = logging.getLogger()


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
            return

        if not port.name in self.all_ports:
            return

        sinks = self.all_ports[port.name]
        connections = self.c.get_all_connections(port)

        for sink in sinks:
            log.debug(sink)
            try:
                sink_port = self.c.get_port_by_name(sink)
            except jack.JackError:
                continue

            if sink_port not in connections:
                log.debug(f"connecting {port.name} -> {sink_port.name}")
                if port.is_output:
                    self.c.connect(port, sink_port)
                else:
                    self.c.connect(sink_port, port)

    def deactivate(self, *args):
        self.c.deactivate()
