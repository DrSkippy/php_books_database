//const baseApiUrl = "http://192.168.127.8/books";

const baseApiUrl = "http://10.0.0.14/books";
var bookCollectionID = 102;

function setval(bcid) {
    //$.ajaxSetup({async: false});  // suppress async so the summary row is always at the bottom
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
            "<td>Tags:</td><td colspan=12>" + obj.join(", ") + "</td></tr>";
        $("#replace-me-two").replaceWith(trTwo);
    });
    $.getJSON(urlRead, function (data) {
        var obj = data['data'];
        console.log(obj);
        var trThree = "<tr id='replace-me-three'>" +
            "<td>Read:</td>" +
            "<td colspan=12>" +
            "<table id='readtable' class=\"styled-inner-table\">\n" +
            "<thead>\n" +
            "<tr>\n" +
            "<th>Read Date</th>\n" +
            "<th>Raad Notes</th>\n" +
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