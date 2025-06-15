from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import Message

@login_required
def delete_user(request):
    """
    Handles the user account deletion process.

    On a GET request, it displays a confirmation page.
    On a POST request, it logs the user out, deletes their account
    (which triggers the cleanup signal), and redirects to a home page.
    """
    if request.method == 'POST':
        user = request.user
        
        # Log the user out before deleting to invalidate the session
        logout(request)
        
        # Deleting the user object will trigger the pre_delete signal
        user.delete()
        
        # Add a success message to be displayed on the next page
        messages.success(request, 'Your account has been successfully deleted.')
        
        # Redirect to a safe page
        try:
            return redirect('home')
        except:
            return redirect('/')

    return render(request, 'messaging/delete_confirm.html')


@login_required
def message_thread_view(request, thread_id):
    """
    Displays a specific message thread, including all replies,
    using the optimized query from the model's ThreadManager.
    """
    # Use our custom manager to fetch the entire thread efficiently
    thread = Message.threads.get_thread(thread_id)

    if not thread:
        from django.http import Http404
        raise Http404("Message thread not found or you are trying to view a reply directly.")

    # A simple authorization check
    if request.user not in [thread.sender, thread.receiver]:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    return render(request, 'messaging/thread_detail.html', {'thread': thread})