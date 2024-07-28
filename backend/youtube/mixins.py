from django.conf import settings
import requests
import json
import os

import googleapiclient.discovery
import googleapiclient.errors

# handles directions from Google
# def Directions(*args, **kwargs):

# formats title for later ig
def title_formatting(title):
    if len(title) >= 30:
        return f'{title[0:26]}'
    else:
        return title

class Youtube:
    def __init__(self, *args, **kwargs):
        self.vid = kwargs.get("vid_id")
        self.api_version = settings.AP_VERSION
        self.developer_key = settings.GOOGLE_API_KEY #enable youtube API in the google console (idk it needs money)
        self.channel_id = settings.CHANNEL_ID #channel id? idk lol

        self.youtube = googleapiclient.discover.build(
            self.api_service_name, # service is youtube
            self.api_version, # v3
            developerKey=self.developer_key # api key saved in settings
        )
    
    def get_data(self): #pulls videos to display on the home page
        playlist_request = self.youtube.playlists().list(
            part = "snippet, contentDetails", 
            channelID = self.channel.id,
        )

        playlist_response = playlist_request.execute()

        # create a list of playlists
        playlists = [p["id"] for p in playlist_response["items"]]

        next_page_token = None # allows us to do a while loop; max number of videos is 50;
                               # if we are trying to loop through playlist with more than 50, this lets us to do so
        
        videos = []
        data = []

        while True:
            for pl in playlists: # for each playlist we wanna grab more stuff from the youtube playlist
                playlist_items_request = self.youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=pl,
                    maxResults=50,
                    pageToken=next_page_token # first iteration is page 1, then page 2, etc.
                    )
                
                playlist_items_response=playlist_items_request.execute()

                for item in playlist_items_response["items"]:
                    videos.append(item["contentDetails"]["videoID"])
                
            video_request = self.youtube.videos.list(
                part="contentDetails,snippet,player",
                id=",".join(videos)
            )

            video_response=video_request.execute()

            for item in video_response["items"]:
                # dictionary for each video to add to the data list
                vid_data = {
                    "id": item["id"],
                    "title": item["snippet"]["title"],
                    "title_formatted": title_formatting(item["snippet"]["title"]),
                    "description": item["snippet"]["description"],
                    "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"], # note the medium is the resolution
                    "iframe": item["player"]["embedHtml"],
                }
                    
                data.append(vid_data)
                
            # get next page token from request + break loop if no more pages
            next_page_token = playlist_response.get("nextPageToken")
            if not next_page_token:
                break
        
        return data
    
    def get_video(self):
        # get data for one video (like the get_data method)

        video_request = self.youtube.videos().list(
            part="contentDetails, snippet, player",
            id=self.vid_id
        )

        video_response = video_request.execute()

        item = video_response["items"][0]

        vid_data = {
            "id": item["id"],
            "title": item["snippet"]["description"],
            "iframe": item["player"]["embedHtml"]
        }

        return vid_data
    
    # basic view for showing a video in an iframe
    def play_video(request):
        vid_id = request.GET.get("vid_id")
        vid_data = Youtube(vid_id=vid_id).get_video()

        context = {
            "vid_data": vid_data,
        }
        return render(request, 'main/play_video.html', context)

                
