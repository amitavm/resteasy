#!/usr/bin/env python3

# This is the client-side (UI) of RestEasy, to be used by users.
# We are building this prototype as a CLI rather than a real browser based UI.

from getpass import getpass
import json
import requests
import sys

# This is the URL where we will find the (web) API to use.
apiurl = 'http://localhost:5000/'


def error_exit(msg):
    sys.stderr.write('%s: error: %s\n' % (sys.argv[0], msg))
    sys.exit(1)


def call_api(endpoint, params={}):
    return requests.get(apiurl + endpoint, params)


def login_user():
    '''Perform the login process for a user.  Return the "uid" returned by the
    server on success, else return None.'''
    uname = input('Username: ')
    pword = getpass()
    resp = call_api('login-user', params={'username': uname, 'password': pword})
    return (True if resp.status_code == 200 else False), resp.text


def get_user_data(uid):
    '''Get data for a user with a given "uid".'''
    resp = call_api('user-data', params={'uid': uid})
    return json.loads(resp.text)


def ping_server():
    try:
        resp = requests.get(apiurl + 'ping')
    except Exception as e:
        error_exit('cannot contact the server... exiting')


if __name__ == '__main__':
    ping_server()
    success, resp = login_user()
    if not success:
        error_exit('login failed: %s' % resp)
    else:
        uid = resp
        uname, fname, phone = get_user_data(uid)
        print('Welcome to RestEasy, %s!' % fname)
