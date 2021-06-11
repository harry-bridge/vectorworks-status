from django.core.management.base import BaseCommand, CommandError

from status.port_check import PortCheck

up = 0
down = 1


class Command(BaseCommand):
    def handle(self, *args, **options):
        PortCheck().check_ports()
