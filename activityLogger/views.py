from datetime import date, timedelta
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F, Case, When, IntegerField, FloatField, Value, DurationField
from django.db.models.functions import TruncMonth, TruncYear, Coalesce, Extract

import pdfkit
from django.template.loader import render_to_string
from django.conf import settings

import logging

logger = logging.getLogger(__name__)
# config = pdfkit.configuration(
#     wkhtmltopdf=settings.WKHTMLTOPDF_PATH
# )


class RegisterView(generic.CreateView):
    """
    View for user registration.

    This view allows users to register by providing their username, email, and password.
    Upon successful registration, users are redirected to the login page.

    Attributes:
        template_name (str): The name of the template used to render the registration form.
        form_class (form): The form class used for user registration.
        redirect_authenticated_user (bool): Whether to redirect authenticated users to the success URL.
    """

    template_name = "activityLogger/register.html"
    form_class = CustomUserCreationForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method to redirect authenticated users.

        If `redirect_authenticated_user` is True and the user is already authenticated,
        they will be redirected to the success URL (login page).
        """
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            logger.warning(
                "Authenticated user attempted to access registration page. Redirecting to %s",
                redirect_to,
            )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Get the URL to redirect to after successful registration.

        Returns:
            str: The URL to redirect to (login page).
        """
        url = reverse("login")
        logger.info("User registration successful. Redirecting to login page: %s", url)
        return url


class HomeView(LoginRequiredMixin, generic.TemplateView):
    """
    View for the home page.

    This view displays the home page after the user has logged in.

    Attributes:
        template_name (str): The name of the template used to render the home page.
    """

    template_name = "activityLogger/home.html"

    def get_success_url(self):
        """
        Get the URL to redirect to after accessing the home page.

        Returns:
            str: The URL to redirect to (login page).
        """
        url = reverse("login")
        logger.info("User accessed the home page. Redirecting to login page: %s", url)
        return url


@login_required
def exercise_list(request):
    """
    View for displaying a list of exercises.

    This view retrieves all exercises from the database and renders them in a list.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered template with the list of exercises.
    """
    logger.info("User accessed the exercise list page.")

    exercises = BaseExercise.objects.all()
    body_parts = BaseExercise.BODY_PARTS
    equipment = BaseExercise.EQUIPMENT

    selected_body_part = request.GET.get("body_part")
    selected_equipment = request.GET.get("equipment")

    if selected_body_part and selected_equipment:
        exercises = exercises.filter(
            body_part=selected_body_part, equipment=selected_equipment
        )
    elif selected_body_part:
        exercises = exercises.filter(body_part=selected_body_part)
    elif selected_equipment:
        exercises = exercises.filter(equipment=selected_equipment)

    return render(
        request,
        "activityLogger/exercise_list.html",
        {
            "exercises": exercises,
            "body_parts": body_parts,
            "equipment": equipment,
            "selected_body_part": selected_body_part,
            "selected_equipment": selected_equipment,
        },
    )


@login_required
def exercise_detail(request, pk):
    """
    View for displaying details of a specific exercise.

    This view retrieves the details of a specific exercise and its statistics (if available) from the database
    and renders them on the exercise detail page.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the exercise.

    Returns:
        HttpResponse: The HTTP response containing the rendered template with the exercise details.
    """

    logger.info("User accessed the exercise detail page for exercise with id: %s", pk)

    
    exercise = get_object_or_404(BaseExercise, pk=pk)

    # Retrieve exercise statistics for the current user from the database
    exercises_stats = ExerciseEntry.objects.filter(
        exercise=exercise, user=request.user
    ).order_by("created")

    weight = ["Barbell", "Dumbbell", "Machine", "Bands"]

    # Initialize variables for statistics and exercise type
    stats = None
    exercise_type = None
    best_stats = None

    # Determine the type of statistics based on the exercise equipment
    if exercise.equipment in weight:
        stats = exercises_stats.values_list("weight", flat=True)[:10]
        best_stats = exercises_stats.order_by('-weight')[:10]
        exercise_type = "Weight (kg)"
    elif exercise.equipment == "Bodyweight":
        stats = exercises_stats.values_list("repetitions", flat=True)[:10]
        best_stats = exercises_stats.order_by('-repetitions')[:10]
        exercise_type = "Repetitions"
        
    elif exercise.equipment == "Cardio":
        stats = exercises_stats.values_list("cardio_duration", flat=True)[:10]
        stats = [duration.total_seconds() for duration in stats]
        best_stats = exercises_stats.order_by('-cardio_duration')[:10]
        exercise_type = "Durations (s)"


    # Retrieve dates of exercise entries
    dates = exercises_stats.values_list("created", flat=True)[:10]
    
    # Format dates for display
    dates = [date.strftime("%d %b") for date in dates]
    

    return render(
        request,
        "activityLogger/exercise_detail.html",
        {
            "exercise": exercise,
            "exercises_stats": exercises_stats,
            "dates": dates,
            "stats": stats,
            "exercise_type": exercise_type,
            "best_stats":best_stats,
            "weight":weight,
            
        },
    )


