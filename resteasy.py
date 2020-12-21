#!/usr/bin/env python3

# This is the client-side (UI) of RestEasy, to be used by users.
# We are building this prototype as a CLI rather than a real browser based UI.

from collections import defaultdict
from datetime import datetime
from getpass import getpass
import json
import os
import requests
import sys
import time


# --- Global variables. ---

# This is the URL where we will find the (web) API to use.
apiurl = 'http://localhost:5000/'

# Data about the user on whose behalf we are acting.
userdata = { 'uid': None, 'uname': None, 'fname': None, 'phone': None, }

# The dishes (and their quantities) selected by the user so far.
cart = []

# Max quantities of a dish we allow to be ordered.
max_qty = 9

# Symbolic constant for HTTP OK status code.
HTTP_OK = 200


# --- Wrapper functions around API calls. ---


def call_api(endpoint, params={}):
    return requests.get(apiurl + endpoint, params)


def user_exists(uname):
    resp = call_api('user-exists', params={'username': uname})
    return json.loads(resp.text)


def get_user_data(uid):
    '''Get data for a user with a given "uid".'''
    resp = call_api('user-data', params={'uid': uid})
    return json.loads(resp.text)


def list_vendors():
    resp = call_api('list-vendors')
    return json.loads(resp.text)


def list_vendors_by_name():
    print_header()
    print('\nEnter full/partial name of vendor(s).')
    print('Or just press <Enter> to return to main menu.')
    name = input('Vendor name: ')
    if not name:
        return

    resp = call_api('list-vendors-by-name', params={'name': name})
    vendors = json.loads(resp.text)
    if not vendors:
        print('\nNo matching vendors found.')
        input('Press <Enter> to return to main menu: ')
        return
    else:
        print('\nMatching vendors:\n')
        header = '%5s  %-25s%-30s' % ('#', 'Name', 'Address')
        print('-' * len(header))
        print(header)
        print('-' * len(header))
        for i, (_, name, addr) in enumerate(vendors, 1):
            print('%5d. %-25s%-30s' % (i, name, addr))
        print('-' * len(header))

    print('\nSelect a vendor to list its dishes.')
    print('Or just press <Enter> to return to previous menu.')
    n = read_choice(len(vendors), 'Vendor to list: ')
    if n:
        list_dishes_by_vendor(vendors[n-1])


def list_dishes_by_name():
    print_header()
    print('\nEnter full/partial name of dishes.')
    print('Or just press <Enter> to return to main menu.')
    name = input('Dish name: ')
    if not name:
        return

    resp = call_api('list-dishes-by-name', params={'name': name})
    dishes = json.loads(resp.text)
    if not dishes:
        print('\nNo matching dishes found.')
        input('Press <Enter> to return to main menu: ')
        return
    else:
        print('\nMatching dishes:')
        header = '%5s  %-25s%-20s%8s' % ('#', 'Item', 'Vendor', 'Price')
        print('-' * len(header))
        print(header)
        print('-' * len(header))
        for i, (_, item, vendor, price) in enumerate(dishes, 1):
            print('%5d. %-25s%-20s%8.2f' % (i, item, vendor, price))
        print('-' * len(header))

    while True:
        print('\nSelect a dish to add it to the cart.')
        print('Or just press <Enter> to return to previous menu.')
        n = read_choice(len(dishes), 'Dish to select: ')
        if not n:
            return

        print('\nEnter the repeat-count (max %d) for "%s".'
              % (max_qty, dishes[n-1][1]))
        print('Or just press <Enter> to order one portion of it.')
        qty = read_choice(max_qty, 'Number of portions to order: ', default=1)
        cart.append(dishes[n-1] + [qty])


def list_dishes_by_vendor(vendor_data):
    print_header()
    vid, vname, _ = vendor_data
    resp = call_api('list-dishes-by-vendor', params={'vid': vid})
    dishes = json.loads(resp.text)
    if not dishes:
        print('\nNo dishes found.')
        input('Press <Enter> to return to main menu: ')
        return
    else:
        print('\nDishes offered by "%s":\n' % vname)
        header = '%5s  %-25s%8s' % ('#', 'Item', 'Price')
        print('-' * len(header))
        print(header)
        print('-' * len(header))
        for i, (_, item, _, price) in enumerate(dishes, 1):
            print('%5d. %-25s%8.2f' % (i, item, price))
        print('-' * len(header))

    while True:
        print('\nSelect a dish to add it to the cart.')
        print('Or just press <Enter> to return to previous menu.')
        n = read_choice(len(dishes), 'Dish to select: ')
        if not n:
            return

        print('\nEnter the repeat-count (max %d) for "%s".'
              % (max_qty, dishes[n-1][1]))
        print('Or just press <Enter> to order one portion of it.')
        qty = read_choice(max_qty, 'Number of portions to order: ', default=1)
        cart.append(dishes[n-1] + [qty])


def show_dishes(dishes):
    header = '%5s  %-25s%-20s%8s%5s%8s' \
             % ('#', 'Item', 'Vendor', 'Price', 'Qty', 'Totals')
    print('-' * len(header))
    print(header)
    print('-' * len(header))
    total = 0
    for i, (_, item, vendor, price, qty) in enumerate(dishes, 1):
        item_price = price * qty
        print('%5d. %-25s%-20s%8.2f%5d%8.2f'
              % (i, item, vendor, price, qty, item_price))
        total += item_price
    print('-' * len(header))
    print('%65s%8.2f' % ('Net price: ', total))
    print('-' * len(header))


