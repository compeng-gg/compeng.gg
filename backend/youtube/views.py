from django.shortcuts import render
from django.conf import settings

from .mixins import Youtube

# Create your views here.
def videos(request):
    videos = Youtube().get_data()
    context = {"videos": videos}
    return render(request, 'mina/videos.html', context)


# basic view for showing a video in an iframe

def play_video(request):
    vid_id = request.GET.get("vid_id")
    vid_data = Youtube(vid_id = vid_id).getvideo()
    context = {
        "vid_data": vid_data,
    }
    return render(request, 'main/play_video.html', context)