@login_required
@staff_member_required
def exercise_create(request):
    """
    View for creating a new exercise.

    This view allows staff members to create a new exercise by submitting a form
    with details such as name, description, body part, image, and equipment.
    Upon successful creation, the user is redirected to the exercise detail page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the exercise creation form or a redirect to the exercise detail page.
    """

    logger.info("Staff member accessed the exercise creation page.")

    if request.method == "POST":
        form = ExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            exercise = form.save()
            logger.info(
                "Exercise '%s' created successfully. Redirecting to exercise detail page.",
                exercise.name,
            )
            return redirect("exercise_detail", exercise.id)
    else:
        form = ExerciseForm()

    return render(request, "activityLogger/exercise_create.html", {"form": form})


@login_required
@staff_member_required
def exercise_edit(request, pk):
    """
    View for editing an existing exercise.

    This view allows staff members to edit the details of an existing exercise
    by submitting a form with updated information.
    Upon successful editing, the user is redirected to the exercise detail page.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the exercise to edit.

    Returns:
        HttpResponse: The HTTP response containing the exercise editing form or a redirect to the exercise detail page.
    """
    logger.info(
        "Staff member accessed the exercise edit page for exercise with id: %s", pk
    )
    exercise = get_object_or_404(BaseExercise, pk=pk)

    if request.method == "POST":
        form = ExerciseForm(request.POST, request.FILES, instance=exercise)
        if form.is_valid():
            form.save()
            logger.info(
                "Exercise '%s' edited successfully. Redirecting to exercise detail page.",
                exercise.name,
            )
            return redirect("exercise_detail", exercise.id)
    else:
        form = ExerciseForm(instance=exercise)

    return render(
        request,
        "activityLogger/exercise_edit.html",
        {"form": form, "exercise_id": exercise.id},
    )


@login_required
def exercise_entry(request, workout_id, exercise_id):
    """
    View for adding an exercise entry to a workout.

    This view allows authenticated users to add an exercise entry to a workout.
    The user must be the owner of the workout to add an entry.
    The type of exercise entry fields is determined based on the equipment used for the exercise.

    Args:
        request (HttpRequest): The HTTP request object.
        workout_id (int): The ID of the workout to which the exercise entry is added.
        exercise_id (int): The ID of the exercise for which the entry is added.

    Returns:
        HttpResponse: The HTTP response containing the exercise entry form or a redirect to the appropriate page.
    """
    logger.info(
        "User accessed the exercise entry page for workout with id: %s and exercise with id: %s",
        workout_id,
        exercise_id,
    )
    workout = get_object_or_404(Workout, pk=workout_id)

    # Check if the user is the owner of the workout
    if workout.user != request.user:
        logger.warning(
            "Unauthorized access attempt to exercise entry page for workout with id: %s",
            workout_id,
        )
        return redirect("home")

    exercise = get_object_or_404(BaseExercise, pk=exercise_id)
    weight_equipment_choices = ["Barbell", "Dumbbell", "Machine", "Bands"]

    # Determine exercise type and fields
    if exercise.equipment == "Bodyweight":
        fields = ["repetitions"]
    elif exercise.equipment in weight_equipment_choices:
        fields = ["repetitions", "weight"]
    elif exercise.equipment == "Cardio":
        fields = ["cardio_duration"]
    else:
        logger.error(
            "Unsupported equipment type '%s' for exercise with id: %s",
            exercise.equipment,
            exercise_id,
        )
        # Handle unsupported exercise type
        return redirect("home")  # Redirect to home or appropriate page

    if request.method == "POST":
        form = ExerciseEntryForm(request.POST, fields=fields)
        if form.is_valid():
            # Create WorkoutExercise instance
            exercise_entry = form.save(commit=False)
            exercise_entry.user = request.user
            exercise_entry.workout = workout
            exercise_entry.exercise = exercise
            exercise_entry.save()
            logger.info(
                "Exercise entry added successfully for workout with id: %s and exercise with id: %s",
                workout_id,
                exercise_id,
            )

            if "save_and_add_another" in request.POST:
                # Redirect to the same page for adding another entry
                return redirect(
                    "exercise_entry", workout_id=workout_id, exercise_id=exercise_id
                )
            else:
                # Redirect to exercise detail page
                return redirect("workout_detail", pk=workout_id)
    else:
        form = ExerciseEntryForm(fields=fields)

    return render(
        request,
        "activityLogger/exercise_entry.html",
        {"form": form, "exercise": exercise, "workout": workout},
    )


