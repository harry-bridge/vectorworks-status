from django.db import models
from django.utils import timezone


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
        # return self.test_ran_at

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

        return info

    def __str__(self):
        return f"{self.product}, {self.in_use} in use at {self.last_updated}"


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