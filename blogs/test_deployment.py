from django.core.management import call_command
from django.test import TestCase, override_settings


class StaticFilesDeploymentTests(TestCase):
    @override_settings(DEBUG=False)
    def test_static_admin_assets_are_served_when_debug_is_disabled(self):
        call_command('collectstatic', interactive=False, verbosity=0)

        response = self.client.get('/static/admin/css/base.css')

        self.assertEqual(response.status_code, 200)