@login_required
def exercise_entry_edit(request, pk):
    """
    View for editing an exercise entry.

    This view allows authenticated users to edit an existing exercise entry.
    The user must be the owner of the exercise entry to edit it.
    The type of exercise entry fields is determined based on the equipment used for the exercise.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the exercise entry to edit.

    Returns:
        HttpResponse: The HTTP response containing the exercise entry form or a redirect to the appropriate page.
    """
    exercise_entry = get_object_or_404(ExerciseEntry, pk=pk)

    # Check if the user is the owner of the exercise entry
    if exercise_entry.user != request.user:
        logger.warning(
            "Unauthorized access attempt to exercise entry edit page for entry with id: %s",
            pk,
        )
        return redirect("home")

    weight_equipment_choices = ["Barbell", "Dumbbell", "Machine", "Bands"]

    # Determine exercise type and fields
    if exercise_entry.exercise.equipment == "Bodyweight":
        fields = ["repetitions"]
    elif exercise_entry.exercise.equipment in weight_equipment_choices:
        fields = ["repetitions", "weight"]
    elif exercise_entry.exercise.equipment == "Cardio":
        fields = ["cardio_duration"]
    else:
        # Handle unsupported exercise type
        logger.error(
            "Unsupported equipment type '%s' for exercise entry with id: %s",
            exercise_entry.exercise.equipment,
            pk,
        )
        return redirect("home")  # Redirect to home or appropriate page

    if request.method == "POST":
        form = ExerciseEntryForm(request.POST, fields=fields, instance=exercise_entry)
        if form.is_valid():
            # Save the edited exercise entry
            exercise_entry = form.save()

            logger.info("Exercise entry with id: %s edited successfully.", pk)

            if "save_and_add_another" in request.POST:
                # Redirect to the same page for adding another entry
                return redirect(
                    "exercise_entry",
                    workout_id=exercise_entry.workout.id,
                    exercise_id=exercise_entry.exercise.id,
                )
            else:
                # Redirect to exercise detail page
                return redirect("workout_detail", pk=exercise_entry.workout.id)
    else:
        form = ExerciseEntryForm(fields=fields, instance=exercise_entry)

    return render(
        request,
        "activityLogger/exercise_entry.html",
        {
            "form": form,
            "exercise": exercise_entry.exercise,
            "workout": exercise_entry.workout,
        },
    )


@login_required
def exercise_entry_delete(request, pk):
    """
    View for deleting an exercise entry.

    This view allows authenticated users to delete an existing exercise entry.
    Only the owner of the exercise entry can delete it.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the exercise entry to delete.

    Returns:
        HttpResponseRedirect: Redirects to the workout detail page after deleting the exercise entry.
    """
    exercise_entry = get_object_or_404(ExerciseEntry, pk=pk)

    # Check if the user is the owner of the exercise entry
    if exercise_entry.user == request.user:
        logger.info("Exercise entry with id: %s deleted successfully.", pk)
        exercise_entry.delete()
    else:
        logger.warning("Unauthorized attempt to delete exercise entry with id: %s", pk)

    return redirect("workout_detail", exercise_entry.workout.id)


@login_required
@staff_member_required
def exercise_delete(request, pk):
    """
    View for deleting an exercise.

    This view allows staff members to delete an existing exercise.
    Only staff members can access this view.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the exercise to delete.

    Returns:
        HttpResponseRedirect: Redirects to the exercise list page after deleting the exercise.
    """
    exercise = get_object_or_404(BaseExercise, pk=pk)

    logger.info("Exercise with id: %s deleted successfully by staff member.", pk)

    exercise.delete()
    return redirect("exercise_list")


def get_exercise_string(workout):
    """
    Get a string representation of exercises in a workout.

    Args:
        workout (Workout): The workout instance.

    Returns:
        str: A comma-separated string of exercise names and equipment types.
    """
    workout_exercises = WorkoutExercise.objects.filter(workout=workout)
    exercise_strings = []

    for workout_exercise in workout_exercises:
        exercise_name = workout_exercise.exercise.name
        exercise_equipment = (
            workout_exercise.exercise.get_equipment_display()
        )  # Get the display value of the equipment choice
        exercise_string = f"{exercise_name} ({exercise_equipment})"
        exercise_strings.append(exercise_string)

    return ", ".join(exercise_strings)


