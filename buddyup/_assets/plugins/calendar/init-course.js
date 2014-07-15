var options = {
    events_source: '../_assets/plugins/calendar/events.json',
    view: 'month',
    tmpl_path: '../_assets/plugins/calendar/tmpls/',
    tmpl_cache: false,
    // remove 'day' key to default to current day
    day: '2013-03-16',
    onAfterViewLoad: function(view) {
    	// Writes the title into the H4 in heading
        $('#calendar-wrapper h4').text(this.getTitle());
    },
    classes: {
        months: {
            general: 'label'
        }
    }
};
var calendar = $("#calendar").calendar(options);

// Functionality for the next/prev buttons 
(function($) {
	$('a[data-calendar-nav]').each(function() {
		var $this = $(this);
		$this.click(function() {
			calendar.navigate($this.data('calendar-nav'));
		});
	});
}(jQuery));