import requests
import sys
import time
import random
from threading import Thread
import m3u8
import json

class TwitchAPI:
    def __init__(self):
        self.client_id = "gp762nuuoqcoxypju8c569th9wz7q5"
        self.access_token = "vvzmmk0zl1nr00rxql4upv5nlclzs1"
        self.base_url = "https://api.twitch.tv/helix"
        
    def get_stream_info(self, username):
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(
            f"{self.base_url}/users",
            headers=headers,
            params={'login': username}
        )
        if response.status_code != 200:
            return None
        user_data = response.json()['data']
        if not user_data:
            return None
        user_id = user_data[0]['id']
        
        response = requests.get(
            f"{self.base_url}/streams",
            headers=headers,
            params={'user_id': user_id}
        )
        if response.status_code != 200:
            return None
        stream_data = response.json()['data']
        return stream_data[0] if stream_data else None

    def get_access_token(self, channel):
        url = 'https://gql.twitch.tv/gql'
        headers = {
            'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
            'Content-Type': 'application/json',
        }
        query = [{
            "operationName": "PlaybackAccessToken",
            "variables": {
                "isLive": True,
                "login": channel,
                "isVod": False,
                "vodID": "",
                "playerType": "embed"
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712"
                }
            }
        }]
        
        response = requests.post(url, headers=headers, json=query)
        if response.status_code == 200:
            data = response.json()
            return data[0]['data']['streamPlaybackAccessToken']
        return None

    def get_playlist_url(self, channel):
        token_data = self.get_access_token(channel)
        if not token_data:
            return None
        
        token = token_data['value']
        sig = token_data['signature']
        
        return f'https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8?client_id=kimne78kx3ncx6brgo4mv6wki5h1ko&token={token}&sig={sig}&allow_source=true&allow_audio_only=true&fast_bread=true&playlist_include_framerate=true&reassignments_supported=true&supported_codecs=avc1'

class ViewerBot:
    def __init__(self):
        self.channel_name = ""
        self.proxies_file = "good_proxy.txt"
        self.target_viewers = 25
        self.all_proxies = []
        self.twitch_api = TwitchAPI()
        self.playlist_url = None
        
    def get_proxies(self):
        try:
            with open(self.proxies_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except IOError as e:
            print(f"Error reading proxy file: {e}")
            sys.exit(1)

    def simulate_viewer(self, proxy_data):
        try:
            current_proxy = {
                "http": proxy_data['proxy'],
                "https": proxy_data['proxy']
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain',
            }

            # Get master playlist
            with requests.Session() as session:
                response = session.get(self.playlist_url, proxies=current_proxy, headers=headers, timeout=15)
                master_playlist = m3u8.loads(response.text)
                
                # Get the lowest quality stream
                playlist_uri = sorted(master_playlist.playlists, key=lambda x: x.stream_info.bandwidth)[0].uri
                
                while True:
                    # Get media playlist
                    response = session.get(playlist_uri, proxies=current_proxy, headers=headers, timeout=15)
                    media_playlist = m3u8.loads(response.text)
                    
                    # Get and download segments
                    for segment in media_playlist.segments:
                        try:
                            response = session.get(segment.uri, proxies=current_proxy, headers=headers, timeout=15)
                            if response.status_code == 200:
                                print(f"Successfully downloaded segment using proxy {proxy_data['proxy']}")
                            time.sleep(1)  # Simulate real playback time
                        except:
                            continue
                    
                    time.sleep(2)  # Wait before getting next playlist

        except Exception as e:
            print(f"Error in viewer simulation: {str(e)}")
            time.sleep(5)  # Wait before potentially reconnecting

    def mainmain(self):
        if len(sys.argv) < 2:
            print("Usage: python script.py <channel_name> [number_of_viewers]")
            sys.exit(1)
            
        self.channel_name = sys.argv[1]
        if len(sys.argv) > 2:
            try:
                self.target_viewers = int(sys.argv[2])
            except ValueError:
                print("Number of viewers must be a number")
                sys.exit(1)
        
        # Verify stream is live
        stream_info = self.twitch_api.get_stream_info(self.channel_name)
        if not stream_info:
            print("Channel is not live or not found!")
            sys.exit(1)
            
        print(f"Found live stream: {stream_info['user_name']} playing {stream_info.get('game_name', 'Unknown')}")
        
        # Get playlist URL
        self.playlist_url = self.twitch_api.get_playlist_url(self.channel_name)
        if not self.playlist_url:
            print("Could not get stream URL!")
            sys.exit(1)
            
        print(f"Successfully got stream URL")
        
        proxies = self.get_proxies()
        if not proxies:
            print("No valid proxies found!")
            sys.exit(1)
        
        proxies = proxies[:self.target_viewers]
        self.all_proxies = [{'proxy': p, 'time': time.time()} for p in proxies]
        
        print(f"Starting with {len(self.all_proxies)} proxies to create {self.target_viewers} viewers")
        
        try:
            threads = []
            for proxy_data in self.all_proxies:
                thread = Thread(target=self.simulate_viewer, args=(proxy_data,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                time.sleep(0.5)  # Stagger the connections
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping viewer bot...")
            sys.exit(0)

if __name__ == "__main__":
    viewer_bot = ViewerBot()
    viewer_bot.mainmain()
