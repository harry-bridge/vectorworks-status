from django.apps import AppConfig
from django.core.exceptions import AppRegistryNotReady
import time

import status.tasks

# while 1:
#     try:
#         import status.port_check
#         print('Apps not ready')
#         break
#     except AppRegistryNotReady:
#         pass
#
#     time.sleep(1)


class VectorworksStatusConfig(AppConfig):
    """
    This is run when the server is loaded and adds all the tasks to the scheduler
    """
    name = "VectorworksStatus"

    def ready(self):
        self.clear_sheduled_tasks()
        self.clear_queue()
        self.start_background_tasks()

    def clear_queue(self):
        try:
            from django_q.models import OrmQ
        except AppRegistryNotReady:
            return

        OrmQ.objects.all().delete()

    def clear_sheduled_tasks(self):
        try:
            from django_q.models import Schedule
        except AppRegistryNotReady:
            return

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
