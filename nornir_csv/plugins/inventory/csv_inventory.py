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

base_attributes = BaseAttributes.__slots__

class CsvInventory:
    def __init__(self,
                 inventory_dir_path: str = "./inventory",
                 hosts_file: str = "hosts.csv",
                 groups_file: str = "groups.csv",
                 defaults_file: str = "defaults.csv"
                 ) -> None:
        self.inventory_dir_path = inventory_dir_path
        self.hosts_file = hosts_file
        self.groups_file = groups_file
        self.defaults_file = defaults_file

    # FIXME This could be a lambda but I'll leave it as a function for now
    def _pop_dict_return(self,in_dict: Dict, key: str) -> Dict:
        copied = in_dict.copy()
        copied.pop(key)
        return copied

    def _csv_to_dictlist(self, csv_file_name: str) -> List[Dict]:
        """Return list of dictionaries with data from csv file."""
        try:
            with open(csv_file_name,'r') as _f:
                dict_reader = csv.DictReader(_f)
                dict_list = list(dict_reader)
        except FileNotFoundError:
            dict_list = [{}]
        except Exception as e:
            raise e

        return dict_list

    def _read_groups_from_string(self, groupstring: str) -> List[str]:
        """Convert a space-separated list of groups to python list"""
        grouplist = groupstring.strip().split(' ')
        return grouplist

    def _get_hosts_and_groups(self) -> Tuple[Hosts, Groups]:
        host_list = self._csv_to_dictlist(
            os.path.join(self.inventory_dir_path,
                         self.hosts_file))

        if host_list == []:
            raise Exception("NoHostsDefined")

        # Convert group string (space-separated) into group list for all hosts
        host_groupslist = []
        for host in host_list:
            if host.get('groups'):
                host['groups'] = self._read_groups_from_string(groupstring = host['groups'])
                host_groupslist.extend(host['groups'])

        # Create Hosts dict-like object (key is name, value is Host(**kwargs))
        hosts_data = Hosts({
            item['name'] : Host(**item) for item in host_list })

        # Enforce unicity as initial list can contain duplicates
        host_groupslist = list(set(host_groupslist))

        # Gather groups from CSV file
        group_list = self._csv_to_dictlist(
            os.path.join(self.inventory_dir_path,
                         self.groups_file))

        groups_data = Groups()
        # Check if any groups were read from csv file
        if group_list == [{}]:
            # Check if any group was read from a host instead of the csv
            if host_groupslist == []:
                # If no grouplist was found on hosts, there are no groups defined.
                pass
            else:
                # If a grouplist was found from hosts, simply populate their names without any
                # other attributes
                for group in host_groupslist:
                    groups_data[group] = Group(name=group)
        else:
            # If groups were read, do some dict unpacking to pass attributes to the Group class,
            # build Groups dict
            groups_data = Groups()
            for group in group_list:
                data_attributes = {}
                group_name = group['name']
                for attribute in list(group.keys()):
                    if attribute not in base_attributes:
                        data_attributes[attribute] = group.pop(attribute)
                groups_data[group_name] =  Group(name=group_name, **group, data={**data_attributes})
        return hosts_data, groups_data

    def _get_defaults(self) -> Defaults:
        defaults = self._csv_to_dictlist(
            os.path.join(self.inventory_dir_path,
                         self.defaults_file))[0]
        defaults_dict = {}
        # Check if defaults file is not empty
        if defaults != []:
            for item in base_attributes:
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
