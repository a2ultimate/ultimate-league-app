var $ = require('jquery'),
    sortable = require('html5sortable'),
    jQueryUi = require('jquery-ui');

$(function() {
    var $alerts = $('.alerts');
    $alerts.on('click', function() {
        $alerts.slideUp('slow');
    });

    if ($alerts.length) {
        setTimeout(function() {
            $alerts.slideUp('slow');
        }, 12000);
    }

    var sortableTables = sortable('.sortable-table', {
        connectWith: '.sortable-table-connected',
        forcePlaceholderSize: true,
        // TODO fix placeholder, does not work as of 0.4.2
        // placeholder: '<tr><td colspan="9">&nbsp;</td></tr>',
    });

    if (sortableTables && sortableTables[0]) {
        sortableTables[0].addEventListener('sortupdate', function(e) {
            if (e.detail.startparent === e.detail.endparent) {
                return;
            }

            var $startParent = $(e.detail.startparent),
                $endParent = $(e.detail.endparent),
                $target = $(e.detail.item),
                baggageId = $target.data('baggage-id');

            $startParent.find('[data-baggage-id="' + baggageId + '"]').insertAfter($target);

            updateTeamInformation($startParent);
            updateTeamInformation($endParent);
        });
    }

    var updateTeamInformation = function($team) {
        var $teamMembers = $team.children('.team-member'),
            $teamInfo = $team.prev('thead'),
            $teamStatsTable = $('#team-stats-table'),
            teamId = $team.attr('id').split('-').pop(),
            teamRatingTotal = 0,
            teamRatingAverage,
            teamSize,
            teamSizeMale,
            teamSizeFemale,
            teamAttendanceTotal = 0,
            teamAttendanceAverage;

        $team.find('.team-member-input').attr('name', 'team_member_' + teamId);
        $team.find('.team-member-captain-input').attr('name', 'team_member_captain_' + teamId);

        $teamMembers.each(function() {
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

        $teamStatsTable.find('.team-stats-' + teamId + ' > .team-rating-average').text(teamRatingAverage);
        $teamStatsTable.find('.team-stats-' + teamId + ' > .team-rating-total').text(teamRatingTotal);
        $teamStatsTable.find('.team-stats-' + teamId + ' > .team-size').text(teamSize);
        $teamStatsTable.find('.team-stats-' + teamId + ' > .team-size-male').text(teamSizeMale);
        $teamStatsTable.find('.team-stats-' + teamId + ' > .team-size-female').text(teamSizeFemale);
        $teamStatsTable.find('.team-stats-' + teamId + ' > .team-attenance-total').text(teamAttendanceTotal);
        $teamStatsTable.find('.team-stats-' + teamId + ' > .team-attendance-average').text(teamAttendanceAverage);

        $teamInfo.find('.team-rating-average').text(teamRatingAverage);
        $teamInfo.find('.team-rating-total').text(teamRatingTotal);
        $teamInfo.find('.team-size').text(teamSize);
        $teamInfo.find('.team-size-male').text(teamSizeMale);
        $teamInfo.find('.team-size-female').text(teamSizeFemale);
        $teamInfo.find('.team-attendance-total').text(teamAttendanceTotal);
        $teamInfo.find('.team-attendance-average').text(teamAttendanceAverage);
    }

    $('.slider').each(function() {
        var $this = $(this),
            $input = $('input', $this),
            $slider = $('.slider-element', $this),
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
                $input.val(slider.value);
            },
            value: $input.val()
        });

        $input.on('blur', function(e) {
            $(this).val($(this).siblings('.slider').slider('value'));
        });

        $input.on('keydown', function(e) {
            if (e.keyCode == '13') {
                e.preventDefault();
                e.stopPropagation();
            }
        });

        $input.on('keyup', function(e) {
            var value = this.value;
            if (parseFloat(value) != parseInt(value, 10) || isNaN(value) || value < 0) {
                value = 0;
            }

            if (value > 10) {
                value = 10;
            }

            $(this).siblings('.slider').slider('value', value);
        });

        $input.on('change', function(e) {
            var value = this.value;
            if (parseFloat(value) != parseInt(value, 10) || isNaN(value) || value < 0) {
                value = 0;
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
