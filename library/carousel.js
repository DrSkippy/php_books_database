$(document).ready(function () {
    topnavbar();

    const endpointUrl = baseApiUrl + "/complete_records_window";
    const windowSize = 20;
    // GET with 2 parameeters /BOOKID/WINDOWSIZE (Optional, default 20)
    var url = endpointUrl + "/2/" + windowSize;
    $.getJSON(url, function (data) {
        for (var bookIdx = 0; bookIdx < windowSize; bookIdx++) {
            var bookString = "\n<li class=\"card-item swiper-slide\">\n" +
                "  <a href=\"#\" class=\"card-link\">\n";
            const bookObj = data[bookIdx]['book'];
            const readObj = data[bookIdx]['reads'];
            const tagObj = data[bookIdx]['tags'];
            bookString += "     <img src=\"https://plus.unsplash.com/premium_photo-173273dd6768075-4738ba4ccf1a?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D\" class=\"card-image\">\n"
            bookString += "     <p class=\"badge\"> Book ID: " + bookObj['data'][0][0] + "</p>\n";
            bookString += "<h3>";
            for (var i = 1; i < bookObj['header'].length; i++) {
                bookString += bookObj['header'][i] + ": " + bookObj['data'][0][i] + "</br>\n";
            }
            if (readObj['data'].length > 0) {
            for (var i = 1; i < readObj['header'].length; i++) {
                bookString += readObj['header'][i] + ": " + readObj['data'][0][i] + "</br>\n";
            }
            }
            bookString += tagObj['header'][0] + ": " + tagObj['data'][0].join("</br>") + "\n";
            bookString += "</h3>" +
                "     <button class=\"card-button\"><i class=\"fa-solid fa-arrow-right\"></i></button>\n" +
                "  </a>\n" +
                "</li>\n";
            console.log(bookObj);
            $("#card-deck").append(bookString);
        }
    });
    swiper.init(); // Initialize Swiper after content is ready
});

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