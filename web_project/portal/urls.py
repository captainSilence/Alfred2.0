from django.urls import path
from portal import views

urlpatterns = [    
    path('', views.index, name='index'),
    path('form', views.form, name='form'),
    path('formepl', views.formepl, name='formepl'),
    path('table', views.table, name='table'),
    path('tableepl', views.table_epl, name='tableepl'),
    path('submit', views.submit, name='submit'),
    path('submitepl', views.submit_epl, name='submit'),
    path('login', views.login_page, name='login'),
    path('authenticate', views.login_request, name='authenticate'),
    path('logout', views.logout_request, name='logout'),
    path('api/v1/submit', views.submit),
    path('api/v1/query-ipv4-address/', views.api_query_ip),
    path('api/v1/query-customer-address/', views.api_query_customer_address),
    path('api/v1/get-access-interfaces/', views.api_get_access_interfaces),
    path('api/v1/get-aggregation-interfaces/', views.api_get_aggregation_interfaces),
    path('api/v1/get-all-interfaces/', views.api_get_all_interfaces),
    path('api/v1/get-all-sysname/', views.api_get_all_sysname),
    path('details/<str:customer_name>/<int:vlan_number>', views.details, name='details'),
    path('detailsepl/<str:customer_name>/<int:vlan_number>', views.detailsepl, name='detailsepl'),
    path('config/<str:customer_name>/<int:vlan_number>', views.device_config, name='config'),
    path('configepl/<str:customer_name>/<int:vlan_number>', views.device_config_epl, name='configepl'),
    path('error', views.error, name='error'),
    path('api/v1/epl-get-all-interfaces/', views.api_get_all_epl_interfaces),
    path('api/v1/epl-get-remote-interfaces/', views.api_epl_get_remoteRouter_interfaces),
]
