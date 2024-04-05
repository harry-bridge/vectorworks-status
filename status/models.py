from django.db import models
from django.db.models import Count, Max
from django.utils import timezone
from datetime import datetime


class UptimeTest(models.Model):
    TEST_TYPE_CHOICES = (
        (0, 'Internal'),
        (1, 'External')
    )

    name = models.CharField(max_length=256)
    hostname = models.CharField(max_length=50, help_text="IP address for internal tests and hostname for external tests")
    port = models.CharField(max_length=50, blank=True, null=True)
    check_interval = models.IntegerField(help_text="Check interval in minutes")
    test_type = models.IntegerField(choices=TEST_TYPE_CHOICES)

    def get_last_uptime(self):
        return self.uptimehistory_set.all().order_by('-test_ran_at').first()

    def all_tests_up(self):
        all_up = True
        for test in UptimeTest.objects.all():
            if test.get_last_uptime().get_status == 'down':
                all_up = False

        return all_up

    def get_all_internal_tests(self):
        return UptimeTest.objects.all().filter(test_type=0)

    def get_all_external_tests(self):
        return UptimeTest.objects.all().filter(test_type=1)

    def __str__(self):
        return self.name


def _get_age_info(age: float, minutes_for_warning=3):
    hours, hr = divmod(age, 60 * 60)
    mins, secs = divmod(hr, 60)

    text_class = 'text-success'
    if age > 60 * 60:
        age_formatted = "{}h {}m".format(int(hours), int(mins))
        text_class = 'text-danger'
    elif age > 60:
        age_formatted = "{}m".format(int(mins))
        # a message that is some minutes old gets yellow text to indicate it is a bit out of date
        if age > minutes_for_warning * 60:
            text_class = 'text-secondary'
    else:
        age_formatted = "{}s".format(int(secs))

    return {"text_class": text_class, "age_formatted": age_formatted}


class UptimeHistory(models.Model):
    class Meta:
        verbose_name_plural = 'Uptime history'

    UPTIME_RESULT_CHOICES = (
        (0, 'Up'),
        (1, 'Down')
    )

    test_ran_at = models.DateTimeField(default=timezone.now)
    test = models.ForeignKey(to=UptimeTest, on_delete=models.CASCADE)
    uptime_result = models.IntegerField(choices=UPTIME_RESULT_CHOICES)
    server_response = models.CharField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    @property
    def get_status(self):
        return self.get_uptime_result_display().lower()

    @property
    def last_updated(self):
        ran_at = timezone.localtime(self.test_ran_at)
        return ran_at.strftime("%H:%M, %d %b %Y")

    @property
    def age_text_col(self):
        age = (timezone.now() - self.test_ran_at).total_seconds()
        return _get_age_info(age)['text_class']

    @property
    def age_str(self):
        age = (timezone.now() - self.test_ran_at).total_seconds()
        if age < 2 * 60 * 60:
            # less than 2 hours old then return age string
            return "{} ago".format(_get_age_info(age)['age_formatted'])
        else:
            return self.test_ran_at.strftime("%H:%M, %d %b")

    def __str__(self):
        return self.test.name + " - " + self.get_uptime_result_display()


class RlmInfo(models.Model):
    """
    Contains the results for scraping the RLM server
    """
    class Meta:
        verbose_name = 'RLM info'
        verbose_name_plural = 'RLM info'

    product = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    count = models.IntegerField()
    in_use = models.IntegerField()
    last_updated = models.DateTimeField(default=timezone.now)

    def get_latest_info_dict(self):
        info = dict()
        for product in RlmInfo.objects.all().order_by('product'):
            info[product.product] = dict()
            prod = info[product.product]
            prod['product'] = product.product
            prod['ver'] = product.version
            prod['count'] = product.count
            prod['inuse'] = product.in_use

            if product.in_use == product.count:
                prod['inuse_text_class'] = 'text-danger'
            elif product.in_use >= int(product.count * 0.8):
                prod['inuse_text_class'] = 'text-secondary'
            else:
                prod['inuse_text_class'] = ''

            age = (timezone.now() - product.last_updated).total_seconds()
            age_info = _get_age_info(age)

            prod['text_class'] = age_info['text_class']
            prod['timedelta'] = age_info["age_formatted"]

        return info

    def __str__(self):
        return f"{self.product}, {self.in_use} in use at {self.last_updated}"


class UserLicenseUsage(models.Model):
    """
    Holds information about what users have checked out a license and when
    """
    class Meta:
        verbose_name = 'Licence Usage'
        verbose_name_plural = 'License Usages'

    user_name = models.CharField(max_length=100)
    host_name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    checkout_stamp = models.DateTimeField()

    @staticmethod
    def get_version_for_user_date(user, stamp):
        return UserLicenseUsage.objects.filter(user_name=user, checkout_stamp=stamp).first().version

    @staticmethod
    def top_users():
        return UserLicenseUsage.objects.values('user_name').annotate(use_count=Count('user_name'), last_checkout=Max('checkout_stamp')).order_by('-use_count')

    def __str__(self):
        return f"User: {self.user_name}, Host: {self.host_name} at {self.checkout_stamp.strftime('%d/%b/%Y %H:%M')}"


class ScraperSettings(models.Model):
    """
    Holds settings for the web scraper tasks
    """
    class Meta:
        verbose_name_plural = "Scraper settings"

    vectorworks_hostname = models.CharField(max_length=100)
    rlm_address = models.CharField(max_length=50)
    rlm_port = models.IntegerField()
    isv_port = models.IntegerField()

    def get_settings(self):
        return ScraperSettings.objects.all().first()

    def __str__(self):
        return "Scraper Settings"


class MaintenancePeriod(models.Model):
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    start_datetime = models.DateTimeField(default=timezone.now)
    default_end = timezone.now() + timezone.timedelta(hours=3)
    end_datetime = models.DateTimeField(default=default_end)

    @property
    def start_formatted(self):
        return self.start_datetime.strftime("%H:%M, %d %b")

    @property
    def end_formatted(self):
        return self.end_datetime.strftime("%H:%M, %d %b")

    @staticmethod
    def get_active_maintenance():
        return MaintenancePeriod.objects.all().filter(end_datetime__gte=timezone.now(), is_active=True).first()

    def __str__(self):
        return "Maintenance period at {}".format(self.start_datetime.strftime("%c"))
