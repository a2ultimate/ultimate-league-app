from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ultimate.captain.models import *
from ultimate.leagues.models import *
from ultimate.user.models import *


class SignupForm(forms.ModelForm):
	username = forms.CharField(widget=forms.HiddenInput, required=False)
	email = forms.EmailField(label=_('Email Address'), max_length=75)
	password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
	password2 = forms.CharField(label=_('Confirm Password'), widget=forms.PasswordInput,
		help_text=_('Enter the same password as above, for verification.'))
	first_name = forms.CharField(label=_('First Name'), max_length=30)
	last_name = forms.CharField(label=_('Last Name'), max_length=30)
	honeypot = forms.CharField(required=False, label=_('Honeypot'),
		help_text=_('If you enter anything in this field your form submission will be treated as spam'))
	blank = forms.CharField(required=False, label=_('Blank'),
		help_text=_('If you enter anything in this field your form submission will be treated as spam'))

	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name',)

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			User.objects.get(email=email)
		except User.DoesNotExist:
			return email
		raise forms.ValidationError(_('A user with that email already exists.'))

	def clean_username(self):
		return self.cleaned_data['username']

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1', '')
		password2 = self.cleaned_data['password2']
		if password1 != password2:
			raise forms.ValidationError(_('The two password fields did not match.'))
		return password2

	def clean_honeypot(self):
		value = self.cleaned_data['honeypot']
		if not value == '':
			print('honeypot!')
			raise forms.ValidationError(self.fields['honeypot'].label)
		return value

	def clean_blank(self):
		value = self.cleaned_data['blank']
		if not value == '':
			print('blank!')
			raise forms.ValidationError(self.fields['blank'].label)
		return value

	def clean(self):
		if not self.errors:
			self.cleaned_data['username'] = self.cleaned_data['email']
		super(SignupForm, self).clean()
		return self.cleaned_data

	def save(self, commit=True):
		user = super(SignupForm, self).save(commit=False)
		user.set_password(self.cleaned_data['password1'])
		if commit:
			user.save()
		return user


class EditProfileForm(forms.ModelForm):
	username = forms.CharField(widget=forms.HiddenInput, required=False)
	email = forms.EmailField(label=_('Email Address*'), max_length=75)
	first_name = forms.CharField(label=_('First Name*'), max_length=30)
	last_name = forms.CharField(label=_('Last Name*'), max_length=30)

	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name',)

	def clean_email(self):
		email = self.cleaned_data['email']
		if email != self.instance.email:
			try:
				User.objects.get(email=email)
			except User.DoesNotExist:
				return email
			raise forms.ValidationError(_('A user with that email already exists.'))
		else:
			return email

	def clean_username(self):
		return self.cleaned_data['username']

	def clean(self):
		if not self.errors:
			self.cleaned_data['username'] = self.cleaned_data['email']
		super(EditProfileForm, self).clean()
		return self.cleaned_data

	def save(self, commit=True):
		user = super(EditProfileForm, self).save(commit=False)
		if commit:
			user.save()
		return user


class EditPlayerForm(forms.ModelForm):
	nickname = forms.CharField(required=False)
	phone = forms.CharField(required=False)
	street_address = forms.CharField(required=False)
	city = forms.CharField(required=False)
	state = forms.CharField(required=False)
	zipcode = forms.CharField(required=False)
	gender = forms.CharField(label='Gender*', widget=forms.Select(choices=(('', '----------'),) + Player.GENDER_CHOICES))
	height_inches = forms.IntegerField(label='Height Inches*')
	birthdate = forms.DateField(label='Birthdate*', help_text='e.g. ' + date.today().strftime('%Y-%m-%d'))
	jersey_size = forms.CharField(label='Jersey Size*', widget=forms.Select(choices=(('', '----------'),) + Player.JERSEY_SIZE_CHOICES))

	class Meta:
		model = Player
		exclude = ('id', 'groups', 'user', 'highest_level', 'post_count',)


