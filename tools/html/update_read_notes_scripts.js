var bookTitle = "Book Title";
var readReadDate = "Read Date";
var bookAuthor = "Book Author";
var bookNote = "Book Note";
var readReadNote = "Read Note";
var idArrayIndex = 0;

$(document).ready(function () {
    topnavbar();
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
    document.getElementById('bookNoteField').innerHTML = '<textarea id="bookNoteValue" ' +
        'cols="45" rows="5">' + bookNote + '</textarea>';
    document.getElementById('readReadNoteField').innerHTML = '<textarea id="readReadNoteValue" ' +
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

function update_note() {
    readNote = document.getElementById("readReadNoteValue").value
    bookNote = document.getElementById("bookNoteValue").value

    var dataRead = JSON.stringify({
        "BookCollectionID": bookCollectionID,
        "ReadNote": readNote
    });
    var dataBook = JSON.stringify({
        "BookCollectionID": bookCollectionID,
        "Note": bookNote
    });
    console.log(dataRead);
    console.log(dataBook);

    var urlBook = baseApiUrl + "/update_book_note_status";
    var urlRead = baseApiUrl + "/update_edit_read_note";

    // Post the data
    xhr = new XMLHttpRequest();
    xhr.open("POST", urlBook, false);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(dataBook);
    xhr = new XMLHttpRequest();
    xhr.open("POST", urlRead, false);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(dataRead);
    navigate(1);
}
