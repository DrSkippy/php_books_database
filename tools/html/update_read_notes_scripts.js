var bookTitle = "Book Title";
var readReadDate = "Read Date";
var bookAuthor = "Book Author";
var bookNote = "Book Note";
var readReadNote = "Read Note";
var idArrayIndex = 0;

$(document).ready(function () {

    $.ajaxSetup({async: false});  // suppress async so the summary row is always at the bottom

    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    // ...&idArray[]=1604&idArray{}=1605&idArray[]=1696
    idArray = urlParams.getAll("idArray[]");
    populateFields();
});

function populateFields() {
    bookCollectionID = idArray[idArrayIndex];

    var urlBook = baseApiUrl + "/books_search?BookCollectionID=" + bookCollectionID;
    var urlRead = baseApiUrl + "/status_read/" + bookCollectionID;

    $.getJSON(urlRead, function (data) {
        var obj = data['data'];
        readReadDate = obj[0][1];
        readReadNote = obj[0][2];
    });

    $.getJSON(urlBook, function (data) {
        var obj = data['data'];
        bookTitle = obj[0][1];
        bookAuthor = obj[0][2];
        bookNote = obj[0][9];
    });

    document.getElementById('bookBookCollectionIDField').innerHTML = bookCollectionID;
    document.getElementById('readBookCollectionIDField').innerHTML = bookCollectionID;
    document.getElementById('bookTitleField').innerHTML = bookTitle;
    document.getElementById('bookAuthorField').innerHTML = bookAuthor;
    document.getElementById('readReadDateField').innerHTML = readReadDate;
    document.getElementById('bookNoteField').innerHTML = '<textarea name="bookNoteValue" ' +
        'cols="45" rows="5">' + bookNote + '</textarea>';
    document.getElementById('readReadNoteField').innerHTML = '<textarea name="readReadNoteValue" ' +
        'cols="45" rows="5">' + readReadNote + '</textarea>';
}

function navigate(idInc) {
    if (idArrayIndex == 0 && idInc == -1) {
        idArrayIndex = idArray.length - 1;
    } else if (idArrayIndex == idArray.length - 1 && idInc == 1) {
        idArrayIndex = 0;
    } else {
        idArrayIndex += idInc;
    }
    populateFields();
}

function update() {
    var dataRead = JSON.stringify({
        "BookCollectionID": bookCollectionID,
        "ReadNote": readReadNoteValue
    });
    var dataBook = JSON.stringify({
        "BookCollectionID": bookCollectionID,
        "ReadDate": readReadDate,
        "ReadNote": readReadNoteValue
    });
    // Creating a XHR object
    var xhr = new XMLHttpRequest();
    var url = "submit.php";
    // open a connection
    xhr.open("POST", url, true);
    // Set the request header i.e. which type of content you are sending
    xhr.setRequestHeader("Content-Type", "application/json");
    // Create a state change callback
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Print received data from server
            result.innerHTML = this.responseText;
        }
    };
    xhr.send(data);
}