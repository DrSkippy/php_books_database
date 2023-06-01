$(document).ready(function () {
    topnavbar();
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    var url = baseApiUrl + "/books_search?Recycled=0&CoverType=Hard&CoverType=Soft&Location=Main";
    $.ajaxSetup({async: false});  // suppress async so the summary row is always at the bottom
    var idArray;
    $.getJSON(url, function (data) {
        var obj = data['data'];
        idArray = obj.map(function(x) {
            return x[0];
        });
        for (var i = 0; i < obj.length; i++) {
            var checkedString = ((parseInt(obj[i][10]) == 1) ? "checked":"");
            console.log(checkedString);
            var tr = "<tr>" +
                "<td><button onclick=\"setval(" + obj[i][0] + ")\">" + obj[i][0].toString() + "</button></td>" +
                "<td>" + obj[i][1] + "</td>" +
                "<td>" + obj[i][2] + "</td>" +
                "<td>" + obj[i][3] + "</td>" +
                "<td>" + obj[i][6] + "</td>" +
                "<td>" + obj[i][13] + "</td>" +
                "<td><input type=\"checkbox\" id=\"recycled\" name=\"recycled\"" + checkedString + "></td></tr>";
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