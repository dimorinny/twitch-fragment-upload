import os

config = {
    'TWITCH_OAUTH': None,
    'TWITCH_CHANNEL': None,
    'RING_BUFFER_SIZE': 1024 * 1024 * 10,  # 10 MB
    'PORT': 8080
}

for k, v in config.items():
    config[k] = os.getenv(k, v)
