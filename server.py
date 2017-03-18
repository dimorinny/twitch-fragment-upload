import asyncio
from datetime import datetime

import pytz
from tornado import httpclient
from tornado import web
from tornado.escape import json_encode
from tornado.platform.asyncio import AsyncIOMainLoop

from config import config
from error import ApiException
from response import success, error, error_with
from upload import VkUploader, AsyncUploaderWrapper
from twitch import Twitch, AsyncTwitchWrapper


def generate_video_name(channel_name, timezone):
    return "{:%d.%m.%y %H:%M} {channel}" \
        .format(datetime.now(timezone), channel=channel_name)


# noinspection PyAbstractClass,PyMethodOverriding,PyAttributeOutsideInit
class TwitchStreamHandler(web.RequestHandler):
    def initialize(self, twitch, uploader):
        self.twitch = twitch
        self.uploader = uploader
        self.timezone = pytz.timezone(config['TIMEZONE'])

    async def get(self):
        name = generate_video_name(config['TWITCH_CHANNEL'], self.timezone)

        data = await self.twitch.get_stream_data()
        response = await self.uploader.upload(name, data)

        self.write_json(success({
            'url': response.url,
            'name': name
        }))

    def write_error(self, status_code, exc_info):
        error_class = exc_info[0]
        error_object = exc_info[1]

        if issubclass(error_class, ApiException):
            self.write_json(error_with(error_object.to_response()))
        else:
            self.write_json(error())

    def write_json(self, data):
        self.add_header('Content-Type', 'application/json')
        self.write(json_encode(data))
        self.finish()


def application(twitch, uploader):
    return web.Application([
        (r"/api/v1/upload", TwitchStreamHandler, dict(
            twitch=twitch,
            uploader=uploader
        )),
    ])


async def pereodic_stream_updates(twitch, interval):
    while True:
        await twitch.update_stream_data()
        await asyncio.sleep(interval)


def main():
    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()

    async_twitch = AsyncTwitchWrapper(
        loop,
        Twitch(
            config['RING_BUFFER_SIZE'] * 1024 * 1024,
            config['STREAM_RESOLUTION'],
            config['TWITCH_OAUTH'],
            config['TWITCH_CHANNEL']
        )
    )
    async_twitch.initialize()

    asyncio.Task(pereodic_stream_updates(async_twitch, 10))

    uploader = AsyncUploaderWrapper(
        loop,
        uploader=VkUploader(
            client=httpclient.AsyncHTTPClient(),
            token=config['VK_OAUTH'],
            group_id=config['VK_GROUP_ID']
        )
    )

    app = application(async_twitch, uploader)
    app.listen(config['PORT'])

    print('Listening port {port}...'.format(port=config['PORT']))
    loop.run_forever()


if __name__ == '__main__':
    main()
