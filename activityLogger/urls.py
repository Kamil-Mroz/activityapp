from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView

app_name = ""
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("exercises/", exercise_list, name="exercise_list"),
    path("exercise/create/", exercise_create, name="exercise_create"),
    path("exercise/<int:pk>/", exercise_detail, name="exercise_detail"),
    path("exercise/<int:pk>/edit/", exercise_edit, name="exercise_edit"),
    path(
        "workout/<int:workout_id>/exercise/<int:exercise_id>/entry/",
        exercise_entry,
        name="exercise_entry",
    ),
    path(
        "workout/exercise/<int:pk>/delete/",
        workout_exercise_delete,
        name="workout_exercise_delete",
    ),
    path(
        "entry/<int:pk>/edit/",
        exercise_entry_edit,
        name="exercise_entry_edit",
    ),
    path(
        "entry/<int:pk>/delete/",
        exercise_entry_delete,
        name="exercise_entry_delete",
    ),
    path("exercise/<int:pk>/delete/", exercise_delete, name="exercise_delete"),
    # path(
    #     "exercise/<int:pk>/download/", download_exercise_pdf, name="download_exercise_pdf"
    # ),

    path("exercise/<int:pk>/workouts/", exercise_workout_list, name="exercise_workout_list"),
    path("exercise/<int:exercise_id>/workouts/<int:workout_id>/", exercise_add_workout, name="exercise_add_workout"),

    path("workouts/", workout_list, name="workout_list"),
    path("workout/create/", workout_create, name="workout_create"),
    path("workout/<int:pk>/", workout_detail, name="workout_detail"),
    path("workout/<int:pk>/edit/", workout_edit, name="workout_edit"),
    path("workout/<int:pk>/delete/", workout_delete, name="workout_delete"),
    # path(
    #     "workout/<int:pk>/download/", download_workout_pdf, name="download_workout_pdf"
    # ),
    path("challenge/", challenge_list, name="challenge_list"),
    path("challenge/create/", challenge_create, name="challenge_create"),
    path("challenge/<int:pk>/", challenge_detail, name="challenge_detail"),
    path("challenge/<int:pk>/stat/", challenge_stat, name="challenge_stat"),
    path("challenge/<int:pk>/edit/", challenge_edit, name="challenge_edit"),
    path("challenge/<int:pk>/join/", challenge_join, name="challenge_join"),
    path("challenge/<int:pk>/leave/", challenge_leave, name="challenge_leave"),
    path("challenge/<int:pk>/delete/", challenge_delete, name="challenge_delete"),
    path("stats/", stats, name="stats"),
]
