from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('deposit/', views.deposit, name='deposit'),

    path('withdraw/', views.withdraw, name='withdraw'),

    path('transfer/', views.transfer, name='transfer'),

    path('transactions/', views.transactions, name='transactions'),
]
