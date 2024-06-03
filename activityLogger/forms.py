from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django_recaptcha.fields import ReCaptchaField

class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ("username","captcha")
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs[
            "class"
        ] = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        self.fields["password1"].widget.attrs[
            "class"
        ] = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        self.fields["password2"].widget.attrs[
            "class"
        ] = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"


class CustomSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["class"] = (
            "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        )


class ExerciseForm(forms.ModelForm):
    name = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        ),
    )
    body_part = forms.ChoiceField(
        choices=BaseExercise.BODY_PARTS, widget=CustomSelect()
    )
    equipment = forms.ChoiceField(choices=BaseExercise.EQUIPMENT, widget=CustomSelect())
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "cols": 40,
                "class": "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }
        )
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
            }
        ),
    )

    class Meta:
        model = BaseExercise
        exclude = ("",)


class WorkoutForm(forms.ModelForm):
    exercises = forms.ModelMultipleChoiceField(
        queryset=BaseExercise.objects.order_by("name"),
        required=True,
        widget=forms.SelectMultiple(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 h-24 block"
            }
        ),
    )
    title = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        ),
    )

    class Meta:
        model = Workout
        fields = ["title", "exercises"]


class ExerciseEntryForm(forms.ModelForm):
    cardio_duration = forms.DurationField(
        help_text="Time format: hh:mm:ss",
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        ),
    )
    weight = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )
    repetitions = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )

    class Meta:
        model = ExerciseEntry
        exclude = ["exercise", "created", "user"]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields:
            for field_name in self.fields.copy():
                if field_name not in fields:
                    del self.fields[field_name]
                else:
                    self.fields[field_name].required = True


class ChallengeForm(forms.ModelForm):
    title = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        ),
    )
    exercise = forms.ModelChoiceField(
        queryset=BaseExercise.objects.all(), required=True, widget=CustomSelect()
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "cols": 40,
                "class": "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            }
        )
    )
    start_date = forms.DateField(
        label="Start date",
        required=True,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            },
        ),
        input_formats=["%Y-%m-%d"],
    )
    end_date = forms.DateField(
        label="End date",
        required=True,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
            },
        ),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = Challenge
        fields = ["title", "exercise", "description", "start_date", "end_date"]


class ChallengeStatForm(forms.ModelForm):
    cardio_duration = forms.DurationField(
        help_text="Time format: hh:mm:ss",
        widget=forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        ),
    )
    weight = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )
    repetitions = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )

    class Meta:
        model = Challenge
        exclude = ["title", "exercise", "description", "start_date", "end_date"]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields:
            for field_name in self.fields.copy():
                if field_name not in fields:
                    del self.fields[field_name]
                else:
                    self.fields[field_name].required = True
