#!/usr/bin/env python3
"""Extract labels from IDA .lst and export to x64dbg database.

This script extracts all the labels found in the LST file that is given as
the script's single argument. An x64dbg database is created in the current
directory based on the extracted labels.

Example:

    $ python3 lst2x64dbg.py sample.lst

Todo:
    * Convert to package with console script
"""
import argparse
import json
import pathlib
import re
import sys

parser = argparse.ArgumentParser(description='Extract labels from IDA .lst file and export x64dbg database.')
parser.add_argument('lst', metavar='LST', help='Filename or path of target LST file.')
parser.add_argument('-p', '--pretty', action='store_true', help='Pretty print the database JSON.')
parser.add_argument('-m', '--module', help='Specify the module name.')
args = parser.parse_args()

lst_file = pathlib.Path(args.lst)
if not lst_file.exists():
    sys.exit('ERROR: File `{}` does not exist'.format(lst_file.name))

with open(lst_file, 'r') as fh:
    lst_data = fh.read()

match = re.search('Imagebase +: (?P<imagebase>[0-9A-F]+$)', lst_data, flags=re.M)
if not match:
    sys.exit('ERROR: Imagebase not found')
imagebase = int(match.group('imagebase'), 16)

if args.module:
    module_name = args.module
else:
    module_name = '{}.exe'.format(lst_file.stem)

labels_raw = re.findall(r'^.+:(?P<offset>[0-9A-F]{8}) {17}public (?P<label>\w+)$', lst_data, flags=re.M | re.A)
labels = list()
for address, label in labels_raw:
    stripped = address.lstrip('0')
    hex_int = int(stripped, 16)
    offset = hex(hex_int - imagebase)
    label_entry = {'module': module_name,
                   'address': '0x{}'.format(offset[2:].upper()),
                   'manual': False,
                   'text': label}
    labels.append(label_entry)

x64dbg_db = {'labels': labels}

here = pathlib.Path.cwd()
x64dbg_db_file = here.joinpath('{}.dd32'.format(lst_file.stem))

if args.pretty:
    x64dbg_db_str = json.dumps(x64dbg_db, sort_keys=True, indent=4)
else:
    x64dbg_db_str = json.dumps(x64dbg_db)

with open(x64dbg_db_file, 'w') as fh:
    fh.write(x64dbg_db_str)

print('Exported x64dbg database: {}'.format(x64dbg_db_file.name))
if args.module:
    print('Module name: {}'.format(args.module))
sys.exit()