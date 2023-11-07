from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from queue_webhook.models import Task

@login_required
def lab5(request):
    social = request.user.social_auth.get(provider='laforge')
    tasks = Task.objects.filter(data__user_id=int(social.uid))
    return render(request, 'lab5/results.html', {'tasks': tasks})
