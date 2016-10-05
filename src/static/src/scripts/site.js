var
$ = require('./jquery.js');

window.jQuery = $;
window.$ = $;

require('./jquery-ui.js');


/*
 * HTML5 Sortable jQuery Plugin
 * https://github.com/voidberg/html5sortable
 *
 * Original code copyright 2012 Ali Farhadi.
 * This version is mantained by Alexandru Badiu <andu@ctrlz.ro>
 *
 * Thanks to the following contributors: andyburke, bistoco, daemianmack, flying-sheep, OscarGodson, Parikshit N. Samant, rodolfospalenza, ssafejava
 *
 * Released under the MIT license.
 */

(function($) {
	"use strict";
	var dragging, placeholders = $();
	$.fn.sortable = function(options) {
		var method = String(options);

		options = $.extend({
			connectWith: false,
			placeholder: null
		}, options);

		return this.each(function() {
			if (method === 'reload') {
				$(this).children(options.items).off('dragstart.h5s dragend.h5s selectstart.h5s dragover.h5s dragenter.h5s drop.h5s');
			}
			if (/^enable|disable|destroy$/.test(method)) {
				var citems = $(this).children($(this).data('items')).attr('draggable', method === 'enable');
				if (method === 'destroy') {
					$(this).off('sortupdate');
					citems.add(this).removeData('connectWith items')
					.off('dragstart.h5s dragend.h5s selectstart.h5s dragover.h5s dragenter.h5s drop.h5s').off('sortupdate');
				}
				return;
			}

			var soptions = $(this).data('opts');

			if (typeof soptions === 'undefined') {
				$(this).data('opts', options);
			}
			else {
				options = soptions;
			}

			var isHandle, index, items = $(this).children(options.items);
			var startParent, newParent;
			// var placeholder = ( options.placeholder === null ) ? $('<' + (/^ul|ol$/i.test(this.tagName) ? 'li' : 'div') + ' class="sortable-placeholder">') : $(options.placeholder).addClass('sortable-placeholder');
			var placeholder;
			if (/^ul|ol$/i.test(this.tagName)) {
				placeholder = $('<li/>');
			} else if (/^tbody$/i.test(this.tagName)) {
				placeholder = $('<tr/>').html($('<td/>').attr({'colspan': options.colspan ? options.colspan : '' }));
			} else {
				placeholder = $('<div/>');
			}
		placeholder.addClass('sortable-placeholder');
			items.find(options.handle).mousedown(function() {
				isHandle = true;
			}).mouseup(function() {
				isHandle = false;
			});
			$(this).data('items', options.items);
			placeholders = placeholders.add(placeholder);
			if (options.connectWith) {
				$(options.connectWith).add(this).data('connectWith', options.connectWith);
			}
			items.attr('draggable', 'true').on('dragstart.h5s', function(e) {
				if (options.handle && !isHandle) {
					return false;
				}
				isHandle = false;
				var dt = e.originalEvent.dataTransfer;
				dt.effectAllowed = 'move';
				dt.setData('Text', 'dummy');
				index = (dragging = $(this)).addClass('sortable-dragging').index();
				startParent = $(this).parent();
			}).on('dragend.h5s', function() {
				if (!dragging) {
					return;
				}
				dragging.removeClass('sortable-dragging').show();
				placeholders.detach();
				newParent = $(this).parent();
				if (index !== dragging.index() || startParent !== newParent) {
					dragging.parent().trigger('sortupdate', {item: dragging, oldindex: index, startparent: startParent, endparent: newParent});
				}
				dragging = null;
			}).not('a[href], img').on('selectstart.h5s', function() {
				if (options.handle && !isHandle) {
					return true;
				}

				if (this.dragDrop) {
					this.dragDrop();
				}
				return false;
			}).end().add([this, placeholder]).on('dragover.h5s dragenter.h5s drop.h5s', function(e) {
				if (!items.is(dragging) && options.connectWith !== $(dragging).parent().data('connectWith')) {
					return true;
				}
				if (e.type === 'drop') {
					e.stopPropagation();
					placeholders.filter(':visible').after(dragging);
					dragging.trigger('dragend.h5s');
					return false;
				}
				e.preventDefault();
				e.originalEvent.dataTransfer.dropEffect = 'move';
				if (items.is(this)) {
					var draggingHeight = dragging.outerHeight(), thisHeight = $(this).outerHeight();
					if (options.forcePlaceholderSize) {
						placeholder.height(draggingHeight);
					}

					// Check if $(this) is bigger than the draggable. If it is, we have to define a dead zone to prevent flickering
					if (thisHeight > draggingHeight){
						// Dead zone?
						var deadZone = thisHeight - draggingHeight, offsetTop = $(this).offset().top;
						if(placeholder.index() < $(this).index() && e.originalEvent.pageY < offsetTop + deadZone) {
							return false;
						}
						else if(placeholder.index() > $(this).index() && e.originalEvent.pageY > offsetTop + thisHeight - deadZone) {
							return false;
						}
					}

					dragging.hide();
					$(this)[placeholder.index() < $(this).index() ? 'after' : 'before'](placeholder);
					placeholders.not(placeholder).detach();
				} else if (!placeholders.is(this) && !$(this).children(options.items).length) {
					placeholders.detach();
					$(this).append(placeholder);
				}
				return false;
			});
		});
	};
})($);



$(function() {
	var $alerts = $('.alerts');
	$alerts.on('click', function () {
		$alerts.slideUp('slow');
	});

	if ($alerts.length) {
		setTimeout(function () {
			$alerts.slideUp('slow');
		}, 12000);
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
			$input = $('input', $this),
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
				$input.val(slider.value);
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
			if (parseFloat(value) != parseInt(value, 10) || isNaN(value) || value < 0) {
				value = 0;
			}

			if (value > 10) {
				value = 10;
			}

			$(this).siblings('.slider').slider('value', value);
		});

		$input.change(function(e) {
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
