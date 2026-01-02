#!/bin/bash
# clean up test records from the book_service database

UN=$(cat ./book_service/config/configuration.json | jq -r .username)
PWD=$(cat ./book_service/config/configuration.json | jq -r .password)
DB=$(cat ./book_service/config/configuration.json | jq -r .database)
DBHOST=$(cat ./book_service/config/configuration.json | jq -r .host)

echo mysql -u $UN -p $PWD -h $DBHOST books < ../book_service/test_books/sql_cleanup_script.sql