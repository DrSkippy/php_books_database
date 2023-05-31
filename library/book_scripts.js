$(document).ready(function () {
    topnavbar();
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    console.log(queryString)
    var url = baseApiUrl + "/books_search?";
    var continue_flag = false;
    if (urlParams.has("author") && urlParams.get("author").trim() != "") {
        url += "Author=" + urlParams.get("author").trim();
        continue_flag = true;
    }
    console.log(url);
    if (urlParams.has("title") && urlParams.get("title").trim() != "") {
        if (continue_flag) {
            url += "&";
        }
        url += "Title=" + urlParams.get("title").trim();
        continue_flag = true;
    }
    console.log(url);
    if (urlParams.has("tags") && urlParams.get("tags").trim() != "") {
        if (continue_flag) {
            url += "&";
        }
        url += "Tags=" + urlParams.get("tags").trim();
    }
    console.log(url);
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