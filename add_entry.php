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
$insert_str = 'INSERT INTO `book collection` ' . '(Title, Author, CopyrightDate, ISBNNumber, ISBNNumber13, PublisherName, ' . 'CoverType, Pages, LastRead, PreviouslyRead, Location, Note, Recycled) ' . 'VALUES ("' . $_REQUEST['title'] . '","' . $_REQUEST['author'] . '","' . date("Y-m-d h:m:s", $dt) . '","' . $_REQUEST['isbnnumber'] . '","' . $_REQUEST['isbnnumber13'] . '","' . $_REQUEST['publishername'] . '","' . $_REQUEST['covertype'] . '","' . $_REQUEST['pages'] . '",0000-00-00,0000-00-00,"' . $_REQUEST['location'] . '","' . $_REQUEST['note'] . '","' . $recycled . '")';

# echo '<hr>'.$insert_str;
$result = @mysqli_query($dbcnx, $insert_str);
if (!$result) {
    echo ('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    exit();
}
include('./footer.php');
?>
