-- This script removes test data entries from various tables in the database.
USE books;
DELETE FROM `tag labels` where label="delete_me";
DELETE FROM `book collection` WHERE PublisherName="Printerman";
DELETE FROM `books read` WHERE ReadDate="1945-10-19";
DELETE FROM `complete date estimates` WHERE LastReadablePage=15000;