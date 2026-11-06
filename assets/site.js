(function () {
    'use strict';

    var button = document.querySelector('.menu-btn');
    var nav = document.getElementById('nav');
    if (button && nav) {
        button.addEventListener('click', function () {
            var open = nav.classList.toggle('open');
            button.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }

    // Формата пише в същия Google Form като другите сайтове. Началото на съобщението
    // казва от кой сайт идва запитването, за да се различава в общата таблица.
    var form = document.getElementById('contact-form');
    if (!form) return;

    var GOOGLE_FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSd6oAve7uoiaXMJWWukyYHWEZQgGTJxPgCpV40E-f3mCNkQtw/formResponse';

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        var status = document.getElementById('form-status');
        var submit = form.querySelector('button[type="submit"]');
        var data = new FormData(form);
        var message = '[' + form.dataset.source + '] ' + data.get('message');
        var target = GOOGLE_FORM
            + '?entry.1843393081=' + encodeURIComponent(data.get('name'))
            + '&entry.1799285576=' + encodeURIComponent(data.get('email'))
            + '&entry.530113389=' + encodeURIComponent(message);

        status.className = '';
        status.textContent = form.dataset.sending;
        submit.disabled = true;

        fetch(target, { method: 'POST', mode: 'no-cors' })
            .then(function () {
                status.textContent = form.dataset.ok;
                status.className = 'ok';
                form.reset();
            })
            .catch(function () {
                status.textContent = form.dataset.err;
                status.className = 'err';
            })
            .then(function () {
                submit.disabled = false;
            });
    });
})();