@login_required
def exercise_workout_list(request,pk):
    workouts = Workout.objects.filter(user=request.user)
    if not workouts.exists():
        return redirect("workout_list")
    return render(request, "activityLogger/exercise_workout_list.html", {"workouts": workouts, "exercise_id":pk})


@login_required
def exercise_add_workout(request,exercise_id, workout_id):
    exercise = get_object_or_404(BaseExercise,pk=exercise_id)
    workout = get_object_or_404(Workout,pk=workout_id)

    if workout.user != request.user:
        return redirect("home")
    
    if not WorkoutExercise.objects.filter(workout=workout, exercise=exercise).exists():
        WorkoutExercise.objects.create(workout=workout, exercise=exercise)
        
    return redirect("workout_detail",workout_id)



# @login_required
# def download_exercise_pdf(request, pk):
#     """
#     Generate a PDF containing exercise data for a specific workout.

#     This function retrieves exercise data for a specific workout, aggregates it,
#     and generates a PDF containing the aggregated data.

#     Args:
#         request: HttpRequest object.
#         pk: Primary key of the BaseExercise object.

#     Returns:
#         HttpResponse: Response containing the generated PDF.

#     Raises:
#         Http404: If the requested workout does not exist or the user does not own it.
#     """
#     # Retrieve workout object and check user ownership
#     exercise = get_object_or_404(BaseExercise, pk=pk)
    
#     interval_value = timedelta(hours=0, minutes=0,seconds=0)

#     entries = ExerciseEntry.objects.filter(exercise=exercise, user=request.user).annotate(
#         year=TruncYear('created'),
#         month=TruncMonth('created')
#     ).values(
#         'year', 'month'
#     ).annotate(
#         sum_repetitions=Coalesce(Sum(
#             Case(
#                 When(exercise__equipment='Bodyweight', then=F('repetitions')),
#                 default=Value(0),
#                 output_field=IntegerField(),
#             )
#         ), 0),
#         sum_cardio_duration=Coalesce(Sum(
#             Case(
#                 When(exercise__equipment='Cardio', then=F('cardio_duration')),
#                 default=Value(interval_value, output_field=DurationField()),
#                 output_field=DurationField()
#             )   
#         ), Value(interval_value, output_field=DurationField())),

#         sum_repetition_weight=Coalesce(Sum(
#             Case(
#                 When(exercise__equipment__in=['Barbell', 'Dumbbell', 'Machine', 'Bands'], then=F('weight')*F('repetitions')),
#                 default=Value(0),
#                 output_field=FloatField()
#             )
#         ), 0.0)
#     ).order_by('-year', '-month')

#     today = date.today()
#     if not entries.exists():
#         return redirect('exercise_detail',pk)

#     # Render the HTML content from the new template
#     html_content = render_to_string(
#         "activityLogger/exercise_pdf_template.html",
#         {"exercise": exercise, "today": today,"entries":entries},
#     )
#     # Set options for pdfkit (optional)
#     options = {
#         "page-size": "A4",
#         "margin-top": "0.75in",
#         "margin-right": "0.75in",
#         "margin-bottom": "0.75in",
#         "margin-left": "0.75in",
#         "encoding": "UTF-8",
#         "enable-local-file-access": "",
#     }

#     # Convert HTML to PDF
#     pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

#     # Create an HTTP response with PDF as content type
#     response = HttpResponse(pdf, content_type="application/pdf")
#     response["Content-Disposition"] = (
#         f'attachment; filename="exercise_{exercise.name.replace(' ','_')}.pdf'
#     )

#     return response


@login_required
def workout_list(request):
    """
    View for listing user's workouts.

    This view retrieves the list of workouts for the authenticated user
    and generates a string representation of exercises in each workout.
    The generated exercise strings are added as attributes to the workout instances
    for display in the template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered template with the list of workouts.
    """
    logger.info("User accessed the workout list page.")

    workouts = Workout.objects.filter(user=request.user)

    for workout in workouts:
        workout.exercise_string = get_exercise_string(workout)

    return render(request, "activityLogger/workout_list.html", {"workouts": workouts})


@login_required
def workout_create(request):
    """
    View for creating a new workout.

    This view allows authenticated users to create a new workout by submitting a form
    with details such as workout name and selected exercises.
    Upon successful creation, the user is redirected to the workout detail page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the workout detail page after creating the workout.
    """
    if request.method == "POST":
        form = WorkoutForm(request.POST)
        if form.is_valid():
            new_workout = form.save(commit=False)
            new_workout.user = request.user
            new_workout.save()

            selected_exercises = form.cleaned_data["exercises"]
            for exercise in selected_exercises:
                WorkoutExercise.objects.create(workout=new_workout, exercise=exercise)

            logger.info("New workout '%s' created successfully.", new_workout.title)

            return redirect("workout_detail", new_workout.id)
    else:
        form = WorkoutForm()
    return render(request, "activityLogger/workout_create.html", {"form": form})


