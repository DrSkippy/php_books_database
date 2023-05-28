$(document).ready(function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    // get form values
    const book_id = urlParams.get("book_id");
    const tag_array = urlParams.get("tag_string").split(",");

    tag_array.forEach(function (arrayItem) {
        console.log(arrayItem);
        var url = baseApiUrl + "/add_tag/" + book_id + "/" + arrayItem;
        console.log(url);
    });

    alert("Entry added successfully!\n ID=" + book_id);

    return false;
})
