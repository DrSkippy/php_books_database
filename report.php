<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->

<?php include('header.php');?>
	
<h1>Book Report</h1>

<?php
	# $debug = 1;
include ('./db_header.php');
########################################################
if ($_REQUEST['search_numbyyear'] <> 'yes'){
if ($_REQUEST['search_type'] == 'Tag'){
	$where_str = ',tags WHERE tags.BookID = `book collection`.BookCollectionID AND Tag LIKE "%'.$_REQUEST['search_term'].'%"';
	echo '<b>Tag Search: </b>'.$_REQUEST['search_term'].'';
	}
elseif ($_REQUEST['search_term'] == ''){
	$where_str = '';
	}
else {
	$where_str = 'WHERE '.$_REQUEST['search_type'].' LIKE "%'.$_REQUEST['search_term'].'%" ';
	}

if ($_REQUEST['search_cat'] == 'All'){
	}
else {  
	if ($where_str == '') {$where_str = 'WHERE ';}
	else {$where_str = $where_str.'AND ';}
	$where_str = $where_str.'Location = "'.$_REQUEST['search_cat'].'" ';
	}
if ($_REQUEST['search_norecycle'] == 'yes'){
	if ($where_str == '') {$where_str = 'WHERE ';}
	else {$where_str = $where_str.'AND ';}
	$where_str = $where_str.'Recycled = 0 ';
	}
$search_str = 'SELECT * FROM `book collection` '.$where_str.' ORDER BY '.$_REQUEST['search_order'];
if ($debug) echo $search_str;
$result = @mysql_query($search_str);
if (!$result) {
	exit('<p>Error performing query: ' . mysql_error() . '</p>');
       	}
$search_str1 = 'SELECT SUM(Pages) AS totalpages FROM `book collection` '.$where_str;
if ($debug) $search_str1;
$result1 = @mysql_query($search_str1);
if (!$result1) {
	exit('<p>Error performing query: ' . mysql_error() . '</p>');
       	}
$row1 = mysql_fetch_array($result1);

echo '<p>'.mysql_num_rows($result).' entries found<hr><table>';
include './report_table_header.php';
include './report_table.php';
echo '</table>';
echo 'Total Pages: '.$row1['totalpages'];
} else {
########################################################
# What was read in what year?
$result = @mysql_query('SELECT min(LastRead) as min FROM `book collection`');
if (!$result) {
	exit('<p>Error performing Min query: ' . mysql_error() . '</p>');
       	}
$row = mysql_fetch_array($result);
$year_min = 1966;
if ($year_min <> substr($row['min'],0,4) AND substr($row['min'],0,4) > 0) echo 'Year read error < 1966!';

$result = @mysql_query('SELECT max(LastRead) as max FROM `book collection`');
if (!$result) {
	exit('<p>Error performing Max query: ' . mysql_error() . '</p>');
       	}
$row = mysql_fetch_array($result);
$year_max = substr($row['max'],0,4);
echo '<table>';
foreach (range($year_min,$year_max) as $year) {
	$where_str = 'LastRead BETWEEN "'.
		$year.'-01-00 00:00:00" AND "'.
		($year+1).'-01-00 00:00:00" ORDER BY '.$_REQUEST['search_order'];
	$search_str = 'SELECT * FROM `book collection` WHERE '.$where_str;
	if ($debug) echo $search_str;
	$result = @mysql_query($search_str);
	if (!$result) {
		exit('<p>Error performing query: ' . mysql_error() . '</p>');
       		}
	if (mysql_num_rows($result) > 0) {		
		$search_str1 = 'SELECT SUM(Pages) AS totalpages FROM `book collection` WHERE '.$where_str;
		if ($debug) echo $search_str1;
		$result1 = @mysql_query($search_str1);
		if (!$result1) {
			exit('<p>Error performing Sum query: ' . mysql_error() . '</p>');
       		}
		$row1 = mysql_fetch_array($result1);
		echo '<tr><td><br><h1>'.$year.'</h1></td></tr>';
		include './report_table_header.php';
        	include ('./report_table.php');
		echo '<tr><td align="right"><i>'.mysql_num_rows($result).' Books ** </i></td><td><i> '.$row1['totalpages'].' Pages</i></td></tr>';
		}
}
echo '</table>';
########################################################
}
include ('./footer.php');
?>
