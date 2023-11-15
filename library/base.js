const baseApiUrl = 'http://192.168.127.13:8083'
var bookCollectionID = 102;

function topnavbar() {
    document.getElementById("insertTopNavBar").innerHTML = '<div class="topnav">' +
        '<a href="/php_books_database/index.php">Browse Collection</a>' +
        '<a href="/php_books_database/js_reports/index.html">Search & Reports</a>' +
        '<a href="/php_books_database/js_reports/progress.html">Yearly Progress</a>' +
        '<a href="/php_books_database/js_reports/books_read_by_year.html">Books Read - All</a>' +
        '<a href="/php_books_database/js_reports/inventory.html">Inventory</a>' +
        '</div>';
}

function setval(bcid) {
    bookCollectionID = bcid;
    var urlId = baseApiUrl + "/books_search?BookCollectionID=" + bookCollectionID;
    var urlTag = baseApiUrl + "/tags/" + bookCollectionID;
    var urlRead = baseApiUrl + "/status_read/" + bookCollectionID;
    $.getJSON(urlId, function (data) {
        var obj = data['data'];
        var trOne = "<tr id='replace-me-one'>" +
            "<td>" + obj[0][0] + "</td>" +
            "<td>" + obj[0][1] + "</td>" +
            "<td>" + obj[0][2] + "</td>" +
            "<td>" + obj[0][3] + "</td>" +
            "<td>" + obj[0][5] + "</td>" +
            "<td>" + obj[0][6] + "</td>" +
            "<td>" + obj[0][7] + "</td>" +
            "<td>" + obj[0][10] + "</td>" +
            "<td>" + obj[0][11] + "</td>" +
            "<td>" + obj[0][4] + "</td>" +
            "<td>" + obj[0][12] + "</td>" +
            "<td>" + obj[0][13] + "</td>" +
            "<td>" + obj[0][9] + "</td></tr>";
        $("#replace-me-one").replaceWith(trOne);
    });
    $.getJSON(urlTag, function (data) {
        var obj = data['tag_list'];
        var trTwo = "<tr id='replace-me-two'>" +
            "<td>Tags:</td><td colspan=6>" + tag_links_list(obj) + "</td>" +
            "   <td colspan=6><form name=\"add_tag\" action=\"/php_books_database/js_reports/add_tags.html\">" +
            "   <label for=\"lname\">Add Tag List:&nbsp; </label>" +
            "   <input type=\"hidden\" id=\"book_id\" name=\"book_id\" value=\"" + data["BookID"] + "\">" +
            "   <input type=\"text\" id=\"tag_string\" name=\"tag_string\">" +
            "   <input type=\"submit\" value=\"submit\">\n" +
            "   </form></td></tr>";
        $("#replace-me-two").replaceWith(trTwo);
    });
    $.getJSON(urlRead, function (data) {
        var obj = data['data'];
        console.log(obj);
        var trThree = "<tr id='replace-me-three'>" +
            "<td>Read:  <a href=\"/php_books_database/js_reports/add_read.html?book_id=" +
            bookCollectionID + "\">Add</a></td>" +
            "<td colspan=12>" +
            "<table id='readtable' class=\"styled-inner-table\">\n" +
            "<thead>\n" +
            "<tr>\n" +
            "<th>Date</th>\n" +
            "<th>Notes</th>\n" +
            "</tr>\n" +
            "</thead>\n" +
            "<tbody>\n";
        for (var i = 0; i < obj.length; i++) {
            trThree += "<tr><td>" + obj[i][1] + "</td>" +
                "<td>" + obj[i][2] + "</td></tr>";
        }
        trThree += "</tbody></table></tr>";
        $("#replace-me-three").replaceWith(trThree);
    });
}

function tag_links_list(tags_list) {
    var tag_links = "";
    for (var i = 0; i < tags_list.length; i++) {
        tag_links += "<a href=\"/php_books_database/js_reports/books_detail.html?tags=" +
            tags_list[i] + "\">"+tags_list[i]+"</a>, ";
    }
    return tag_links.substring(0,tag_links.length - 2);
}

function createDetailTableRows() {
    var trOne = "<tr id='replace-me-one'>" +
        "<td/><td>(select a record)</td><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/>" +
        "</tr>";
    $("#sumtable").append(trOne);
    var trTwo = "<tr id='replace-me-two'>" +
        "<td>Tags:</td><td colspan=12></td></tr>";
    $("#sumtable").append(trTwo);
    var trThree = "<tr id='replace-me-three'>" +
        "<td>Read:</td><td colspan=12></td></tr>";
    $("#sumtable").append(trThree);
}

function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("mytable-sorted");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";
    /* Make a loop that will continue until no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir == "asc") {
                if (sortNumber(x.innerHTML, n) > sortNumber(y.innerHTML, n)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (sortNumber(x.innerHTML, n) < sortNumber(y.innerHTML, n)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}


function sortNumber(columnValue, columnIndex) {
    if (columnIndex > 0) {
        return parseInt(columnValue);
    } else {
        const re = /\d+</g;
        const found = columnValue.match(re);
        return parseInt(found);

    }
}
