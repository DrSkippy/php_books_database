$(document).ready(function () {
    topnavbar();
    var url1 = baseApiUrl + "/summary_books_read_by_year";
    $.getJSON(url1, function (data) {
        var obj = data['data'];
        for (var i = 0; i < obj.length; i++) {
            var url = new URL("/php_books_database/js_reports/books_read_by_year.html", window.location);
            url.searchParams.append("year", obj[i][0]);
            var tr = "<tr>" +
                "<td><a href=" + url.href + ">" + obj[i][0] + "</a></td>" +
                "<td>" + obj[i][1] + "</td>" +
                "<td>" + obj[i][2] + "</td></tr>";
            $("#mytable-sorted").append(tr);
        }
    });
    var url2 = baseApiUrl + "/recent";
    $.getJSON(url2, function (data) {
        var obj = data['data'];
        for (var i = 0; i < obj.length; i++) {
            var url = new URL("/php_books_database/js_reports/books_detail.html?author=&title=" +
                obj[i][2].toString().substring(0,20) + "&tags=", window.location);
            var tr = "<tr><td><a href=\"" + url.href + "\">" + obj[i][2] + "\"</a></td>" +
                "<td>" + obj[i][1] + "</td></tr>";
            console.log(tr);
            $("#mytable-recent").append(tr);
        }
    });
})