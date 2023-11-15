$(document).ready(function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    // get form values
    const book_id = urlParams.get("book_id");
    const tag_array = urlParams.get("tag_string").split(",");

    tag_array.forEach(function (arrayItem) {
        console.log(arrayItem);
        var url = baseApiUrl + "/add_tag/" + book_id + "/" + arrayItem.trim().toLowerCase();
        console.log(url);
        $.ajax({
            url: url,
            type: "PUT",
            success: function(data) {
                console.log(url);
            }
        })
    });
    alert("Tags (" + tag_array + ") added successfully to ID=" + book_id);
    window.location.href = "./index.html";
    return false;
})
