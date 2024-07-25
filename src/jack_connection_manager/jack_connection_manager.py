import jack
import click
import logging
from pathlib import Path
import sys
import signal

from sdnotify import SystemdNotifier
from jack_connection_manager.ConnectionManager import ConnectionManager

logFormat = "%(asctime)s [%(levelname)-5.5s]: %(message)s"
timeFormat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=logFormat, datefmt=timeFormat)
log = logging.getLogger()


# lists for constructing default config paths
default_config_file_path = Path("jack-connection-manager")
default_config_file_name_options = [
    "connections.yml",
    "connection.yml",
    "jack-connection-manager_conf.yml",
    "jack-connection-manager-conf.yml",
    "jack-connection-manager_config.yml",
    "jack-connection-manager-config.yml",
    "config.yml",
    "conf.yml",
]
default_config_file_locations = [
    Path.home() / ".config",
    Path("/etc"),
    Path("/usr/local/etc"),
]


def get_default_config_path():
    for possible_config_path in (
        base / default_config_file_path / filename
        for base in default_config_file_locations
        for filename in default_config_file_name_options
    ):
        if possible_config_path.exists():
            return possible_config_path
    return None


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


@click.command(
    help="Set Jack Connections",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    default=None,
    help="path to connection file",
)
@click.option(
    "-r",
    "--remove-connections",
    "disconnect",
    is_flag=True,
    default=False,
    help="remove all connections except for those specified with -e",
)
@click.option(
    "-e",
    "--exclude",
    multiple=True,
    default=[],
    help="clients that start with the specified string will not be disconnected, can be specified multiple times",
)
@click.option(
    "--client-name", help="Name for the jack client", default="jack_connection_manager"
)
@click.option(
    "-l",
    "--list-missing",
    help="List missing ports and connections",
    is_flag=True,
    default=False,
)
@click.option("-v", "--verbose", count=True, help="increase verbosity level.")
@click.version_option()
def main(config_path, disconnect, exclude, client_name, list_missing, verbose):
    if list_missing:
        log.setLevel(logging.WARN)
    elif verbose == 0:
        log.setLevel(logging.INFO)
    elif verbose >= 1:
        log.setLevel(logging.DEBUG)

    # do the disconnect!
    if disconnect:
        remove_connections(exclude)
        log.info("exiting...")
        sys.exit(0)

    # find config path
    if config_path is None:
        # check different paths for a config file, with the highest one taking precedence
        config_path = get_default_config_path()

    if config_path is None:
        log.error("could not find connection file, please supply one using -c")
        sys.exit(-1)

    cm = ConnectionManager(config_path, client_name)
    if list_missing:
        cm.print_missing_connections()
        sys.exit(0)
    systemd = SystemdNotifier()

    log.info("jack-connection-manager is running")
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, cm.deactivate)
    systemd.notify("READY=1")
    # start the connection loop
    cm.connection_loop()


if __name__ == "__main__":

    main()
