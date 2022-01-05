# nornir_csv
[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/matman26/nornir_csv)

Use CSV files as a Nornir Inventory source with hosts, groups and defaults.
This can be used as an equivalent to the Simple Inventory plugin but 
using CSV files instead of YAML. This does not generate any new files,
but instead reads host data from three files:
+ hosts.csv
+ groups.csv
+ defaults.csv

## Installation
As of right now, the code hasn't been published to PyPi, so it must be
installed from source. Be sure to clone the repository locally:

```
cd /directory/where/you/clone/git/stuff/
git clone https://github.com/matman26/nornir_csv.git
```

The nornir_csv directory can then be copied to your project root and added
as an external library.

```
cp nornir_csv/nornir_csv /destination/project/root
```

## Usage
Since this is an external plugin for Nornir 3.0+, it must be registered
before usage. The main project file must therefore contain something similar to:

```python
from nornir import InitNornir
from nornir_csv.plugins.inventory.csv_inventory import CsvInventory
from nornir.core.plugins.inventory import InventoryPluginRegister

InventoryPluginRegister.register("CsvInventoryPlugin", CsvInventory)

nr = InitNornir(config_file='sample_config.yaml')
```

By default, the plugin will look for the files hosts.csv, groups.csv and defaults.csv inside the 
./inventory/ directory, but the directory can be changed by specifying the plugin option 
`inventory_dir_path`. A sample file such as below can be used:

```yaml
inventory:
  plugin: CsvInventoryPlugin
  options:
    inventory_dir_path: /path/to/inventory/dir/
runner:
  plugin: threaded
  options:
    num_workers: 20
```

The name of the csv files to be read for hosts, groups and defaults can also be customized by setting the options `hosts_file`, `groups_file` and `defaults_file`, respectively. These should correspond to the file's basenames (no paths) with extension, if any.

## CSV Syntax
### Hosts
The `hosts_file` follows a specific syntax to make it nornir-compatible, see sample below:
```csv
name,hostname,username,password,port,platform,groups,custom_var
R1,192.168.122.10,cisco,cisco,22,cisco_ios,core main,foo
R2,192.168.122.20,cisco,cisco,22,cisco_xr,,bar
```

Note that name, hostname, username, password, port, platform and groups are nornir
base attributes. This means they are hosts attributes directly, such that
```python
nr.inventory.hosts['R1'].password
```

will yield the return value of 'cisco' as expected. Any custom variables that are
added will be put inside the 'data' dictionary on the target host. So

```python
nr.inventory.hosts['R1'].data['custom_var']
```

will return 'foo'.

Notice also that to specify the list of groups to which a host belongs the list must be 
specified one group at a time, separated by spaces. In the csv above, R1 belongs to the
groups 'core' and 'main'. A hosts file is mandatory.

### Groups
The `groups_file` is optional. It can be used to set 
default values for the base attributes of each host (for example, if every host of the same
group uses the same credentials). Any attributes that are non-base attributes will
be added to the 'data' container inside the generated group, similar to how it 
behaves with hosts. If no groups are specified in the csv file, hosts can still be assigned 
to groups but these will hold no data.

```csv
name,username,password,dns_server
core,cisco,cisco,8.8.8.8
main,,,,
```

Notice that the groups csv does not have any mandatory fields other than name.

### Defaults
The `defaults_file` specifies any default variables. This file is also free-form, but is only 
composed of two lines: a header with the name of the variable and a second line with 
its value. The defaults file is optional.

```csv
message_of_the_day,foo,port
hello world!,bar,22
```