@login_required
def workout_detail(request, pk):
    """
    View for displaying the details of a workout.

    This view retrieves the details of a workout specified by its ID.
    It checks if the authenticated user is the owner of the workout.
    The view also retrieves the latest exercise statistics for each exercise in the workout.
    The retrieved data is passed to the template for rendering.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the workout to display.

    Returns:
        HttpResponse: The HTTP response containing the rendered template with the workout details.
    """
    logger.info("User accessed the workout detail page for workout with id: %s", pk)

    workout = get_object_or_404(Workout, pk=pk)
    if workout.user != request.user:
        logger.warning(
            "Unauthorized access attempt to workout detail page for workout with id: %s",
            pk,
        )
        return redirect("workout_list")

    # Retrieve exercises associated with the workout
    workout_exercises = WorkoutExercise.objects.filter(workout=workout)

    exercises_stat = {}

    # Retrieve latest exercise statistics for each exercise in the workout
    for workout_exercise in workout_exercises:
        latest_exercise_stat = ExerciseEntry.objects.filter(
            exercise=workout_exercise.exercise, user=request.user
        ).order_by("-created")[:5]
        exercises_stat[workout_exercise] = latest_exercise_stat
    weight = ["Barbell", "Dumbbell", "Machine", "Bands"]

    context = {"workout": workout, "exercises_stat": exercises_stat, "weight": weight}

    return render(request, "activityLogger/workout_detail.html", context)


@login_required
def workout_edit(request, pk):
    """
    View for editing a workout.

    This view allows authenticated users to edit an existing workout by submitting a form
    with updated details such as workout name and selected exercises.
    Only the owner of the workout can edit it.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the workout to edit.

    Returns:
        HttpResponseRedirect: Redirects to the workout detail page after editing the workout.
    """
    workout = get_object_or_404(Workout, pk=pk)

    # Check if the user is the owner of the workout
    if workout.user != request.user:
        logger.warning("Unauthorized attempt to edit workout with id: %s", pk)
        return redirect("home")

    if request.method == "POST":
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()

            selected_exercises = form.cleaned_data["exercises"]
            workout.exercises.set(selected_exercises)

            logger.info("Workout with id: %s edited successfully.", pk)
            return redirect("workout_detail", workout.id)
    else:
        form = WorkoutForm(instance=workout)
    return render(
        request,
        "activityLogger/workout_edit.html",
        {"form": form, "workout_id": workout.id},
    )


@login_required
def workout_exercise_delete(request, pk):
    """
    View for deleting a workout exercise.

    This view allows authenticated users to delete a workout exercise from a workout.
    Only the owner of the workout can delete a workout exercise.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the workout exercise to delete.

    Returns:
        HttpResponseRedirect: Redirects to the workout detail page after deleting the workout exercise.
    """
    workout_exercise = get_object_or_404(WorkoutExercise, exercise__id=pk)

    if workout_exercise.workout.user == request.user:
        logger.info("Workout exercise with id: %s deleted successfully.", pk)
        workout_exercise.delete()
    else:
        logger.warning(
            "Unauthorized attempt to delete workout exercise with id: %s", pk
        )

    return redirect("workout_detail", workout_exercise.workout.id)


@login_required
def workout_delete(request, pk):
    """
    View for deleting a workout.

    This view allows authenticated users to delete an existing workout.
    Only the owner of the workout can delete it.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the workout to delete.

    Returns:
        HttpResponseRedirect: Redirects to the workout list page after deleting the workout.
    """
    workout = get_object_or_404(Workout, pk=pk)

    if workout.user == request.user:
        logger.info("Workout with id: %s deleted successfully.", pk)
        workout.delete()
    else:
        logger.warning("Unauthorized attempt to delete workout with id: %s", pk)

    return redirect("workout_list")


# @login_required
# def download_workout_pdf(request, pk):
#     # Retrieve workout object and check user ownership
#     workout = get_object_or_404(Workout, pk=pk)
#     if workout.user != request.user:
#         return redirect("Home")

