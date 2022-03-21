<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->

<?php
echo '<tr>';
if (isset($_REQUEST['chk_author'])) {
    echo '<th>AUTHOR</th>';
}
if (isset($_REQUEST['chk_title'])) {
    echo '<th>TITLE</th>';
}
if (isset($_REQUEST['chk_isbnnumber'])) {
    echo '<th>ISBN</th>';
}
if (isset($_REQUEST['chk_isbnnumber13'])) {
    echo '<th>ISBN 13</th>';
}
if (isset($_REQUEST['chk_publishername'])) {
    echo '<th>PUBLISHER</th>';
}
if (isset($_REQUEST['chk_pages'])) {
    echo '<th>PAGES</th>';
}
if (isset($_REQUEST['chk_copyrightdate'])) {
    echo '<th>� DATE</th>';
}
if (isset($_REQUEST['chk_readdate'])) {
    echo '<th>READ DATE</th>';
}
if (isset($_REQUEST['chk_location'])) {
    echo '<th>LOCATION</th>';
}
if (isset($_REQUEST['chk_recycled'])) {
    echo '<th>REC\'D</td>';
}
if (isset($_REQUEST['chk_covertype'])) {
    echo '<th>COVER</th>';
}
echo '</tr>';
?>
