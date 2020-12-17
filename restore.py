# This module implements one possible Data Layer for RestEasy, using SQLite3.

import configparser
import sqlite3


class REStore:
    '''
    Abstraction of the data store used in our app.

    Currently we use SQLite3 to store the data.
    This class is a wrapper around the DB: it provides an API on top of it.
    '''
    def __init__(self, cfile):
        self.__config = self.__read_config(cfile)
        self.__conn = self.__init_db(self.__config['dbfile'])
        self.__tbl_users = _TableUsers(self.__conn)
        self.__tbl_admins = _TableAdmins(self.__conn)
        self.__tbl_vendors = _TableVendors(self.__conn)
        self.__tbl_items = _TableItems(self.__conn)
        self.__tbl_dishes = _TableDishes(self.__conn)
        self.__tbl_orders = _TableOrders(self.__conn)
        self.__tbl_orderlist = _TableOrderList(self.__conn)


    def __init_db(self, dbfile):
        try:
            conn = sqlite3.connect(dbfile)
            # NOTE: SQLite3 requires us to explicitly enable foreign-key
            # support at runtime.
            conn.execute('PRAGMA foreign_keys = ON;')
            return conn
        except Exception as e:
            raise RuntimeError('failed to connect with DB: %s' % e)


    # Read the config at startup.
    def __read_config(self, cfile):
        config = configparser.ConfigParser()
        config.read(cfile)
        return config['DEFAULT']


    # --- API around the `users` table. ---
    def add_user(self, uname, pword, fname, phone):
        '''Add a new user with specified user data.'''
        self.__tbl_users.add_user(uname, pword, fname, phone)


    def user_exists(self, uname):
        '''Return True if user "uname" already exists; False otherwise.'''
        return self.__tbl_users.user_exists(uname)


    def del_user(self, uname):
        '''Delete the user with username "uname" from the "users" table.'''
        self.__tbl_users.del_user(uname)


    # --- API around the `admins` table. ---
    def add_admin(self, uname, pword, vid):
        '''Add a new admin with specified user data.'''
        self.__tbl_admins.add_admin(uname, pword, vid)


    def admin_exists(self, uname):
        '''Return True if admin "uname" already exists; False otherwise.'''
        return self.__tbl_admins.admin_exists(uname)


    def del_admin(self, uname):
        '''Delete the admin with username "uname" from the "admins" table.'''
        self.__tbl_users.del_admin(uname)


    # --- API around the `vendors` table. ---
    def get_vid(self, name):
        '''Return the unique ID for vendor "name" if it exists.
        Otherwise return None.'''
        return self.__tbl_vendors.get_vid(name)

    def add_vendor(self, name, addr):
        '''Add a new vendor with specified data.  Return the vendor ID.'''
        return self.__tbl_vendors.add_vendor(name, addr)


    def vendor_exists(self, name):
        '''Return True if vendor "name" already exists; False otherwise.'''
        return self.__tbl_vendors.vendor_exists(name)


    def del_vendor(self, name):
        '''Delete vendor "name" from the "vendors" table.'''
        self.__tbl_vendor.del_vendor(name)

    def list_vendors(self, substr):
        '''Return a list of all vendors with "substr" in their names.'''
        return self.__tbl_vendor.list_vendors(substr)


    # --- API around the `items` table. ---
    def add_item(self, name, cals=0):
        '''Add a new item with specified data.
        Return the corresponding unique (item) ID.'''
        return self.__tbl_items.add_item(name, cals)


    def item_exists(self, name):
        '''Return True if item "name" already exists; False otherwise.'''
        return self.__tbl_items.item_exists(name)


    def del_item(self, name):
        '''Delete item "name" from the "items" table.'''
        self.__tbl_items.del_item(name)


    # --- API around the `dishes` table. ---
    def add_dish(self, iid, vid, price):
        '''Add a dish to the "dishes" table.'''
        self.__tbl_dishes.add_dish(iid, vid, price)


    def dish_exists(self, iid, vid):
        '''Check if the dish "iid,vid" exists in the "dishes" table.'''
        return self.__tbl_dishes.dish_exists(iid, vid)


    def del_dish(self, iid, vid):
        '''Delete a dish from the "dishes" table.'''
        self.__tbl_dishes.del_dish(iid, vid)


    def list_dishes_by_name(self, name):
        '''List dishes (by all vendors) that have "name" in their names.'''
        return self.__tbl_dishes.list_dishes_by_name(name)


    def list_dishes_by_vendor(self, vid):
        '''List dishes offered by the vendor with ID "vid".'''
        return self.__tbl_dishes.list_dishes_by_vendor(vid)


    # Close the DB connection.
    def close(self):
        self.__conn.close()


