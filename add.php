<!---
//
// Scott Hendrickson
// 2013-11-30
// https://github.com/DrSkippy27/php_books_database
//
--->

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<?php
include('header.php');
?>
<h1>Add Entry</h1>

<?php
include('./db_header.php');
?>
<form name="add" action="./add_entry.php">
<table>
<tr>
	<td align="right">Author:</td>
	<td><input type="text" size="25" name="author"></td>
	<td align="right">Title:</td>
	<td><input type="text" size="25" name="title"></td>
</tr><tr>
	<td align="right">ISBN #:</td>
	<td><input type="text" size="25" name="isbnnumber"></td>
		<td align="right">ISBN13 #:</td>
	<td><input type="text" size="25" name="isbnnumber13"></td>
</tr><tr>
	<td align="right">Publisher:</td>
	<td><input type="text" size="25" name="publishername"></td>
	<td></td>
	<td></td>
</tr><tr>
	<td align="right">Note:</td>
	<td colspan="2"><textarea name="note" cols="28" rows="3"></textarea></td>
	<td><input type="radio" name="covertype" value="Hard"> Hard Cover<br>
	    <input type="radio" name="covertype" value="Soft" checked> Soft Cover<br>
		<input type="radio" name="covertype" value="Digital"> Digital<br>
	Recycled: <input type="checkbox" name=recycled value="yes">
	</td>
</tr><tr>
	<td align="right">Location:</td>
	<td><select name="location">
<?php
$result = mysqli_query($dbcnx, 'SELECT DISTINCT Location FROM `book collection` order by Location');
if (!$result) {
    exit('<p>Error performing query: ' . mysqli_error($dbcnx) . '</p>');
}
while ($row = mysqli_fetch_array($result)) {
    echo '<option>' . $row['Location'] . '</option>';
}
?>
	</select></td>
	<td align="right">Pages:</td>
	<td><input type="text" name="pages" size="10"></td>
</tr><tr>
	<td align="right">Copyright:</td>
	<td><input type="text" name="copyrightdate" size="6"> yyyy only!</td>
	<td></td>
	<td align="right"><input type="submit" value="      Add Entry     "></td>
</tr>
</table>
</form>

<?php
include './footer.php';
?>
