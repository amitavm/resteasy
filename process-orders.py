#!/usr/bin/env python3

# Process a set of orders.  Modifies the `orders' and `orderlist' tables.
# The info for each order is taken from a specified CSV file.

import argparse
import sys
import time

from restore import REStore


def parse_args():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', type=str,
                        help='specify the configuration file')
    parser.add_argument('-i', '--input-file', type=str,
                        help='specify the input (CSV) file')
    parser.add_argument('-u', '--user', type=str,
                        help='specify the user placing the order')
    return parser.parse_args()


def error_exit(msg, status):
    sys.stderr.write('Failed to process order: %s\n' % msg)
    sys.exit(status)


def get_uid_or_exit(store, uname):
    uid = store.get_uid(uname)
    if uid is None:
        error_exit('invalid user "%s"' % uname)
    return uid


def get_iid_or_exit(store, item):
    iid = store.get_iid(item)
    if iid is None:
        error_exit('invalid item "%s"' % item)
    return iid


def get_vid_or_exit(store, vendor):
    vid = store.get_vid(vendor)
    if vid is None:
        error_exit('invalid vendor "%s"' % vendor)
    return vid


def get_did_or_exit(store, item, vendor):
    iid = get_iid_or_exit(store, item)
    vid = get_vid_or_exit(store, vendor)
    did = store.get_did(iid, vid)
    if did is None:
        error_exit('vendor "%s" does not offer dish "%s"' % (vendor, item))
    return did


# Place orders from `ofile' (a CSV file with order data).
def process_orders(store, uname, ofile):
    orders = []
    with open(ofile) as of:
        separator = ','
        for line in of:
            line = line.strip()
            item, vendor, qty = line.split(separator)
            did = get_did_or_exit(store, item, vendor)
            orders.append((did, qty))

    ts = int(time.time())
    uid = get_uid_or_exit(store, uname)
    oid = store.add_order(uid, ts)
    for did, qty in orders:
        store.add_order_dish(oid, did, qty)


if __name__ == '__main__':
    args = parse_args()
    if not args.config_file:
        error_exit('config file must be specified', 1)
    if not args.input_file:
        error_exit('input file must be specified', 1)
    if not args.user:
        error_exit('user must be specified', 1)
    store = REStore(args.config_file)
    process_orders(store, args.user, args.input_file)
    store.close()
