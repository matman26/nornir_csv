"""Reads CSV file as a Nornir inventory."""
from nornir.core.inventory import Inventory
from nornir.core.inventory import Hosts
from nornir.core.inventory import Host
from nornir.core.inventory import Groups
from nornir.core.inventory import Group
from nornir.core.inventory import Defaults
from nornir.core.inventory import BaseAttributes
from nornir.core.configuration import Config
from typing import List, Dict, Tuple, Any
import os
import csv



class CsvInventory:
    base_attributes = BaseAttributes.__slots__
    extended_attributes = ('name', 'hostname', 'username',
                           'password', 'platform', 'groups', 'port')

    def __init__(self,
                 inventory_dir_path: str = "./inventory",
                 hosts_file: str = "hosts.csv",
                 groups_file: str = "groups.csv",
                 defaults_file: str = "defaults.csv",
                 options_file: str = "connection_options.csv"
                 ) -> None:
        self.inventory_dir_path = inventory_dir_path
        self.hosts_file = os.path.join(inventory_dir_path, hosts_file)
        self.groups_file = os.path.join(inventory_dir_path, groups_file) 
        self.defaults_file = os.path.join(inventory_dir_path, defaults_file)
        self.connection_options = os.path.join(inventory_dir_path, options_file)

    @staticmethod
    def _getfields(hosts: Hosts) -> list:
        fields = list(CsvInventory.extended_attributes)
        for host, host_data in hosts.items():
            fields.extend([item for item in host_data.data])

        # set completely breaks the fields ordering, use this instead
        seen = set()
        return [ field for field in fields if field not in seen and not seen.add(field) ]


    @staticmethod
    def _write_hosts(dest_file: str, hosts: Hosts) -> None:
        """Write hosts dict back to file"""
        with open(dest_file,'w') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=CsvInventory._getfields(hosts),
                                    extrasaction='ignore')
            writer.writeheader()
            for host, parameters in hosts.items():
                host_dict = { **parameters.dict(), **parameters.dict()['data'] }
                if host_dict.get('groups',False):
                    host_dict['groups'] = " ".join(host_dict['groups'])
                writer.writerow(host_dict)

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

    # FIXME This could be a lambda but I'll leave it as a function for now
    def _pop_dict_return(self,in_dict: Dict, key: str) -> Dict:
        copied = in_dict.copy()
        copied.pop(key)
        return copied

    def _organize_hosts_dictlist(self) -> List:
        host_list = self._csv_to_dictlist(self.hosts_file)
        for i, host in enumerate(host_list):
            host, host['data'] = { key: host_list[i].get(key) for key in self.extended_attributes }, { key: host_list[i].get(key) for key in host if key not in self.extended_attributes }
            #host['data'] = 
            host_list[i] = host

        return host_list

    def _get_hosts_and_groups(self) -> Tuple[Hosts, Groups]:
        #host_list = self._csv_to_dictlist(self.hosts_file)
        host_list = self._organize_hosts_dictlist()
        if host_list == []:
            raise Exception("NoHostsDefined")

        # Convert group string (space-separated) into group list for all hosts
        host_groupslist = []
        for host in host_list:
            if host.get('groups'):
                host['groups'] = [
                    Group(name=groupname)
                    for groupname
                    in self._read_groups_from_string(host['groups']) ]

                host_groupslist.extend(host['groups'])
        
        # Create Hosts dict-like object (key is name, value is Host(**kwargs))
        hosts_data = Hosts({item['name']: Host(**item) for item in host_list })

        # Enforce unicity as initial list can contain duplicates
        host_groupslist = list(set(host_groupslist))

        # Gather groups from CSV file
        group_list = self._csv_to_dictlist(self.groups_file)

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
                    if attribute not in CsvInventory.base_attributes:
                        data_attributes[attribute] = group.pop(attribute)
                groups_data[group_name] =  Group(name=group_name, **group, data={**data_attributes})
        return hosts_data, groups_data

    def _get_defaults(self) -> Defaults:
        defaults = self._csv_to_dictlist(self.defaults_file)[0]
        defaults_dict = {}
        # Check if defaults file is not empty
        if defaults != []:
            for item in CsvInventory.base_attributes:
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

    @staticmethod
    def write(inventory: Inventory, dest_file: str ="./inventory/hosts.csv") -> None:
        """Convert current Inventory back to CSV"""
        CsvInventory._write_hosts(dest_file, inventory.hosts)


if __name__ == '__main__':
    pass
