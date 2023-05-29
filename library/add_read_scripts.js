// Handle form submission
let form = document.forms.add_read;
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
var book_id = urlParams.get("book_id");

window.addEventListener('DOMContentLoaded', function() {
    topnavbar();
    setval(book_id);
    // Populate location dropdown with data from web API
//    var url = baseApiUrl + "/books_search?BookCollectionId=" + book_id;
//    console.log(url)
//    $.getJSON(url, function (response) {
//        var data = response['data'];
//        console.log(data);
//    }).catch(error => {
//        console.error('Error fetching locations:', error);
//    });
//
//    if (isbn_target != null) {
//        // Populate fields from isbn.com
//        var url = baseApiUrl + "/books_by_isbn";
//        console.log(url);
//        params = '{"isbn_list":["' + isbn_target + '"]}';
//        console.log(params);
//        var xhr = new XMLHttpRequest();
//        xhr.open("POST", url, true);
//        xhr.setRequestHeader("Content-type", "application/json");
//        xhr.onreadystatechange = function () {
//            if (this.readyState == 4 && this.status == 200) {
//                console.log(xhr.responseText);
//                var isbn = JSON.parse(xhr.responseText).book_records[0];
//                // Set values
//                document.forms["add"]["author"].value = isbn.Author;
//                document.forms["add"]["title"].value = isbn.Title;
//                document.forms["add"]["isbnnumber"].value = isbn.ISBNNumber;
//                document.forms["add"]["isbnnumber13"].value = isbn.ISBNNumber13;
//                document.forms["add"]["publishername"].value = isbn.PublisherName;
//                document.forms["add"]["note"].value = isbn.Note;
//                document.forms["add"]["pages"].value = isbn.Pages;
//                document.forms["add"]["copyrightdate"].value = isbn.CopyrightDate;
//            }
//        };
//        xhr.send(params);
//    }
});

form.addEventListener('submit', function(event) {
    event.preventDefault(); // prevent page reload
    console.log("submit called...");
    // get form values
    var note = document.forms["add_read"]["read_note"].value;
    var date = document.forms["add_read"]["read_date"].value;

    // submit form data
    var xhr = new XMLHttpRequest();
    var url = baseApiUrl + "/add_read_dates";
    console.log(url);
    params = '[{"BookCollectionId":"' + book_id + '","DateREad":"'  + date + '","ReadNote":"'  + note + '"}]';
    console.log(params);
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(xhr.responseText);
            alert("Entry added successfully!\n ID=" + book_id);
            window.location.href = "./index.html";
        }
    };
    xhr.send(params);
    return false;
})