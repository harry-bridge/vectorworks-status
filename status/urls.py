from django.urls import path

from status import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('update', views.UpdateIndex.as_view(), name='update_index'),
    path('is-up', views.IsUpPage.as_view(), name='is_up_page'),
    path('usage', views.LicenseUsageList.as_view(), name='license_usage_list'),

    path('accounts/login/', views.Login.as_view(), name='login'),
    path('accounts/logout/', views.Logout.as_view(), name='logout'),
]
