from concurrent.futures import ThreadPoolExecutor

from livestreamer import Livestreamer

from buffer import RingBuffer
from error import StreamBufferIsEmptyException


class Twitch(object):
    RING_BUFFER_SIZE_KEY = 'ringbuffer-size'
    OAUTH_TOKEN_KEY = 'oauth_token'
    LIVESTREAMER_PLUGIN_TWITCH = 'twitch'

    def __init__(self, buffer_size, resolution, oauth, channel):
        self.oauth = oauth
        self.resolution = resolution
        self.channel = channel

        self.buffer_size = buffer_size
        self.buffer = RingBuffer(
            buffer_size=buffer_size
        )

        self.initialized = False
        self.stream = None

    def __del__(self):
        if self.initialized:
            self.stream.close()

    def initialize(self):
        self.buffer.clear()
        stream = self._init_stream(self.oauth, self.channel)
        if stream:
            self.initialized = True
            self.stream = stream.open()

    def get_stream_data(self):
        if not self.initialized:
            print('Read: Try to initialize')
            self.initialize()
            raise StreamBufferIsEmptyException

        return self.buffer.read_all()

    def update_stream_data(self):
        if self.initialized:
            data = self.stream.read(self.buffer_size)
            print('Update: {length}'.format(length=len(data)))

            if len(data) != 0:
                self.buffer.write(data)
            else:
                print('Update: Try to initialize')
                self.initialize()

        else:
            print('Update: Try to initialize')
            self.initialize()

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
        return streams.get(self.resolution)

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

    async def update_stream_data(self):
        await self.loop.run_in_executor(self.executor, self.twitch.update_stream_data)
