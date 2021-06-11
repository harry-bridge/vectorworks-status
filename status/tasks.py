from django.core.exceptions import AppRegistryNotReady
from django.db.utils import OperationalError, ProgrammingError
from datetime import datetime, timedelta
from django.core.management import call_command

# from status.port_check import PortCheck
# from status import port_check
# import status.port_check


def schedule_task(taskname, **kwargs):
    """
    Create a scheduled task.
    If the task has already been scheduled, ignore!
    """

    # If unspecified, repeat indefinitely
    repeats = kwargs.pop('repeats', -1)
    kwargs['repeats'] = repeats

    try:
        from django_q.models import Schedule
    except AppRegistryNotReady:
        print("Could not start background tasks - App registry not ready")
        return

    try:
        # If this task is already scheduled, don't schedule it again
        # Instead, update the scheduling parameters
        if Schedule.objects.filter(func=taskname).exists():
            print(f"Scheduled task '{taskname}' already exists - updating!")

            Schedule.objects.filter(func=taskname).update(**kwargs)
        else:
            print(f"Creating scheduled task '{taskname}'")

            Schedule.objects.create(
                name=taskname,
                func=taskname,
                **kwargs
            )
    except (OperationalError, ProgrammingError):
        # Required if the DB is not ready yet
        pass


def heartbeat():
    """
    Simple task which runs at 5 minute intervals,
    so we can determine that the background worker
    is actually running.
    (There is probably a less "hacky" way of achieving this)?
    """

    try:
        from django_q.models import Success
        print("Could not perform heartbeat task - App registry not ready")
    except AppRegistryNotReady:
        return

    threshold = datetime.now() - timedelta(minutes=30)

    # Delete heartbeat results more than half an hour old,
    # otherwise they just create extra noise
    heartbeats = Success.objects.filter(
        func='VectorworksStatus.tasks.heartbeat',
        started__lte=threshold
    )

    heartbeats.delete()


def delete_successful_tasks():
    """
    Delete successful task logs
    which are more than a month old.
    """

    try:
        from django_q.models import Success
    except AppRegistryNotReady:
        print("Could not start background tasks - App registry not ready")
        return

    threshold = datetime.now() - timedelta(days=10)

    results = Success.objects.filter(
        started__lte=threshold
    )

    results.delete()


def check_ports_q_task():
    """
    Check all the ports needed are internally and externally accessible
    """
    try:
        from status.port_check import PortCheck
    except AppRegistryNotReady:
        print("Could not start background tasks - App registry not ready")
        return

    print('running port check')
    PortCheck().check_ports_multithread()
    # print("hello")


def scrape_rlm_q_task():
    """
    Scrape the RLM server for current count of licenses in use
    """
    try:
        from status.rlm_scraper import RLMScrape
        from django.conf import settings
        import os
    except AppRegistryNotReady:
        print("Could not start background tasks - App registry not ready")
        return

    print('running rlm beat')
    RLMScrape().beat_task()
