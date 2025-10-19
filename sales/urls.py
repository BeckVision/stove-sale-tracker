from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('add-sale/', views.add_sale, name='add_sale'),
    path('sales/', views.sale_list, name='sale_list'),
    path('dashboard/', views.investor_dashboard, name='investor_dashboard'),
    path('worker/', views.worker_dashboard, name='worker_dashboard'),
    path('worker/add/', views.add_production, name='add_production'),
]
