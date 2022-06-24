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

<h1>Browse Book Collection</h1>

<?php
$debug = 0;
include './db_header.php';

#############################################
# Find the maximum and minimum record numbers
# for browser limits, allows looping at end.
$search_str = 'SELECT MAX(BookCollectionID) AS max FROM `book collection`';
if ($debug)
    echo $search_str;
$result = @mysqli_query($dbcnx, $search_str);
if (!$result) {
    exit('<p>Error performing Max query: ' . mysqli_error($dbcnx) . '</p>');
}
$row        = mysqli_fetch_array($result);
$max_id     = $row['max'];
$search_str = 'SELECT MIN(BookCollectionID) AS min FROM `book collection`';
if ($debug)
    echo $search_str;
$result = @mysqli_query($dbcnx, $search_str);
if (!$result) {
    exit('<p>Error performing Min query: ' . mysqli_error($dbcnx) . '</p>');
}
$row    = mysqli_fetch_array($result);
$min_id = $row['min'];

#############################################
# Record displayed on basis of what recordselector is set to.
# Default is rs, the page passed state variable.
$recordselector = $_REQUEST['rs'];
$sterm          = '';
if (substr($_REQUEST['submit'], 0, 4) == 'Find') {
    $sterm      = $_REQUEST['searchterm'];
    $tmp_min_id = $min_id;
    #if ($_REQUEST['submit'] == 'Find Again') {
    $tmp_min_id = $_REQUEST['rs'] + 1;
    if (!($tmp_min_id < $max_id))
        $tmp_min_id = $min_id;
    #	}
    $search_str = 'SELECT BookCollectionID FROM `book collection` WHERE ' . $_REQUEST['searchtype'];
    $search_str .= ' LIKE "%' . $_REQUEST['searchterm'] . '%" AND BookCollectionID BETWEEN ';
    $search_str .= $tmp_min_id . ' AND ' . $max_id;
    if ($debug)
        echo $search_str;
    $result = @mysqli_query($dbcnx, $search_str);
    if (!$result) {
        exit('<p>' . $search_str . '</p><p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    }
    $row = mysqli_fetch_array($result);
    if ($row['BookCollectionID'] == '') {
        echo 'No record found';
        $recordselector = $min_id;
    } else
        $recordselector = $row['BookCollectionID'];
}
# scroll forward or backward
else if ($_REQUEST['submit'] == '   >   ') {
    $recordselector = $_REQUEST['rs'] + 1;
    if ($recordselector > $max_id)
        $recordselector = $min_id;
} else if ($_REQUEST['submit'] == '   <   ') {
    $recordselector = $_REQUEST['rs'] - 1;
    if ($recordselector < $min_id)
        $recordselector = $max_id;
}
# Update record with changes
else if ($_REQUEST['submit'] == 'Update Record') {
    if ($_REQUEST['readtoday']) {
        $readdate       = date('Y-m-d h:m:s');
    } else {
        $readdate       = $_REQUEST['readdate'];
    }
    // if entry is new, add to db
    $update_str = 'INSERT IGNORE INTO `books read` (BookCollectionID, ReadDate) VALUES ("' . $_REQUEST['id'];
    $update_str .= '","' . $readdate . '")';
    if ($debug)
        echo $update_str;
    $result = @mysqli_query($dbcnx, $update_str);
    if (!$result) {
        exit('<p>' . $search_str . '</p><p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    } else {
        echo '<td>Record ' . $_REQUEST['id'] . ' updated.</td>';
        $recordselector = $_REQUEST['id'];
    }

    $dt = mktime(0, 0, 0, 1, 1, substr($_REQUEST['copyrightdate'], 0, 4));
    if ($_REQUEST['recycled'] == 'on')
        $recycled = 1;
    else
        $recycled = 0;
    $update_str = 'UPDATE `book collection` SET Title="' . $_REQUEST['title'] . '", ';
    $update_str .= 'Author= "' . $_REQUEST['author'] . '", CopyrightDate="' . date("Y-m-d h:m:s", $dt) . '", ';
    $update_str .= 'ISBNNumber13="' . $_REQUEST['isbnnumber13'] . '", ISBNNumber="' . $_REQUEST['isbnnumber'] . '", ';
    $update_str .= 'PublisherName= "' . $_REQUEST['publishername'] . '", CoverType="' . $_REQUEST['covertype'] . '", ';
    $update_str .= 'Pages= "' . $_REQUEST['pages'] . '", ';
    $update_str .= 'Location="' . $_REQUEST['location'] . '", ';
    $update_str .= 'Note="' . $_REQUEST['note'] . '", Recycled="' . $recycled . '" ';
    $update_str .= 'WHERE BookCollectionID = ' . $_REQUEST['id'];
    if ($debug)
        echo $update_str;
    $result = @mysqli_query($dbcnx, $update_str);
    if (!$result) {
        exit('<p>' . $search_str . '</p><p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    } else {
        echo '<td>Record ' . $_REQUEST['id'] . ' updated.</td>';
        $recordselector = $_REQUEST['id'];
    }
}
# Add new tag to this record
else if ($_REQUEST['submit'] == 'Add Tag') {
    $insert_str = 'INSERT into tags (Tag, BookID) VALUES ("' . $_REQUEST['newtag'] . '","' . $_REQUEST['id'] . '")';
    
    if ($debug)
        echo $insert_str;
    if ($_REQUEST['newtag'] != '') {
        $result = @mysqli_query($dbcnx, $insert_str);
        if (!$result) {
            echo ('<p>' . $insert_str . 'Error performing query: ' . mysqli_error($dbcnx) . '</p>');
            exit();
        }
    }
} else {
    $recordselector = $min_id;
    $searchtype     = 'Author';
}
##########################################
# Find the record and populate the fields
# Make sure query return an actual record, if not, move to the next id number
$no_record = TRUE;
while ($no_record) {
    $search_str = 'SELECT a.*, b.ReadDate FROM `book collection` as a LEFT JOIN `books read` as b ';
    $search_str .= ' ON a.BookCollectionID=b.BookCollectionID WHERE a.BookCollectionID = ' . $recordselector;
    if ($debug)
        echo $search_str;
    $result = @mysqli_query($dbcnx, $search_str);
    if (!$result) {
        exit('<p>' . $search_str . '</p><p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
    }
    $row = mysqli_fetch_array($result);
    if ($row['BookCollectionID'] <> '') {
        $no_record = FALSE;
    } else {
        if ($_REQUEST['submit'] == '   >   ')
            $recordselector = $recordselector + 1;
        else
            $recordselector = $recordselector - 1;
    }
}
# Once we have found a valid record, populate the tags string for display
$tagsearch_str = 'SELECT DISTINCT Tag FROM tags WHERE BookID = ' . $row['BookCollectionID'];
if ($debug)
    echo $tagsearch_str;
$tagresult = @mysqli_query($dbcnx, $tagsearch_str);
if (!$tagresult) {
    exit('<p>' . $tagsearch_str . 'Error performing query: ' . mysqli_error($dbcnx) . '</p>');
}
if ($tagrows = mysqli_fetch_array($tagresult)) {
    $itemtags = $tagrows['Tag'];
    while ($tagrows = mysqli_fetch_array($tagresult)) {
        $itemtags = $itemtags . ', ' . $tagrows['Tag'];
    }
} else {
    $itemtags = "";
}
?>
<form name="add" action="./index.php">
<?php
echo ('<input type="hidden" name="rs" value="' . $recordselector . '">');
?>
<table>
<tr>
	<td align="right" width="100">Author:</td>
	<td><input type="text" size="25" name="author" value="<?php
echo $row['Author'];
?>"></td>
	<td align="right" width="110">Title:</td>
	<td><input type="text" size="30" name="title" value="<?php
echo $row['Title'];
?>"></td>
</tr><tr>
	<td align="right">ISBN #:</td>
	<td><input type="text" size="15" name="isbnnumber" value="<?php
echo $row['ISBNNumber'];
?>"></td>
	<td align="right">ISBN13 #:</td>
	<td><input type="text" size="15" name="isbnnumber13" value="<?php
echo $row['ISBNNumber13'];
?>"></td>
</tr><tr>
	<td align="right">Publisher:</td>
	<td><input type="text" size="25" name="publishername" value="<?php
echo $row['PublisherName'];
?>"></td>
	<td align="right"> </td>
	<td> </td>
</tr><tr>
	<td align="right" valign="top">Note:</td>
	<td colspan="2"><textarea name="note" cols="28" rows="3"><?php
echo $row['Note'];
?></textarea>
	</td>
	<td><input type="radio" name="covertype" value="Hard"<?php
if (substr($row['CoverType'], 0, 4) == 'Hard')
    echo 'checked';
?>
	> Hard Cover</br>
	    <input type="radio" name="covertype" value="Soft"<?php
if (substr($row['CoverType'], 0, 4) == 'Soft')
    echo 'checked';
?>
	> Soft Cover</br>
		<input type="radio" name="covertype" value="Digital"<?php
if (substr($row['CoverType'], 0, 4) == 'Digi')
    echo 'checked';
?>
	> Digital</br>
	Recycled: <input type="checkbox" name="recycled"
<?php
if ($row['Recycled'])
    echo 'checked';
?>></input>
	</td>
</tr><tr>
	<td align="right">Location:</td>
	<td><select name="location">
<?php
# Don't use include here because need to mark selected option
$result1 = @mysqli_query($dbcnx, 'SELECT DISTINCT Location FROM `book collection` ORDER BY Location');
if (!$result1) {
    exit('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
}
while ($row1 = mysqli_fetch_array($result1)) {
    if ($row1['Location'] == $row['Location']) {
        echo '<option selected>';
    } else {
        echo '<option>';
    }
    echo $row1['Location'] . '</option>';
}
?>
	</select></td>
	<td align="right">Pages:</td>
	<td><input type="text" name="pages" size="6" value="<?php
echo $row['Pages'];
?>"></td>
</tr><tr>
	<td align="right">Copyright:</td>
	<td><input type="text" name="copyrightdate" size="5" value="<?php
echo substr($row['CopyrightDate'], 0, 4);
?>"></td>
	<td></td>
	<td></td>
</tr><tr>
	<td align="right">Last Read:</td>
	<td><input type="text" name="readdate" size="9" value="<?php
if ($row['ReadDate'] != '' and $row['ReadDate'] != '0000-00-00 00:00:00') {
    $tmp = explode(" ", $row['ReadDate']);
    echo $tmp[0];
} else {
    echo '0000-00-00';
}
?>"></input>
	<input type="checkbox" name="readtoday"> Today</td>
	<td> </td>
	<td align="right">(dates: YYYY-mm-dd)</td>
</tr><tr>
	<td colspan="4"><input type="text" name="newtag" size="6">&nbsp; <input type="submit" name="submit" value="Add Tag"> Tags: <span class="tags"> <?php
echo $itemtags;
?></span></td>
</tr></table>
<table>
<tr>
	<td align="left">
	<input type="submit" name="submit" value="   <   ">&nbsp;&nbsp;
	<input type="submit" name="submit" value="   >   ">&nbsp;&nbsp;|&nbsp;&nbsp;
	<input type="submit" name="submit" value="Update Record">
	<a href="http://www.amazon.com/exec/obidos/ASIN/<?php
echo $row['ISBNNumber'];
?>/" target="_blank">See it @ Amazon</a></td>
	<td>ID:<?php
echo $row['BookCollectionID'];
?>
	<input type="hidden" name="id" value="<?php
echo $row['BookCollectionID'];
?>">
	&nbsp;&nbsp;&nbsp;&nbsp;<a href="./add.php">Add Entry</a></td>
</tr><tr>
	<td align="center">
		<input type="text" name="searchterm" size="25" value="<?php
echo $sterm;
?>">
	<input type="submit" name="submit" value="Find">
<!--	<input type="submit" name="submit" value="Find Again"> -->
	<input type="radio" name="searchtype" value="Title"
<?php
if ($_REQUEST['searchtype'] == "Title")
    echo 'checked';
echo '>Title&nbsp;&nbsp;<input type="radio" name="searchtype" value="Author"';
if ($_REQUEST['searchtype'] <> "Title")
    echo 'checked';
?>
>Author</td>
</tr>
</table>
</form>
<hr>
<form name="query" action="./report.php">
<h1>Create Reports</h1>
<table>
<tr>
	<td align="right">Column</td>
	<td align="center">| Display |</td>
	<td align="center">Order by</td>
	<td align="right"><a href="./100_day.php">100 Days</a>&nbsp;&nbsp; <a href="./year_rank.php">Year Rank</a></td>
	<td></td>
</tr><tr>
	<td align="right">Author</td>
	<td align="center"><input type="checkbox" name="chk_author" value="Author" checked></td>
	<td align="center"><input type="radio" name="search_order" value="Author, Title" checked></td>
	<td></td>
	<td></td>
</tr><tr>
	<td align="right">Title</td>
	<td align="center"><input type="checkbox" name="chk_title" value="Title" checked></td>
	<td align="center"><input type="radio" name="search_order" value="Title"></td>
	<td></td>
	<td>Search Term: <input type="text" name="search_term" size="25"></td>
</tr><tr>
	<td align="right">Copyright Date</td>
	<td align="center"><input type="checkbox" name="chk_copyrightdate" value="CopyrightDate"></td>
	<td align="center"><input type="radio" name="search_order" value="CopyrightDate, Author"></td>
	<td></td>
	<td><input type="radio" name="search_type" value="Author">Author &nbsp;&nbsp;<input type="radio" name="search_type" value="Title" checked>Title &nbsp;&nbsp;<input type="radio" name="search_type" value="ISBNNumber">ISBN # &nbsp;&nbsp;<input type="radio" name="search_type" value="ISBNNumber13">ISBN13 # &nbsp;&nbsp;<input type="radio" name="search_type" value="Tag">Tag</td>
</tr><tr>
	<td align=right>Date Last Read</td>
	<td align="center"><input type="checkbox" name="chk_readdate" value="ReadDate"></td>
	<td align="center"><input type="radio" name="search_order" value="ReadDate"></td>
    <td><input type="checkbox" name="search_unread" value="yes"> Filter Read</td> 
	<td align="left">Location: <select name="search_cat">
	<option selected>All</option>
	<?php
include('./location_option.php');
?>
	</select></td>
</tr><tr>
	<td align="right">ISBN Number</td>
	<td align="center"><input type="checkbox" name="chk_isbnnumber" value="ISBNNumber"></td>
	<td></td>
	<td></td>
	<td></td>
</tr><tr>
	<td align="right">ISBN Number 13</td>
	<td align="center"><input type="checkbox" name="chk_isbnnumber13" value="ISBNNumber13"></td>
	<td></td>
	<td></td>
	<td></td>
</tr><tr>
	<td align="right"> Publisher Name</td>
	<td align="center">
	<input type="checkbox" name="chk_publishername" value="PublisherName"></td>
	<td></td>
	<td></td>
	<td></td>
</tr><tr>
	<td align="right">Pages</td>
	<td align="center">
	<input type="checkbox" name="chk_pages" value="Pages"></td>
	<td></td>
	<td></td>
	<td></td>
</tr><tr>
	<td align="right"> Location</td>
	<td align="center">
	<input type="checkbox" name="chk_location" value="Location"></td>
	<td align="center"><input type="radio" name="search_order" value="Location, Author"></td>
	<td></td>
	<td align="left"><input type="checkbox" name="search_numbyyear" value="yes"> Number Read/Year</td>
	<td></td>
</tr><tr>
	<td align="right"> Recycled</td>
	<td align="center">
	<input type="checkbox" name="chk_recycled" value="Recycled"></td>
	<td></td>
	<td><input type="checkbox" name="search_norecycle" value="yes">Filter Recycled</td>
</tr><tr>
	<td align=right> Cover Type</td>
	<td align="center"><input type="checkbox" name="chk_covertype" value="CoverType"></td>
	<td></td>
    <td align="left"><input type="checkbox" name="search_nodigital" value="yes">Filter Digital</td>
    <td><input type="submit" value="   Create Report   "></td>
</tr>
</table>
</form>
<?php
include './footer.php';
?>
</body>
</html>
