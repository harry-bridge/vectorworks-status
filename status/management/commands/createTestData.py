import random
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta

from django.conf import settings

from status import models

# Use the same seed so the random data is repeatable
random.seed = "SeedMyRandomness"

class Command(BaseCommand):
    help = 'Creates a super user'

    def handle(self, *args, **options):
        if not (settings.DEBUG or settings.STAGING):
            raise CommandError('You cannot run this command in production')

        self.create_test_license_usage_data()

    def create_test_license_usage_data(self):
        for _ in range(20):
            models.UserLicenseUsage.objects.create(
                user_name=random.choice(['Ethyl', 'Athena', 'Kellia', 'Vincent', 'Keelia', 'Jon', 'Willette', 'Rachelle', 'Colline', 'Tammy']),
                host_name='fake_host',
                version=2024,
                checkout_stamp=timezone.now() - timedelta(days=random.randint(-24, 0), hours=random.randint(-8, 0), minutes=random.randint(-60, 0))
            )
