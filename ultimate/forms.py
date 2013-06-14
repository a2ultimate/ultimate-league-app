from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36

from ultimate.captain.models import *
from ultimate.leagues.models import *
from ultimate.user.models import *

class SignupForm(forms.ModelForm):
	username = forms.CharField(widget=forms.HiddenInput, required=False)
	email = forms.EmailField(label=_('Email Address'), max_length=75)
	password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
	password2 = forms.CharField(label=_('Confirm Password'), widget=forms.PasswordInput,
		help_text = _('Enter the same password as above, for verification.'))
	first_name = forms.CharField(label=_('First Name'), max_length=30)
	last_name = forms.CharField(label=_('Last Name'), max_length=30)

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
			raise forms.ValidationError(_('The two password fields didn\'t match.'))
		return password2

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
	email = forms.EmailField(label=_('Email Address'), max_length=75)
	first_name = forms.CharField(label=_('First Name'), max_length=30)
	last_name = forms.CharField(label=_('Last Name'), max_length=30)

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
	nickname = forms.CharField(max_length=30, required=False)
	phone = forms.CharField(max_length=15, required=False)
	street_address = forms.CharField(max_length=255, required=False)
	city = forms.CharField(max_length=127, required=False)
	state = forms.CharField(max_length=6, required=False)
	zipcode = forms.CharField(max_length=15, required=False)

	class Meta:
		model = Player
		exclude = ('id', 'groups', 'user', 'highest_level', 'post_count',)

SKILL_CHOICES = [ (i,i) for i in range(0,11) ]

class EditSkillsForm(forms.ModelForm):
	athletic = forms.IntegerField(min_value=1, max_value=10, initial=1)
	experience = forms.IntegerField(min_value=1, max_value=10, initial=1)
	forehand = forms.IntegerField(min_value=1, max_value=10, initial=1)
	backhand = forms.IntegerField(min_value=1, max_value=10, initial=1)
	receive = forms.IntegerField(min_value=1, max_value=10, initial=1)
	strategy = forms.IntegerField(min_value=1, max_value=10, initial=1)

	class Meta:
		model = Skills
		exclude = ('id', 'skills_report', 'skills_type', 'user', 'submitted_by', 'updated', 'spirit',)

class PlayerSurveyForm(forms.ModelForm):
	user_id = forms.IntegerField(widget=forms.HiddenInput, required=True)
	athletic = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=SKILL_CHOICES))
	forehand = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=SKILL_CHOICES))
	backhand = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=SKILL_CHOICES))
	receive = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=SKILL_CHOICES))
	strategy = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=SKILL_CHOICES))
	spirit = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=SKILL_CHOICES))
	not_sure = forms.BooleanField(required=False)

	class Meta:
		model = Skills
		exclude = ('id', 'skills_report', 'highest_level', 'experience', 'position', 'skills_type', 'user', 'submitted_by', 'updated',)

	def clean(self):
		if self.cleaned_data.get('not_sure'):
			self.removeErrorsFromSkills()
		elif (not self.cleaned_data.get('athletic')
				and not self.cleaned_data.get('forehand')
				and not self.cleaned_data.get('backhand')
				and not self.cleaned_data.get('receive')
				and not self.cleaned_data.get('handle')
				and not self.cleaned_data.get('strategy')
				and not self.cleaned_data.get('spirit')):
			self.removeErrorsFromSkills()
			raise forms.ValidationError, 'You must fill in values greater than 1 or mark "Not Sure"'

		return self.cleaned_data

	def removeErrorsFromSkills(self):
		del self._errors['athletic']
		del self._errors['forehand']
		del self._errors['backhand']
		del self._errors['receive']
		del self._errors['strategy']
		del self._errors['spirit']

class EditTeamInformationForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ('name', 'color',)

class GameReportCommentForm(forms.ModelForm):
	spirit = forms.IntegerField(min_value=1, max_value=10, widget=forms.Select(choices=SPIRIT_CHOICES))
	comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Praise, pickups, spririt issues, stoppages, field issues, etc...'}),)

	class Meta:
		model = GameReportComment
		fields = ('spirit', 'comment',)

class GameReportScoreForm(forms.ModelForm):
	id = forms.IntegerField(widget=forms.HiddenInput, required=False)
	score = forms.IntegerField(widget=forms.TextInput(attrs={'autocomplete':'off', 'autocorrect':'off'}),
		min_value=1, required=True)

	class Meta:
		model = GameReportScore
		fields = ('id', 'score',)


class RegistrationAttendanceForm(forms.ModelForm):
	id = forms.IntegerField(widget=forms.HiddenInput, required=True)
	attendance = forms.IntegerField(min_value=0, initial=0)
	captain = forms.IntegerField(min_value=1, max_value=10, initial=1)

	class Meta:
		model = Registrations
		fields = ('id', 'attendance', 'captain',)

class ScheduleGenerationForm(forms.Form):
	field_names = forms.ModelMultipleChoiceField(FieldNames.objects.all(), required=True, label=_('Fields'), help_text=_('You must pick enough fields to cover the number of games for an event. (Hold CTRL or Command to select more than one.)'))



