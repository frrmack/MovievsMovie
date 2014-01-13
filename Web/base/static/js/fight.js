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

    // Sidebar lock links
    $('#sidebar-lock-left').click( function(){
	$('#lock-left-button').click();
        $(this).toggleClass('active');
        if ($(this).hasClass('active')) {
            if  ($('#sidebar-lock-right').hasClass('active')){
		$('#sidebar-lock-right').html("<span class=\"glyphicon\"></span>Lock Right</a></li>");
		$('#sidebar-lock-right').removeClass('active');
            }
            $('#fight-result-form').attr('action', window.result_url_lock_left);
	    $(this).html("<span class=\"glyphicon\"></span>Unlock Left<span class=\"glyphicon glyphicon-lock\"></span></a></li>")
        }
        else {
            $('#fight-result-form').attr('action', window.result_url_no_lock);
	    $(this).html("<span class=\"glyphicon\"></span>Lock Left</a></li>")
        }
    });

    $('#sidebar-lock-right').click( function(){
	$('#lock-right-button').click();
        $(this).toggleClass('active');
        if ($(this).hasClass('active')) {
            if  ($('#sidebar-lock-left').hasClass('active')){
		$('#sidebar-lock-left').html("<span class=\"glyphicon\"></span>Lock Left</a></li>");
		$('#sidebar-lock-left').removeClass('active');
            }
            $('#fight-result-form').attr('action', window.result_url_lock_right);
	    $(this).html("<span class=\"glyphicon\"></span>Unlock Right<span class=\"glyphicon glyphicon-lock\"></span></a></li>")
        }
        else {
            $('#fight-result-form').attr('action', window.result_url_no_lock);
	    $(this).html("<span class=\"glyphicon\"></span>Lock Right</a></li>")
        }
    });
    
});
    
