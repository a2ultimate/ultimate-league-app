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