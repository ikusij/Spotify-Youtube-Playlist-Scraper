from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os

class Spotify:

    def __init__(self):

        # Generate token
        self._generate_token()
    
    def _generate_token(self):

        url = "https://accounts.spotify.com/api/token"
        headers = { "Content-Type": "application/x-www-form-urlencoded" }

        load_dotenv()

        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        data = "grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}".format(client_id=client_id, client_secret=client_secret)

        response = requests.post(url=url, headers=headers, data=data)
        response_json = response.json()

        self.access_token_expires_at = datetime.now() + timedelta(hours=1)
        self.access_token = response_json["access_token"]
        self.token_type = response_json["token_type"]

class SpotifyPlaylist:

    def __init__(self, spotify_token: Spotify, playlist_id: str) -> None:

        self.spotify_token = spotify_token

        if (spotify_token.access_token_expires_at < datetime.now()):
            spotify_token.__init__()

        self.playlist_id = playlist_id
        
        self._get_playlist_tracks()

    def _get_playlist_tracks(self) -> None:
        
        url = "https://api.spotify.com/v1/playlists/{playlist_id}".format(playlist_id=self.playlist_id)

        auth_val = "{token_type} {access_token}".format(token_type=self.spotify_token.token_type, access_token=self.spotify_token.access_token)
        headers = { "Authorization": auth_val }

        response = requests.get(url=url, headers=headers)
        
        playlist_data = response.json()

        self.name = playlist_data.get("name")
        self.tracks = playlist_data.get("tracks").get("items")

        self._format_playlist_tracks()

    def _format_playlist_tracks(self) -> None:

        formatted_tracks = []

        for track in self.tracks:

            artist = track.get("track").get("artists")[0].get("name")
            song = track.get("track").get("name")
            
            formatted_track = "{artist} - {song} (Music Video)".format(artist=artist, song=song)
            formatted_tracks.append(formatted_track)
        
        self.tracks = formatted_tracks

    def get_playlist_name(self) -> None:
        return self.name

    def get_playlist_tracks(self) -> None:
        return self.tracks

class YouTube:

    def __init__(self):

        # Generate token
        self._generate_token()

    def _generate_token(self):

        load_dotenv()

        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

        url = "https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token&refresh_token={refresh_token}".format(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)

        response = requests.post(url=url)
        response_json = response.json()

        self.access_token_expires_at = datetime.now() + timedelta(hours=1)
        self.access_token = response_json["access_token"]
        self.token_type = response_json["token_type"]

class YouTubePlaylist:
    
    def __init__(self, youtube_token: YouTube, name: str, tracks: list[str]):

        self.youtube_token = youtube_token

        if (youtube_token.access_token_expires_at < datetime.now()):
            youtube_token.__init__()
        
        self.name = name
        
        self.create_playlist(tracks=tracks)
    
    def create_playlist(self, tracks: list[str]):
        
        url = "https://youtube.googleapis.com/youtube/v3/playlists?part=snippet"

        auth_val = "{token_type} {access_token}".format(token_type=self.youtube_token.token_type, access_token=self.youtube_token.access_token)
        headers = { 
            "Authorization": auth_val,
            "Content-Type": "application/json"
        }

        data = { 
            "snippet": {
                "title": self.name
            }
        }

        response = requests.post(url=url, headers=headers, json=data)
        json_response = response.json()
        
        self.playlist_id = json_response.get("id")

        self._insert_to_playlist(tracks=tracks)

    def _tracks_to_resource_ids(self, tracks: list[str]):

        key = os.getenv("YOUTUBE_API_KEY")

        resource_ids = []

        for q in tracks:

            url = "https://youtube.googleapis.com/youtube/v3/search?q={q}&key={key}".format(q=q, key=key)

            response = requests.get(url=url)
            json_response = response.json()

            resource_id = json_response.get("items")[0].get("id").get("videoId")
            
            resource_ids.append(resource_id)
        
        self.resource_ids = resource_ids

    def _insert_to_playlist(self, tracks: list[str]):

        self._tracks_to_resource_ids(tracks=tracks)

        url = "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet"

        auth_val = "{token_type} {access_token}".format(token_type=self.youtube_token.token_type, access_token=self.spotify_token.access_token)
        headers = { 
            "Authorization": auth_val,
            "Content-Type": "application/json"
        }

        total = len(self.resource_ids)

        for idx, resource_id in enumerate(self.resource_ids):

            data = { 
                "snippet": {
                    "playlistId": self.playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": resource_id
                    }
                }
            }

            response = requests.post(url=url, headers=headers, json=data)
            json_response = response.json()
            print("Added Track %2d / %2d" % (idx, total))

if __name__ == "__main__":

    spotify_token = Spotify()
    playlist = SpotifyPlaylist(spotify_token=spotify_token, playlist_id="35u7I78NSnl6aRdaWK2LLk")
    name = playlist.get_playlist_name()
    tracks = playlist.get_playlist_tracks()

    youtube_token = YouTube()
    youtube_playlist = YouTubePlaylist(youtube_token=youtube_token, name=name, tracks=tracks)
