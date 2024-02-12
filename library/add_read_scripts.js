// Handle form submission
let form = document.forms.add_read;
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
var book_id = urlParams.get("book_id");

$(document).ready(function () {
    topnavbar();
    createDetailTableRows();
    setval(book_id);
    let now = new Date();
    console.log(now.toISOString().split('T')[0]);
    document.forms["add_read"]["read_date"].value = now.toISOString().split('T')[0];
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
    params = '[{"BookCollectionID":' + book_id + ',"ReadDate":"'  + date + '","ReadNote":"'  + note + '"}]';
    console.log(params);
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader('x-api-key', apiKey);
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
