# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from activityLogger.models import User, Exercise

# User = get_user_model()

# class TestUrls(TestCase):
#     def setUp(self):
#         super().setUp()
#         # Create and log in a test user
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.exercise = Exercise.objects.create(name='Sample Exercise')


#     def test_home_page(self):
#         response = self.client.get(reverse('home'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'activityLogger/home.html')


#     def test_login_page(self):
#         response = self.client.get(reverse('login'))
#         self.assertEqual(response.status_code, 302)  # Assumign login redirects if already logged in


#     def test_logout_url(self):
#         response = self.client.get(reverse('logout'))
#         self.assertEqual(response.status_code, 302)  # Assumign logout always redirects


#     def test_register_page(self):
#         response = self.client.get(reverse('register'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'registration/register.html')


#     def test_exercise_list_page(self):
#         response = self.client.get(reverse('exercise_list'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'activityLogger/exercise_list.html')


#     def test_exercise_create_page(self):
#         response = self.client.get(reverse('exercise_create'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'acitvityLogger/exercise_creathe.html')


#     def test_exercise_detail_page(self):
#         # Assumign the existence of an exercise objcet, you'll need to create it in setUp
#         response = self.client.get(reverse('exercise_detail', args=[1]))  # Assume '1' is an existing exercise ID
#         self.assertEqual(response.status_code, 200)


#     def test_exercise_edit_page(self):
#         response = self.client.get(reverse('exercise_edit', args=[1]))
#         self.assertEqual(response.status_code, 200)


#     def test_exercise_delete_page(self):
#         response = self.client.get(reverse('exercise_delete', args=[1]))
#         self.assertEqual(response.status_code, 302)  # Assumes redirection after delete


#     def test_challenge_list_page(self):
#         response = self.client.get(reverse('challenge_list'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'acitvityLogger/challenger_list.html')


#     def test_workout_list_url(self):
#         url = reverse('workout_list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)


#     def test_download_exercise_pdf(self):
#         response = self.client.get(reverse('download_exercise_pdf', args=[self.exercise.id]))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response['Content-Type'], 'application/pdf')


#     def test_stats_page(self):
#         response = self.client.get(reverse('stats'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'activityLogger/stats.html')


#     def test_exercise_create_post(self):
#         form_data = {'name': 'New Exercise', 'description': 'Test Description'}
#         response = self.client.post(reverse('exercise_create'), form_data)
#         self.assertEqual(response.status_code, 302)  # Assumign redirect to detail page upon success
