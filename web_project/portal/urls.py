from django.urls import path
from portal import views

urlpatterns = [    
    path('', views.index, name='index'),
    path('form', views.form, name='form'),
    path('table', views.table, name='table'),
    path('submit', views.submit, name='submit'),
    path('login', views.login_page, name='login'),
    path('authenticate', views.login_request, name='authenticate'),
    path('logout', views.logout_request, name='logout'),
    path('api/v1/submit', views.submit),
    path('api/v1/query-ipv4-address/', views.api_query_ip),
    path('api/v1/get-access-interfaces/', views.api_get_access_interfaces),
    path('api/v1/get-aggregation-interfaces/', views.api_get_aggregation_interfaces),
    path('api/v1/get-all-interfaces/', views.api_get_all_interfaces),
    path('details/<str:customer_name>/<int:vlan_number>', views.details, name='details'),
    path('error', views.error, name='error'),
]
