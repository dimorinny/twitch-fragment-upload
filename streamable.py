import json
from datetime import datetime
from functools import partial
from uuid import uuid4

from tornado import httpclient

from error import UploadingException
from util import multipart_producer


class UploadResult(object):
    INVALID_ID = -1

    def __init__(self, response):
        self.status = response.get('status', self.INVALID_ID)
        self.shortcode = response.get('shortcode')


class Streamable(object):
    UPLOAD_URL = 'https://api.streamable.com/upload'
    UPLOADED_VIDEO_TEMPLATE = 'https://streamable.com/{video_id}'

    REQUEST_TIMEOUT = 60 * 3  # 3 minutes

    def __init__(self, client):
        self.client = client

    def video_url(self, video_id):
        return self.UPLOADED_VIDEO_TEMPLATE.format(video_id=video_id)

    async def upload(self, channel_name, data):
        boundary = uuid4().hex
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}

        producer = partial(
            multipart_producer,
            boundary,
            self._generate_video_name(channel_name),
            data
        )
        request = httpclient.HTTPRequest(
            method='POST',
            url=self.UPLOAD_URL,
            headers=headers,
            body_producer=producer,
            request_timeout=self.REQUEST_TIMEOUT
        )

        result = await self.client.fetch(request, raise_error=False)

        if result.code != 200:
            raise UploadingException

        return UploadResult(
            json.loads(str(result.body.decode("utf-8")))
        )

    @staticmethod
    def _generate_video_name(channel_name):
        return "{:%d.%m.%y %H:%M} {channel}" \
            .format(datetime.now(), channel=channel_name)
