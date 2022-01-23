"""Reads CSV file as a Nornir inventory."""
from nornir.core.inventory import Inventory, ParentGroups
from nornir.core.inventory import Hosts
from nornir.core.inventory import Host
from nornir.core.inventory import Groups
from nornir.core.inventory import Group
from nornir.core.inventory import Defaults
from nornir.core.inventory import ConnectionOptions
from nornir.core.inventory import BaseAttributes
from typing import List, Dict, Tuple
import os
import csv

def sanitize_dictlist(dict_list):
    """Do some cleanup. String 'True' and 'False' must be
    interpreted as bool values. Empty string should evaluate
    to None."""
    for element in dict_list:
        for key,value in element.items():
            if   value == 'False': element[key] = False
            if   value == 'True' : element[key] = True
            if   value == ''     : element[key] = None
            else: element[key] = element[key]
    return dict_list

def csv_to_dictlist(csv_file_name: str) -> List[Dict]:
    """Return list of dictionaries with data from csv file."""
    if not os.path.exists(csv_file_name):
        return [{}]
    try:
        with open(csv_file_name,'r') as _f:
            dict_reader = csv.DictReader(_f)
            dict_list = list(dict_reader)
            # DictReader by default reads empty fields as '' which
            # blocks defaults from loading properly...
            dict_list = sanitize_dictlist(dict_list)
    except FileNotFoundError:
        dict_list = [{}]
    return dict_list

def get_defaults_from_file(defaults_file: str) -> Defaults:
    defaults = csv_to_dictlist(defaults_file)[0]
    if defaults == {}:
        return Defaults()

    defaults_dict = {}
    if defaults != [{}]:
        for item in CsvInventory.base_attributes:
            if item in defaults.keys():
                defaults_dict[item] = defaults[item]
                defaults.pop(item)
        defaults_dict['data'] = {**defaults}
    return Defaults(**defaults_dict)

def get_connection_options_from_file(connection_options_file: str) -> Dict[str,ConnectionOptions]:
    options = csv_to_dictlist(connection_options_file)
    if options == [{}]:
        return {}

    options_dict = {}
    for co in options:
        if co.get('name',False):
            name = co.pop('name')
            options_dict[name] = {}
            for item in CsvInventory.base_attributes:
                if item in co.keys():
                    options_dict[name][item] = co[item]
                    co.pop(item)
            options_dict[name]['extras'] = {**co}
            options_dict[name] = ConnectionOptions(**options_dict[name])
        else:
            continue

    return options_dict

def read_groups_from_string(groupstring: str) -> List[str]:
    """Convert a space-separated list of groups to python list"""
    grouplist = groupstring.strip().split(' ')
    if isinstance(grouplist, str):
        grouplist = [ grouplist ]
    return grouplist

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
        """
        CsvInventory is a flexible csv-based inventory plugin for Nornir. Hosts,
        Groups, Defaults and Connection Options are each represented by separate
        csv files.

        Args:

          inventory_dir_path: Path to the directory where inventory files are located
          hosts_file: Filename with extension to the hosts file in csv format
          groups_file: Filename with extension to the groups file in csv format
          defaults_file: Filename with extension to the defaults file in csv format
          connection_options_file: Filename with extension to the connection
              options file in csv format
        """
        self.inventory_dir_path = inventory_dir_path
        self.hosts_file = os.path.join(inventory_dir_path, hosts_file)
        self.groups_file = os.path.join(inventory_dir_path, groups_file)
        self.defaults_file = os.path.join(inventory_dir_path, defaults_file)
        self.options_file = os.path.join(inventory_dir_path, options_file)
        self.defaults = get_defaults_from_file(self.defaults_file)
        self.connection_options = get_connection_options_from_file(self.options_file)

    @staticmethod
    def _getfields(hosts: Hosts) -> list:
        fields = list(CsvInventory.extended_attributes)
        for host_data in hosts.values():
            fields.extend([item for item in host_data.data])

        # set completely breaks the fields ordering, use this instead
        seen = set()
        return [ field
                 for field in fields if field not in seen and not seen.add(field) ]

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

    def _organize_hosts_dictlist(self) -> List[Dict]:
        host_list = csv_to_dictlist(self.hosts_file)
        for i, host in enumerate(host_list):
            (host, host['data']) = ({ key: host_list[i].get(key)
                                      for key in self.extended_attributes },
                                    { key: host_list[i].get(key)
                                      for key in host if key
                                      not in self.extended_attributes })
            host_list[i] = host
        return host_list

    def _get_hosts_and_groups(self) -> Tuple[Hosts, ParentGroups]:
        # FIXME: This needs refactoring. Turn this into a function independent
        # from class instance
        host_list = self._organize_hosts_dictlist()
        if host_list == []:
            raise Exception("NoHostsDefined")

        # Gather groups from CSV file
        group_list = csv_to_dictlist(self.groups_file)
        groups_data = Groups()
        if group_list != [{}]:
            for group in group_list:
                data_attributes = {}
                group_name = group['name']
                for attribute in list(group.keys()):
                    if attribute not in CsvInventory.base_attributes:
                        data_attributes[attribute] = group.pop(attribute)
                groups_data[group_name] =  Group(name=group_name,
                                                    **group,
                                                    defaults=self.defaults,
                                                    connection_options=self.connection_options,
                                                    data={**data_attributes})

        # Convert group string (space-separated) into group list for all hosts
        host_groupslist = []
        for host in host_list:
            if host.get('groups'):
                host_groupslist.extend(host['groups'])
                host['groups'] = ParentGroups([
                    #groupname
                    #Group(**groups_data.get(groupname,{'name':groupname}))
                    Group(**groups_data[groupname].dict())
                    if groups_data.get(groupname)
                    else Group(name=groupname)
                    for groupname
                    in read_groups_from_string(host['groups']) ])

        # Create Hosts dict-like object (key is name, value is Host(**kwargs))
        hosts_data = Hosts({item['name']: Host(**item,defaults=self.defaults,
                                               connection_options=self.connection_options)
                            for item in host_list })

        # Enforce unicity as initial list can contain duplicates
        host_groupslist = list(set(host_groupslist))
        if groups_data == {}:
            groups_data = ParentGroups([ Group(name=groupname)
                                         for groupname in host_groupslist])

        return hosts_data, groups_data


    def load(self) -> Inventory:
        # Load data from three csv files as dict (hosts, groups,defaults)
        #connection_options = get_connection_options_from_file(self.options_file)
        hosts, groups = self._get_hosts_and_groups()

        # Pass dict to their respective function, generate Hosts,
        # Groups and Defaults objects.
        return Inventory(hosts=hosts, groups=groups, defaults=self.defaults)

    @staticmethod
    def write(inventory: Inventory,
              dest_file: str = "./inventory/hosts.csv") -> None:
        """Convert current Inventory back to CSV"""
        CsvInventory._write_hosts(dest_file, inventory.hosts)

if __name__ == '__main__':
    pass
