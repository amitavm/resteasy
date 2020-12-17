# Rest Easy: An Online Food Ordering App

## Introduction

This is an implementation of an online food ordering app.
We will only implement the backend for now.  The UI will
be a simple CLI for now, for demo purposes.

## Requirements

The app should support users (those who will order food) and
vendors (those who will supply food: restaurants).  It should also
let vendors have admins who will manage their menu.

Users should be able to:

- Sign-up
- Login
- List vendors matching a given string (name, area)
- List items matching a given string, sorted by vendor/price
- Select specific items from the displayed list
- Place order

Admins should be able to:

- Update existing dishes
- Add new dishes to their menu
- Delete existing dishes from their menu
- Toggle the availability status for items in their menu
- View orders for their restaurants

## Design

### The API Layer

### The Data Layer

The data layer consists of the database (SQLite 3), and a Python wrapper that
provides an API around the data.  The idea of having a separate data layer,
instead of making it part of the web service layer, is to make it easy to
switch the data storage technology.

#### Database Tables

The data in the data-layer is stored in tables in an SQLite 3 database.
We have the following tables in our database:

* Table `users`
```
    - uid INTEGER PRIMARY KEY           [Unique row/entry identifier]
    - username TEXT NOT NULL UNIQUE     [Unique login user-name of this person]
    - password TEXT NOT NULL            [This user's login password (encrypted)]
    - fullname TEXT NOT NULL            [Full name of the user]
    - phonenum TEXT NOT NULL            [Phone number of this person]
```

* Table `admins`
```
    - aid INTEGER PRIMARY KEY           [Unique row/entry identifier]
    - username TEXT NOT NULL UNIQUE     [Unique login user-name of this person]
    - password TEXT NOT NULL            [This user's login password (encrypted)]
    - vid INTEGER NOT NULL              [Foreign key: ID from the table `vendors`]
```

* Table `vendors`
```
    - vid INTEGER PRIMARY KEY           [Unique vendor identifier]
    - name TEXT NOT NULL UNIQUE         [Name of the vendor/restaurant]
    - address TEXT NOT NULL             [Address of restaurant]
```

* Table `items`
```
    - iid INTEGER PRIMARY KEY           [Unique item identifier]
    - name TEXT NOT NULL UNIQUE         [Name of the dish]
    - calories INTEGER DEFAULT 0        [Amount of calories in this item]
```

* Table `dishes`
```
    - did INTEGER PRIMARY KEY           [Unique dish ID]
    - iid INTEGER NOT NULL              [Foreign key: ID from the table `items`]
    - vid INTEGER NOT NULL              [Foreign key: ID from the table `vendors`]
    - price REAL NOT NULL               [Price of this dish from this vendor]
```

* Table `orders`
```
    - oid INTEGER PRIMARY KEY           [Unique order identifier]
    - uid INTEGER NOT NULL              [Foreign key: ID from the table `users`]
    - timestamp INTEGER NOT NULL        [Epoch-time when order was placed]
```

* Table `orderdishes`
```
    - oid INTEGER NOT NULL              [Foreign key: ID from the table `orders`]
    - did INTEGER NOT NULL              [Foreign key: ID from the table `dishes`]
    - quantity INTEGER NOT NULL         [Number of portions/plates ordered]
    - cancelled INTEGER DEFAULT 0       [Epoch-time when this order was cancelled]
```

#### Supported Operations

The data layer supports the following operations (names and parameters) to be
performed by normal users:

- `signup(name, phone)`: Sign up for a user account.
- `login(uname, pword)`: Login user.
- `list-vendors(word)`:  List vendors with word (a string) in their names.
- `list-items(word)`:  List food items with word (a string) in their names.
- `new-order(uid, tstamp)`: Initiate new order; returns order ID.
- `order-item(oid, iid, quantity)`: Order one item.

The data layer also supports the following operations (names and parameters) to
be performed by admin users:

- *TBD*

Each of these is implemented in the database as stored procs, and the Python
layer simply invokes them to get the result.
