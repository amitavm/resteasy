#!/usr/bin/env python3

# This client-side RestEasy app is meant for admins.
# We are building this prototype as a CLI rather than a real browser based UI.

from collections import defaultdict
from datetime import datetime
from getpass import getpass
import json
import os
import requests
import sys
import time

# Project modules.
from reutils import (
    call_api,
    check_tty,
    clear_screen,
    HTTP_OK,
    ping_server,
    quit_app,
    read_choice,
    select
)


# --- Global variables. ---

# This is the URL where we will find the (web) API to use.
apiurl = 'http://localhost:5000/'

# Data about the admin on whose behalf we are acting.
admindata = { 'aid': None, 'uname': None, 'vid': None }


# --- Our "business logic" functions. ---

def print_header():
    clear_screen()
    uname = admindata['uname'] or 'Guest'
    print('\n>>> RestEasy Admin | %s' % uname)


def list_orders(orders):
    header = '%5s  %-25s%-3s' \
             % ('#', 'Item', 'Qty')
    print('-' * len(header))
    print(header)
    print('-' * len(header))
    for i, (_, _, dish, qty) in enumerate(orders, 1):
        print('%5d. %-25s%3d' % (i, dish, qty))
    print('-' * len(header))


def view_all_orders():
    resp = call_api('list-order-by-vid', params={'vid': admindata['vid']})
    if resp.status_code == HTTP_OK:
        all_orders = json.loads(resp.text)
        if len(all_orders) == 0:
            print('\nNo orders have been placed against your restaurant.')
        else:
            orders = []; prev_oid = None; i = 0
            for oid, ts, name, dish, qty in all_orders:
                if oid != prev_oid and orders:
                    # All entries in `orders` should have the same timestamp
                    # and customer: they belong to the same order.
                    dt = datetime.fromtimestamp(orders[0][0])
                    customer = orders[0][1]
                    i += 1
                    print('\n%5d. Order placed on %s at %s by %s'
                          % (i, dt.strftime('%F'), dt.strftime('%T'), customer))
                    list_orders(orders)
                    orders = []
                orders.append((ts, name, dish, qty))
                prev_oid = oid
    else:
        print('Failed to fetch orders')
    input('\nPress <Enter> to return to main menu: ')


def view_orders_on_date():
    print('Sorry, this functionality is not implemented yet...')
    input('\nPress <Enter> to return to main menu: ')
    pass


def login():
    '''Perform the login process for an admin.  Return the "aid" returned by the
    server on success, else return None.'''
    print_header()
    print('\nEnter your credentials to login.')
    uname = input('username: ')
    if not uname:
        print('*** Error: Username cannot be blank/empty.')
    else:
        pword = getpass('password: ')
        resp = call_api('login-admin',
                        params={'username': uname, 'password': pword})
        if resp.status_code == HTTP_OK:
            admindata['aid'], admindata['vid'] = json.loads(resp.text)
            admindata['uname'] = uname
            print('Welcome, %s!' % admindata['uname'])
        else:
            print('Login failed.')
    input('\nPress <Enter> to return to main menu: ')


if __name__ == '__main__':
    check_tty()         # Make sure we are running in a terminal.
    ping_server()       # Make sure the server is reachable.

    # This is the top-level loop.
    while True:
        print_header()
        if admindata['aid'] is None:
            choice = select(choices = [
                ('Login', login),
                ('Quit', quit_app),
            ])
        else:
            choice = select(choices = [
                ('View all of your orders.', view_all_orders),
                ('View your orders on a specific date', view_orders_on_date),
                ('Quit', quit_app),
            ])
