from django.contrib import admin
from status import models


@admin.register(models.ScraperSettings)
class ScraperSettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return self.model.objects.count() == 0


@admin.register(models.UptimeTest)
class UptimeTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'hostname', 'port', 'test_type']


@admin.register(models.UptimeHistory)
class UptimeHistoryAdmin(admin.ModelAdmin):
    list_display = ['test', 'uptime_result', 'test_ran_at']

    # def get_readonly_fields(self, request, obj=None):
    #     return [f.name for f in self.model._meta.fields]
