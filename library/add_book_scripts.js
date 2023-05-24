window.addEventListener('DOMContentLoaded', function() {
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

	// Handle form submission
	let form = document.forms.add;
	form.addEventListener('submit', function(event) {
        event.preventDefault(); // prevent page reload

        function addEntry() {
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
        xhr.onreadystatechange = function () {
          if (this.readyState == 4 && this.status == 200) {
            alert("Entry added successfully!");
            window.location.href = "./index.php";
          }
        };
        // xhr.open("POST", "./add_entry.php", true);
        xhr.open("POST", baseAPIUrl + "/add_books", true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.send("author=" + author + "&title=" + title + "&isbnnumber=" + isbnnumber + "&isbnnumber13=" + isbnnumber13 + "&publishername=" + publishername + "&note=" + note + "&covertype=" + covertype + "&recycled=" + recycled + "&location=" + location + "&pages=" + pages + "&copyrightdate=" + copyrightdate);

        return false;
      }
    })
})