class EditPlayerRatingsForm(forms.ModelForm):
	experience = forms.TypedChoiceField(coerce=int, choices=PlayerRatings.RATING_EXPERIENCE_CHOICES, widget=forms.RadioSelect, label='1. How much experience do you have playing ultimate?')
	strategy = forms.TypedChoiceField(coerce=int, choices=PlayerRatings.RATING_STRATEGY_CHOICES, widget=forms.RadioSelect, label='2. How would you rate your knowledge of ultimate rules, strategies, and gameplay?')
	throwing = forms.TypedChoiceField(coerce=int, choices=PlayerRatings.RATING_THROWING_CHOICES, widget=forms.RadioSelect, label='3. How would you rate your throwing ability?')
	athleticism = forms.TypedChoiceField(coerce=int, choices=PlayerRatings.RATING_ATHLETICISM_CHOICES, widget=forms.RadioSelect, label='4. How would you rate your endurance and speed?')
	competitiveness = forms.TypedChoiceField(coerce=int, choices=PlayerRatings.RATING_COMPETITIVENESS_CHOICES, widget=forms.RadioSelect, label='5. How competitively do you like to play?')

	class Meta:
		model = PlayerRatings
		exclude = ('id', 'spirit', 'user', 'submitted_by', 'ratings_type', 'ratings_report', 'not_sure', 'updated',)


class PlayerSurveyForm(forms.ModelForm):
	user_id = forms.IntegerField(widget=forms.HiddenInput, required=True)
	strategy = forms.IntegerField(min_value=1, max_value=6, widget=forms.Select(choices=[ (i,i) for i in range(7) ]))
	throwing = forms.IntegerField(min_value=1, max_value=6, widget=forms.Select(choices=[ (i,i) for i in range(7) ]))
	athleticism = forms.IntegerField(min_value=1, max_value=6, widget=forms.Select(choices=[ (i,i) for i in range(7) ]))
	spirit = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=[ (i,i) for i in range(11) ]))
	not_sure = forms.BooleanField(required=False)

	class Meta:
		model = PlayerRatings
		exclude = ('id', 'experience', 'competitiveness', 'user', 'submitted_by', 'ratings_type', 'ratings_report', 'updated',)

	def clean(self):
		if not self.cleaned_data.get('strategy') or \
			not self.cleaned_data.get('throwing') or \
			not self.cleaned_data.get('athleticism') or \
			not self.cleaned_data.get('spirit'):

			if self.cleaned_data.get('not_sure'):
				self.removeErrorsFromRatings()
			else:
				raise forms.ValidationError(_('You must fill in values greater than 1 or mark "Not Sure"'))

		return self.cleaned_data

	def removeErrorsFromRatings(self):
		if ('strategy' in self._errors):
			del self._errors['strategy']

		if ('throwing' in self._errors):
			del self._errors['throwing']

		if ('athleticism' in self._errors):
			del self._errors['athleticism']

		if ('spirit' in self._errors):
			del self._errors['spirit']


class EditTeamInformationForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ('name', 'color',)


class GameReportCommentForm(forms.ModelForm):
	spirit = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=GameReportComment.SPIRIT_CHOICES))
	comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Praise, pickups, spririt issues, stoppages, field issues, etc...'}),)

	class Meta:
		model = GameReportComment
		fields = ('spirit', 'comment',)


class GameReportScoreForm(forms.ModelForm):
	id = forms.IntegerField(widget=forms.HiddenInput, required=False)
	team = forms.ModelChoiceField(label='', queryset=Team.objects.all(), widget=forms.HiddenInput(), required=True)
	score = forms.IntegerField(widget=forms.TextInput(attrs={'autocomplete':'off', 'autocorrect':'off'}),
		min_value=1, required=True)

	class Meta:
		model = GameReportScore
		fields = ('id', 'team', 'score',)


class RegistrationAttendanceForm(forms.ModelForm):
	id = forms.IntegerField(widget=forms.HiddenInput, required=True)
	attendance = forms.IntegerField(min_value=0, initial=0)
	captain = forms.IntegerField(min_value=0, max_value=4, initial=0)

	class Meta:
		model = Registrations
		fields = ('id', 'attendance', 'captain',)


class ScheduleGenerationForm(forms.Form):
	field_names = forms.ModelMultipleChoiceField(FieldNames.objects.all(), required=True, label=_('Fields'), help_text=_('You must pick enough fields to cover the number of games for an event. (Hold CTRL or Command to select more than one.)'))
