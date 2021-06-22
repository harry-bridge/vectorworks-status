import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import mechanize
from django.conf import settings
# from pathlib import Path
# import csv
# from datetime import datetime
import time
from django.utils import timezone

from status import models


class RLMScrape:
    def __init__(self):
        self._site_location = models.ScraperSettings().get_settings().rlm_address
        self._br = mechanize.Browser()
        self._br.set_handle_robots(False)

    @staticmethod
    def _get_last_updated_time():
        # return datetime.now().strftime("%H:%M %d/%b/%Y")
        return timezone.now()

    def _scrape_rlm_for_users(self):
        try:
            response = self._br.open(urljoin(self._site_location, 'goforms/login_process'), timeout=5)
            self._br._factory.is_html = True
        except Exception as exc:
            print("Browser open failed with exception: {}".format(exc))
            self._server_online = False
            return

        if response.code != 200:
            return

        self._br.form = list(self._br.forms())[0]
        user = self._br.form.find_control("username")
        user.value = settings.RLM_USER
        passw = self._br.form.find_control("password")
        passw.value = settings.RLM_PASS
        resp = self._br.submit()
        # print(resp.read())

        response = self._br.open(urljoin(self._site_location, 'goforms/rlmstat'))
        # print(response.read())
        # print(br.forms()[2])
        self._br.form = list(self._br.forms())[2]
        resp = self._br.submit()
        # print(resp.read())

        soup = BeautifulSoup(resp.read(), 'html.parser')
        tables = soup.findAll("table")
        pool_table = tables[2]

        licence_info = dict()
        for row in pool_table.findAll("tr")[1:-1]:
            col = row('td')
            licence_info[col[0].text.strip()] = dict()
            _info = licence_info[col[0].text.strip()]
            _info['ver'] = col[2].text.strip()
            _info['count'] = col[4].text.strip()
            _info['inuse'] = col[6].text.strip()

        print(licence_info)

        for product, info in licence_info.items():
            defaults = {
                'count': info['count'],
                'in_use': info['inuse'],
                'last_updated': timezone.now()
            }

            models.RlmInfo.objects.update_or_create(product=product, version=info['ver'], defaults=defaults)

    def beat_task(self):
        self._scrape_rlm_for_users()


if __name__ == '__main__':
    app = RLMScrape()
    app._scrape_rlm_for_users()
