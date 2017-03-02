from concurrent.futures import ThreadPoolExecutor

from livestreamer import Livestreamer

from error import StreamBufferIsEmptyException


class Twitch(object):
    BUFFER_PING_PART = 5

    RING_BUFFER_SIZE_KEY = 'ringbuffer-size'
    OAUTH_TOKEN_KEY = 'oauth_token'
    LIVESTREAMER_PLUGIN_TWITCH = 'twitch'
    RESOLUTION_KEY = 'medium'

    def __init__(self, buffer_size, oauth, channel):
        self.oauth = oauth
        self.channel = channel
        self.buffer_size = buffer_size + (buffer_size // self.BUFFER_PING_PART)
        self.initialized = False
        self.stream = None

    def __del__(self):
        if self.initialized:
            self.stream.close()

    def initialize(self):
        stream = self._init_stream(self.oauth, self.channel)
        if stream:
            self.initialized = True
            self.stream = stream.open()

    def get_stream_data(self):

        # Try to initialize again
        if not self.initialized:
            self.initialize()
            raise StreamBufferIsEmptyException

        return self.stream.read(self.buffer_size)

    def ping_read(self):
        if self.initialized:
            self.stream.read(self.buffer_size // self.BUFFER_PING_PART)

    def stream_initialized(self):
        return self.stream is not None

    def _init_stream(self, oauth, channel):
        session = Livestreamer()

        session.set_plugin_option(
            self.LIVESTREAMER_PLUGIN_TWITCH,
            self.OAUTH_TOKEN_KEY,
            oauth
        )
        session.set_option(self.RING_BUFFER_SIZE_KEY, self.buffer_size)

        streams = session.streams(self._generate_stream_url(channel))
        return streams.get(self.RESOLUTION_KEY)

    @staticmethod
    def _generate_stream_url(channel):
        return 'https://www.twitch.tv/{channel}'.format(channel=channel)


class AsyncTwitchWrapper(object):
    def __init__(self, loop, twitch):
        self.executor = ThreadPoolExecutor()
        self.loop = loop
        self.twitch = twitch

    def initialize(self):
        self.twitch.initialize()

    async def get_stream_data(self):
        return await self.loop.run_in_executor(self.executor, self.twitch.get_stream_data)

    async def ping_read(self):
        return await self.loop.run_in_executor(self.executor, self.twitch.ping_read)
