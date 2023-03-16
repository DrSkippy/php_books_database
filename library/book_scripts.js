$(document).ready(function () {
    topnavbar();
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    var url = baseApiUrl + "/books_search?";
    if (urlParams.has("author")) {
        url += "author=" + urlParams.get("author");
    } else if (urlParams.has("title")) {
        url += "title=" + urlParams.get("title");
    } else if (urlParams.has("tag")) {
        url += "Tags=" + urlParams.get("tags");
    }
    $.getJSON(url, function (data) {
        var obj = data['data'];
        for (var i = 0; i < obj.length; i++) {
            var tr = "<tr>" +
                "<td><button onclick=\"setval(" + obj[i][0] + ")\">" + obj[i][0].toString() + "</button></td>" +
                "<td>" + obj[i][1] + "</td>" +
                "<td>" + obj[i][2] + "</td>" +
                "<td>" + obj[i][3] + "</td>" +
                "<td>" + obj[i][7] + "</td>" +
                "<td>" + obj[i][13] + "</td></tr>";
            $("#mytable").append(tr);
        }
    });
    createDetailTableRows();
});