class _TableUsers:
    '''Abstraction of the "users" table.'''
    def __init__(self, conn):
        self.__conn = conn
        self.__create_table()


    def __create_table(self):
        self.__conn.execute('''\
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                fullname TEXT NOT NULL,
                phonenum TEXT NOT NULL
            );''')
        self.__conn.commit()


    def add_user(self, uname, pword, fname, phone):
        if self.user_exists(uname):
            raise RuntimeError('user "%s" already exists' % uname)
        self.__conn.execute('''\
            INSERT INTO users (username, password, fullname, phonenum)
            VALUES (?, ?, ?, ?);''', (uname, pword, fname, phone))
        self.__conn.commit()


    def user_exists(self, uname):
        cursor = self.__conn.execute(
            'SELECT username FROM users WHERE username = ?;', (uname,))
        return len(cursor.fetchall()) != 0


    def del_user(self, uname):
        self.__conn.execute('DELETE FROM users WHERE username = ?;', (uname,))
        self.__conn.commit()


class _TableAdmins:
    '''Abstraction of the "admins" table.'''
    def __init__(self, conn):
        self.__conn = conn
        self.__create_table()


    def __create_table(self):
        self.__conn.execute('''\
            CREATE TABLE IF NOT EXISTS admins (
                aid INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                vid INTEGER NOT NULL,
                FOREIGN KEY(vid) REFERENCES vendors(vid)
            );''')
        self.__conn.commit()


    def add_admin(self, uname, pword, vid):
        if self.admin_exists(uname):
            raise RuntimeError('admin "%s" already exists' % uname)
        self.__conn.execute('''\
            INSERT INTO admins (username, password, vid)
            VALUES (?, ?, ?);''', (uname, pword, vid))
        self.__conn.commit()


    def admin_exists(self, uname):
        cursor = self.__conn.execute(
            'SELECT username FROM admins WHERE username = ?;', (uname,))
        return len(cursor.fetchall()) != 0


    def del_admin(self, uname):
        self.__conn.execute('DELETE FROM admins WHERE username = ?;', (uname,))
        self.__conn.commit()


class _TableVendors:
    '''Abstraction of the "vendors" table.'''
    def __init__(self, conn):
        self.__conn = conn
        self.__create_table()


    def __create_table(self):
        self.__conn.execute('''\
            CREATE TABLE IF NOT EXISTS vendors (
                vid INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                address TEXT NOT NULL
            );''')
        self.__conn.commit()


    def get_vid(self, name):
        cursor = self.__conn.execute(
            'SELECT vid FROM vendors WHERE name = ?;', (name,))
        row = cursor.fetchone()
        return row[0] if row else None


    def add_vendor(self, name, addr):
        if self.get_vid(name) is not None:
            raise RuntimeError('vendor "%s" already exists' % name)
        self.__conn.execute(
            'INSERT INTO vendors (name, address) VALUES (?, ?);', (name, addr))
        self.__conn.commit()
        return self.get_vid(name)


    def vendor_exists(self, name):
        return self.get_vid(name) is not None


    def del_vendor(self, name):
        self.__conn.execute('DELETE FROM vendors WHERE name = ?;', (name,))
        self.__conn.commit()


    def list_vendors(self, substr):
        cursor = self.__conn.execute(
            'SELECT vid, name FROM vendors WHERE name LIKE %?%);', (substr,))
        return [row for row in cursor]


