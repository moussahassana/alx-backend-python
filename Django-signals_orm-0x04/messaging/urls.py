from django.urls import path
from . import views

urlpatterns = [
     # URL for the user's inbox (a list of all conversations)
     path('inbox/', views.inbox, name='inbox'),

     # URL to view a specific conversation thread
     path('thread/<int:thread_id>/', views.message_thread_view, name='message_thread'),
    
     # URL to handle posting a reply to a thread
     path('thread/<int:thread_id>/reply/', views.send_reply, name='send_reply'),
     path('account/delete/', views.delete_user, name='delete_account'),
]
