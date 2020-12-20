#!/usr/bin/env python3

# Add a vendor to the RestEasy DB.
# The data for the vendor is taken from a specified input file.

import argparse
import sys

from restore import REStore


def parse_args():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', type=str,
                        help='specify the configuration file')
    parser.add_argument('-i', '--input-file', type=str,
                        help='specify the input (CSV) file')
    return parser.parse_args()


def error_exit(msg, status):
    sys.stderr.write('%s\n' % msg)
    sys.exit(status)


def add_metadata(store, mdline):
    # Format of the metadata line (`mdline') is:
    # NAME;ADDRESS;ADMIN-USERNAME;ADMIN-PASSWORD
    separator = ';'
    name, addr, uname, pword = mdline.split(separator)
    vid = store.add_vendor(name.title(), addr.title())
    store.add_admin(uname, pword, vid)
    return vid


def add_dishes(store, vid, dishes):
    # Format of each dish record/line:
    # ITEM-NAME;PRICE
    separator = ';'
    for dish in dishes:
        item, price = dish.split(separator)
        iid = store.add_item(item.title())
        store.add_dish(iid, vid, price)


# Add a vendor from `vfile' (a file with the vendor data) into the appropriate
# tables in the RestEasy DB.
def add_vendor(store, vfile):
    with open(vfile) as vf:
        lines = [line.strip() for line in vf]

    try:
        vid = add_metadata(store, lines[0]) # First line is the metadata.
        add_dishes(store, vid, lines[1:])   # All other lines are dishes.
    except Exception as e:
        sys.stderr.write('Failed to add vendor: %s\n' % e)
        sys.exit(1)


if __name__ == '__main__':
    args = parse_args()
    if not args.config_file:
        error_exit('config file must be specified', 1)
    if not args.input_file:
        error_exit('input file must be specified', 1)
    store = REStore(args.config_file)
    add_vendor(store, args.input_file)
    store.close()
