// Handle form submission
let form = document.forms.add_book_estimate;
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
var book_id = urlParams.get("book_id");
window.addEventListener('DOMContentLoaded', function() {
    topnavbar();
})

form.addEventListener('submit', function(event) {
    event.preventDefault(); // prevent page reload
    console.log("submit called...");
    // get form values
    var start_date = document.forms["add_book_estimate"]["start_date"].value;
    var readable_pages = document.forms["add_book_estimate"]["readable_pages"].value;
    // get form values
    console.log(start_date, readable_pages, record_id);
    // submit form data
    var xhr = new XMLHttpRequest();
    var url = baseApiUrl + "/add_book_estimate/" + book_id;
    baseApiUrl += "/" + readable_pages + "/" + start_date + "/";
    console.log(url);
    xhr.open("PUT", url, true);
    xhr.setRequestHeader('x-api-key', apiKey);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(xhr.responseText);
            var book_id = JSON.parse(xhr.responseText).add_date_page.BookCollectionID;
            alert("Entry added successfully!\n ID=" + book_id);
            window.location.href = "./books_detail.html?bookid=" + book_id.toString();
        }
    };
    xhr.send(params);
    window.location.href = "./books_detail.html?bookid=" + book_id.toString();
    return false;
})