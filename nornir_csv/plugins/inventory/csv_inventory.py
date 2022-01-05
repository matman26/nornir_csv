"""Reads CSV file as a Nornir inventory."""
import os
import csv
from nornir.core.inventory import (Inventory,
                                   Hosts,
                                   Host,
                                   Groups,
                                   Group,
                                   Defaults,
                                   BaseAttributes)
from typing import List, Dict, Tuple, Any

attributes = BaseAttributes.__slots__

class CsvInventory:
    def __init__(self, inventory_dir_path: str = "./inventory") -> None:
        self.inventory_dir_path = inventory_dir_path

    def _pop_dict_return(self,in_dict: Dict, key: str) -> Dict:
        copied = in_dict.copy()
        copied.pop(key)
        return copied

    def _csv_to_dictlist(self, csv_file_name: str) -> List[Dict]:
        """Return list of dictionaries with data from csv file."""
        print(f"Opening file {csv_file_name}")
        with open(csv_file_name,'r') as _f:
            dict_reader = csv.DictReader(_f)
            dict_list = list(dict_reader)
        return dict_list

    def _get_hosts_and_groups(self) -> Tuple[Hosts, Groups]:
        host_list = self._csv_to_dictlist(
            os.path.join(self.inventory_dir_path,
                         'hosts.csv'))
        hosts_data = Hosts({
            item['name'] : Host(**item) for item in host_list })
        return Hosts(**hosts_data), Groups()

    def _get_defaults(self) -> Defaults:
        defaults = self._csv_to_dictlist(
            os.path.join(self.inventory_dir_path,
                         'defaults.csv'))[0]
        defaults_dict = {}
        for item in attributes:
            if item in defaults.keys():
                defaults_dict[item] = defaults[item]
                defaults.pop(item)
        defaults_dict['data'] = {**defaults}
        return Defaults(**defaults_dict)

    def load(self) -> Inventory:
        # Load data from three csv files as dict (hosts, groups,defaults)
        hosts, groups = self._get_hosts_and_groups()
        defaults = self._get_defaults()
        # Pass dict to their respective function, generate Hosts, Groups and Defaults objects.
        return Inventory(hosts=hosts, groups=groups, defaults=defaults)
