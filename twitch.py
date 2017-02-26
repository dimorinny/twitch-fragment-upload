from concurrent.futures import ThreadPoolExecutor

from livestreamer import Livestreamer


class Twitch(object):
    OAUTH_TOKEN_KEY = 'oauth_token'
    LIVESTREAMER_PLUGIN_TWITCH = 'twitch'
    RESOLUTION_KEY = 'source'

    def __init__(self, buffer, oauth, channel):
        self.buffer = buffer
        self.stream = self._init_stream(oauth, channel).open()

    def __del__(self):
        self.stream.close()

    def get_stream_file(self):
        return self.stream.read(self.buffer)

    # TODO: Initialize livestreamer's ring buffer size
    def _init_stream(self, oauth, channel):
        session = Livestreamer()
        session.set_plugin_option(
            self.LIVESTREAMER_PLUGIN_TWITCH,
            self.OAUTH_TOKEN_KEY,
            oauth
        )

        streams = session.streams(self._generate_stream_url(channel))
        return streams[self.RESOLUTION_KEY]

    @staticmethod
    def _generate_stream_url(channel):
        return 'https://www.twitch.tv/{channel}'.format(channel=channel)


class AsyncTwitchWrapper(object):
    def __init__(self, loop, twitch):
        self.executor = ThreadPoolExecutor()
        self.loop = loop
        self.twitch = twitch

    async def get_stream_file(self):
        return await self.loop.run_in_executor(self.executor, self.twitch.get_stream_file)
