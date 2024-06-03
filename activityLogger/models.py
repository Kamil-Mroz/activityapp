from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    User model extending the AbstractUser model to include a profile image.
    """

    profile_img = models.ImageField(blank=True, null=True)


class BaseExercise(models.Model):
    """
    Model representing a base exercise with attributes such as name, body part, equipment,
    description, and image.
    """

    BODY_PARTS = (
        ("Forearms", "Forearms"),
        ("Triceps", "Triceps"),
        ("Biceps", "Biceps"),
        ("Neck", "Neck"),
        ("Shoulders", "Shoulders"),
        ("Chest", "Chest"),
        ("Back", "Back"),
        ("Core", "Core"),
        ("Upper Legs", "Upper Legs"),
        ("Glutes", "Glutes"),
        ("Calves", "Calves"),
        ("Full Body", "Full Body"),
        ("Other", "Other"),
    )
    EQUIPMENT = (
        ("Barbell", "Barbell"),
        ("Dumbbell", "Dumbbell"),
        ("Machine", "Machine"),
        ("Bodyweight", "Bodyweight"),
        ("Bands", "Bands"),
        ("Cardio", "Cardio"),
    )
    name = models.CharField(max_length=64)
    body_part = models.CharField(max_length=16, choices=BODY_PARTS)
    equipment = models.CharField(max_length=16, choices=EQUIPMENT)
    description = models.TextField(max_length=512, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)

    class Meta:
        unique_together = ("body_part", "name", "equipment")

    def __str__(self):
        return f"{self.name} ({self.equipment}) "


class Workout(models.Model):
    """
    Model representing a workout which includes a user, creation date, title,
    and many-to-many relationship with BaseExercise through WorkoutExercise.
    """

    user = models.ForeignKey(User, related_name="workouts", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=150)
    exercises = models.ManyToManyField(BaseExercise, through="WorkoutExercise")

    def __str__(self):
        return f"{self.title}"


class WorkoutExercise(models.Model):
    """
    Intermediate model representing the many-to-many relationship between Workout
    and BaseExercise.
    """

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(BaseExercise, on_delete=models.CASCADE)

    def __str__(self):
        return f"Workout: {self.workout.title} - Exercise: {self.exercise.name}"


class ExerciseEntry(models.Model):
    """
    Model representing an entry for an exercise performed by a user, associated with a workout.
    It includes details like repetitions, weight, and cardio duration.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(BaseExercise, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    repetitions = models.PositiveIntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    cardio_duration = models.DurationField(blank=True, null=True)

    def __str__(self):
        return f"Stats for Exercise: {self.exercise.name}"


class Challenge(models.Model):
    """
    Model representing a challenge that includes a title, description, an optional exercise,
    repetitions, weight, cardio duration, start date, and end date.
    """

    title = models.CharField(max_length=150)
    description = models.TextField()
    exercise = models.ForeignKey(
        BaseExercise, on_delete=models.CASCADE, blank=True, null=True
    )
    repetitions = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    cardio_duration = models.DurationField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        """
        Ensure that the start date is not after the end date.
        """
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date cannot be after the end date.")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_date__lt=models.F("end_date")),
                name="start_date_before_end_date",
            )
        ]

    def __str__(self):
        return f"Challenge: {self.title}"


class UserChallenge(models.Model):
    """
    Model representing the association between a user and a challenge.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    def __str__(self):
        return f"Challenge: {self.challenge.title} - User: {self.user}"
