jQuery(document).ready(function($) {
    var saving = false;
    var currentPostType = bcco_admin.selected_pt;

    function bccoShowSaved($ctx) {
        var $msg = $ctx.closest('.bcco-collection').find('.bcco-saved-msg');
        if (!$msg.length) {
            $msg = $('<span class="bcco-saved-msg">' + bcco_admin.strings.saved + '</span>');
            $ctx.closest('.bcco-collection').find('.bcco-collection-header h2').after($msg);
        }
        $msg.show().fadeOut(2000);
    }

    function bccoSeriesHasVisiblePosts($series) {
        return $series.find('.bcco-post:visible').length > 0;
    }

    function bccoInitSortable($list) {
        if ($list.hasClass('ui-sortable')) return;
        $list.sortable({
            handle: '.bcco-post-handle',
            axis: 'y',
            placeholder: 'ui-sortable-placeholder',
            tolerance: 'pointer',
            update: function() {
                if (saving) return;
                saving = true;
                var $l = $(this);
                var postIds = $l.sortable('toArray').map(function(id) {
                    return id.replace('bcco-post-', '');
                });
                $.post(bcco_admin.ajax_url, {
                    action: 'bcco_reorder_posts',
                    post_ids: postIds,
                    nonce: bcco_admin.nonce
                }).done(function() {
                    var i = 1;
                    $l.find('.bcco-post').each(function() {
                        $(this).find('.bcco-post-order').text(i + '.');
                        i++;
                    });
                    bccoShowSaved($l);
                }).fail(function() {
                    alert(bcco_admin.strings.error);
                }).always(function() {
                    saving = false;
                });
            }
        });
    }

    $('.bcco-series-list').sortable({
        handle: '.bcco-series-handle',
        axis: 'y',
        placeholder: 'ui-sortable-placeholder',
        tolerance: 'pointer',
        update: function() {
            if (saving) return;
            saving = true;
            var $list = $(this);
            var seriesIds = $list.sortable('toArray').map(function(id) {
                return id.replace('bcco-series-', '');
            });
            $.post(bcco_admin.ajax_url, {
                action: 'bcco_reorder_series',
                series_ids: seriesIds,
                nonce: bcco_admin.nonce
            }).done(function() {
                var i = 1;
                $list.find('.bcco-series').each(function() {
                    $(this).find('.bcco-series-order').text(i + '.');
                    i++;
                });
                bccoShowSaved($list);
            }).fail(function() {
                alert(bcco_admin.strings.error);
            }).always(function() {
                saving = false;
            });
        }
    });

    $('.bcco-toggle-coll').on('click', function(e) {
        var $header = $(this);
        var $body = $header.next('.bcco-collection-body');
        var $icon = $header.find('.bcco-toggle-icon');
        $body.slideToggle(200);
        $icon.toggleClass('dashicons-arrow-right dashicons-arrow-down');
    });

    $('.bcco-toggle-series').on('click', function(e) {
        var $header = $(this);
        var $series = $header.closest('.bcco-series');
        var $body = $series.find('.bcco-series-body');
        var $icon = $header.find('.bcco-series-toggle-icon');
        var isOpen = $body.is(':visible');

        if (isOpen) {
            $body.slideUp(200);
            $icon.removeClass('dashicons-arrow-down').addClass('dashicons-arrow-right');
            return;
        }

        var loaded = $series.data('loaded') === true;
        if (!loaded) {
            bccoLoadPosts($series);
        }

        $body.slideDown(200);
        $icon.removeClass('dashicons-arrow-right').addClass('dashicons-arrow-down');
    });

    function bccoLoadPosts($series) {
        var seriesId = $series.data('series-id');
        var offset = parseInt($series.data('offset'), 10);
        var perPage = bcco_admin.per_page || 20;

        $series.find('.bcco-loading-spinner').show();

        $.post(bcco_admin.ajax_url, {
            action: 'bcco_load_series_posts',
            series_id: seriesId,
            offset: offset,
            per_page: perPage,
            post_type: currentPostType,
            nonce: bcco_admin.nonce
        }).done(function(res) {
            if (!res.success) return;
            var data = res.data;
            var $postsList = $series.find('.bcco-posts-list');
            var $loadMore = $series.find('.bcco-load-more');

            $postsList.append(data.html);
            $series.data('loaded', true);
            $series.data('offset', data.offset);
            $series.data('total', data.total);

            if (data.has_more) {
                $loadMore.show();
            } else {
                $loadMore.hide();
            }

            bccoInitSortable($postsList);
        }).always(function() {
            $series.find('.bcco-loading-spinner').hide();
            $series.data('loading', false);
        });
    }

    $('#bcco-collections-container').on('click', '.bcco-load-more button', function() {
        var $series = $(this).closest('.bcco-series');
        var seriesId = $series.data('series-id');
        var offset = parseInt($series.data('offset'), 10);
        var perPage = bcco_admin.per_page || 20;

        $.post(bcco_admin.ajax_url, {
            action: 'bcco_load_series_posts',
            series_id: seriesId,
            offset: offset,
            per_page: perPage,
            post_type: currentPostType,
            nonce: bcco_admin.nonce
        }).done(function(res) {
            if (!res.success) return;
            var data = res.data;
            var $postsList = $series.find('.bcco-posts-list');
            var $loadMore = $series.find('.bcco-load-more');

            $postsList.append(data.html);
            $series.data('offset', data.offset);

            if (data.has_more) {
                $loadMore.show();
            } else {
                $loadMore.hide();
            }

            bccoInitSortable($postsList);
        });
    });

    $('#bcco-filter-ptype').on('change', function() {
        var val = $(this).val();
        var url = new URL(window.location.href);
        if (val) {
            url.searchParams.set('ptype', val);
        } else {
            url.searchParams.delete('ptype');
        }
        window.location.href = url.toString();
    });

    $('#bcco-global-search').on('input', function() {
        var q = $(this).val().toLowerCase().trim();

        $('.bcco-collection').each(function() {
            var name = $(this).find('.bcco-collection-header h2').text().toLowerCase();
            $(this).toggle(!q || name.indexOf(q) !== -1);
        });
    });

    if (typeof bcco_term !== 'undefined') {
        var $parentSelect = $('#parent');
        var $indicator = $('<p class="bcco-type-indicator"></p>');

        function updateIndicator() {
            var val = parseInt($parentSelect.val(), 10);
            if (val > 0) {
                $indicator.html('<span class="dashicons dashicons-category" style="font-size:14px;width:14px;height:14px;color:#2271b1;"></span> ' + bcco_term.msg_series);
            } else {
                $indicator.html('<span class="dashicons dashicons-folder-open" style="font-size:14px;width:14px;height:14px;color:#46b450;"></span> ' + bcco_term.msg_collection);
            }
        }

        $parentSelect.after($indicator);
        $parentSelect.on('change', updateIndicator);
        setTimeout(updateIndicator, 100);
    }
});