#     # Retrieve workout details and exercise statistics
#     workout_exercises = WorkoutExercise.objects.filter(workout=workout)
#     exercises_stat = {}
#     for workout_exercise in workout_exercises:
#         latest_exercise_stat = ExerciseEntry.objects.filter(
#             exercise=workout_exercise.exercise, user=request.user
#         ).order_by("-created")[:5]
#         exercises_stat[workout_exercise] = latest_exercise_stat
#     weight = ["Barbell", "Dumbbell", "Machine", "Bands"]


#     # Render the HTML content from the new template
#     html_content = render_to_string(
#         "activityLogger/workout_pdf_template.html",
#         {"workout": workout, "exercises_stat": exercises_stat,"weight": weight},
#     )

#     # Set options for pdfkit (optional)
#     options = {
#         "page-size": "A4",
#         "margin-top": "0.75in",
#         "margin-right": "0.75in",
#         "margin-bottom": "0.75in",
#         "margin-left": "0.75in",
#         "encoding": "UTF-8",
#         "enable-local-file-access": "",
#     }

#     # Convert HTML to PDF
#     pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

#     # Create an HTTP response with PDF as content type
#     response = HttpResponse(pdf, content_type="application/pdf")
#     response["Content-Disposition"] = (
#         f'attachment; filename="workout_{workout.title.replace(' ','_')}.pdf'
#     )

#     return response


@login_required
def challenge_list(request):
    """
    View for listing challenges.

    This view retrieves all challenges and user-specific challenges.
    It separates challenges into two categories: 'challenges' and 'not_ready'.
    Challenges without setup goals are categorized as 'not_ready'.
    The view passes the data to the template for rendering.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered template with the list of challenges.
    """
    logger.info("User accessed the challenge list page.")

    all_challenges = Challenge.objects.all()
    user_challenges = UserChallenge.objects.filter(user=request.user)
    today = date.today()
    not_ready = []
    challenges = []

    # Separate challenges into 'not_ready' and 'challenges' categories
    for challenge in all_challenges:
        if (
            (challenge.repetitions is None)
            and (challenge.weight is None)
            and (challenge.cardio_duration is None)
        ):
            # If the challenge doesn't have setup goals, categorize it as 'not_ready'
            not_ready.append(challenge)
        else:
            # Otherwise, categorize it as 'challenges'
            challenges.append(challenge)

    # Create a dictionary to store user-specific challenge IDs for quick lookup
    user_challenge_dict = {uc.challenge.id for uc in user_challenges}

    return render(
        request,
        "activityLogger/challenge_list.html",
        {
            "challenges": challenges,
            "today": today,
            "user_challenge_dict": user_challenge_dict,
            "not_ready": not_ready,
        },
    )


