// $(function() {
//     $('.jcarousel').jcarousel({
//         list: '.jcarousel-list',
//         wrap: 'both'
//     });

//     $('.jcarousel-prev').jcarouselControl({
//         target: '-=1'
//     });

//     $('.jcarousel-next').jcarouselControl({
//         target: '+=1'
//     });

//     $('.jcarousel-pagination').jcarouselPagination({
//     	'perPage': 3
// 	});
// });

// $('.jcarousel')
//     .on('jcarousel:create jcarousel:reload', function() {
//         var element = $(this),
//             width = element.innerWidth();

//         if (width > 900) {
//             width = width / 3;
//         } else if (width > 600) {
//             width = width / 2;
//         }

//         element.jcarousel('items').css('width', width + 'px');
//     })
//     .jcarousel({
//         list: '.jcarousel-list',
//         wrap: 'both'
//     });


(function($) {
    $(function() {
        $('.jcarousel').jcarousel();

        $('.jcarousel-control-prev')
            .on('jcarouselcontrol:active', function() {
                $(this).removeClass('inactive');
            })
            .on('jcarouselcontrol:inactive', function() {
                $(this).addClass('inactive');
            })
            .jcarouselControl({
                target: '-=1'
            });

        $('.jcarousel-control-next')
            .on('jcarouselcontrol:active', function() {
                $(this).removeClass('inactive');
            })
            .on('jcarouselcontrol:inactive', function() {
                $(this).addClass('inactive');
            })
            .jcarouselControl({
                target: '+=1'
            });

        $('.jcarousel-pagination')
            .on('jcarouselpagination:active', 'a', function() {
                $(this).addClass('active');
            })
            .on('jcarouselpagination:inactive', 'a', function() {
                $(this).removeClass('active');
            })
            .jcarouselPagination();
    });
})(jQuery);