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

    def __init__(self, tokens, playlist_id):

        self.tokens = tokens

        if (tokens.access_token_expires_at < datetime.now()):
            tokens.__init__()
        
        self.playlist_id = playlist_id
        
        # Get playlist
        self._get_playlist_data()

    def _get_playlist_data(self):
        
        url = "https://api.spotify.com/v1/playlists/{playlist_id}".format(playlist_id=self.playlist_id)

        auth_val = "{token_type} {access_token}".format(token_type=self.tokens.token_type, access_token=self.tokens.access_token)
        headers = { "Authorization": auth_val }

        response = requests.get(url=url, headers=headers)
        
        playlist_data = response.json()

        self.tracks = playlist_data.get("tracks").get("items")
    
    def get_playlist_tracks(self):
        return self.tracks

def print_playlist_tracks(playlist):

    tracks = playlist.get_playlist_tracks()

    for track in tracks:
        artists = track.get("track").get("artists")
        
        artists_formatted = ""
        for artist in artists:
            artists_formatted += artist.get("name") + " & "
        artists_formatted = artists_formatted[:-3]

        song = track.get("track").get("name")
        print(f"{artists_formatted} - {song} (Music Video)")

if __name__ == "__main__":

    tokens = Spotify()

    playlist = SpotifyPlaylist(tokens, "2CHagwsEDr98e1ms7bv5Im")
    print_playlist_tracks(playlist)

    playlist2 = SpotifyPlaylist(tokens, "7aZIGyJVxYEkoyB3T55QZS")
    print_playlist_tracks(playlist2)
