import yaml
from pathlib import Path

base_path = Path(__file__).parent

if __name__ == "__main__":
    for conf_file in base_path.glob("*.yml"):
        server_name = conf_file.name.split("_")[0]
        with open(conf_file) as f:
            conf = yaml.load(f, yaml.Loader)

        with open(base_path / f"{server_name}_patterns.txt", "w") as f:
            for client in conf:
                from_base = client["from"]
                n_channels = client["n_channels"]
                from_start_index = client["start_index"]

                for to_client in client["to"]:
                    to_base = to_client["client"]
                    to_start_index = to_client["start_index"]

                    for i in range(n_channels):
                        f.write(
                            f"{from_base}{from_start_index+i}\n\t{to_base}{to_start_index+i}\n"
                        )
