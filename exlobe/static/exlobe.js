$(function(){
    $('.idea-list').nestedSortable({
        connectWith: ".idea-list",
        handle: 'div',
        items: 'li',
        toleranceElement: '> div'
    }).disableSelection();

    $('a.copy').live('click', function(){
        li1 = $(this).parents('li');
        li2 = li1.clone();
        li1.after(li2);
        return false;
    });

    $('a.remove').live('click', function(){
        li1 = $(this).parents('li');
        $(li1).remove();
        return false;
    });

    $('a.change-title').live('click', function(){
        title = $(this).parent('span')
        title.next('form.page-title').show();
        title.hide();
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
});
