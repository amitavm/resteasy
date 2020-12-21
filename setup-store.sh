#!/bin/bash

# Reset/populate the store with our test data, bypassing the API layer.

dbfile="restore.db"

set -x
rm -f $dbfile
./process-users.py -c config.ini -i users.csv
./process-vendor.py -c config.ini -i vendor1.txt
./process-vendor.py -c config.ini -i vendor2.txt
