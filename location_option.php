<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->
<?php 
$result = @mysql_query('SELECT DISTINCT Location FROM `book collection` ORDER BY Location');
if (!$result) {
	exit('<p>Error performing query: ' . mysql_error() . '</p>');
}
while ($row = mysql_fetch_array($result)) {
	echo '<option>'.$row['Location'].'</option>' ;
}     
?> 
