<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->

<?php include('./header.php');?>

<h1>Ranked Years by Pages Read</h1>
<?php
$debug = 0;
include './db_header.php';

##########################################
# count pages read by year, omitting 1966
$search_str = 'select year(LastRead) as year, sum(Pages) as total from `book collection` where LastRead is not NULL and LastRead <> "0000-00-00 00:00:00" and year(LastRead) <> "1966" group by year order by total desc';
if ($debug) echo $search_str;
$result = @mysql_query($search_str);
	
if (!$result) {
	exit('<p>'.$search_str.'</p><p>Error performing query: ' . mysql_error() . '</p>');
       	}
?>
<table cellspacing=5 cellpadding=1 border=0>
<tr><th>Rank</th><th>Year</th><th>Pages Read</th></tr>
<?php
$count = 0;
while ($row = mysql_fetch_array($result)) {
	$count += 1;
	echo '<tr><td align=center>'.$count.'</td>';
	echo '<td>'.$row['year'].'</td>';
	echo '<td align=center>'.$row['total'].'</td></tr>';
	}
?>
</table>
<?php include('./footer.php');?>
</body>
</html>
