$(document).ready(function () {
    topnavbar();

    var url = baseApiUrl + "/books_search?Recycled=0&Location=Main";
    var idArray;
    $.getJSON(url, function (data) {
        var obj = data['data'];
        idArray = obj.map(function (x) {
            return x[0];
        });
        $.ajaxSetup({async: false});  // suppress async so the summary row is always at the bottom
        /* for (var i = 0; i < obj.length; i++) { */
        for (var i = 0; i < 100; i++) {
            var bookCollectionID = obj[i][0];
            var urlTag = baseApiUrl + "/tags/" + bookCollectionID;
            var tagStr = "Not Found";
            var readStr = "Not Found";
            $.getJSON(urlTag, function (data) {
                var tagObj = data['tag_list'];
                tagStr = "Tags: " + tagObj.join(", ").slice(0,50) + "...";
            });
            var urlRead = baseApiUrl + "/status_read/" + bookCollectionID;
            $.getJSON(urlRead, function (data) {
                var readObj = data['data'];
                readStr = "";
                for (var i = 0; i < readObj.length; i++) {
                    readStr += readObj[i][1] + "</br>\n" +
                        readObj[i][2] + "</br>\n";
                }
                if (readStr.length >0) {
                    readStr = "Read: " + readStr;
                }
            });
            var bookString = "\n" +
                "<li class=\"card-item swiper-slide\">\n" +
                "  <a href=\"#\" class=\"card-link\">\n" +
                "     <img src=\"https://plus.unsplash.com/premium_photo-1732736768075-4738ba4ccf1a?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D\" class=\"card-image\">\n" +
                "     <p class=\"badge\"> Title: " + obj[i][1] + "</p>\n" +
                "     <h3 class=\"card-title\"> Author: " +
                obj[i][2] + " (pub. " + obj[i][3].slice(0,4) + ")</br>\n Pages: " +
                obj[i][7] + " &nbsp;&nbsp;&nbsp; Cover Type: " +
                obj[i][6] + "</br>\n ISBN: " +
                obj[i][12] + "</br>\n" +
                tagStr + "</br>" +
                readStr + "</h3>\n" +
                "     <button class=\"card-button\"><i class=\"fa-solid fa-arrow-right\"></i></button>\n" +
                "   </a>\n" +
                "</li>\n"
            console.log(bookString);
            $("#card-deck").append(bookString);
        }
    });
    swiper.init(); // Initialize Swiper after content is ready
});

const swiper = new Swiper('.card-wrapper', {
    init: false,
    loop: true,
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