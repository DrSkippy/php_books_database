<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->

<?php
while ($row = mysql_fetch_array($result)) {
        echo '<tr>';
        if ($_REQUEST['chk_author']) {
	       echo '<td> '.$row['Author'].'</td>';}
	if ($_REQUEST['chk_title']) {
               echo '<td> '.$row['Title'].'</td>';}
	if ($_REQUEST['chk_isbnnumber']) {
               echo '<td> '.$row['ISBNNumber'].'</td>';}
    if ($_REQUEST['chk_isbnnumber13']) {
               echo '<td> '.$row['ISBNNumber13'].'</td>';}
	if ($_REQUEST['chk_publishername']) {
               echo '<td> '.$row['PublisherName'].'</td>';}
	if ($_REQUEST['chk_pages']) {
               echo '<td> '.$row['Pages'].'</td>';}
	if ($_REQUEST['chk_copyrightdate']) {
               echo '<td> '.substr($row['CopyrightDate'],0,4).'</td>';}
	if ($_REQUEST['chk_lastread'] AND (substr($row['LastRead'],0,10) <> '0000-00-00')) {
               echo '<td> '.substr($row['LastRead'],0,10).'</td>';}
	if ($_REQUEST['chk_location']) {
               echo '<td> '.$row['Location'].'</td>';}
	if ($_REQUEST['chk_recycled']) {
		if ($row['Recycled'] == 0){
               		echo '<td>[&nbsp;&nbsp;]</td>';}
		else {
               		echo '<td>[X]</td>';}
		}
	if ($_REQUEST['chk_covertype']) {
               echo '<td> '.$row['CoverType'].'</td>';}
        echo '</tr>';
	}
?>
