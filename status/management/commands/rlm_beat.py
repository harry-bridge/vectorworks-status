from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions
from django.conf import settings

from status.rlm_scraper import RLMScrape


class Command(BaseCommand):
    help = "Runs the RLM beat task from rlm scraper, this task is usually ran via a cron job"

    def handle(self, *args, **options):
        RLMScrape().beat_task()
        # print("Done")
