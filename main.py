import httplib2
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from oauth2client.client import OAuth2WebServerFlow

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
You will need to provide a client_secret.json file
"""

# The location of the secrets file
CLIENT_SECRETS_FILE = "client_secret.json"
CLIENT_ID = "my client id"
CLIENT_SECRET = "my client secret"
YOUTUBE_READONLY_SCOPE = 'https://www.googleapis.com/auth/youtube.force-ssl'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
flow = OAuth2WebServerFlow(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=YOUTUBE_READONLY_SCOPE)
storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()
if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                http=credentials.authorize(httplib2.Http()))


# ======== Configure the following variables ===========
# uploads id
cid =  "youtube channle cid"   
lastvid = ""
# waiting time intervel in seconds
intervel = 1
# comment you need to post
comment = "my comment"

#get last video
def lastvideo(channel_id):

    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token = None

    res = youtube.playlistItems().list(playlistId=playlist_id,
                                       part='snippet',
                                       maxResults=1,
                                       pageToken=next_page_token).execute()
    return res["items"][0]['snippet']


def insert_comment(parent_id, text):
    insert_result = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": parent_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": text
                    }
                }
            }
        }
    )
    response = insert_result.execute()
    print("comment added: %s" % text)


#insert new comment when there new video uploaded after running this script

i = 0
lv = lastvideo(cid)
lastvid = lv["resourceId"]["videoId"]
print("Current latest video: %s" % lv['title'])
print("Waiting for new video")
while True:
    l = lastvideo(cid)
    last = l["resourceId"]["videoId"]
    i = i+1
    if(last != lastvid):
        print("Found New video: %s" % l['title'])
        try:
            insert_comment(last, comment)
            # print("Liking video")
            # youtube.videos().rate(rating='like', id=last).execute()
            # print("Liked!")
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s") % (
                e.resp.status, e.content)
        else:
            print("Comment Inserted")
            break
    else:
        print(".")
    time.sleep(intervel)
