from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserFlowTests(TestCase):
    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse('users:register'),
            {
                'username': 'blogger',
                'password1': 'complex-test-password-123',
                'password2': 'complex-test-password-123',
            },
        )

        self.assertRedirects(response, reverse('blogs:home'))
        self.assertTrue(get_user_model().objects.filter(username='blogger').exists())
        self.assertEqual(self.client.get(reverse('blogs:post_new')).status_code, 200)

    def test_logout_only_accepts_post(self):
        user = get_user_model().objects.create_user('logout-user', password='test-password')
        self.client.force_login(user)

        response = self.client.get(reverse('users:logout'))

        self.assertEqual(response.status_code, 405)
