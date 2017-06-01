import os

config = {
    'TWITCH_OAUTH': None,
    'TWITCH_CHANNEL': None,
    'RING_BUFFER_SIZE': 10,
    'STREAM_RESOLUTION': 'medium',
    'PORT': 8080,
    'TIMEZONE': 'UTC',
    'UPLOAD_BACKEND': None,
    'VK_OAUTH': None,
    'VK_GROUP_ID': None
}

for k, v in config.items():
    config[k] = os.getenv(k, v)
