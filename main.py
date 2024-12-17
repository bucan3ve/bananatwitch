import requests
import sys
import time
import random
import threading
from datetime import datetime
from threading import Thread
import m3u8
import json
import logging
import psutil
from typing import Dict, Any
from colorama import Fore, Style, init
import signal

class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored logs"""
    COLORS = {
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
        'DEBUG': Fore.BLUE,
        'RESOURCE': Fore.GREEN,
        'PROXY': Fore.CYAN
    }

    def format(self, record):
        # Add custom color for our resource and proxy logs
        if hasattr(record, 'color'):
            color = record.color
        else:
            color = self.COLORS.get(record.levelname, '')
        
        # Reset color after the message
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

class CustomLogger:
    """Custom logger with colored output and different handlers"""
    def __init__(self, name: str, log_file: str, verbose: bool = False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.verbose = verbose

        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(name)s - %(message)s',
            '%H:%M:%S'
        ))

        # Add filter for non-verbose mode
        if not verbose:
            console_handler.addFilter(self.important_only)

        # File handler for complete logging (always verbose)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def important_only(self, record):
        """Filter for important messages in non-verbose mode"""
        important_patterns = [
            'Error',
            'CPU',
            'Resource Usage',
            'Starting with',
            'Found live stream',
            'Channel is not live',
            'Shutdown signal received',
            'Successfully got stream URL'
        ]
        return any(pattern in record.getMessage() for pattern in important_patterns)

    def resource(self, message):
        """Custom level for resource messages"""
        self.logger.info(message, extra={'color': Fore.GREEN})

    def proxy(self, message):
        """Custom level for proxy messages"""
        # Only log proxy messages if verbose
        if self.verbose:
            self.logger.info(message, extra={'color': Fore.CYAN})

class ResourceMonitor:
    """Monitor system resources and bandwidth usage"""
    def __init__(self, logger: CustomLogger, viewer_bot=None):
        self.running = True
        self.monitor_thread = None
        self.logger = logger
        self.process = psutil.Process()
        self.start_time = time.time()
        self.viewer_bot = viewer_bot  # Reference to main bot for status
        
        # Bandwidth tracking
        self.proxy_bandwidth = {}
        self.total_bandwidth = {
            'sent': 0,
            'received': 0
        }
        self.bandwidth_lock = threading.Lock()
        self.active_viewers = 0  # Track active viewers

    def update_active_viewers(self, count: int):
        """Update the count of currently active viewers"""
        self.active_viewers = count

    def monitor_resources(self):
        last_net_io = self.process.io_counters()
        last_time = time.time()

        while self.running:
            try:
                # Calculate CPU and Memory
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Calculate network speed
                current_net_io = self.process.io_counters()
                current_time = time.time()
                time_delta = current_time - last_time
                
                bytes_sent = (current_net_io.write_bytes - last_net_io.write_bytes) / time_delta
                bytes_recv = (current_net_io.read_bytes - last_net_io.read_bytes) / time_delta
                
                # Enhanced status message with active viewers
                self.logger.resource(
                    f"\nBot Status and Resource Usage:\n"
                    f"Active Viewers: {self.active_viewers}/{self.viewer_bot.config.get('target_viewers')} "
                    f"({'on track' if self.active_viewers == self.viewer_bot.config.get('target_viewers') else 'reconnecting'})\n"
                    f"CPU: {cpu_percent}% | RAM: {memory.percent}%\n"
                    f"Network Speed - Upload: {bytes_sent/1024:.2f} KB/s, Download: {bytes_recv/1024:.2f} KB/s\n"
                    f"Total Transfer - Upload: {self.total_bandwidth['sent']/1024/1024:.2f}MB, Download: {self.total_bandwidth['received']/1024/1024:.2f}MB"
                )
                
                last_net_io = current_net_io
                last_time = current_time
                
            except Exception as e:
                self.logger.logger.error(f"Error monitoring resources: {str(e)}")
            
            time.sleep(5)
    
    def start(self):
        self.monitor_thread = threading.Thread(target=self.monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self._save_bandwidth_report()

    def _save_bandwidth_report(self):
        """Save bandwidth usage report to file"""
        report_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"bandwidth_report_{report_time}.txt"
        
        total_duration = (time.time() - self.start_time) / 3600  # Convert to hours
        
        try:
            with open(report_file, 'w') as f:
                f.write(f"Bandwidth Usage Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Runtime: {total_duration:.2f} hours\n\n")
                
                f.write("=== Total Bandwidth Usage ===\n")
                f.write(f"Total Upload: {self.total_bandwidth['sent']/1024/1024:.2f} MB\n")
                f.write(f"Total Download: {self.total_bandwidth['received']/1024/1024:.2f} MB\n")
                f.write(f"Average Upload Speed: {self.total_bandwidth['sent']/1024/total_duration:.2f} KB/h\n")
                f.write(f"Average Download Speed: {self.total_bandwidth['received']/1024/total_duration:.2f} KB/h\n\n")
                
                f.write("=== Per-Proxy Bandwidth Usage ===\n")
                for proxy, bandwidth in self.proxy_bandwidth.items():
                    f.write(f"\nProxy: {proxy}\n")
                    f.write(f"Upload: {bandwidth['sent']/1024/1024:.2f} MB\n")
                    f.write(f"Download: {bandwidth['received']/1024/1024:.2f} MB\n")
                    f.write(f"Average Upload Speed: {bandwidth['sent']/1024/total_duration:.2f} KB/h\n")
                    f.write(f"Average Download Speed: {bandwidth['received']/1024/total_duration:.2f} KB/h\n")
                    
                f.write("\n=== End of Report ===")
                
            self.logger.logger.info(f"Bandwidth report saved to {report_file}")
            
        except Exception as e:
            self.logger.logger.error(f"Error saving bandwidth report: {str(e)}")

class Config:
    """Configuration management"""
    DEFAULT_CONFIG = {
        "target_viewers": 25,
        "proxies_file": "good_proxy.txt",
        "log_file": "viewer_bot.log",
        "check_interval": 5,
        "connection_timeout": 15,
        "retry_attempts": 3,
        "retry_delay": 5
    }

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                return {**self.DEFAULT_CONFIG, **user_config}
        except FileNotFoundError:
            print(f"Config file not found, using defaults")
            return self.DEFAULT_CONFIG
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {str(e)}, using defaults")
            return self.DEFAULT_CONFIG

    def get(self, key: str) -> Any:
        return self.config.get(key)

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
class TwitchAPI:
    def __init__(self, logger: CustomLogger):
        self.client_id = "gp762nuuoqcoxypju8c569th9wz7q5"
        self.access_token = "vvzmmk0zl1nr00rxql4upv5nlclzs1"
        self.base_url = "https://api.twitch.tv/helix"
        self.logger = logger
        
    def get_stream_info(self, username):
        try:
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
                self.logger.logger.error(f"API Error: {response.status_code}")
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
        except Exception as e:
            self.logger.logger.error(f"Error in get_stream_info: {str(e)}")
            return None

    def get_access_token(self, channel):
        try:
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
        except Exception as e:
            self.logger.logger.error(f"Error in get_access_token: {str(e)}")
            return None

    def get_playlist_url(self, channel):
        try:
            token_data = self.get_access_token(channel)
            if not token_data:
                return None
            
            token = token_data['value']
            sig = token_data['signature']
            
            return f'https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8?client_id=kimne78kx3ncx6brgo4mv6wki5h1ko&token={token}&sig={sig}&allow_source=true&allow_audio_only=true&fast_bread=true&playlist_include_framerate=true&reassignments_supported=true&supported_codecs=avc1'
        except Exception as e:
            self.logger.logger.error(f"Error in get_playlist_url: {str(e)}")
            return None

class ViewerBot:
    def __init__(self, verbose: bool = False):
        self.config = Config()
        self.logger = CustomLogger('ViewerBot', self.config.get('log_file'), verbose)
        self.resource_monitor = ResourceMonitor(self.logger)
        self.twitch_api = TwitchAPI(self.logger)
        
        self.channel_name = ""
        self.playlist_url = None
        self.running = True
        self.active_connections = 0
        self.all_proxies = []
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        self.logger.logger.info("Shutdown signal received, cleaning up...")
        self.running = False
        self.resource_monitor.stop()
        sys.exit(0)

    def get_proxies(self):
        try:
            with open(self.config.get('proxies_file'), 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.logger.logger.error(f"Error reading proxy file: {e}")
            sys.exit(1)

    def simulate_viewer(self, proxy_data):
        retry_count = 0
        proxy_address = proxy_data['proxy']
        
        while retry_count < self.config.get('retry_attempts') and self.running:
            try:
                current_proxy = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain',
                }

                with requests.Session() as session:
                    # Get master playlist
                    response = session.get(
                        self.playlist_url, 
                        proxies=current_proxy, 
                        headers=headers, 
                        timeout=self.config.get('connection_timeout')
                    )
                    master_playlist = m3u8.loads(response.text)
                    
                    # Get the lowest quality stream
                    playlist_uri = sorted(master_playlist.playlists, key=lambda x: x.stream_info.bandwidth)[0].uri
                    
                    while self.running:
                        # Get media playlist
                        response = session.get(
                            playlist_uri, 
                            proxies=current_proxy, 
                            headers=headers, 
                            timeout=self.config.get('connection_timeout')
                        )
                        media_playlist = m3u8.loads(response.text)
                        
                        # Track bandwidth for each segment download
                        for segment in media_playlist.segments:
                            if not self.running:
                                break
                                
                            start_time = time.time()
                            response = session.get(
                                segment.uri, 
                                proxies=current_proxy, 
                                headers=headers, 
                                timeout=self.config.get('connection_timeout')
                            )
                            
                            if response.status_code == 200:
                                # Calculate and track bandwidth
                                content_length = len(response.content)
                                self.resource_monitor.update_proxy_bandwidth(
                                    proxy_address,
                                    content_length,  # sent (headers etc)
                                    content_length   # received (segment data)
                                )
                                
                                self.logger.proxy(
                                    f"Successfully downloaded segment using proxy {proxy_address}"
                                )
                                
                            time.sleep(1)  # Simulate real playback time
                        
                        time.sleep(2)  # Wait before getting next playlist

            except requests.exceptions.RequestException as e:
                retry_count += 1
                self.logger.logger.error(f"Connection error with proxy {proxy_address}: {str(e)}")
                time.sleep(self.config.get('retry_delay') * retry_count)  # Exponential backoff
                
            except Exception as e:
                self.logger.logger.error(f"Unexpected error with proxy {proxy_address}: {str(e)}")
                retry_count += 1
                time.sleep(self.config.get('retry_delay') * retry_count)

    def mainmain(self):
        if len(sys.argv) < 2:
            self.logger.logger.error("Usage: python script.py <channel_name> [number_of_viewers]")
            sys.exit(1)
            
        self.channel_name = sys.argv[1]
        if len(sys.argv) > 2:
            try:
                self.config.config['target_viewers'] = int(sys.argv[2])
            except ValueError:
                self.logger.logger.error("Number of viewers must be a number")
                sys.exit(1)
        
        # Verify stream is live
        stream_info = self.twitch_api.get_stream_info(self.channel_name)
        if not stream_info:
            self.logger.logger.error("Channel is not live or not found!")
            sys.exit(1)
            
        self.logger.logger.info(
            f"Found live stream: {stream_info['user_name']} playing {stream_info.get('game_name', 'Unknown')}"
        )
        
        # Get playlist URL
        self.playlist_url = self.twitch_api.get_playlist_url(self.channel_name)
        if not self.playlist_url:
            self.logger.logger.error("Could not get stream URL!")
            sys.exit(1)
            
        self.logger.logger.info("Successfully got stream URL")
        
        proxies = self.get_proxies()
        if not proxies:
            self.logger.logger.error("No valid proxies found!")
            sys.exit(1)
        
        # Limit proxies to target viewers
        proxies = proxies[:self.config.get('target_viewers')]
        self.all_proxies = [{'proxy': p, 'time': time.time()} for p in proxies]
        
        self.logger.logger.info(
            f"Starting with {len(self.all_proxies)} proxies to create {self.config.get('target_viewers')} viewers"
        )
        
        # Start resource monitoring
        self.resource_monitor.start()
        
        try:
            threads = []
            for proxy_data in self.all_proxies:
                if not self.running:
                    break
                    
                thread = Thread(target=self.simulate_viewer, args=(proxy_data,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                time.sleep(0.5)  # Stagger the connections
            
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            self.logger.logger.error(f"Error in main loop: {str(e)}")
        finally:
            self.running = False
            self.resource_monitor.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitch Viewer Bot')
    parser.add_argument('channel', type=str, help='Channel name to watch')
    parser.add_argument('viewers', type=int, nargs='?', default=25, help='Number of viewers (default: 25)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    viewer_bot = ViewerBot(verbose=args.verbose)
    sys.argv = [sys.argv[0], args.channel, str(args.viewers)]  # Reconstruct sys.argv for existing code
    viewer_bot.mainmain()
