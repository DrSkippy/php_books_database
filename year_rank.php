<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->

<?php
include('./header.php');
?>
<h1>Ranked Years by Pages Read</h1>
<?php
$debug = 0;
include './db_header.php';
##########################################
# count pages read by year, omitting 1966
// 2022-03-21 $search_str = 'select year(LastRead) as year, sum(Pages) as total from `book collection` where LastRead
// is not NULL and LastRead <> "0000-00-00 00:00:00" and year(LastRead) <> "1966" group by year order by total desc';
$search_str = 'select year(b.ReadDate) as year, sum(a.Pages) as total, count(*) as books';
$search_str .= 'from `book collection` as a JOIN `books read` as b ON a.BookCollectionID=b.BookCollectionID ';
$search_str .= 'where b.ReadDate is not NULL and b.ReadDate <> "0000-00-00 00:00:00" and year(b.ReadDate) <> "1966" ';
$search_str .= 'group by year order by total desc';
if ($debug)
    echo $search_str;
$result = @mysqli_query($dbcnx, $search_str);
if (!$result) {
    exit('<p>' . $search_str . '</p><p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
}
?>
<div class="two-column-row">
<div class="column">
<table class="styled-table">
<tr><thead><th>Rank</th><th>Year</th><th>Books Read</th><th>Pages Read</th></thead></tr>
<?php
$count = 0;
while ($row = mysqli_fetch_array($result)) {
    $count += 1;
    echo '<tr><td align=center>' . $count . '</td>';
    echo '<td>' . $row['year'] . '</td>';
    echo '<td>' . $row['books'] . '</td>';
    echo '<td align=center>' . $row['total'] . '</td></tr>';
}
?>
</table>
</div>
<div class="column">
(Ranked by Pages Read)
</div>
</div>
<?php
include('./footer.php');
?>
</body>
</html>
