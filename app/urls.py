from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('box/<int:box_id>/', views.box_detail, name='box_detail'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('calculator/', views.calculator, name='calculator'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('checkout/<int:box_id>/', views.checkout, name='checkout'),
    path('payment/<int:box_id>/', views.payment, name='payment'),
]