$.urlParam = function(name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);

    if (results==null) {
       return null;
    }

    return decodeURI(results[1]) || 0;
};

$( document ).ready(function() {
    var videoRepository = 'https://meteoros.s3.amazonaws.com/';
    var video = $.urlParam('v').replace('P.jpg', '.mp4');
    var data = video.split('/');
    var base_file = data.pop().split('_');
    var date = base_file[0].substr(1, 8);
    var time = base_file[1].substr(0, 6);

    $('#videoSource').attr('src', videoRepository + video);
    $('#videoPlayer')[0].load();

    $('#capture-date').text(date.substr(6, 2) + '/' + date.substr(4, 2) + '/' + date.substr(0, 4));
    $('#capture-time').text(time.substr(0, 2) + ':' + time.substr(2, 2) + ':' + time.substr(4, 2));
});
