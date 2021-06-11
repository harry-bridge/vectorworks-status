from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command

from status import models
from status.rlm_scraper import RLMScrape
from status.port_check import PortCheck


class Login(auth_views.LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse_lazy('index')


class Logout(auth_views.LogoutView):
    template_name = 'registration/logout.html'


class Index(LoginRequiredMixin, generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['license_info'] = models.RlmInfo().get_latest_info_dict()

        context['uptime_error'] = False
        context['rlm_status'] = models.UptimeTest.objects.get(name="vectorworks_server").get_last_uptime()
        context['port1_status'] = models.UptimeTest.objects.get(name="rlm_port_1").get_last_uptime()
        context['port2_status'] = models.UptimeTest.objects.get(name="rlm_port_2").get_last_uptime()

        try:
            if context['rlm_status'].get_status == 'down' or \
                    context['port1_status'].get_status == 'down' or \
                    context['port2_status'].get_status == 'down':

                context['all_servers_up'] = False
            else:
                context['all_servers_up'] = True
        except AttributeError:
            # can't find any uptime histories so return false
            context['all_servers_up'] = False
            context['uptime_error'] = True

        return context


class UpdateIndex(LoginRequiredMixin, generic.View):
    def get(self, request):
        PortCheck().check_ports_multithread()
        RLMScrape().beat_task()

        return HttpResponseRedirect(reverse_lazy('index'))


class IsUpPage(generic.View):
    def get(self, request):
        if models.UptimeTest().all_tests_up():
            return HttpResponseRedirect(reverse_lazy('index'))
        else:
            return HttpResponse(status=500)
