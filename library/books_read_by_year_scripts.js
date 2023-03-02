$(document).ready(function () {
    topnavbar();
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    var url = baseApiUrl + "/books_read";
    $.ajaxSetup({async: false});  // suppress async so the summary row is always at the bottom
    if (urlParams.has("year")) {
        const year = urlParams.get('year');
        url = url + "/" + year
        const url1 = baseApiUrl + "/summary_books_read_by_year/" + year;
        $.getJSON(url1, function (data) {
            var obj = data['data'];
            for (var i = 0; i < obj.length; i++) {
                var tr = "<tr class='summary-row'>" +
                    "<td>" + obj[i][0] + "</td><td></td><td></td><td></td>" +
                    "<td>" + obj[i][1] + "</td>" +
                    "<td>" + obj[i][2] + "</td></tr>";
                $("#mytable").append(tr);
            }
        });
    }
    var idArray;
    $.getJSON(url, function (data) {
        var obj = data['data'];
        idArray = obj.map(function(x) {
            return x[0];
        });
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
    const idArrayURLEnc = idArray.map(function(x) {return "idArray=" + x.toString();}).join("&");
    console.log(idArray);
    console.log(idArrayURLEnc);
    document.getElementById("updatereadnotesurl").innerHTML = '<a href=' +
        '"/php_books_database/js_reports/update_read_notes.html?' + idArrayURLEnc + '">' +
        'Update book read notes for items in this list</a>';
    createDetailTableRows();
    $.ajaxSetup({async: true});  // suppress async so the summary row is always at the bottom
});