import asyncio

from tornado import httpclient
from tornado import web
from tornado.escape import json_encode
from tornado.platform.asyncio import AsyncIOMainLoop

from config import config
from response import success, error
from streamable import Streamable
from twitch import Twitch, AsyncTwitchWrapper


# noinspection PyAbstractClass,PyMethodOverriding,PyAttributeOutsideInit
class TwitchStreamHandler(web.RequestHandler):
    def initialize(self, twitch, streamable):
        self.twitch = twitch
        self.streamable = streamable

    async def get(self):
        data = await self.twitch.get_stream_file()
        response = await self.streamable.upload(
            config['TWITCH_CHANNEL'],
            data
        )
        self.write_json(success({
            'url': self.streamable.video_url(response.shortcode)
        }))

    def write_json(self, data):
        self.add_header('Content-Type', 'application/json')
        self.write(json_encode(data))
        self.finish()

    def write_error(self, status_code, **kwargs):
        self.write_json(error())


def application(twitch, streamable):
    return web.Application([
        (r"/api/v1/upload", TwitchStreamHandler, dict(
            twitch=twitch,
            streamable=streamable
        )),
    ])


def main():
    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()

    async_twitch = AsyncTwitchWrapper(
        loop,
        Twitch(
            config['RING_BUFFER_SIZE'],
            config['TWITCH_OAUTH'],
            config['TWITCH_CHANNEL']
        )
    )
    streamable = Streamable(
        client=httpclient.AsyncHTTPClient()
    )

    app = application(async_twitch, streamable)
    app.listen(config['PORT'])

    print('Listening port {port}...'.format(port=config['PORT']))

    loop.run_forever()


if __name__ == '__main__':
    main()
