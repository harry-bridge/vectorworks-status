import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import mechanize
from django.conf import settings
from pathlib import Path
import csv
# from datetime import datetime
import time
from django.utils import timezone

from status import models


class RLMScrape:
    _log_location = settings.BASE_DIR / 'rlm_users.csv'
    _rlm_csv_headers = ['last_updated', 'product', 'ver', 'count', 'inuse']

    _server_log_location = Path.cwd() / 'rlm_server_info.csv'
    _server_csv_headers = ['last_updated', 'server_online', 'response_time']

    _server_online = False

    def __init__(self):
        self._site_location = models.ScraperSettings().get_settings().rlm_address
        # self._site_location = 'http://10.0.0.152:5054'
        self._br = mechanize.Browser()

    @staticmethod
    def _get_last_updated_time():
        # return datetime.now().strftime("%H:%M %d/%b/%Y")
        return timezone.now()

    def _check_server_online(self):
        response_time = None

        try:
            _start_time = time.time()
            response = self._br.open(urljoin(self._site_location, 'goforms/login_process'), timeout=2)
            _end_time = time.time()
            self._server_online = True
        except mechanize.HTTPError:
            self._server_online = False

        if self._server_online:
            if response.code != 200:
                self._server_online = False

            else:
                self._server_online = True

            response_time = "{:.2f}ms".format((_end_time-_start_time) * 1000)

        with open(self._server_log_location, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self._server_csv_headers)
            writer.writerow([self._get_last_updated_time(), self._server_online, response_time])

    def _scrape_rlm_for_users(self):
        # site_location = "http://10.0.0.152:5054/"

        # br = mechanize.Browser()
        # br.set_all_readonly(False)
        # br.set_handle_robots(False)
        # br.set_handle_refresh(False)

        try:
            response = self._br.open(urljoin(self._site_location, 'goforms/login_process'), timeout=5)
            self._br._factory.is_html = True
        except mechanize.HTTPError:
            self._server_online = False
            return

        if response.code != 200:
            return

        self._br.form = list(self._br.forms())[0]
        user = self._br.form.find_control("username")
        user.value = os.environ.get('RLM_USERNAME')
        passw = self._br.form.find_control("password")
        passw.value = os.environ.get('RLM_PASSWORD')
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

        with open(self._log_location, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self._rlm_csv_headers)

            for key, value in licence_info.items():
                writer.writerow([self._get_last_updated_time(), key, value['ver'], value['count'], value['inuse']])

        return licence_info

    def read_rlm_info_log(self):
        info = dict()

        if self._log_location.exists():
            with open(self._log_location, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    try:
                        info[row['product']] = {key: row[key] for key in self._rlm_csv_headers}
                    except KeyError:
                        info = {'error': 'Key not found in RLM log'}
                        return info

        return info

    def read_rlm_server_log(self):
        info = dict()

        if self._server_log_location.exists():
            with open(self._server_log_location, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    try:
                        info = {key: row[key] for key in self._server_csv_headers}
                    except KeyError:
                        info = {"error": "Key not found in server log"}
                        return info

        return info

    def beat_task(self):
        # self._check_server_online()
        self._scrape_rlm_for_users()


if __name__ == '__main__':
    app = RLMScrape()
    app._scrape_rlm_for_users()
