'use strict';

$(function () {
    $('.word-input').keyup(function (e) {
        if (e.keyCode == 13) {
            $('#submit').click();
        }
    });
    $('#submit').click(function () {
        var word_a = $('#word-a-input').val().toLowerCase(),
            word_b = $('#word-b-input').val().toLowerCase(),
            stream = new EventSource('/pun/' + word_a + '/' + word_b);
        stream.addEventListener('progress', function (event) {
            var progress = parseFloat(event.data);
            $('#progress').text((progress * 100).toFixed(2) + '%');
        });
        stream.addEventListener('result', function (event) {
            var json = JSON.parse(event.data),
                $ul = $('#results-list');
            $ul.empty();
            json.results.forEach(function (obj) {
                $ul.append($(
                    '<li>' + obj.data.result.join('') + ' (' + obj.data.a_info.syllables.join('') + '+' + obj.data.b_info.syllables.join('') + ', ' + obj.score.toFixed(2) + ')</li>'
                ));
            });
        });
    });
});