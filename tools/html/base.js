const baseApiUrl = "http://192.168.127.8/books";
var bookCollectionID = 102;

function setval(bcid) {
    //$.ajaxSetup({async: false});  // suppress async so the summary row is always at the bottom
    bookCollectionID = bcid;
    var urlId = baseApiUrl + "/books_search?BookCollectionID=" + bookCollectionID;
    var urlTag = baseApiUrl + "/tags/" + bookCollectionID;
    $.getJSON(urlId, function (data) {
        var obj = data['data'];
        for (var i = 0; i < obj.length; i++) {
            var trOne = "<tr id='replace-me-one'>" +
                "<td>" + obj[i][0] + "</td>" +
                "<td>" + obj[i][1] + "</td>" +
                "<td>" + obj[i][2] + "</td>" +
                "<td>" + obj[i][3] + "</td>" +
                "<td>" + obj[i][5] + "</td>" +
                "<td>" + obj[i][6] + "</td>" +
                "<td>" + obj[i][7] + "</td>" +
                "<td>" + obj[i][10] + "</td>" +
                "<td>" + obj[i][11] + "</td>" +
                "<td>" + obj[i][4] + "</td>" +
                "<td>" + obj[i][12] + "</td>" +
                "<td>" + obj[i][13] + "</td>" +
                "<td>" + obj[i][9] + "</td></tr>";
            $("#replace-me-one").replaceWith(trOne);
        }
    });
    $.getJSON(urlTag, function (data) {
        var obj = data['tag_list'];
        console.log(obj);
        var trTwo = "<tr id='replace-me-two'>" +
            "<td>Tags:</td><td colspan=13>" + obj.join(", ") + "</td></tr>";
        $("#replace-me-two").replaceWith(trTwo);
    });
}

function createDetailTableRows() {
    var trOne = "<tr id='replace-me-one'>" +
        "<td/><td>(select a record)</td><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/>" +
        "</tr>";
    $("#sumtable").append(trOne);
    var trTwo = "<tr id='replace-me-two'>" +
        "<td>Tags:</td><td colspan=13></td></tr>";
    $("#sumtable").append(trTwo);
}