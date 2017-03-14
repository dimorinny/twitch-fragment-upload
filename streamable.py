from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import requests
import time

from error import UploadingException, UploadingCheckLimitException


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

    def upload(self, name, data):
        for _ in range(self.RETRIES_COUNT):
            answer = self._do_upload(name, data)

            print(answer)

            if answer.status_code != requests.codes.ok:
                raise UploadingException

            result = UploadResult(answer.json())

            print('Checking uploaded video with shortcode: {shortcode}'
                  .format(shortcode=result.shortcode))

            if self._check_uploading(result):
                return result

            time.sleep(self.RETRIES_INTERVAL)

        raise UploadingCheckLimitException

    def _do_upload(self, name, data):
        return requests.post(
            url=self.UPLOAD_URL,
            files={name: BytesIO(data)}
        )

    def _check_uploading(self, result):
        return requests.get(self.video_url(result.shortcode)).status_code == 200


class AsyncStreamableWrapper(object):
    def __init__(self, loop, streamable):
        self.executor = ThreadPoolExecutor()
        self.loop = loop
        self.streamable = streamable

    def video_url(self, video_id):
        return self.streamable.video_url(video_id)

    async def upload(self, name, data):
        return await self.loop.run_in_executor(
            self.executor,
            self.streamable.upload,
            name,
            data
        )
