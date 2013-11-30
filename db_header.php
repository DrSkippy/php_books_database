<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->
<?php
$dbcnx = @mysql_connect('host', 'username', 'password');
if (!$dbcnx) {
	exit('<p>Unable to connect to the database server at this time.</p>');
	}
	
if (!@mysql_select_db('databse')) {
	exit('<p>Unable to locate the database at this time.</p>');
	}
?>
