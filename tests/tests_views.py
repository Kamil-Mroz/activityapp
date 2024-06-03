from datetime import timedelta, date

from unittest.mock import patch

from django.test import TestCase
from django_recaptcha.client import RecaptchaResponse
from django.urls import reverse

from activityLogger.models import (
    User,
    BaseExercise,
    ExerciseEntry,
    WorkoutExercise,
    Workout,
    Challenge,
)


class ExerciseDetailTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Create a test exercise
        self.exercise = BaseExercise.objects.create(
            name="Sprint", body_part="Legs", equipment="Cardio"
        )

        # Create a workout for the user
        self.workout = Workout.objects.create(user=self.user, title="Morning Cardio")

        # Create a WorkoutExercise linking the workout and the exercise
        self.workout_exercise = WorkoutExercise.objects.create(
            workout=self.workout, exercise=self.exercise
        )

        # Create an ExerciseEntry with the exercise and workout details
        ExerciseEntry.objects.create(
            user=self.user,
            exercise=self.exercise,
            workout=self.workout,
            cardio_duration=timedelta(minutes=10),
        )

    def test_exercise_statistics(self):
        # Log in the test user
        self.client.login(username="testuser", password="testpass")

        # Make a GET request to the exercise detail view
        response = self.client.get(
            reverse("exercise_detail", kwargs={"pk": self.exercise.pk})
        )

        # Check that the context contains the expected status
        # This assumes that your view correctly extracts and computes the stats
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["stats"], [600])  # 10 minutes in seconds


class ExerciseListTests(TestCase):
    def setUp(self):
        # Create test user and login
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create a test exercise
        self.exercise = BaseExercise.objects.create(
            name="Push Up", body_part="Chest", equipment="Bodyweight"
        )

        # Create a workout for the user
        self.workout = Workout.objects.create(
            user=self.user,
            title="Doing push ups quietly in my room so my parents won't hear it",
        )

        # Create a WorkoutExercise linking the workout and the exercise
        self.workout_exercise = WorkoutExercise.objects.create(
            workout=self.workout, exercise=self.exercise
        )

        # Create an ExerciseEntry with the exercise and workout details
        ExerciseEntry.objects.create(
            user=self.user, exercise=self.exercise, workout=self.workout, repetitions=12
        )

    def test_view_with_filters(self):
        response = self.client.get(reverse("exercise_list") + "?body_part=Chest")
        exercise_names = [exercise.name for exercise in response.context["exercises"]]
        self.assertIn("Push Up", exercise_names)

    def test_view_with_no_filters(self):
        response = self.client.get(reverse("exercise_list"))
        exercise_names = [exercise.name for exercise in response.context["exercises"]]
        self.assertIn("Push Up", exercise_names)


class HomeViewTests(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_uses_correct_template(self):
        User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "activityLogger/home.html")


class RegisterViewTests(TestCase):
    def test_authenticated_user_redirect(self):
        User.objects.create_user(username="user", password="password")
        self.client.login(username="user", password="password")
        response = self.client.get(reverse("register"), follow=True)
        self.assertRedirects(
            response, reverse("home"), status_code=302, target_status_code=200
        )  # Assuming 'home' is the success URL

    @patch("django_recaptcha.fields.client.submit")
    def test_registration_redirects_to_login(self, mocked_submit):
        # Setup the mock to pass validation
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "asdjkfl;asdkasdfjkjkl;aslasdfj1234",
                "password2": "asdjkfl;asdkasdfjkjkl;aslasdfj1234",
                "g-recaptcha-response": "PASSED",
            },
            follow=True,
        )
        # Use assertRedirects with the follow argument
        self.assertRedirects(response, reverse("login"))


class ChallengeViewTests(TestCase):
    """
    np w challenge_detail pobierasz challenge i dla danego challenge pobierasz wszystkie wpisy dla danego użytownika i cwiczenia z ExerciseEntry i
    tam masz zaleznie od exercise.equipment oblicza progres to możesz napisać test który dla danego wyzwania i zdanymi wpisami obliczy progress i
    czy się zgadza.

    np pompki na poręczy czyli bodyweight to suma wszystkich wpisów muszą być np = 10 suma repetitions
    """

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="challenge_user", password="challenge_pass"
        )
        self.client.login(username="challenge_user", password="challenge_pass")

        # Create exercises
        self.exercise = BaseExercise.objects.create(
            name="Push Ups",
            body_part="Chest",
            equipment="Bodyweight",
            description="Push ups on the railing",
        )

        self.challenge = Challenge.objects.create(
            title="Challenge",
            description="challenge description",
            exercise=self.exercise,
            repetitions=300,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        # Create a workout for the user
        self.workout = Workout.objects.create(
            user=self.user,
            title="Doing push ups quietly in my room so my parents won't hear it",
        )

        # Create a WorkoutExercise linking the workout and the exercise
        self.workout_exercise = WorkoutExercise.objects.create(
            workout=self.workout, exercise=self.exercise
        )

        ExerciseEntry.objects.create(
            user=self.user, exercise=self.exercise, repetitions=30, workout=self.workout
        )

        ExerciseEntry.objects.create(
            user=self.user, exercise=self.exercise, repetitions=40, workout=self.workout
        )

        ExerciseEntry.objects.create(
            user=self.user, exercise=self.exercise, repetitions=30, workout=self.workout
        )

    def test_calculate_progess(self):
        entries = ExerciseEntry.objects.filter(user=self.user, exercise=self.exercise)
        total_repetitions = sum(entry.repetitions for entry in entries)
        progress = min(int((total_repetitions / self.challenge.repetitions) * 100), 100)

        self.assertEqual(
            progress, min(int((100 / self.challenge.repetitions) * 100), 100)
        )
