// Handle form submission
let form = document.forms.add;
window.addEventListener('DOMContentLoaded', function() {
    topnavbar();
    // Populate location dropdown with data from web API
    var url = baseApiUrl + "/valid_locations";
    console.log(url)
    $.getJSON(url, function (response) {
        var data = response['data'];
        let locationDropdown = document.querySelector('select[name="location"]');
        for (var i = 0; i < data.length; i++) {
            let option = document.createElement('option');
            option.value = data[i];
            option.textContent = data[i];
            locationDropdown.appendChild(option);
        }
    }).catch(error => {
        console.error('Error fetching locations:', error);
    });

    // Populate fields from isbn.com
    var url = baseApiUrl + "/books_by_isbn";
    console.log(url);
    params = '{"isbn_list":["0060929480"]}';
    console.log(params);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(xhr.responseText);
            console.log(xhr.responseXML)
            var isbn = JSON.parse(xhr.responseText).book_records[0];
            // Set values
            document.forms["add"]["author"].value = isbn.Author;
            document.forms["add"]["title"].value = isbn.Title;
            document.forms["add"]["isbnnumber"].value = isbn.ISBNNumber;
            document.forms["add"]["isbnnumber13"].value = isbn.ISBNNumber13;
            document.forms["add"]["publishername"].value = isbn.PublisherName;
            document.forms["add"]["note"].value = isbn.Note;
            document.forms["add"]["pages"].value = isbn.Pages;
            document.forms["add"]["copyrightdate"].value = isbn.CopyrightDate;
        }
    };
    xhr.send(params);

});

form.addEventListener('submit', function(event) {
    event.preventDefault(); // prevent page reload
    console.log("submit called...");
    // get form values
    var author = document.forms["add"]["author"].value;
    var title = document.forms["add"]["title"].value;
    var isbnnumber = document.forms["add"]["isbnnumber"].value;
    var isbnnumber13 = document.forms["add"]["isbnnumber13"].value;
    var publishername = document.forms["add"]["publishername"].value;
    var note = document.forms["add"]["note"].value;
    var covertype = document.querySelector('input[name="covertype"]:checked').value;
    var recycled = document.forms["add"]["recycled"].checked ? "yes" : "no";
    var location = document.forms["add"]["location"].value;
    var pages = document.forms["add"]["pages"].value;
    var copyrightdate = document.forms["add"]["copyrightdate"].value;

    // validate form values
    if (author == "" || title == "" || isbnnumber == "" || publishername == "" || location == "" || pages == "" || copyrightdate == "") {
      alert("Please fill in all required fields.");
      return false;
    }

    if (isNaN(pages) || isNaN(copyrightdate)) {
      alert("Please enter a valid number for Pages and Copyright.");
      return false;
    }

    // submit form data
    var xhr = new XMLHttpRequest();
    var url = baseApiUrl + "/add_books";
    console.log(url);
    params = '[{"Author":"' + author + '","Title":"'  + title + '","ISBNNumber":"'  + isbnnumber + '","ISBNNumber13":"'  +
        isbnnumber13 + '","PublisherName":"'  + publishername + '","Note":"'  + note + '","CoverType":"'  + covertype +
        '","Recycled":"'  + recycled + '","Location":"'  + location + '","Pages":"'  + pages + '","CopyrightDate":"'  +
        copyrightdate + '"}]';
    console.log(params);
    // xhr.open("POST", "./add_entry.php", true);
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            alert("Entry added successfully!\n" + xhr.responseText);
            window.location.href = "../index.php";
        }
    };
    xhr.send(params);

    return false;
})