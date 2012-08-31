$(function(){
    function appendMenu(i, div){
        $($('#menu-skeleton').html()).appendTo(div);
    }

    $('div.idea').each(appendMenu);

    function savePage(trigger){
        var _document = $(trigger).parents('.document');
        _document.children('form.save-page').submit();
        return false;
    }

    // sort/copy/move ideas
    var overCount = 0, copiedItem, parentItem = [], prevItem = [];

    function moveStart(e, ui){}

    function moveOver(e, ui){}

    function moveReceive(e, ui){}

    function copyStart(e, ui){
        overCount = 0;
        parentItem = ui.item.parent('ol');
        prevItem = ui.item.prev('li');

        copiedItem = ui.item.clone();
        copiedItem.addClass('copied');
        copiedItem.attr('style','');
    }

    function copyOver(e, ui){
        overCount++;
        if( overCount % 2 == 0 ){
            $('.copied').remove();
        } else {
            if( prevItem.length > 0 ){
                prevItem.after(copiedItem);
            } else {
                parentItem.prepend(copiedItem);
            }
        }
    }

    function copyReceive(e, ui){
        $('.copied').removeClass('copied');
    }

    var startFunc = moveStart, overFunc = moveOver, receiveFunc = moveReceive;

    $('#mode').buttonset();

    $('#move-mode').click(function(){
        overCount = 0, copiedItem, parentItem = [], prevItem = [];
        startFunc = moveStart;
        overFunc = moveOver;
        receiveFunc = moveReceive;
    });

    $('#copy-mode').click(function(){
        startFunc = copyStart;
        overFunc = copyOver;
        receiveFunc = copyReceive;
    });

    $('.idea-list').nestedSortable({
        connectWith: ".idea-list",
        tolerance: 'pointer',
        handle: '.idea',
        placeholder: 'placeholder',
        forcePlaceholderSize: true,
        items: 'li',
        toleranceElement: '> div',
        distance: 5,
        update: function(){
            var _document = $(this).parents('.document');
            savePage(this);
        },
        start: function(e, ui){ startFunc(e, ui) },
        over: function(e,ui){ overFunc(e, ui) },
        receive: function(e,ui){ receiveFunc(e, ui) }

    }).disableSelection();

    $('a.copy').live('click', function(){
        li1 = $(this).parentsUntil('ol', 'li');
        li2 = li1.clone();
        li1.after(li2);
        closeForm(li2.find('form'));

        return savePage(this);

    });

    $('a.remove').live('click', function(){
        var _document = $(this).parents('.document'),
            li1 = $(this).parentsUntil('ol', 'li'),
            append = li1.find('li[id=0]');
        if( append.length > 0 ) li1.before(append);
        li1.remove();

        _document.children('form.save-page').submit();
        return false;
    });

    $('.content').live('click', function(){
        var li = $(this).parentsUntil('ol', 'li'),
            div = li.children('.idea'),
            text = div.children('.content').text();

        div.children('.content').hide()

        var form = $('#edit-skeleton').children('form').clone();
        div.append(form);

        form.find('textarea').val(text);

        var action = form.attr('action');
        form.attr('action', action+li.attr('id'));

        form.find('textarea').focus();
        $('html').bind('click.xxx', function(e){
            console.log(li.has($(e.target)));
            if( li.has($(e.target)).length == 0 ){
                closeForm(form);
            }
        });
        return false;
    });

    function closeForm(form){
        $('html').unbind('click.xxx');
        form.siblings('.content').show();
        form.remove();
    }

    $('a.change-title').live('click', function(){
        title = $(this).parent('span')
        title.next('form.page-title').show();
        title.hide();
        return false;
    });

    function getTree(ol){
        var struct = ''
        ol.children('li').each(function(){
            var id = $(this).attr('id');
            if( id > 0 ){
                struct += id + ' ';
                var ol = $(this).children('ol');
                if( ol.length > 0 ){
                    struct += '[ ' + getTree(ol) + '] ';
                }
            }
        });
        return struct
    }

    $('form.save-page').submit(function(){
        var ol = $(this).parent('.document').children('ol.idea-list');
        var struct = getTree(ol);
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {struct: struct},
        })
        return false;
    });

    $('form.new-idea').submit(function(){
        var textarea = $(this).children('textarea[name=content]');
        var content = textarea.val();
        textarea.val('');
        var _document = $(this).parents('.document');
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {content: content},
            dataType: 'html',
            success: function(data){
                ol = _document.children('ol.idea-list');
                var item = $(data);
                item.find('.idea').each(appendMenu);
                ol.prepend(item);
            }
        })
        return false;
    });

    $('form.append-idea').submit(function(){
        var li = $(this).parentsUntil('ol', 'li');
        var textarea = $(this).children('textarea[name=content]');
        var content = textarea.val();
        textarea.val('');
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {content: content},
            dataType: 'html',
            success: function(data){
                var item = $(data);
                item.find('.idea').each(appendMenu);
                li.before(item);
                savePage(li);
            }
        })
        return false;
    })

    $('.new-area').keydown(function(e){
        if( e.keyCode == 13 ){
            e.preventDefault();
            $(this).parent('form').submit();
            $(this).focus();
        }
    });

    $('.append-idea textarea').keydown(function(e){
        if( e.keyCode == 9){ // TAB
            e.preventDefault();
            var li = $(this).parentsUntil('ol','li');
            if(e.shiftKey){ // SHIFT TAB
                // dedent
                var parent_li = li.parent().parentsUntil('ol', 'li');
                if ( parent_li.length > 0 ){
                    parent_li.after(li);
                }

            } else {
                // indent
                var prev = li.prev('li');
                if ( prev.length > 0 ){
                    var ol = prev.children('ol');
                    if ( ol.length == 0 ){
                        ol = $('<ol></ol>');
                        ol.appendTo(prev);
                    }
                    li.appendTo(ol);
                }
            }
            $(this).focus();
        }
    });

    $('form.edit-idea').live('submit', function(){
        var form = $(this),
            idea_id = form.parentsUntil('ol', 'li').attr('id'),
            content = form.children('textarea').val();

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {content: content},
            success: function(data){
                $('li#'+idea_id+'>.idea>.content').text(content);
                closeForm(form);
            }
        });
        return false;
    });

    $('form.page-title').submit(function(){
        form = $(this)
        title = $(this).children('input').val();
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {title: title},
            success: function(data, textStatus, jqXHR){
                title = form.prev('span');
                title.children('span').text(data);
                title.show();
                form.hide();
            }
        });
        return false;
    });

    function getText(ol){
        var text = ''
        ol.children('li').each(function(){
            var id = $(this).attr('id');
            if( id > 0 ){
                if( $(this).parent('.idea-list').length > 0){
                    text += '<p>'
                }
                text += '<span>' + $(this).children('.idea').text() + '</span>';
                var ol = $(this).children('ol');
                if( ol.length > 0 ){
                    text += getText(ol);
                }
            }
        });
        return text;
    }
    $('a.view-text').click(function(){
        var documents = $('.document'),
            outline = documents[0],
            ol = $(outline).find('.idea-list')
            text = documents[1];

        $(text).html(getText(ol));

        return false;
    });
});
