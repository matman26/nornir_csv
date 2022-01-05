# nornir_csv
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

## Usage
Since this is an external plugin for Nornir 3.0+, it must be registered
before usage. The main project file must therefore contain something similar to:

```python
from nornir import InitNornir
from csv_inventory import CsvInventory
from nornir.core.plugins.inventory import InventoryPluginRegister

InventoryPluginRegister.register("CsvInventoryPlugin", CsvInventory)

nr = InitNornir(inventory={'plugin': 'CsvInventoryPlugin'},
                runner={'plugin': 'threaded','options': {'num_workers': 20}})
```

By default, the plugin will look for the files hosts.csv, groups.csv and defaults.csv inside the ./inventory/ directory, but the directory can be changed by specifying the plugin option `inventory_dir_path`
