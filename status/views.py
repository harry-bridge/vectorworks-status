from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command

from status import models
from status.rlm_scraper import RLMScrape


class Login(auth_views.LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse_lazy('index')


class Logout(auth_views.LogoutView):
    template_name = 'registration/logout.html'


def extract_info_from_rml(context, rml_info):
    context['current_users'] = 0

    for key, value in rml_info.items():
        context['current_users'] = max(context['current_users'], int(value['inuse']))
        context['last_updated'] = value['last_updated']

    return context


class Index(LoginRequiredMixin, generic.TemplateView):
    template_name = 'index.html'
    # template_name = 'starter-template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rlm = RLMScrape()
        context['license_info'] = rlm.read_rlm_info_log()
        extract_info_from_rml(context, context['license_info'])
        # context['server_online'] = rlm.read_rlm_server_log()

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

        # if rlm_status.get_status() == 'down':
        #     context['server_status'] = 'down'




        # context['rlm_server_status'] = models.UptimeTest.objects.get(name="vectorworks_server").get_last_uptime()


        return context


class UpdateIndex(LoginRequiredMixin, generic.View):
    def get(self, request):
        call_command('port_check')
        call_command('rlm_beat')

        return HttpResponseRedirect(reverse_lazy('index'))


class IsUpPage(generic.View):
    def get(self, request):
        if models.UptimeTest().all_tests_up():
            return HttpResponseRedirect(reverse_lazy('index'))
        else:
            return HttpResponse(status=500)