@login_required
@staff_member_required
def challenge_create(request):
    """
    View for creating a challenge.

    This view allows staff members to create a new challenge by submitting a form
    with details such as title, description, exercise, start date, and end date.
    Upon successful creation, the user is redirected to the challenge statistics page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the challenge statistics page after creating the challenge.
    """
    if request.method == "POST":
        form = ChallengeForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            exercise = form.cleaned_data["exercise"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            challenge = Challenge.objects.create(
                title=title,
                description=description,
                exercise=exercise,
                start_date=start_date,
                end_date=end_date,
            )

            logger.info("Challenge '%s' created successfully by staff member.", title)

            return redirect("challenge_stat", challenge.id)
    else:
        form = ChallengeForm()
    return render(request, "activityLogger/challenge_create.html", {"form": form})


@login_required
@staff_member_required
def challenge_stat(request, pk):
    """
    View for updating challenge statistics.

    This view allows staff members to update the statistics of a challenge by submitting a form
    with updated details such as exercise statistics (repetitions, weight, or cardio duration).
    The view determines the exercise type and available fields based on the equipment used.
    Upon successful update, the user is redirected to the challenge detail page.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the challenge to update.

    Returns:
        HttpResponseRedirect: Redirects to the challenge detail page after updating the statistics.
    """
    challenge = Challenge.objects.get(pk=pk)

    if not challenge.exercise:
        # Handle case where exercise is not assigned to the challenge
        logger.warning("No exercise assigned to the challenge with id: %s", pk)
        return redirect("home")

    weight_equipment_choices = ["Barbell", "Dumbbell", "Machine", "Bands"]
    # Determine exercise type and fields
    if challenge.exercise.equipment == "Bodyweight":
        fields = ["repetitions"]
    elif challenge.exercise.equipment in weight_equipment_choices:
        fields = ["weight"]
    elif challenge.exercise.equipment == "Cardio":
        fields = ["cardio_duration"]
    else:
        # Handle unsupported exercise type
        logger.warning(
            "Unsupported exercise type encountered in challenge with id: %s", pk
        )
        return redirect("home")

    if request.method == "POST":
        form = ChallengeStatForm(request.POST, fields=fields, instance=challenge)
        if form.is_valid():
            form.save()
            logger.info("Statistics updated successfully for challenge with id: %s", pk)
            return redirect("challenge_detail", challenge.id)
    else:
        form = ChallengeStatForm(fields=fields, instance=challenge)

    return render(
        request,
        "activityLogger/challenge_stat.html",
        {"form": form, "challenge": challenge},
    )


@login_required
def challenge_detail(request, pk):
    """
    View for displaying challenge details and progress.

    This view retrieves the details of a challenge including its associated exercise,
    user-specific challenge entry, exercise entries within the challenge duration,
    and calculates the progress based on the exercise type and user entries.
    The progress is calculated as a percentage of the goal set for the challenge.
    The view passes the data to the template for rendering.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the challenge to display details.

    Returns:
        HttpResponse: The HTTP response containing the rendered template with the challenge details.
    """


    challenge = Challenge.objects.get(pk=pk)

    # Retrieve user-specific challenge entry if exists
    user_challenge = UserChallenge.objects.filter(
        user=request.user, challenge=challenge
    )

    # Retrieve exercise entries within the challenge duration
    exercise_entries = ExerciseEntry.objects.filter(
        created__gte=challenge.start_date,
        created__lte=challenge.end_date,
        exercise=challenge.exercise,
        user=request.user,
    )
    
    today = date.today()
    weight_equipment_choices = ["Barbell", "Dumbbell", "Machine", "Bands"]
    progress = None
    end_goal = 0
    stat = 0

    # Calculate progress based on the exercise type and user entries
    if challenge.exercise.equipment in weight_equipment_choices:
        if challenge.weight:
            end_goal = challenge.weight
            for entry in exercise_entries:
                if entry.weight is not None and entry.repetitions is not None:
                    stat += entry.weight * entry.repetitions
            progress = min(int((stat / end_goal) * 100), 100)

    if challenge.exercise.equipment == "Bodyweight":
        if challenge.repetitions:
            end_goal = challenge.repetitions
            for entry in exercise_entries:
                if entry.repetitions is not None:
                    stat += entry.repetitions
            progress = min(int((stat / end_goal) * 100), 100)

    if challenge.exercise.equipment == "Cardio":
        if challenge.cardio_duration:
            end_goal = challenge.cardio_duration.total_seconds()
            for entry in exercise_entries:
                if entry.cardio_duration is not None:
                    stat += entry.cardio_duration.total_seconds()
            progress = min(int((stat / end_goal) * 100), 100)
            stat = timedelta(seconds=stat)
            end_goal = timedelta(seconds=end_goal)

    logger.info("Challenge detail page accessed for challenge with id: %s", pk)

    return render(
        request,
        "activityLogger/challenge_detail.html",
        {
            "challenge": challenge,
            "user_challenge": user_challenge,
            "today": today,
            "exercise_entries": exercise_entries,
            "progress": progress,
            "end_goal": end_goal,
            "stat": stat,
        },
    )


@login_required
@staff_member_required
def challenge_edit(request, pk):
    """
    View for editing challenge details.

    This view allows staff members to edit the details of a challenge by submitting a form
    with updated information such as title, description, start date, end date, and exercise.
    If the exercise is changed, any existing setup goals (repetitions, weight, cardio duration)
    are reset to None. Upon successful update, the user is redirected to the challenge detail page.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the challenge to edit.

    Returns:
        HttpResponseRedirect: Redirects to the challenge detail page after updating the challenge details.
    """
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == "POST":
        form = ChallengeForm(request.POST, instance=challenge)
        prev_exercise = challenge.exercise.id
        if form.is_valid():
            challenge.title = form.cleaned_data["title"]
            challenge.description = form.cleaned_data["description"]
            challenge.start_date = form.cleaned_data["start_date"]
            challenge.end_date = form.cleaned_data["end_date"]
            exercise = form.cleaned_data["exercise"]

            if exercise.id != prev_exercise:
                # Reset setup goals if exercise is changed
                challenge.repetitions = None
                challenge.weight = None
                challenge.cardio_duration = None

            challenge.exercise = exercise
            challenge.save()

            # Log the successful update
            logger.info("Challenge details edited for challenge with ID: %s", pk)

            return redirect("challenge_detail", challenge.id)
    else:
        form = ChallengeForm(instance=challenge)
    return render(
        request,
        "activityLogger/challenge_edit.html",
        {"form": form, "challenge_id": challenge.id},
    )


@login_required
def challenge_join(request, pk):
    """
    View for joining a challenge.

    This view allows users to join a challenge if it is currently ongoing (between start and end dates).
    Once a user joins a challenge, a UserChallenge object is created to indicate their participation.
    If the user is already part of the challenge, they are redirected to the challenge detail page.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the challenge to join.

    Returns:
        HttpResponseRedirect: Redirects to the challenge detail page after joining the challenge.
    """
    challenge = get_object_or_404(Challenge, pk=pk)
    user_challenge = UserChallenge.objects.filter(
        user=request.user, challenge=challenge
    )
    today = date.today()

    if user_challenge:
        # Log if the user is already part of the challenge
        logger.info("User already joined challenge with ID: %s", pk)
        return redirect("challenge_detail", pk)

    if today >= challenge.start_date and today <= challenge.end_date:
        # Create UserChallenge entry if challenge is ongoing
        UserChallenge.objects.create(user=request.user, challenge=challenge)
        # Log the successful join
        logger.info("User joined challenge with ID: %s", pk)
    return redirect("challenge_detail", pk)


@login_required
def challenge_leave(request, pk):
    """
    View for leaving a challenge.

    This view allows users to leave a challenge they are currently participating in.
    Users can only leave the challenge if they are already part of it and if the challenge
    is ongoing (between start and end dates). Upon leaving the challenge, the UserChallenge
    object associated with the user and challenge is deleted.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the challenge to leave.

    Returns:
        HttpResponseRedirect: Redirects to the challenge detail page after leaving the challenge.
    """
    challenge = get_object_or_404(Challenge, pk=pk)
    user_challenge = UserChallenge.objects.filter(
        user=request.user, challenge=challenge
    )
    today = date.today()
    if user_challenge and today >= challenge.start_date and today <= challenge.end_date:
        # Log when a user leaves a challenge
        logger.info("User left challenge with ID: %s", pk)
        user_challenge.delete()
    return redirect("challenge_detail", pk)


@login_required
@staff_member_required
def challenge_delete(request, pk):
    """
    View for deleting a challenge.

    This view allows staff members to delete a challenge. Upon deletion, the challenge
    and all associated data, including UserChallenge entries, are permanently removed
    from the database.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the challenge to delete.

    Returns:
        HttpResponseRedirect: Redirects to the home page after deleting the challenge.
    """
    challenge = get_object_or_404(Challenge, pk=pk)
    challenge.delete()
    logger.info(
        f"Challenge with ID {pk} deleted successfully by staff member {request.user.username}"
    )
    return redirect("home")


@login_required
@staff_member_required
def stats(request):
    """
    View for displaying statistics.

    This view calculates and displays statistics related to challenges and exercises.
    It retrieves data such as the number of participants in challenges and exercises,
    calculates percentages, and prepares data for visualization.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the stats page with calculated statistics.
    """
    # Query challenges with the count of participants
    challenges_with_participants_count = Challenge.objects.annotate(
        num_participants=Count("userchallenge")
    )

    # Calculate the total number of participants across all challenges
    total_participants = challenges_with_participants_count.aggregate(
        total_participants=Sum("num_participants")
    )["total_participants"]

    # Process data for top 5 challenges
    data_challenge = []
    colors_challenge = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    labels_challenge = []
    if total_participants:
        top_5_challenges = challenges_with_participants_count.order_by(
            "-num_participants"
        )[:5]

        for challenge in top_5_challenges:
            percentage = round((challenge.num_participants / total_participants) * 100)
            data_challenge.append(percentage)
            labels_challenge.append(challenge.title.replace(" ", "_"))

    # Query top 5 exercises with the count of participants
    top_5_exercises = (
        ExerciseEntry.objects.values("exercise__name")
        .annotate(num_participants=Count("user", distinct=True))
        .order_by("-num_participants")[:5]
    )

    # Process data for top 5 exercises
    data_exercise = []
    colors_exercise = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    labels_exercise = []

    total_exercise_participants = ExerciseEntry.objects.aggregate(
        total_participants=Count("user", distinct=True)
    )["total_participants"]

    if total_exercise_participants:
        for exercise in top_5_exercises:
            percentage = round(
                (exercise["num_participants"] / total_exercise_participants) * 100
            )
            data_exercise.append(percentage)
            labels_exercise.append(exercise["exercise__name"].replace(" ", "_"))

    context = {
        "data_challenge": data_challenge,
        "colors_challenge": colors_challenge,
        "labels_challenge": labels_challenge,
        "data_exercise": data_exercise,
        "colors_exercise": colors_exercise,
        "labels_exercise": labels_exercise,
    }

    logger.info("Statistics retrieved successfully")
    return render(request, "activityLogger/stats.html", context)
