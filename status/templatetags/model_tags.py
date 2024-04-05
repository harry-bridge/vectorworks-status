from django import template

register = template.Library()

from status import models

@register.simple_tag
def get_last_usage_version(user, stamp):
    return models.UserLicenseUsage.get_version_for_user_date(user, stamp)