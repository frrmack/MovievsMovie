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
    
    // Sidebar lock links
    var lock_left   = "<span class=\"glyphicon\"></span>Lock Left";
    var lock_right   = "<span class=\"glyphicon\"></span>Lock Right";
    var unlock_left = "<span class=\"glyphicon\"></span>Unlock Left<span class=\"glyphicon glyphicon-lock\"></span>";
    var unlock_right = "<span class=\"glyphicon\"></span>Unlock Right<span class=\"glyphicon glyphicon-lock\"></span>";

    $('#sidebar-lock-left').click( function(){
        $(this).toggleClass('active');
        if ($(this).hasClass('active')) {
            if  ($('#sidebar-lock-right').hasClass('active')){
		$('#sidebar-lock-right').html(lock_right);
		$('#sidebar-lock-right').removeClass('active');
            }
            $('#fight-result-form').attr('action', window.result_url_lock_left);
	    $(this).html(unlock_left)
        }
        else {
            $('#fight-result-form').attr('action', window.result_url_no_lock);
	    $(this).html(lock_left)
        }
    });

    $('#sidebar-lock-right').click( function(){
        $(this).toggleClass('active');
        if ($(this).hasClass('active')) {
            if  ($('#sidebar-lock-left').hasClass('active')){
		$('#sidebar-lock-left').html(lock_left);
		$('#sidebar-lock-left').removeClass('active');
            }
            $('#fight-result-form').attr('action', window.result_url_lock_right);
	    $(this).html(unlock_right)
        }
        else {
            $('#fight-result-form').attr('action', window.result_url_no_lock);
	    $(this).html(lock_right)
        }
    });
    
});
    
