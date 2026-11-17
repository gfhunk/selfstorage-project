from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('box/<int:box_id>/', views.box_detail, name='box_detail'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
]