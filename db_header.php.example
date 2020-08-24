<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->
<?php
$dbcnx = @mysqli_connect('76.12.234.190', 'your user name here', 'your password here');
if (!$dbcnx) {
    exit('<p>Unable to connect to the database server at this time.</p>');
}
if (!@mysqli_select_db($dbcnx, 'your database here')) {
    exit('<p>Unable to locate the database at this time.</p>');
}
?>
