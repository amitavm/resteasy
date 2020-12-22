'''Utility functions used in client apps.'''

import os
import requests
import sys

# --- Variables. ---

# This is the URL where we will find the (web) API to use.
# TODO: This should really be coming from a config file.
apiurl = 'http://localhost:5000/'

# Symbolic constant for HTTP OK status code.
HTTP_OK = 200


# --- Functions. ---

def call_api(endpoint, params={}):
    '''Call the given API `endpoint' with query parameters `params'.'''
    return requests.get(apiurl + endpoint, params)


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


def quit_app():
    print('\nThanks for using RestEasy!  Have a great day!\n')
    sys.exit(0)


def clear_screen():
    os.system('clear')


def read_choice(hi, prompt='Your choice: ', default=None):
    '''Read (and return) an integer from the user in the range [1,hi].
    Prompt the user with `prompt'.  If the user enters no input,
    return `default'.'''
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
