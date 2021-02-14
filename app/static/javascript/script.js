/**
 * Function to check if the element has scrolled into view
 * @param {HTMLElement} elem DOMElement beeing scrolled into view
 */
function isScrolledIntoView(elem){
    var docViewTop = $(window).scrollTop();
    var docViewBottom = docViewTop + $(window).height();
    var elemTop = $(elem).offset().top;
    var elemBottom = elemTop + $(elem).height();
    return ((elemBottom >= docViewTop) && (elemTop <= docViewBottom) && (elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}

$(function() {
    // Toggle timeline modal
    $('.link-modal').on('click', function(e){
        let target = $(e.target);
        let title = target.data('title');
        let content = target.data('content');
        let description = target.data('description');
        let source = target.data('source');
        let highlight = target.data('highlight');

        let modal = $('#timelineModal');
        modal.find('.modal-title').html(title);
        modal.find('.modal-description').html(description);
        modal.find('.modal-body').html(content);
        modal.find('.modal-source').html("Source: " + source);
        modal.find('.modal-title').removeClass('warning-level-1 warning-level-2 warning-level-3 warning-level-4 warning-level-5')
        modal.find('.modal-title').removeClass('warning-level-1.0 warning-level-2.0 warning-level-3.0 warning-level-4.0 warning-level-5.0')
        modal.find('.modal-title').addClass(highlight);

        $('#timelineModalBtn').trigger('click');
    });

    // Check if the events should appear on the timeline
    $(window).on('scroll', function(){
        var lines = $('.timeline-event-line');
        var events = $('.timeline-event');
        for (let i = 0; i < lines.length; i++) {
            let curEvent = events[i];
            let curLine = lines[i];
            if(isScrolledIntoView(curEvent)){       
                $(curEvent).addClass('show');
                $(curLine).addClass('show');
            }
        }
    });

    // Reset modal
    $(reportEventModalBtn).on('click', function(){
        let form = $('.form-new-event')
        let loading = $('.form-event-loading')
        let success = $('.form-event-success')

        $(form).removeClass('d-none')
        $(loading).addClass('d-none')
        $(success).addClass('d-none')
    })

    // Submit report event form
    $('.form-event-submit').on('click', function(){
        let form = $('.form-new-event')
        let loading = $('.form-event-loading')
        let success = $('.form-event-success')

        $(form).toggleClass('d-none')
        $(loading).toggleClass('d-none')

        let place = $(form).find('.form-event-place').val()
        let type = $(form).find('.form-event-type').val()
        let description = $(form).find('.form-event-description').val()
        let date = $(form).find('.form-event-date').val()
        let source = $(form).find('.form-event-source').val()

        $.ajax({
            method: 'POST',
            url: '/new-event',
            contentType: 'application/json',
            data: JSON.stringify({
                place,
                type,
                description,
                date,
                source
            })
        }).done(function(){
            $(loading).toggleClass('d-none')
            $(success).toggleClass('d-none')
        }).catch(function(err){
            console.log(err)
            $(loading).toggleClass('d-none')
            $(form).toggleClass('d-none')
        })

    });
})