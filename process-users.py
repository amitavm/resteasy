#!/usr/bin/env python3

# Process a set of users.  Modifies the `users' table.
# The info for each user is taken from a specified CSV file.

import argparse
import sys

from restore import REStore


def parse_args():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=str, choices=['add', 'del'],
                        default='add', help='specify the configuration file')
    parser.add_argument('-c', '--config-file', type=str,
                        help='specify the configuration file')
    parser.add_argument('-i', '--input-file', type=str,
                        help='specify the input (CSV) file')
    return parser.parse_args()


def error_exit(msg, status):
    sys.stderr.write('%s\n' % msg)
    sys.exit(status)


# Add users from `ufile' (a CSV file with user data) into the `users' table.
def add_users(store, ufile):
    with open(ufile) as uf:
        for line in uf:
            line = line.strip()
            uname, pword, fname, phone = line.split(',')
            try:
                store.add_user(uname, pword, fname, phone)
            except Exception as e:
                sys.stderr.write(
                    'Failed to add user "%s": %s.  Ignored.\n' % (uname, e))


# Delete users from `ufile' (a CSV file with user data) from the `users' table.
def del_users(store, ufile):
    with open(ufile) as uf:
        for line in uf:
            line = line.strip()
            uname, _, _, _ = line.split(',')
            store.del_user(uname)


# Mapping of actions to the corresponding processors.
processor = {'add': add_users, 'del': del_users}


if __name__ == '__main__':
    args = parse_args()
    if not args.config_file:
        error_exit('config file must be specified', 1)
    if not args.input_file:
        error_exit('input file must be specified', 1)
    store = REStore(args.config_file)
    processor[args.action](store, args.input_file)
    store.close()
