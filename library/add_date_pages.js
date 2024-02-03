// Handle form submission
let form = document.forms.add_date_pages;
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
var record_id = urlParams.get("record_id");
var book_id = urlParams.get("book_id");
window.addEventListener('DOMContentLoaded', function() {
    topnavbar();
    var url = baseApiUrl + "/date_page_records/" + record_id;
    console.log(url);
        $.getJSON(url, function (data) {
        var obj = data['date_page_records'];
        for (var i = 0; i < obj.length; i++) {
            var tr = "<tr>" +
                "<td>" + obj[i][0] + "</td>" +
                "<td>" + obj[i][1] + "</td>" +
                "<td></td>";
            $("#mytable").append(tr);
        }
        var lastLine = "<tr><td><input type=\"date\" name=\"date\" id=\"date\" required></td>" +
            "<td><input type=\"number\" name=\"page\" id=\"page\" required></td>" +
            "<td><input type=\"submit\" value=\"submit\"></td></tr>";
        $("#mytable").append(lastLine);
    });
})

form.addEventListener('submit', function(event) {
    event.preventDefault(); // prevent page reload
    console.log("submit called...");
    // get form values
    var date = document.forms["add_date_pages"]["date"].value;
    var page = document.forms["add_date_pages"]["page"].value;
    // get form values
    console.log(date, page, record_id);
    // submit form data
    var xhr = new XMLHttpRequest();
    var url = baseApiUrl + "/add_date_page";
    console.log(url);
    params = '{"RecordID":' + record_id + ',"RecordDate":"'  + date +
        '","Page":'  + page + '}';
    console.log(params);
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader('x-api-key', apiKey);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(xhr.responseText);
            var record_id = JSON.parse(xhr.responseText).add_date_page.RecordID;
            alert("Entry added successfully!\n ID=" + record_id);
            window.location.href = "./books_detail.html?bookid=" + book_id.toString();
        }
    };
    xhr.send(params);
    window.location.href = "./books_detail.html?bookid=" + book_id.toString();
    return false;
})