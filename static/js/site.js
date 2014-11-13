$(function() {
	var $alerts = $('#alerts_container');
	$alerts.on('click', function () {
		$alerts.slideUp('slow');
	});

	if ($alerts.length) {
		setTimeout(function () {
			$alerts.slideUp('slow');
		}, 10000);
	}

	$('.sortable_table').sortable({
		colspan: 9,
		connectWith: '.sortable_table_connected',
		forcePlaceholderSize: true,
		items: 'tr'
	}).on('sortupdate', function(e, ui) {
		if (ui.startparent.get(0) === ui.endparent.get(0)) {
			return;
		}

		var $startParent = $(ui.startparent),
			$endParent = $(ui.endparent),
			$target = $(ui.item),
			baggageId = $target.data('baggage-id');

		$startParent.find('[data-baggage-id="' + baggageId + '"]').insertAfter($target);

		updateTeamInformation($startParent);
		updateTeamInformation($endParent);
	});

	function updateTeamInformation($team) {
		var $teamMembers = $team.children('.team_member'),
			$teamInfo = $team.prev('thead'),
			$teamStatsTable = $('#team_stats_table'),
			teamId = $team.attr('id').split('_').pop(),
			teamRatingTotal = 0, teamRatingAverage,
			teamSize, teamSizeMale, teamSizeFemale,
			teamAttendanceTotal = 0, teamAttendanceAverage;

		$team.find('.team_member_input').attr('name', 'team_member_' + teamId);
		$team.find('.team_member_captain_input').attr('name', 'team_member_captain_' + teamId);

		$teamMembers.each(function () {
			teamRatingTotal += parseFloat($(this).data('rating-total'));
			teamAttendanceTotal += parseFloat($(this).data('attendance-total'));
		});

		teamRatingTotal = teamRatingTotal.toFixed(2);
		teamRatingAverage = parseFloat(teamRatingTotal / $teamMembers.length).toFixed(2);
		teamSize = $teamMembers.length;
		teamSizeMale = $teamMembers.filter('[data-gender="M"]', $).length;
		teamSizeFemale = $teamMembers.filter('[data-gender="F"]', $).length;
		teamAttendanceTotal = teamAttendanceTotal.toFixed(2);
		teamAttendanceAverage = parseFloat(teamAttendanceTotal / $teamMembers.length).toFixed(2);

		$teamStatsTable.find('.team_stats_' + teamId + ' > .team_rating_average').text(teamRatingAverage);
		$teamStatsTable.find('.team_stats_' + teamId + ' > .team_rating_total').text(teamRatingTotal);
		$teamStatsTable.find('.team_stats_' + teamId + ' > .team_size').text(teamSize);
		$teamStatsTable.find('.team_stats_' + teamId + ' > .team_size_male').text(teamSizeMale);
		$teamStatsTable.find('.team_stats_' + teamId + ' > .team_size_female').text(teamSizeFemale);
		$teamStatsTable.find('.team_stats_' + teamId + ' > .team_attenance_total').text(teamAttendanceTotal);
		$teamStatsTable.find('.team_stats_' + teamId + ' > .team_attendance_average').text(teamAttendanceAverage);

		$teamInfo.find('.team_rating_average').text(teamRatingAverage);
		$teamInfo.find('.team_rating_total').text(teamRatingTotal);
		$teamInfo.find('.team_size').text(teamSize);
		$teamInfo.find('.team_size_male').text(teamSizeMale);
		$teamInfo.find('.team_size_female').text(teamSizeFemale);
		$teamInfo.find('.team_attendance_total').text(teamAttendanceTotal);
		$teamInfo.find('.team_attendance_average').text(teamAttendanceAverage);
	}

	$('.slide_selector').each(function () {
		var $this = $(this),
			$input = $('input[type=text]', $this),
			$slider = $('.slider', $this),
			sliderMax = $this.data('slider-max') || 10,
			sliderMin = $this.data('slider-min') || 0;

		if (!$input.val()) {
			$input.val(sliderMin);
		}

		$slider.slider({
			animate: true,
			max: sliderMax || 10,
			min: sliderMin || 0,
			slide: function(event, slider) {
				$(this).siblings('input[type=text]').val(slider.value);
			},
			value: $input.val()
		});

		$input.blur(function (e) {
			$(this).val($(this).siblings('.slider').slider('value'));
		});

		$input.keydown(function(e) {
			if (e.keyCode == '13') {
				e.preventDefault();
				e.stopPropagation();
			}
		});

		$input.keyup(function(e) {
			var value = this.value;
			if (parseFloat(value) != parseInt(value, 10) || isNaN(value) || value < 1) {
				value = 1;
			}

			if (value > 10) {
				value = 10;
			}

			$(this).siblings('.slider').slider('value', value);
		});
	});

	// login
	$('#id_username').focus();
});