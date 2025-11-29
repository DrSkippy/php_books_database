# Book Tools

## Four tools here:

2. Book Service - A REST API service to manage book records and reading progress (see documentation in `tools/book_service/books/README.md`)
2. Book CLI - A command line interface to interact with the Book Service. This is a REPL interface to issue commands to the Book Service API.  (See inline help)
3. Book Database Backup - A SQLite database to store book records and reading progress
4. Jupyter Notebooks for interacting with API and REPL utilities

```aiignore
$ bash backup_db 
****************************************
 BOOKS BACKUP STARTING...

Reading database books from host 192.168.127.166 for user scott.
Results in /mnt/raid1/shares/backups//booksdb_2025-11-28_1314.sql...
mysqldump: [Warning] Using a password on the command line interface can be insecure.
mysqldump: [Warning] Using a password on the command line interface can be insecure.
Backups present:
1.4M -rw-rw-r-- 1 scott scott 1.4M Nov 28 13:14 /mnt/raid1/shares/backups//booksdb_2025-11-28_1314.sql
8.0K -rw-rw-r-- 1 scott scott 5.6K Nov 28 13:14 /mnt/raid1/shares/backups//schema_booksdb_2025-11-28_1314.sql
Done.
```

## Configuration

All tools and book service depend on a common configuration file located at `tools/book_service/config/configuration.json`.  You will need to create this file before using the tools or service.  An example configuration file is shown below:

```
{
  "username": "<db user name>",
  "password": "<db password>",
  "database": "<db database>",
  "host": "192.168.127.3",
  "port": 3306,
  "isbn_com": {
    "url_isbn": "https://api2.isbndb.com/book/{}",
    "key": "<your key>"
  },
  "endpoint": "http://192.168.127.13:8083",
  "api_key": "your local api key for book service api"
}
```
