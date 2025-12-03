let minCarouselBookId = 0;
let maxCarouselBookId = 0;
const windowSize = 20;
const startingBookId = 2;

$(document).ready(function () {
    topnavbar();

    const endpointUrl = baseApiUrl + "/complete_records_window";
    // GET with 2 parameeters /BOOKID/WINDOWSIZE
    const url = endpointUrl + "/" + startingBookId + "/" + windowSize;
    $.getJSON(url, function (data) {
        minCarouselBookId = data[0]['book']['data'][0][0];
        maxCarouselBookId = data[windowSize - 1]['book']['data'][0][0];
        for (var bookIdx = 0; bookIdx < windowSize; bookIdx++) {
            const bookObj = data[bookIdx]['book'];
            const readObj = data[bookIdx]['reads'];
            const tagObj = data[bookIdx]['tags'];
            var bookString = listItems(bookObj, readObj, tagObj);
            $("#card-deck").append(bookString);
        }
        //console.log(minCarouselBookId, maxCarouselBookId, url);
        swiper.init(); // Initialize Swiper after content is ready
    });
});

function listItems(bookObj, readObj, tagObj)  {
    let bookString = "\n<li class=\"card-item swiper-slide\">\n" +
        " <a href=\"#\" class=\"card-link\">\n";
    bookString += "  <div class=\"book-record\">\n";
    bookString += "    <img src=\"/img/bookparts.webp\" class=\"card-image\">\n";
    bookString += "    <div class=\"badge\"> Book ID: " + bookObj['data'][0][0] + "</div>\n";
    let fieldsList = [1,2,3,4,12,5,6,7,11,9];
    for (const i of fieldsList) {
        bookString += "    <span class='field-title'>" + bookObj['header'][i] + ":</span> " + bookObj['data'][0][i] + "</br>\n";
    }
    if (readObj['data'].length > 0) {
        for (var i = 1; i < readObj['header'].length; i++) {
            bookString += "    <span class='field-title'>" + readObj['header'][i] + ":</span> " + readObj['data'][0][i] + "</br>\n";
        }
    }
    bookString += "    <span class='field-title'>" + tagObj['header'][0] + ":</span> " + tagObj['data'][0].join(", ") + "</br>\n";
    bookString += "    <button class=\"card-button\"><i class=\"fa-solid fa-arrow-right\"></i></button>\n";
    bookString += "  </div>\n  </a>\n</li>\n";
    //console.log(bookString);
    return bookString;
}

const swiper = new Swiper('.card-wrapper', {
    init: false,
    loop: false,
    speed: 700,
    spaceBetween: 30,
    direction: 'horizontal',

    // If we need pagination
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
        dynamicBullets: true,
    },

    // Navigation arrows
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },

    breakpoints: {
        0: {
            slidesPerView: 1
        },
        768: {
            slidesPerView: 2
        },
        1024: {
            slidesPerView: 3
        },
    }
});

swiper.on('reachBeginning', function () {
    const endpointUrl = baseApiUrl + "/complete_record";
    const direction = "previous";
    const url = endpointUrl + "/" + minCarouselBookId + "/" + direction;
    //console.log(minCarouselBookId, maxCarouselBookId, url);
    $.getJSON(url, function (data) {
        minCarouselBookId = data['book']['data'][0][0];
        const bookObj = data['book'];
        const readObj = data['reads'];
        const tagObj = data['tags'];
        swiper.prependSlide(listItems(bookObj, readObj, tagObj));
        swiper.update(); // Update Swiper after adding new slides
    });
});

swiper.on('reachEnd', function () {
    const endpointUrl = baseApiUrl + "/complete_record";
    const direction = "next";
    const url = endpointUrl + "/" + maxCarouselBookId + "/" + direction;
    //console.log(minCarouselBookId, maxCarouselBookId, url);
    $.getJSON(url, function (data) {
        maxCarouselBookId = data['book']['data'][0][0];
        const bookObj = data['book'];
        const readObj = data['reads'];
        const tagObj = data['tags'];
        swiper.appendSlide(listItems(bookObj, readObj, tagObj));
        swiper.update(); // Update Swiper after adding new slides
    });
});
