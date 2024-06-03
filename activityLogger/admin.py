# admin.py
"""
Django admin registrations.

This module contains registrations of Django models with the admin site.
"""

from django.contrib import admin
from .models import (
    User,
    Workout,
    WorkoutExercise,
    BaseExercise,
    ExerciseEntry,
    Challenge,
    UserChallenge,
)


class BaseExerciseAdmin(admin.ModelAdmin):
    """
    Admin interface for the BaseExercise model.
    """

    list_display = ["name", "body_part", "equipment"]
    search_fields = ["name", "body_part", "equipment"]
    list_filter = ["body_part", "equipment"]


class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for the User model.
    """

    list_display = ["username", "email"]
    search_fields = ["username", "email"]


class WorkoutAdmin(admin.ModelAdmin):
    """
    Admin interface for the Workout model.
    """

    list_display = ["user", "title"]
    search_fields = ["user__username", "title"]


class WorkoutExerciseAdmin(admin.ModelAdmin):
    """
    Admin interface for the Workout model.
    """

    list_display = ["workout", "exercise"]
    search_fields = ["workout__title", "exercise__name", "workout__user__username"]


class ExerciseEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for the ExerciseEntry model.
    """

    list_display = ["user", "exercise", "workout"]
    search_fields = ["user__username", "exercise__name", "workout__title"]


class ChallengeAdmin(admin.ModelAdmin):
    """
    Admin interface for the Challenge model.
    """

    list_display = ["title", "exercise", "start_date", "end_date"]
    search_fields = ["title", "exercise", "start_date", "end_date"]


class UserChallengeAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserChallenge model.
    """

    list_display = ["user", "challenge"]
    search_fields = ["user__username", "challenge__title"]


# Registering models with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(Workout, WorkoutAdmin)
admin.site.register(WorkoutExercise, WorkoutExerciseAdmin)
admin.site.register(BaseExercise, BaseExerciseAdmin)
admin.site.register(ExerciseEntry, ExerciseEntryAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(UserChallenge, UserChallengeAdmin)
