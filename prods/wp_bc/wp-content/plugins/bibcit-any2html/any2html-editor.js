(function ($) {
    'use strict';

    var $panel = $('#any2html-panel');
    if (!$panel.length) return;

    var $input = $('#any2html-input');
    var $btn = $('#any2html-convert');
    var $status = $('#any2html-status');
    var $progress = $('#a2h-progress');
    var $bar = $('#a2h-progress-bar');
    var $dropzone = $('#any2html-upload-area');
    var $fileInput = $('#any2html-file-input');
    var $fileChip = $('#a2h-file-chip');
    var $fileName = $('#a2h-file-name');
    var $fileSize = $('#a2h-file-size');
    var $tabs = $('.a2h-tab');
    var $diagType = $('#a2h-diag-type');
    var $diagInput = $('#any2html-diag-input');

    var MAX_BYTES = 5 * 1024 * 1024;
    var activeTab = 'md';
    var selectedFile = null;

    /* ── Tabs ── */
    $tabs.on('click', function () {
        var id = $(this).attr('id');
        var target = id === 'a2h-tab-file' ? 'file' : id === 'a2h-tab-diag' ? 'diag' : 'md';
        switchTab(target);
    });

    function switchTab(tab) {
        activeTab = tab;
        $('#a2h-tab-md').toggleClass('a2h-tab--active', tab === 'md').attr('aria-selected', tab === 'md');
        $('#a2h-tab-file').toggleClass('a2h-tab--active', tab === 'file').attr('aria-selected', tab === 'file');
        $('#a2h-tab-diag').toggleClass('a2h-tab--active', tab === 'diag').attr('aria-selected', tab === 'diag');
        $('#a2h-pane-md').prop('hidden', tab !== 'md');
        $('#a2h-pane-file').prop('hidden', tab !== 'file');
        $('#a2h-pane-diag').prop('hidden', tab !== 'diag');
        updateConvertBtn();
        clearStatus();
    }

    /* ── Clear markdown ── */
    $('#any2html-md-clear').on('click', function () {
        $input.val('').focus();
        updateConvertBtn();
        clearStatus();
    });

    /* ── Diagram tab: classify + enable/disable convert button ── */
    var classifyTimer = null;

    $diagType.on('change', updateConvertBtn);

    $diagInput.on('input', function () {
        updateConvertBtn();
        clearTimeout(classifyTimer);
        var code = $diagInput.val().trim();
        if (!code) {
            $diagType.val('');
            return;
        }
        classifyTimer = setTimeout(function () { classifyDiagram(code); }, 600);
    });

    $('#any2html-diag-clear').on('click', function () {
        $diagInput.val('');
        $diagType.val('');
        clearTimeout(classifyTimer);
        updateConvertBtn();
        clearStatus();
        $diagInput.focus();
    });

    function updateConvertBtn() {
        if (activeTab !== 'diag') {
            $btn.prop('disabled', false);
            return;
        }
        var ready = $diagInput.val().trim() !== '' && $diagType.val() !== '';
        $btn.prop('disabled', !ready);
    }

    /* ── Classify diagram code ── */
    function classifyDiagram(code) {
        $.post(any2htmlEditor.ajaxUrl, {
            action: 'any2html_diag_classify',
            diag_code: code,
            _ajax_nonce: any2htmlEditor.diagNonce
        })
            .done(function (res) {
                if (res.success && res.data.diag_type) {
                    $diagType.val(res.data.diag_type);
                    updateConvertBtn();
                }
            });
    }

    /* ── Dropzone interactions ── */
    $dropzone.on('click', function () { $fileInput.trigger('click'); });

    $dropzone.on('dragover dragenter', function (e) {
        e.preventDefault();
        $dropzone.addClass('a2h-dropzone--hover');
    }).on('dragleave dragend', function () {
        $dropzone.removeClass('a2h-dropzone--hover');
    }).on('drop', function (e) {
        e.preventDefault();
        $dropzone.removeClass('a2h-dropzone--hover');
        var file = e.originalEvent.dataTransfer.files[0];
        if (file) selectFile(file);
    });

    $fileInput.on('change', function () {
        if (this.files[0]) selectFile(this.files[0]);
        this.value = '';
    });

    $('#a2h-file-remove').on('click', function (e) {
        e.stopPropagation();
        clearFile();
    });

    function selectFile(file) {
        var allowed = /^(application\/pdf|image\/.+)$/;
        if (!allowed.test(file.type)) {
            setStatus('Unsupported file type. Please upload a PDF or image.', 'error');
            return;
        }
        if (file.size > MAX_BYTES) {
            setStatus('File is too large. Maximum allowed size is 5 MB.', 'error');
            return;
        }
        selectedFile = file;
        $fileName.text(file.name);
        $fileSize.text('(' + formatBytes(file.size) + ')');
        $fileChip.prop('hidden', false);
        $dropzone.addClass('a2h-dropzone--has-file');
        clearStatus();
    }

    function clearFile() {
        selectedFile = null;
        $fileChip.prop('hidden', true);
        $dropzone.removeClass('a2h-dropzone--has-file');
        clearStatus();
    }

    /* ── Convert button ── */
    $btn.on('click', function () {
        if ($btn.prop('disabled')) return;
        clearStatus();

        if (activeTab === 'file') {
            if (!selectedFile) {
                setStatus('Please select a file first.', 'error');
                return;
            }
            uploadFile(selectedFile);
        } else if (activeTab === 'diag') {
            var diagCode = $diagInput.val().trim();
            var diagType = $diagType.val();
            if (diagType === 'unknown') {
                diagType = '';
                setStatus('Unable to autodetect Diagram type. Please select a type manually.', 'error');
                return;
            }

            if (!diagCode) {
                setStatus('Please enter Diagram code.', 'error');
                return;
            }
            if (!diagType) {
                setStatus('Please select Diagram type.', 'error');
                return;
            }

            convertDiagram(diagType, diagCode);
        } else {
            var markdown = $input.val().trim();
            if (!markdown) {
                setStatus('Please enter some Markdown first.', 'error');
                return;
            }
            convertMarkdown(markdown);
        }
    });

    function extractSVG(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const svg = doc.querySelector("svg");
        //return svg ? svg.outerHTML : null;
        if (!svg) return null;

        // 1. Remove fixed dimensions
        svg.removeAttribute("width");
        svg.removeAttribute("height");

        // 2. Ensure viewBox exists (fallback if missing)
        if (!svg.getAttribute("viewBox")) {
            const width = svg.getAttribute("width") || 840;
            const height = svg.getAttribute("height") || 560;
            svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
        }

        // 3. Add responsive scaling behavior
        svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

        // 4. Optional: make it behave nicely in layouts
        svg.style.width = "100%";
        svg.style.height = "auto";
        svg.style.display = "block";

        return svg.outerHTML;
    };

    /* ── Diagram → HTML ── */
    function convertDiagram(type, code) {
        setBusy('Converting\u2026');
        // $.post(any2htmlEditor.ajaxUrl, {
        //     action: 'any2html_diag_convert',
        //     diag_type: type,
        //     diag_code: code,
        //     _ajax_nonce: any2htmlEditor.diagNonce
        // })

        $.ajax({
            url: any2htmlEditor.ajaxUrl + '?action=any2html_diag_convert&_ajax_nonce=' + any2htmlEditor.diagNonce + '&diag_type=' + encodeURIComponent(type),
            type: 'POST',
            contentType: 'text/plain',
            data: code,
            processData: false
        })
            .done(function (res) {
                if (res.success) {
                    insertHtml(extractSVG(res.data.html));
                    setStatus('Done \u2014 inserted into editor.', 'success');
                    $diagInput.val('');
                    $diagType.val('');
                    updateConvertBtn();
                } else {
                    handleError(res);
                }
            })
            .fail(function () { setStatus('Request failed. Please try again.', 'error'); })
            .always(setIdle);
    }

    /* ── Markdown → HTML ── */
    function convertMarkdown(markdown) {
        setBusy('Converting\u2026');
        $.post(any2htmlEditor.ajaxUrl, {
            action: 'any2html_convert',
            markdown: markdown,
            _ajax_nonce: any2htmlEditor.nonce
        })
            .done(function (res) {
                if (res.success) {
                    insertHtml(res.data.html);
                    setStatus('Done \u2014 inserted into editor.', 'success');
                    $input.val('');
                } else {
                    handleError(res);
                }
            })
            .fail(function () { setStatus('Request failed. Please try again.', 'error'); })
            .always(setIdle);
    }

    /* ── File → markdown → HTML ── */
    function uploadFile(file) {
        setBusy('Uploading\u2026');
        showProgress(true);

        var formData = new FormData();
        formData.append('action', 'any2html_file_convert');
        formData.append('_ajax_nonce', any2htmlEditor.fileNonce);
        formData.append('file', file);

        $.ajax({
            url: any2htmlEditor.ajaxUrl,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            xhr: function () {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        var pct = Math.round((e.loaded / e.total) * 80);
                        $bar.css('width', pct + '%');
                        if (pct >= 80) setStatus('Processing\u2026', 'loading');
                    }
                });
                return xhr;
            }
        })
            .done(function (res) {
                $bar.css('width', '100%');
                if (res.success) {
                    insertHtml(res.data.html);
                    setStatus('Done \u2014 inserted into editor.', 'success');
                    clearFile();
                } else {
                    handleError(res);
                }
            })
            .fail(function () { setStatus('Request failed. Please try again.', 'error'); })
            .always(function () {
                setIdle();
                setTimeout(function () { showProgress(false); }, 600);
            });
    }

    /* ── Insert HTML into editor ── */
    function insertHtml(html) {
        var id = 'content';
        if (document.body.classList.contains('block-editor-page')) {
            var block = wp.blocks.createBlock('core/freeform', { content: html });
            wp.data.dispatch('core/editor').insertBlocks(block);
        } else if (window.tinyMCE && tinyMCE.get(id) && !tinyMCE.get(id).isHidden()) {
            var ed = tinyMCE.get(id);
            var marker = 'a2h_' + Math.random().toString(36).slice(2);
            ed.selection.setContent(marker);
            ed.setContent(ed.getContent().replace(new RegExp(marker, 'g'), function () { return html; }));
        } else {
            var el = document.getElementById(id);
            if (el) {
                var s = el.selectionStart;
                el.value = el.value.substring(0, s) + html + el.value.substring(el.selectionEnd);
            }
        }
    }

    /* ── Helpers ── */
    function setBusy(label) {
        $btn.prop('disabled', true).find('span.a2h-btn-label').text(label);
        setStatus(label, 'loading');
    }

    function setIdle() {
        $btn.prop('disabled', false).find('span.a2h-btn-label').text('Convert to HTML');
    }

    function showProgress(show) {
        $progress.prop('hidden', !show);
        if (!show) $bar.css('width', '0%');
    }

    function setStatus(msg, type, isHtml) {
        $status.attr('class', 'any2html-status any2html-status--' + (type || ''));
        isHtml ? $status.html(msg) : $status.text(msg);
    }

    function clearStatus() {
        $status.attr('class', '').empty();
    }

    function handleError(res) {
        if (res.data && res.data.key_invalid) {
            let referenceMsg = (res.data.code === 401) ? ' <a href="' + res.data.settings_url + '">Re-validate \u2192</a>' : ' <a href="https://bibcit.com/" style="color: blue;">Bibcit \u2192</a>';
            setStatus(
                res.data.message + referenceMsg,
                'error', true
            );
        } else {
            setStatus('Error: ' + (res.data && res.data.message ? res.data.message : 'Unknown error.'), 'error');
        }
    }

    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

}(jQuery));
