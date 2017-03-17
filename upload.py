from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import requests

from error import UploadingException


class UploadResult(object):
    INVALID_ID = -1

    def __init__(self, response):
        self.status = 'success'
        self.url = response['player']


class VkUploader(object):
    VK_API_VERSION = '5.62'
    PREPARE_UPLOAD_URL = 'https://api.vk.com/method/video.save'
    UPLOADED_VIDEO_INFO_URL = 'https://api.vk.com/method/video.get'

    REQUEST_TIMEOUT = 60 * 3  # 3 minutes

    def __init__(self, client, token, group_id):
        self.client = client
        self.token = token
        self.group_id = group_id

    def upload(self, name, data):
        prepare_result = self._prepare_upload(name)

        print('Prepare: ' + prepare_result.text)
        if prepare_result.status_code != requests.codes.ok:
            raise UploadingException
        prepare_result_json = prepare_result.json()

        upload_result = self._upload(
            url=prepare_result_json['response']['upload_url'],
            data=data
        )
        print('Upload: ' + upload_result.text)
        if upload_result.status_code != requests.codes.ok:
            raise UploadingException
        video_id = upload_result.json()['video_id']

        get_result = self._get_uploaded(video_id)
        print('Result: ' + get_result.text)
        if get_result.status_code != requests.codes.ok:
            raise UploadingException

        items_response = get_result.json()['response']
        item = items_response[1] if len(items_response) > 1 else None
        if not item:
            raise UploadingException

        return UploadResult(
            response=item
        )

    def _prepare_upload(self, name):
        return requests.get(
            url=self.PREPARE_UPLOAD_URL,
            params=dict(
                name=name,
                group_id=self.group_id,
                version=self.VK_API_VERSION,
                access_token=self.token
            )
        )

    def _get_uploaded(self, video_id):
        return requests.get(
            url=self.UPLOADED_VIDEO_INFO_URL,
            params=dict(
                videos='-{group_id}_{video_id}'
                    .format(group_id=self.group_id, video_id=video_id),
                version=self.VK_API_VERSION,
                access_token=self.token
            )
        )

    @staticmethod
    def _upload(url, data):
        return requests.post(
            url=url,
            files={'file': BytesIO(data)}
        )


class AsyncUploaderWrapper(object):
    def __init__(self, loop, uploader):
        self.executor = ThreadPoolExecutor()
        self.loop = loop
        self.uploader = uploader

    async def upload(self, name, data):
        return await self.loop.run_in_executor(
            self.executor,
            self.uploader.upload,
            name,
            data
        )
