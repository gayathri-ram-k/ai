from django.urls import path
from . import views

urlpatterns = [

    path('', views.user_login, name='login'),
    path('login/', views.user_login, name='login'),  # Login page
    path('signup/', views.user_signup, name='signup'),  # Signup page
    path('home/', views.home, name='home'),  # Home page
      path('run-diagnosis/', views.run_diagnosis, name='run_diagnosis'),
    path('logout/', views.user_logout, name='logout'),  # Logout page
]

