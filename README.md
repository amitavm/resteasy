# Rest Easy: An Online Food Ordering App

## Introduction

This is an implementation of an online food ordering app.  We will mainly focus
on the backend.  The UI will be a simple CLI, for demo purposes.

## Requirements

The app should support users (those who will order food) and vendors (those who
will supply food: restaurants).  It should let vendors have admins who will
manage their menu.

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

***Note***: The app is currently under development, so all features listed
above are not available yet.  The basic design is in place, and the user
workflow is working.  Additional workflows are being added.

## Design

We use a simple three-tier design for this app.  From bottom-up, the tiers are:

1. The data tier.  This is the database layer, and consists of the various DB
   tables that store user and vendor data.
2. The web service tier.  This is a web API layer that abstracts the data store
   and provides web APIs for reading and updating the data in the data tier.
3. The client tier.  These are the "apps" that end users of our system will
   use.  Currently, we have planned two clients:
   
   - One for normal end users who will order food.
   - Another for the vendor's admins who will update/change their menus.

### The Data Layer

The data layer consists of the database (SQLite 3), and a Python wrapper that
provides an API around the data.  (See the Implementation section below for
more on this.)  The idea of having a separate data layer, instead of making it
part of the web service layer, is to make it easy to switch the data storage
technology.

#### Database Tables

The most important thing to understand in a piece of software is the way it
models the data it deals with.  Once the modeling of the data is clear, rest of
the code becomes (much) easier to follow.  To that end, we list the schemas for
our DB tables here.

The data in the data-layer is stored in tables in an SQLite3 database.  We have
the following tables in our database:

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

### The API Layer

*TBD*

## Implementation

We have used Python as our implementation language for the entire stack.
Additional implementation notes for the individual tiers:

- For the data store, we have used SQLite3 for this prototype.  (In a
  production setting, we would go for something like MariaDB, or PostgreSQL.)
  This tier also includes a thin Python wrapper on top of the DB to provide an
  API around the data store.
  
  This choice (of using SQLite3) has had some consequence in implementing the
  (Python) API layer on top of the data store: most of the database queries are
  embedded right inside the Python functions that abstract those queries.
  Although Python makes it easier to do this compared to other langauges (using
  its multi-line strings), we would still prefer to separate them by using
  stored procedures.  However, SQLite3 doesn't support stored procedures, so we
  end up embedding the SQL queries inside Python code.
- For the web service tier, we have used the Flask microframework.  (Again,
  it's a Python based framework).
- The client apps use the `requests` module from the Python standard library to
  be able to make HTTP calls to the web service.
