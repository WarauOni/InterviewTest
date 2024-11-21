from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='home'),
    path('about/', views.about, name='about'),
    path('contact-us/', views.contact, name='contact'),
    path('support-us/', views.support, name='support'),
    path('sign-up/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('edit-profile/', views.user_profile, name='user_profile'),
    path('user-profile/', views.view_profile, name='view_profile'),
    path('logout/', views.user_logout, name='logout'),
    path('adopt/<int:kitty_id>/', views.adopt_kitty, name='adopt_kitty'), 
    path('add-kitty/', views.add_kitty, name='add_kitty'),
    path('adopt/details/<str:adopt_id>/', views.adopt_details, name='adopt_details'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
