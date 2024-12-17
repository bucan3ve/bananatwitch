# TwitchBot System Documentation

## System Overview
TwitchBot is a Python-based system designed to simulate multiple viewers for Twitch streams using proxy servers. The system handles resource monitoring, proxy management, and Twitch API interactions while providing configurable logging and status reporting.

## Core Components

### ViewerBot
The main orchestrator class that coordinates all system activities.
- Initializes all system components
- Manages viewer threads
- Handles system shutdown
- Coordinates proxy usage

### ResourceMonitor
Tracks and reports system resource usage and bandwidth consumption.
- Monitors CPU and RAM usage
- Tracks bandwidth per proxy
- Generates bandwidth reports
- Provides real-time status updates

### TwitchAPI
Handles all interactions with Twitch's API services.
- Verifies stream status
- Obtains stream access tokens
- Retrieves playlist URLs
- Manages API authentication

### CustomLogger
Provides configurable logging with different verbosity levels.
- Supports verbose and quiet modes
- Color-coded output
- File and console logging
- Filters non-important messages in quiet mode

### Config
Manages system configuration with defaults and overrides.
- Loads from JSON file
- Provides default values
- Allows runtime configuration updates

## Operation Flow

1. **Initialization Phase**
   ```
   User Input → Config Loading → Component Initialization → System Setup
   ```

2. **Viewer Creation Process**
   ```
   Load Proxies → Verify Stream → Get Stream URL → Create Viewer Threads
   ```

3. **Monitoring Loop**
   ```
   Resource Monitoring → Bandwidth Tracking → Status Updates → Report Generation
   ```

4. **Viewer Simulation Process**
   ```
   Proxy Connection → Stream Access → Segment Download → Bandwidth Tracking
   ```

## Key Features

### Proxy Management
- Each viewer operates through a unique proxy
- Proxy rotation and retry mechanisms
- Bandwidth tracking per proxy
- Connection error handling

### Resource Monitoring
- Real-time CPU and RAM monitoring
- Network bandwidth tracking
- Per-proxy statistics
- Detailed reporting

### Logging System
- Dual-mode logging (verbose/quiet)
- Color-coded console output
- Complete file logging
- Error tracking and reporting

### Configuration
- JSON-based configuration
- Command-line arguments
- Runtime configuration updates
- Default fallback values

## Usage Example

```bash
# Basic usage
python threads_viewer.py channel_name 25

# Verbose mode
python threads_viewer.py channel_name 25 -v
```

## System Requirements
- Python 3.8+
- Required packages (see requirements.txt)
- Sufficient system resources based on viewer count
- Valid proxy list
- Internet connection

## Best Practices
1. Start with a small number of viewers and scale up
2. Monitor system resources regularly
3. Use reliable proxies
4. Keep configuration updated
5. Check logs for issues

## Common Issues and Solutions
1. **Connection Errors**
   - Verify proxy list
   - Check network connection
   - Ensure Twitch API tokens are valid

2. **Resource Issues**
   - Reduce viewer count
   - Monitor system resources
   - Check for memory leaks

3. **Stream Access Issues**
   - Verify channel is live
   - Check API tokens
   - Ensure proper authentication
