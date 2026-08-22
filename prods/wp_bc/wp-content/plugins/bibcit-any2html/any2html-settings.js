(function ($) {
    'use strict';

    var $keyInput = $('#any2html_api_key');
    var $statusWrap = $('#any2html-key-status-wrap');
    var $hiddenStatus = $('#any2html_api_status');
    var $validateBtn = $('#any2html-validate-key');
    var $saveBtn = $('#any2html-save-btn');
    var $saveMsg = $('#any2html-save-status');

    var VALIDATE_LABEL =
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg> Validate Key';

    var SAVE_LABEL =
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg> Save Settings';

    /* ── Eye / show-hide key ─────────────────────────────── */
    $('#any2html-toggle-eye').on('click', function () {
        var isPassword = $keyInput.attr('type') === 'password';
        $keyInput.attr('type', isPassword ? 'text' : 'password');
        $('#any2html-icon-show').toggle(!isPassword);
        $('#any2html-icon-hide').toggle(isPassword);
        $(this).attr('aria-pressed', isPassword ? 'true' : 'false');
    });

    /* Clear invalid state when user starts typing */
    $keyInput.on('input', function () {
        $keyInput.removeClass('is-invalid');
    });

    /* ── Validate key ────────────────────────────────────── */
    $validateBtn.on('click', function () {
        if ($validateBtn.prop('disabled')) return;

        var key = $keyInput.val().trim();
        if (!key) {
            $keyInput.addClass('is-invalid').focus();
            setStatus('invalid', 'Please enter an API key first.');
            return;
        }

        $keyInput.removeClass('is-invalid');
        setBusy($validateBtn,
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Validating\u2026'
        );
        setStatus('checking', 'Checking\u2026');

        $.post(any2htmlSettings.ajaxUrl, {
            action: 'any2html_validate_key',
            api_key: key,
            _ajax_nonce: any2htmlSettings.nonce
        })
            .done(function (res) {
                var ok = res.success && res.data.valid;
                if (ok) {
                    $keyInput.removeClass('is-invalid');
                    setStatus('valid', 'Key validated successfully');
                    $('#any2html-form-footer').show();
                } else {
                    $keyInput.addClass('is-invalid');
                    setStatus('invalid', 'Invalid or unauthorized key');
                }
                $hiddenStatus.val(ok ? 'valid' : 'invalid');
            })
            .fail(function () {
                $keyInput.addClass('is-invalid');
                setStatus('invalid', 'Connection error \u2014 please try again.');
                $hiddenStatus.val('invalid');
            })
            .always(function () {
                setIdle($validateBtn, VALIDATE_LABEL);
            });
    });

    /* ── Save settings ───────────────────────────────────── */
    $saveBtn.on('click', function () {
        if ($saveBtn.prop('disabled')) return;

        setBusy($saveBtn,
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Saving\u2026'
        );
        $saveMsg.attr('class', '').empty();

        $.post(any2htmlSettings.ajaxUrl, {
            action: 'any2html_save_settings',
            nonce: any2htmlSettings.saveNonce,
            api_key: $keyInput.val(),
            api_status: $hiddenStatus.val()
        })
            .done(function (res) {
                if (res.success) {
                    $saveMsg.attr('class', 'any2html-save-msg any2html-save-msg--ok')
                        .html('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg> Settings saved');
                    setTimeout(function () {
                        $saveMsg.fadeOut(400, function () {
                            $(this).attr('class', '').empty().show();
                        });
                    }, 3000);
                } else {
                    $saveMsg.attr('class', 'any2html-save-msg any2html-save-msg--err')
                        .text('Save failed. Please try again.');
                }
            })
            .fail(function () {
                $saveMsg.attr('class', 'any2html-save-msg any2html-save-msg--err')
                    .text('Connection error. Please try again.');
            })
            .always(function () {
                setIdle($saveBtn, SAVE_LABEL);
            });
    });

    /* ── Helpers: busy / idle state ──────────────────────── */
    function setBusy($btn, label) {
        $btn.prop('disabled', true).html(label);
    }

    function setIdle($btn, label) {
        $btn.prop('disabled', false).html(label);
    }

    /* ── Status pill helper ──────────────────────────────── */
    function setStatus(type, text) {
        var icons = {
            valid: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
            invalid: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
            checking: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
        };
        var cls = {
            valid: 'any2html-status-pill any2html-status-valid',
            invalid: 'any2html-status-pill any2html-status-invalid',
            checking: 'any2html-status-pill any2html-status-checking'
        };
        $statusWrap.html(
            '<span class="' + cls[type] + '">' +
            (icons[type] || '') + ' ' +
            $('<span>').text(text).html() +
            '</span>'
        );
    }

    /* Init save button label with icon */
    $saveBtn.html(SAVE_LABEL);

}(jQuery));
