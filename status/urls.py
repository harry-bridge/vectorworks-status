from django.urls import path

from status import views
from status import api

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('update', views.UpdateIndex.as_view(), name='update_index'),
    path('is-up', views.IsUpPage.as_view(), name='is_up_page'),
    path('usage', views.LicenseUsageList.as_view(), name='license_usage_list'),

    path('accounts/login/', views.Login.as_view(), name='login'),
    path('accounts/logout/', views.Logout.as_view(), name='logout'),

    path('api/in-use-all', api.LicenseInUseListView.as_view({'get': 'list'}), name='api-license_in_use_all'),
    path('api/in-use/<str:product>', api.LicenseInUseDetailView.as_view({'get': 'retrieve'}), name='api-license_in_use'),
    path('api/license-usage-top', api.LicenseUsageTopListView.as_view({'get': 'list'}), name='api-license_in_use'),
]
