import time
import urllib.error
from concurrent.futures import ThreadPoolExecutor
import threading
import socket
import mechanize
from bs4 import BeautifulSoup

from status import models

up = 0
down = 1


class PortCheck:
    _port_check_url = "https://portchecker.co/"
    _fails = 0
    _max_runs = 2

    def __init__(self):
        self._settings = models.ScraperSettings().get_settings()

    @staticmethod
    def _get_site_ip(hostname):
        return socket.gethostbyname(hostname)

    @staticmethod
    def _get_port_tests():
        models.UptimeTest().objects.all()

    def _log_uptime_result(self, port_test, result, server_response=None, details=None):
        models.UptimeHistory.objects.create(
            test=port_test,
            uptime_result=result,
            server_response=server_response,
            details=details
        )

    def _internal_port_check(self, port_test):
        print("Testing internal - {}".format(port_test.name))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((port_test.hostname, int(port_test.port)))
            s.shutdown(2)
            result = up
            print("{} - OK".format(port_test.name))

        except socket.timeout:
            result = down
            self._fails += 1
            print("{} - ERROR".format(port_test.name))

        self._log_uptime_result(port_test, result)

    def _external_port_check(self, port_test):
        print("Testing external - {}".format(port_test.name))
        _br = mechanize.Browser()
        _br.set_handle_robots(False)

        try:
            resp = _br.open(self._port_check_url)
        except urllib.error.URLError as err:
            print("Error opening browser")
            print(err)
            self._log_uptime_result(port_test, down, details=err)
            return

        _br.form = list(_br.forms())[0]
        ip = _br.form.find_control("target_ip")
        ip.value = self._get_site_ip(port_test.hostname)
        port = _br.form.find_control("port")
        port.value = port_test.port
        resp = _br.submit()

        soup = BeautifulSoup(resp.read(), 'html.parser')
        result_wrapper = soup.find("div", {"id": "results-wrapper"}).find("span").text

        if result_wrapper.lower() == 'open':
            result = up
            print("{} - OK".format(port_test.name))
        else:
            print("{} - ERROR".format(port_test.name))
            result = down
            self._fails += 1

        self._log_uptime_result(port_test, result)

    def check_ports_multithread(self):
        _run_num = 1
        while self._max_runs > 0:
            with ThreadPoolExecutor(max_workers=3) as executor:
                print("Running test #{}".format(_run_num))
                _run_num += 1

                print("Testing internal ports")
                for test in models.UptimeTest().get_all_internal_tests():
                    # self._internal_port_check(test)
                    executor.submit(self._internal_port_check, test)

                print("Testing external ports")
                for test in models.UptimeTest().get_all_external_tests():
                    executor.submit(self._external_port_check, test)

            if self._fails > 0:
                time.sleep(10)
                self._max_runs -= 1
                continue
            else:
                break

    def check_ports_singlethread(self):
        print("Testing internal ports")
        for test in models.UptimeTest().get_all_internal_tests():
            self._internal_port_check(test)

        print("Testing external ports")
        for test in models.UptimeTest().get_all_external_tests():
            self._external_port_check(test)
