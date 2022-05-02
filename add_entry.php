<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->
<?php

echo ('<html><head><meta http-equiv="refresh" content="2; URL=./index.php">');
echo ('<link href="./books.css" rel="stylesheet" type="text/css">');
echo ('</head><body> <h3>Entry Added</h3>');
include('./db_header.php');
if ($_REQUEST['recycled'] == "yes") {
    $recycled = 1;
} else {
    $recycled = 0;
}
$dt         = mktime(0, 0, 0, 1, 1, $_REQUEST['copyrightdate']);
$insert_str  = 'INSERT INTO `book collection` ';
$insert_str .= '(Title, Author, CopyrightDate, ISBNNumber, ISBNNumber13, PublisherName, ';
// $insert_str .= 'CoverType, Pages, LastRead, PreviouslyRead, Location, Note, Recycled) ';
$insert_str .= 'CoverType, Pages, Location, Note, Recycled) ';
$insert_str .= 'VALUES ("' . $_REQUEST['title'] . '","' . $_REQUEST['author'] . '","' . date("Y-m-d h:m:s", $dt);
$insert_str .= '","' . $_REQUEST['isbnnumber'] . '","' . $_REQUEST['isbnnumber13'] . '","';
$insert_str .= $_REQUEST['publishername'] . '","' . $_REQUEST['covertype'] . '","' . $_REQUEST['pages'];
// $insert_str .= '",0000-00-00,0000-00-00,"' . $_REQUEST['location'] . '","' . $_REQUEST['note'] . '","' . $recycled . '")';
$insert_str .= $_REQUEST['location'] . '","' . $_REQUEST['note'] . '","' . $recycled . '")';

# echo '<hr>'.$insert_str;
$result = @mysqli_query($dbcnx, $insert_str);
if (!$result) {
    echo ('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    exit();
}
include('./footer.php');
?>
