<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->
<?php
$result = @mysqli_query($dbcnx, 'SELECT DISTINCT Location FROM `book collection` ORDER BY Location');
if (!$result) {
    exit('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
}
while ($row = mysqli_fetch_array($result)) {
    echo '<option>' . $row['Location'] . '</option>';
}
?> 