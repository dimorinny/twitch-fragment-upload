import os

config = {
    'TWITCH_OAUTH': None,
    'TWITCH_CHANNEL': None,
    'VK_OAUTH': None,
    'VK_GROUP_ID': None,
    'RING_BUFFER_SIZE': 1024 * 1024 * 15,  # 15 MB
    'STREAM_RESOLUTION': 'medium',
    'PORT': 8080
}

for k, v in config.items():
    config[k] = os.getenv(k, v)
