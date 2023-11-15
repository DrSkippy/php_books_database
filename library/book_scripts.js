$(document).ready(function () {
    topnavbar();
    
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    
    var url = baseApiUrl + "/books_search?";
    var params_continue_flag = false;
    
    if (urlParams.has("author") && urlParams.get("author").trim() != "") {
        url += "Author=" + urlParams.get("author").trim();
        params_continue_flag = true;
    }

    if (urlParams.has("bookid") && urlParams.get("bookid").trim() != "") {
        url += "BookCollectionID=" + urlParams.get("bookid").trim();
        params_continue_flag = true;
    }

    if (urlParams.has("title") && urlParams.get("title").trim() != "") {
        if (params_continue_flag) {
            url += "&";
        }
        url += "Title=" + urlParams.get("title").trim();
        params_continue_flag = true;
    }

    if (urlParams.has("tags") && urlParams.get("tags").trim() != "") {
        if (params_continue_flag) {
            url += "&";
        }
        url += "Tags=" + urlParams.get("tags").trim();
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
