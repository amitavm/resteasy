from flask import Flask, abort, jsonify, request

# Our data layer.
from restore import REStore

app = Flask(__name__)
store = REStore('config.ini')


# --- Helper functions to reduce boilerplate. ---
def get_qparams_or_abort(*qpnames):
    '''Return the values of the named query parameters as a tuple, if present.
    Abort otherwise.'''
    for arg in request.args:
        if arg not in qpnames:
            abort(400, "unexpected parameter '%s'" % arg)

    qpvals = []
    for qpname in qpnames:
        qpval = request.args.get(qpname)
        if qpval is None:
            abort(400, "missing parameter '%s'" % qpname)
        qpvals.append(qpval)

    return qpvals


def check_result(val, badval, msg, stcode=400):
    '''Return the value "val" (jsonified), if it does not equal "badval".
    Abort otherwise.'''
    if val == badval:
        abort(stcode, msg)
    return jsonify(val)


def check_exception(func, *params):
    try:
        func(*params)
    except Exception as e:
        abort(400, e)
    else:
        return jsonify('OK')


# --- General endpoints. ---
@app.route('/ping')
def ping():
    return jsonify('OK')


# --- API around users. ---
@app.route('/get-uid')
def get_uid():
    username, = get_qparams_or_abort('username')
    return check_result(store.get_uid(username), None,
                        "could not find user '%s'" % username)


@app.route('/user-exists')
def user_exists():
    uname, = get_qparams_or_abort('username')
    return jsonify(store.user_exists(uname))


@app.route('/add-user')
def add_user():
    params = get_qparams_or_abort('username', 'password', 'fullname', 'phone')
    return check_exception(store.add_user, *params)


@app.route('/del-user')
def del_user():
    params = get_qparams_or_abort('username')
    return check_exception(store.del_user, *params)


@app.route('/login-user')
def login_user():
    params = get_qparams_or_abort('username', 'password')
    return check_result(store.check_user_credentials(*params), None,
                        "incorrect username and/or password", 401)


@app.route('/user-data')
def get_user_data():
    params = get_qparams_or_abort('uid')
    return check_result(store.user_data(*params), None, 'invalid user ID', 400)


# --- API around admins. ---
@app.route('/add-admin')
def add_admin():
    params = get_qparams_or_abort('username', 'password', 'vid')
    return check_exception(store.add_admin, *params)


@app.route('/del-admin')
def del_admin():
    params = get_qparams_or_abort('username')
    return check_exception(store.del_admin, *params)


@app.route('/login-admin')
def login_admin():
    params = get_qparams_or_abort('username', 'password')
    return check_result(store.check_admin_credentials(*params), None,
                        "incorrect username and/or password", 401)


# --- API around vendors. ---
@app.route('/list-vendors')
def list_vendors():
    return jsonify(store.list_vendors())


@app.route('/list-vendors-by-name')
def list_vendors_by_name():
    name, = get_qparams_or_abort('name')
    return jsonify(store.list_vendors_by_name(name))


# --- API around dishes. ---
@app.route('/list-dishes-by-vendor')
def list_dishes_by_vendor():
    vid, = get_qparams_or_abort('vid')
    return jsonify(store.list_dishes_by_vendor(vid))


@app.route('/list-dishes-by-name')
def list_dishes_by_name():
    name, = get_qparams_or_abort('name')
    return jsonify(store.list_dishes_by_name(name))


# --- API around orders. ---
@app.route('/add-order')
def add_order():
    uid, ts = get_qparams_or_abort('uid', 'timestamp')
    return jsonify(store.add_order(uid, ts))


@app.route('/add-order-dish')
def add_order_dish():
    oid, did, qty = get_qparams_or_abort('oid', 'did', 'quantity')
    try:
        store.add_order_dish(oid, did, qty)
    except Exception:
        abort(500, 'failed to order dish')
    else:
        return jsonify('OK')


@app.route('/list-order-by-uid')
def list_order_by_uid():
    uid, = get_qparams_or_abort('uid')
    return jsonify(store.list_order_by_uid(uid))
