from bs4 import BeautifulSoup
from urllib.parse import urljoin
import mechanize
from django.conf import settings
from datetime import datetime
from django.utils import timezone

from status import models


class RLMScrape:
    def __init__(self):
        self._site_location = models.ScraperSettings().get_settings().rlm_address
        self._br = mechanize.Browser()
        self._br.set_handle_robots(False)

    @staticmethod
    def _get_last_updated_time():
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
            _info['count'] = int(col[4].text.strip())
            _info['inuse'] = int(col[6].text.strip())

        # print(licence_info)

        for product, info in licence_info.items():
            defaults = {
                'count': info['count'],
                'in_use': info['inuse'],
                'last_updated': timezone.now()
            }

            models.RlmInfo.objects.update_or_create(product=product, version=info['ver'], defaults=defaults)

        # Get user info for licences in use
        # First submit the first 'usage' form from the licences table
        self._br.form = list(self._br.forms())[0]
        resp = self._br.submit()
        # print(resp.read())

        soup = BeautifulSoup(resp.read(), 'html.parser')
        users_table = soup.findAll("table")[0]

        users_info = list()
        for row in users_table.findAll("tr")[1:]:
            col = row('td')
            # Convert check out time from RLM to tz aware datetime
            out_time = datetime.strptime(col[9].text.strip(), "%m/%d %H:%M").replace(year=datetime.now().year)
            out_time = timezone.make_aware(out_time)

            _info = {
                "version": col[2].text.strip(),
                "user": col[3].text.strip(),
                "host": col[4].text.strip(),
                "time_out": out_time
            }
            users_info.append(_info)

        # print(users_info)

        for info in users_info:
            models.UserLicenseUsage.objects.get_or_create(user_name=info['user'],
                                                          host_name=info['host'],
                                                          version=info['version'],
                                                          checkout_stamp=info['time_out'])

    def beat_task(self):
        self._scrape_rlm_for_users()


if __name__ == '__main__':
    app = RLMScrape()
    app.beat_task()
