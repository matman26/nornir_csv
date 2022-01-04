"""Reads CSV file as a Nornir inventory."""
import csv
from nornir.core.inventory import (Inventory,
                                   Hosts,
                                   Host,
                                   Groups,
                                   Group)
from typing import Dict, Any

class CsvInventory:
    def __init__(self, inventory_dir_path: str = "./inventory/") -> None:
        self.inventory_dir_path = inventory_dir_path

    def _csv_to_dict(self):
        pass

    def _hosts_dict_to_hostobject(self, hosts_dict: Dict[Any, Any]) -> Hosts:
        print(hosts_dict)
        return Hosts()

    def _groups_dict_to_groupobject(self, groups_dict: Dict[Any,Any]) -> Groups:
        print(groups_dict)
        return Groups()

    def _load_defaults_file(self, defaults_file_name: str) -> Dict[str, Any]:
        print(defaults_file_name)
        return {}

    def load() -> Inventory:
        # Load data from three csv files as dict (hosts, groups,defaults)
        # Pass dict to their respective function, generate Hosts, Groups and Defaults objects.
        return Inventory(hosts=Hosts(), groups=Groups())
