from django.apps import AppConfig
from django.core.exceptions import AppRegistryNotReady
from django.db import connection

import status.tasks


class VectorworksStatusConfig(AppConfig):
    """
    This is run when the server is loaded and adds all the tasks to the scheduler
    """
    name = "VectorworksStatus"

    def ready(self):
        self.clear_sheduled_tasks()
        self.clear_queue()
        self.start_background_tasks()

    @staticmethod
    def db_table_exists(table_name):
        return table_name in connection.introspection.table_names()

    def clear_queue(self):
        try:
            from django_q.models import OrmQ
        except AppRegistryNotReady:
            return

        if self.db_table_exists('django_q_ormq'):
            if OrmQ.objects.all().count():
                OrmQ.objects.all().delete()

    def clear_sheduled_tasks(self):
        try:
            from django_q.models import Schedule
        except AppRegistryNotReady:
            return

        if self.db_table_exists('django_q_schedule'):
            if Schedule.objects.all().count():
                Schedule.objects.all().delete()

    def start_background_tasks(self):
        try:
            from django_q.models import Schedule
        except AppRegistryNotReady:
            return

        status.tasks.schedule_task(
            'status.tasks.delete_successful_tasks',
            schedule_type=Schedule.DAILY,
        )

        status.tasks.schedule_task(
            'status.tasks.heartbeat',
            schedule_type=Schedule.MINUTES,
            minutes=5
        )

        status.tasks.schedule_task(
            'status.tasks.check_ports_q_task',
            schedule_type=Schedule.MINUTES,
            minutes=5
        )

        status.tasks.schedule_task(
            'status.tasks.scrape_rlm_q_task',
            schedule_type=Schedule.MINUTES,
            minutes=5
        )

        status.tasks.schedule_task(
            'status.tasks.delete_old_uptime_history',
            schedule_type=Schedule.DAILY
        )
