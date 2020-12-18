from flask import Flask, abort, jsonify, request

# Our data layer.
from restore import REStore

app = Flask(__name__)
store = REStore('config.ini')


# --- Helper functions to reduce boilerplate. ---
def get_qparams_or_abort(*qpnames):
    '''Return the values of the named query parameters as a tuple, if present.
    Abort otherwise.'''
    qpvals = []
    for qpname in qpnames:
        qpval = request.args.get(qpname)
        if qpval is None:
            abort(400, "missing parameter '%s'" % qpname)
        qpvals.append(qpval)
    return qpvals


def check_result(val, badval, msg):
    '''Return the value "val" (jsonified), if it does not equal "badval".
    Abort otherwise.'''
    if val == badval:
        abort(400, msg)
    return jsonify(val)


def check_exception(func, *params):
    try:
        func(*params)
    except Exception as e:
        abort(400, e)
    else:
        return jsonify('OK')


# --- API around users. ---
@app.route('/get-uid')
def get_uid():
    username, = get_qparams_or_abort('username')
    return check_result(store.get_uid(username), None,
                        "could not find user '%s'" % username)


@app.route('/add-user')
def add_user():
    params = get_qparams_or_abort('username', 'password', 'fullname', 'phone')
    return check_exception(store.add_user, *params)


@app.route('/del-user')
def del_user():
    params = get_qparams_or_abort('username')
    return check_exception(store.del_user, *params)


# --- API around vendors. ---
@app.route('/list-vendors')
def list_vendors():
    name = get_qparam_or_abort('name')
    return check_result(store.list_vendors(name), [],
                        "'%s' did not match any vendors" % name)
