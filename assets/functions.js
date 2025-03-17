$(document).ready(function() {
    $('.link.date')
        .datepicker({
        format: 'yyyy/mm/dd',
        language: "pt-BR",
        autoclose: true,
        endDate: '0d',
        startDate: '2018/08/28'
    })
    .on('hide', function(e) {
        if (!e.date) {
            return;
        }

        window.location.href = '/' + e.format('yyyy/mm/dd') + '/captures/';
    });

    $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });

    $('#back-to-top').click(function () {
        $('#back-to-top').tooltip('hide');
        $('body,html').animate({
            scrollTop: 0
        }, 800);
        return false;
    });

    $('#back-to-top').tooltip('show');
});