class _TableItems:
    '''Abstraction of the "items" table.'''
    def __init__(self, conn):
        self.__conn = conn
        self.__create_table()


    def __create_table(self):
        self.__conn.execute('''\
            CREATE TABLE IF NOT EXISTS items (
                iid INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                calories INTEGER DEFAULT 0
            );''')
        self.__conn.commit()


    def get_iid(self, name):
        cursor = self.__conn.execute(
            'SELECT iid FROM items WHERE name = ?;', (name,))
        row = cursor.fetchone()
        return row[0] if row else None


    def add_item(self, name, cals):
        # NOTE: Trying to add an item that already exists is not considered a
        # problem.  We expect multiple vendors to have the same item; in that
        # case, we simply return the `iid' of the existing item.
        iid = self.get_iid(name)
        if iid:
            return iid

        self.__conn.execute(
            'INSERT INTO items (name, calories) VALUES (?, ?);', (name, cals))
        self.__conn.commit()
        return self.get_iid(name)


    def item_exists(self, name):
        iid = self.get_iid(name)
        return iid is not None


    def del_item(self, name):
        self.__conn.execute('DELETE FROM items WHERE name = ?;', (name,))
        self.__conn.commit()


class _TableDishes:
    '''Abstraction of the "dishes" table.'''
    def __init__(self, conn):
        self.__conn = conn
        self.__create_table()


    def __create_table(self):
        self.__conn.execute('''\
            CREATE TABLE IF NOT EXISTS dishes (
                did INTEGER PRIMARY KEY,
                iid INTEGER NOT NULL,
                vid INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY(iid) REFERENCES items(iid),
                FOREIGN KEY(vid) REFERENCES vendors(vid)
            );''')
        self.__conn.commit()


    def add_dish(self, iid, vid, price):
        if self.dish_exists(iid, vid):
            raise RuntimeError('dish "%d,%d" already exists' % (iid, vid))
        self.__conn.execute('''\
            INSERT INTO dishes (iid, vid, price)
            VALUES (?, ?, ?);''', (iid, vid, price))
        self.__conn.commit()


    def dish_exists(self, iid, vid):
        cursor = self.__conn.execute(
            'SELECT did FROM dishes WHERE iid = ? AND vid = ?;', (iid, vid))
        return len(cursor.fetchall()) != 0


    def del_dish(self, iid, vid):
        self.__conn.execute(
            'DELETE FROM dishes WHERE iid = ? AND vid = ?;', (iid, vid))
        self.__conn.commit()


    def list_dishes_by_name(self, name):
        cursor = self.__conn.execute('''\
            SELECT items.name, vendors.name, price FROM dishes
            INNER JOIN items ON items.iid = dishes.iid
            INNER JOIN vendors ON vendors.vid = dishes.vid
            WHERE items.name LIKE %?%);''', (name,))
        return [row for row in cursor]


    def list_dishes_by_vendor(self, vid):
        cursor = self.__conn.execute('''\
            SELECT items.name, vendors.name, price FROM dishes
            INNER JOIN items ON items.iid = dishes.iid
            INNER JOIN vendors ON vendors.vid = dishes.vid
            WHERE dishes.vid = ?);''', (vid,))
        return [row for row in cursor]


class _TableOrders:
    '''Abstraction of the "orders" table.'''
    def __init__(self, conn):
        self.__conn = conn
        self.__create_table()


    def __create_table(self):
        self.__conn.execute('''\
            CREATE TABLE IF NOT EXISTS orders (
                oid INTEGER PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                uid INTEGER NOT NULL,
                FOREIGN KEY(uid) REFERENCES users(uid)
            );''')
        self.__conn.commit()


    def add_order(self, ts, uid):
        self.__conn.execute('''\
            INSERT INTO orders (timestamp, uid) VALUES (?, ?);''', (ts, uid))
        self.__conn.commit()


class _TableOrderList:
    '''Abstraction of the "orderlist" table.'''
    def __init__(self, conn):
        self.__conn = conn
        self.__create_table()


    def __create_table(self):
        self.__conn.execute('''\
            CREATE TABLE IF NOT EXISTS orderlist (
                oid INTEGER NOT NULL,
                did INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                cancelled INTEGER DEFAULT 0,
                FOREIGN KEY(oid) REFERENCES orders(oid),
                FOREIGN KEY(did) REFERENCES dishes(did)
            );''')
        self.__conn.commit()


    def add_order(self, oid, did, qty):
        self.__conn.execute('''\
            INSERT INTO orderlist (oid, did, quantity)
            VALUES (?, ?, ?);''', (oid, did, qty))
        self.__conn.commit()


    def cancel_order(self, oid, did, ts):
        self.__conn.execute('''\
            UPDATE orderlist SET cancelled = ?
            WHERE oid = ? AND did = ?;''', (ts, oid, did))
        self.__conn.commit()
