$(function(){
    var KEY_ENTER = 13;

    // controller
    function Controller(){
        this.temp = '';
        this.temp_id = null;
        this.mode = 'notext';
    }
    var controller = new Controller();

    // common functions
    function parent_li(that){
        return $(that).parentsUntil('ol', 'li')
    }


    function appendMenu(i, div){
        $($('#menu-skeleton').html()).appendTo(div);
    }

    $('div.idea').each(appendMenu);

    var outline = $('.outline');
    if( outline.length > 0 ){
        var summary = $('.summary');
        $('ol.idea-list>li').each(function(){
            var text = $(this).children('.idea').children('.content').text();
            summary.append('<li id="'+$(this).attr('id')+'">'+text+'</li>');
        });
    }

    function savePage(trigger){
        var _document = $(trigger).parents('.document');
        _document.children('form.save-page').submit();
        return false;
    }

    function editIdea(idea_id, content){
        var hidden = $('ol>li#'+idea_id+'>.idea').hasClass('hidden');
        $.ajax({
            url: '/idea/'+idea_id,
            type: 'POST',
            data: {content: content, hidden: hidden},
        });
    }

    // resize
    function resizeScrollable(){
        var menu = $('#menu'),
            body = $('body'),
            h = $(window).height() - menu.height()
                - parseInt(menu.css('margin-bottom'))
                - 2*parseInt($('.document').css('padding'))
                - 20;
        $('.scrollable').height(h);
    }

    resizeScrollable();
    $(window).resize(resizeScrollable);

    // scroll at edge
    function activeScrollEdge(e){
            var threshold = 20,
                step = 200;
            $('.scrollable').each(function(){
                $(this).stop();
                var offset = $(this).offset(),
                    width = parseInt($(this).css('width')),
                    height = parseInt($(this).css('height'));

                if( offset.left < e.pageX && e.pageX < offset.left + width ){
                    var pos = $(this).scrollTop();
                    if( Math.abs(offset.top - e.pageY) < threshold ){
                        scr = { scrollTop: 0 }//$(this).scrollTop() - step }
                        $(this).animate(scr, 2*pos);

                    } else if( Math.abs(offset.top + height - e.pageY)
                               < threshold ){
                        var bottom = this.scrollHeight;
                        scr = { scrollTop: bottom }//$(this).scrollTop() + step }
                        $(this).animate(scr, 2*(bottom-pos));
                    }
                }
            });
    }

    function deactiveScrollEdge(e){
    }

    scrollEdge = deactiveScrollEdge;

    $(document).mousemove(function(e){
        scrollEdge(e);
    });

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
            updateText();
            savePage(this);
        },
        start: function(e, ui){
            scrollEdge = activeScrollEdge;
            startFunc(e, ui);
        },
        over: function(e,ui){ overFunc(e, ui) },
        receive: function(e,ui){ receiveFunc(e, ui) },
        stop: function(e, ui){
            scrollEdge = deactiveScrollEdge;
        }

    }).disableSelection();

    // edit form
    $('a.copy').live('click', function(){
        li1 = parent_li(this),
        li2 = li1.clone();
        li2.find('textarea').val(li1.find('textarea').val());
        li1.after(li2);
        closeForm(li1.find('form'));
        closeForm(li2.find('form'));

        return savePage(this);

    });


    $('a.indent-following').live('click', function(){
        var li = parent_li(this),
            grandparent_li = parent_li(li.parent());
        if( grandparent_li.length > 0 ){
            var ol = li.children('ol');
            if( ol.length == 0 ) ol = $('<ol></ol>').appendTo(li);

            li.nextAll('li').each(function(){
                $(this).appendTo(ol);
            });
        }
        return savePage(this);
    });


    $('a.dedent-children').live('click', function(){
        var li = parent_li(this),
            ol = li.children('ol');
        if( ol.length > 0 ){
            li.after(ol.html());
            ol.remove();
        }
        return savePage(this);
    });


    $('input.toggle-hide').live('change', function(){
        var form = $(this).parents('form'),
            idea = $(this).parents('.idea');

        if ($(this).is(':checked')){
            idea.addClass('hidden');
        } else {
            idea.removeClass('hidden');
        }

        closeForm(form);
    });


    $('a.remove').live('click', function(){
        var _document = $(this).parents('.document'),
            li1 = parent_li(this),
            append = li1.find('li[id=0]');
        if( append.length > 0 ) li1.before(append);

        $('.sentence#'+li1.attr('id')).remove();
        li1.remove();

        _document.children('form.save-page').submit();
        return false;
    });


    $('.edit-area').live('keydown', function(e){
        if( e.keyCode == KEY_ENTER ){
            e.preventDefault();
            var form = $(this).parents('form'),
                li = parent_li(this),
                ol = li.children('ol'),
                append = $(this).parents('.document').find('li[id=0]');
            closeForm(form);
            li.after(append);
            append.find('textarea').focus();
        }
    });


    $('.content').live('click', function(){
        var li = parent_li(this),
            div = li.children('.idea'),
            text = div.children('.content').text(),
            form = $('#edit-skeleton').children('form').clone(),
            textarea = form.find('textarea');

        controller.temp = text;
        controller.temp_id = li.attr('id');

        div.children('.content').hide()

        if (div.hasClass('hidden')){
            form.children('input.toggle-hide').attr('checked',true);
        }

        div.append(form);

        textarea.val(text);

        var action = form.attr('action');
        form.attr('action', action+li.attr('id'));

        textarea.focus();
        $('html').bind('click.xxx', function(e){
            if( li.has($(e.target)).length == 0 ){
                closeForm(form);
            }
        });
    });


    $('a.undo').click(function(){
        var li = $('ol>li#'+controller.temp_id),
            content = li.find('.content:first'),
            textarea = li.find('textarea');

        if( textarea.length > 0 ){
            textarea.val(controller.temp);
            textarea.focus();
        } else {
            content.text(controller.temp);
            editIdea(controller.temp_id, controller.temp);
        }

        return false;
    });


    function startScroll(id, item, div, target){
        if( div.length > 0 && target.length > 0 ){
            scrollTop = {
                scrollTop: target.offset().top - div.offset().top
                    + div.scrollTop()
                    - (item.offset().top
                        - item.parents('.scrollable').offset().top) }
            div.animate(scrollTop , 100);
            target.css('background', '#99CCFF');
        }
    }


    $('.content').live('mouseover', function(){
        // scroll the text
        var li = parent_li(this),
            id = li.attr('id');

        startScroll(id, $(this), $('.text'), $('.sentence#'+id));
        startScroll(id, $(this), $('.summary'), $('.summary li#'+id));
        $(this).css('background', '#99CCFF');
    });


    $('.sentence').live('mouseover', function(){
        var id = $(this).attr('id');
        startScroll(id, $(this), $('.outline'), $('.outline li#'+id+'>.idea>.content'));
        startScroll(id, $(this), $('.summary'), $('.summary li#'+id));
        $(this).css('background', '#99CCFF');
    });


    $('.summary li').live('mouseover', function(){
        var id = $(this).attr('id');
        startScroll(id, $(this), $('.outline'), $('.outline li#'+id+'>.idea>.content'));
        startScroll(id, $(this), $('.text'), $('.sentence#'+id));
        $(this).css('background', '#99CCFF');
    });


    function stopScroll(){
        $('.text').stop();
        $('.outline').stop();

        $('.summary li').css('background', '');
        $('.content').css('background', '');
        $('.sentence').css('background', '');
    }
    $('.content').live('mouseout', stopScroll);
    $('.sentence').live('mouseout', stopScroll);
    $('.summary li').live('mouseout', stopScroll);


    function closeForm(form){

        var idea_id = parent_li(form).attr('id'),
            hidden = parent_li(form).children('.idea').hasClass('hidden'),
            content = form.children('textarea').val();

        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: {content: content, hidden: hidden},
            success: function(data){
                $('li#'+idea_id+'>.idea>.content').text(content);
                var sentence = $('.sentence#'+idea_id);
                sentence.text(content);

                if( hidden ){
                    sentence.addClass('hidden');
                } else {
                    sentence.removeClass('hidden');
                }

                $('html').unbind('click.xxx');
                form.siblings('.content').show();
                form.remove();
            }
        });
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
        var li = parent_li(this),
            textarea = $(this).children('textarea[name=content]'),
            content = textarea.val();
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
                updateText();
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
            var li = parent_li(this);
            if(e.shiftKey){ // SHIFT TAB
                // dedent
                var grandparent_li = parent_li(li.parent());
                if ( grandparent_li.length > 0 ){
                    grandparent_li.after(li);
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

                var idea = $(this).children('.idea'),
                    cls = '';
                if ( idea.hasClass('hidden') ){
                    cls = ' hidden';
                }

                text += '<span class="sentence' + cls + '" id="' + id + '">' +
                    idea.text() + '</span>';
                var ol = $(this).children('ol');
                if( ol.length > 0 ){
                    text += getText(ol);
                }
            }
        });
        return text;
    }

    function updateText(){
        if( controller.mode == 'text' ){
            var documents = $('.document'),
                outline = documents[0],
                ol = $(outline).find('.idea-list')
                text = $('.text');

            text.html(getText(ol));
        }
    }

    $('a.view-text').click(function(){
        $(this).parents('ul').hide();
        $('.text').show();
        controller.mode = 'text';
        updateText();
        return false;
    });


    $('a.close-text').click(function(){
        $(this).siblings('ul').show();
        $('.text').hide();
        controller.mode = 'notext';
        return false;
    });
});
