from django.urls import path
from . import views

urlpatterns = [
     path('account/delete/', views.delete_user, name='delete_account'),
]
