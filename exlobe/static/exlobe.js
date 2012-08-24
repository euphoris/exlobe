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
});
