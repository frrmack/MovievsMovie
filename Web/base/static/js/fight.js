// these three variables concerning lock buttons 
// are filled by django in the template)
var result_url_lock_left;
var result_url_lock_right;
var result_url_no_lock;


$(function(){

    // Key Presses for Choosing Match Outcome 
    // [: Left wins  ]: Right wins  \: Draw  
    // Esc: Skip   Backspace: Revote the last one
    $(document).keydown(function(event) {
        if ( event.which == 219 ) {            // [
            $("#left_wins_button").click();
        } else if ( event.which == 221) {      // ]
            $("#right_wins_button").click();
        } else if ( event.which == 220) {      // \
            $("#draw_button").click();
        } else if ( event.which == 27) {      // esc
            $("#skip_button").click();      
        } else if ( event.which == 8) {       // backspace
            history.go(-1);
        }
    });
    
    // Lock buttons
    $('#lock-left-button').click( function(){
        $(this).toggleClass('active');
        if ($(this).hasClass('active')) {
            $('#lock-right-button').removeClass('active');
            $('#fight-result-form').attr('action', window.result_url_lock_left);
        }
        else {
            $('#fight-result-form').attr('action', window.result_url_no_lock);
        }
    });
    
    $('#lock-right-button').click( function(){
        $(this).toggleClass('active');
        if ($(this).hasClass('active')) {
            $('#lock-left-button').removeClass('active');
            $('#fight-result-form').attr('action', window.result_url_lock_right);
        }
        else {
            $('#fight-result-form').attr('action', window.result_url_no_lock);
        }
    });
    
});
    
