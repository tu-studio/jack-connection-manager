import yaml
import jack
from time import sleep
from dataclasses import dataclass

from pathlib import Path

base_path = Path(__file__).parent


# damit kann man checken, ob ein client existiert
# print(c.get_uuid_for_client_name("spotify"))
# gibt auch ein callback on_port_creation oder so (kann man dann trotzdem noch connections setzen?)


def parse_connection_file(filename):
    with open(base_path / "connections.yml") as f:
        conf = yaml.load(f, yaml.Loader)

    connections = {}

    for client in conf:
        source_name, port_name = client["from"].split(":")
        n_channels = client["n_channels"]
        source_start_index = client["start_index"]
        connections[source_name] = {
            "source_name": source_name,
            "source_port": port_name,
            "n_channels": n_channels,
            "source_start_index": source_start_index,
            "sinks": {},
        }

        for sink in client["to"]:
            sink_name, sink_port = sink["client"].split(":")
            sink_start_index = sink["start_index"]
            connections[source_name]["sinks"][sink_name] = {
                "sink_name": sink_name,
                "sink_port": sink_port,
                "sink_start_index": sink_start_index,
            }

    return connections


if __name__ == "__main__":
    conf = parse_connection_file(base_path / "connections.yml")

    c = jack.Client("jack_conneeect", no_start_server=True)

    for conn in conf.values():
        in_prefix = f'{conn["source_name"]}:{conn["source_port"]}'
        # out_ports = [
        #     c.get_ports(
        #         f"{sink['sink_name']}:{sink['sink_port']}", is_audio=True, is_input=True
        #     )
        #     for sink in conn["sink"]
        # ]
        in_ports = c.get_ports(
            in_prefix,
            is_audio=True,
            is_output=True,
        )
        for p in in_ports:
            idx = int(p.name.removeprefix(in_prefix)) - conn["source_start_index"]
            if idx >= conn["n_channels"] or idx < 0:
                continue
            print(idx)
            p_name, p_port = p.name.split(":")
            for sink in conn["sinks"].values():
                print(sink["sink_name"])
                out_port = c.get_port_by_name(
                    f"{sink['sink_name']}:{sink['sink_port']}{idx + sink['sink_start_index']}"
                )
                print(f"connectiing {p.name} -> {out_port.name}")
                c.connect(p, out_port)

        # print(c.get_all_connections(p))
        # out_ports = c.get_ports(is_audio=True, is_input=True)
