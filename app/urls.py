from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('box/<int:box_id>/', views.box_detail, name='box_detail'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('calculator/', views.calculator, name='calculator'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('checkout/<int:box_id>/', views.checkout, name='checkout'),
    path('payment/<int:box_id>/', views.payment, name='payment'),
    path('api/catalog/', views.catalog_api, name='catalog_api'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/data/', views.profile_data, name='profile_data'),
    path('profile/payments/', views.payment_history, name='payment_history'),
]