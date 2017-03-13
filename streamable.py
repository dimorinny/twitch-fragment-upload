import asyncio
import json
from functools import partial
from uuid import uuid4

from tornado import httpclient

from error import UploadingException, UploadingCheckLimitException
from util import multipart_producer


class UploadResult(object):
    INVALID_ID = -1

    def __init__(self, response):
        self.status = response.get('status', self.INVALID_ID)
        self.shortcode = response.get('shortcode')


class Streamable(object):
    UPLOAD_URL = 'https://api.streamable.com/upload'
    UPLOADED_VIDEO_TEMPLATE = 'https://streamable.com/e/{video_id}'

    REQUEST_TIMEOUT = 60 * 3  # 3 minutes
    RETRIES_COUNT = 10
    RETRIES_INTERVAL = 10  # 10 seconds

    def __init__(self, client):
        self.client = client

    def video_url(self, video_id):
        return self.UPLOADED_VIDEO_TEMPLATE.format(video_id=video_id)

    async def upload(self, name, data):
        for _ in range(self.RETRIES_COUNT):
            answer = await self._do_upload(name, data)

            print(answer)

            if answer.code != 200:
                raise UploadingException

            result = UploadResult(
                json.loads(str(answer.body.decode("utf-8")))
            )

            if self._check_uploading(result):
                return result

            await asyncio.sleep(self.RETRIES_INTERVAL)

        raise UploadingCheckLimitException

    async def _do_upload(self, name, data):
        boundary = uuid4().hex
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}

        producer = partial(
            multipart_producer,
            boundary,
            name,
            data
        )
        request = httpclient.HTTPRequest(
            method='POST',
            url=self.UPLOAD_URL,
            headers=headers,
            body_producer=producer,
            request_timeout=self.REQUEST_TIMEOUT
        )

        return await self.client.fetch(request, raise_error=False)

    async def _check_uploading(self, result):
        request = httpclient.HTTPRequest(
            url=self.video_url(result.shortcode),
            request_timeout=self.REQUEST_TIMEOUT
        )

        print('Checking uploaded video with shortcode: {shortcode}'.format(shortcode=result.shortcode))

        answer = await self.client.fetch(request, raise_error=False)

        return answer.code == 200
