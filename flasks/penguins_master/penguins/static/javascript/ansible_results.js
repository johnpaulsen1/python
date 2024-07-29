'use strict';

function populatePre(url) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
        document.getElementById('output').textContent = this.responseText;
    };
    xhr.open('GET', url, false);
    xhr.send();
}
populatePre('/static/ansible_log');
