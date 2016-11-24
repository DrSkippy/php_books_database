<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->

<?php
include('header.php');
?>
	
<h1>Book Report</h1>

<?php
$debug = 0;
include('./db_header.php');
########################################################
if ($_REQUEST['search_numbyyear'] <> 'yes') {
    if ($_REQUEST['search_type'] == 'Tag') {
        $where_str = ',tags WHERE tags.BookID = `book collection`.BookCollectionID AND Tag LIKE "%' . $_REQUEST['search_term'] . '%"';
        echo '<b>Tag Search: </b>' . $_REQUEST['search_term'] . '';
    } elseif ($_REQUEST['search_term'] == '') {
        $where_str = '';
    } else {
        $where_str = 'WHERE ' . $_REQUEST['search_type'] . ' LIKE "%' . $_REQUEST['search_term'] . '%" ';
    }
    
    if ($_REQUEST['search_cat'] != 'All') {
        if ($where_str == '') {
            $where_str = 'WHERE ';
        } else {
            $where_str = $where_str . 'AND ';
        }
        $where_str = $where_str . 'Location = "' . $_REQUEST['search_cat'] . '" ';
    }
    
    if ($_REQUEST['search_norecycle'] == 'yes') {
        if ($where_str == '') {
            $where_str = 'WHERE ';
        } else {
            $where_str = $where_str . 'AND ';
        }
        $where_str = $where_str . ' Recycled = 0 ';
    }
    if ($_REQUEST['search_nodigital'] == 'yes') {
        if ($where_str == '') {
            $where_str = 'WHERE ';
        } else {
            $where_str = $where_str . 'AND ';
        }
        $where_str = $where_str . ' CoverType != "Digital"';
    }
    if ($_REQUEST['search_unread'] == 'yes') {
        if ($where_str == '') {
            $where_str = 'WHERE ';
        } else {
            $where_str = $where_str . 'AND ';
        }
        $where_str = $where_str . ' (LastRead = "0000-00-00" OR LastRead = "")';
    }
    $search_str = 'SELECT BookCollectionID, Title, Author, CopyrightDate, ISBNNumber, PublisherName, CoverType, Pages, LastRead, PreviouslyRead, Category, Note, Recycled, Location, ISBNNumber13 FROM `book collection` ' . $where_str . ' ORDER BY ' . $_REQUEST['search_order'];
    
    if ($debug)
        echo $search_str . "<br>";
    $result = @mysqli_query($dbcnx, $search_str);
    if (!$result) {
        exit('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    }
    
    echo '<p>' . mysqli_num_rows($result) . ' entries found<hr><table>';
    include './report_table_header.php';
    include './report_table.php';
    
    echo '</table>';
    
    $search_str1 = 'SELECT SUM(Pages) AS totalpages FROM `book collection` ' . $where_str;
    if ($debug)
        echo $search_str1 . "<br>";
    $result1 = @mysqli_query($dbcnx, $search_str1);
    if (!$result1) {
        exit('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    }
    
    $row1 = mysqli_fetch_array($result1);
    
    echo 'Total Pages: ' . $row1['totalpages'];
} else {
    ########################################################
    # What was read in what year?
    $result = @mysqli_query($dbcnx, 'SELECT min(LastRead) as min FROM `book collection`');
    if (!$result) {
        exit('<p>Error performing Min query: ' . mysqli_error($dbcnx) . '</p>');
    }
    $row = mysqli_fetch_array($result);
    
    $year_min = 1966;
    if ($year_min <> substr($row['min'], 0, 4) AND substr($row['min'], 0, 4) > 0)
        echo 'Year read error < 1966!';
    
    $result = @mysqli_query($dbcnx, 'SELECT max(LastRead) as max FROM `book collection`');
    if (!$result) {
        exit('<p>Error performing Max query: ' . mysqli_error($dbcnx) . '</p>');
    }
    $row      = mysqli_fetch_array($result);
    $year_max = substr($row['max'], 0, 4);
    
    echo '<table>';
    
    foreach (range($year_min, $year_max) as $year) {
        $where_str  = 'LastRead BETWEEN "' . $year . '-01-00 00:00:00" AND "' . ($year + 1) . '-01-00 00:00:00" ORDER BY ' . $_REQUEST['search_order'];
        $search_str = 'SELECT BookCollectionID, Title, Author, CopyrightDate, ISBNNumber, PublisherName, CoverType, Pages, LastRead, PreviouslyRead, Category, Note, Recycled, Location, ISBNNumber13 FROM `book collection` WHERE ' . $where_str;
        if ($debug)
            echo $search_str . "<br>";
        $result = @mysqli_query($dbcnx, $search_str);
        if (!$result) {
            exit('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
        }
        if (mysqli_num_rows($result) > 0) {
            $search_str1 = 'SELECT SUM(Pages) AS totalpages FROM `book collection` WHERE ' . $where_str;
            if ($debug)
                echo $search_str1 . "<br>";
            $result1 = @mysqli_query($dbcnx, $search_str1);
            if (!$result1) {
                exit('<p>Error performing Sum query: ' . mysqli_error($dbcnx) . '</p>');
            }
            $row1 = mysqli_fetch_array($result1);
            echo '<tr><td><br><h1>' . $year . '</h1></td></tr>';
            include './report_table_header.php';
            include('./report_table.php');
            echo '<tr><td align="right"><i>' . mysqli_num_rows($result) . ' Books ** </i></td><td><i> ' . $row1['totalpages'] . ' Pages</i></td></tr>';
            mysqli_free_result($result1);
        }
        mysqli_free_result($result);
    }
    echo '</table>';
    ########################################################
}
include('./footer.php');
?>