def view_cart():
    print_header()
    if len(cart) == 0:
        print('\nNo entries found in cart.')
        input('Press <Enter> to return to main menu: ')
    else:
        print('\nCart entries:')
        show_dishes(cart)
        print('\nEnter "y|yes" to place the order.')
        print('Or just press <Enter> to return to main menu.')
        resp = input('Place order?  Enter "y|yes" to confirm: ')
        if resp and (resp.lower() == 'y' or resp.lower() == 'yes'):
            place_order()


def view_orders():
    print_header()
    resp = call_api('list-order-by-uid', params={'uid': userdata['uid']})
    if resp.status_code != HTTP_OK:
        print('\nFailed to fetch your orders.')
    else:
        ordlist = json.loads(resp.text)
        if len(ordlist) == 0:
            print('\nCould not find any orders placed by you.')
        else:
            print('\nOrders placed by you:')
            orders = defaultdict(list)
            # Segregate the orders by (order-id, timestamp) pairs.
            # NOTE: We include None's in the tuples below, as placeholders for
            # dish-IDs, so that we can reuse show_dishes().
            for oid, ts, item, vendor, price, qty in ordlist:
                orders[(oid, ts)].append((None, item, vendor, price, qty))

            for i, ((oid, ts), dishes) in enumerate(orders.items(), 1):
                dt = datetime.fromtimestamp(ts)
                print('\n%5d. Order placed on %s at %s'
                      % (i, dt.strftime('%F'), dt.strftime('%T')))
                show_dishes(dishes)
    input('\nPress <Enter> to return to main menu: ')


def place_order():
    ts = int(time.time())   # NOTE: We ignore fractions of a second for now.
    resp = call_api('add-order',
                    params={'uid': userdata['uid'], 'timestamp': ts})
    if resp.status_code == HTTP_OK:
        oid = resp
        for did, _, _, _, qty in cart:
            call_api('add-order-dish',
                     params={'oid': oid, 'did': did, 'quantity': qty})
        print('Order placed successfully!')
    else:
        print('Failed to place order.')
    input('Press <Enter> to return to main menu: ')


# --- General support/utility functions. ---

def error_exit(msg):
    sys.stderr.write('%s: error: %s\n' % (sys.argv[0], msg))
    sys.exit(1)


def check_tty():
    if not sys.stdin.isatty():
        error_exit('not running in a terminal; exiting')


def ping_server():
    try:
        resp = requests.get(apiurl + 'ping')
    except Exception:
        error_exit('cannot contact server; exiting')


def login():
    '''Perform the login process for a user.  Return the "uid" returned by the
    server on success, else return None.'''
    print_header()
    print('\nEnter your credentials to login.')
    uname = input('username: ')
    if not uname:
        print('*** Error: Username cannot be blank/empty.')
    else:
        pword = getpass('password: ')
        resp = call_api('login-user',
                        params={'username': uname, 'password': pword})
        if resp.status_code == HTTP_OK:
            userdata['uid'] = resp
            data = get_user_data(userdata['uid'])
            userdata['uname'], userdata['fname'], userdata['phone'] = data
            print('Welcome, %s!' % userdata['fname'])
        else:
            print('Login failed.')
        input('\nPress <Enter> to return to main menu: ')


def signup():
    '''Perform the signup process for a new user.'''
    uname = input('Username: ')
    if user_exists(uname):
        print('Sorry, that username is already taken!')
    else:
        print('OK, that username is available.  Congratulations!')


def quit():
    print('\nThanks for using RestEasy!  Have a great day!\n')
    sys.exit(0)


def clear_screen():
    os.system('clear')


def print_header():
    clear_screen()
    name = userdata['fname'] or 'Guest'
    print('\n>>> RestEasy | %s' % name)


def read_choice(hi, prompt='Your choice: ', default=None):
    while True:
        i = input(prompt)
        if not i:
            return default

        try:
            i = int(i)
            if 1 <= i <= hi:
                return i
            else:
                print('Please enter a choice between 1 and %d.' % hi)
        except Exception:
            print('Sorry, that is not an integer; try again.')


def select(choices):
    '''Ask the user to make a choice from "choices".
    Invoke the corresponding action/function.'''
    print('\nSelect an option by entering its number on the left.')
    print('Or just press <Enter> to return to previous menu.')
    for i, c in enumerate(choices, 1):
        print('   %2d. %s' % (i, c[0]))
    n = read_choice(len(choices))
    if n:
        choices[n-1][1]()


if __name__ == '__main__':
    check_tty()     # Make sure we are running in a terminal.
    ping_server()   # Make sure the server is reachable.

    # This is the top-level loop.
    while True:
        print_header()
        if userdata['uid'] is None:
            choice = select(choices = [
                ('Signup [If you do not have login credentials.]', signup),
                ('Login  [If you already signed up.]', login),
                ('Quit', quit),
            ])
        else:
            choice = select(choices = [
                ('List vendors by name.', list_vendors_by_name),
                ('List dishes by name.', list_dishes_by_name),
                ('View cart.  (And optionally place the order.)', view_cart),
                ('View orders placed by you.', view_orders),
                ('Quit', quit),
            ])
