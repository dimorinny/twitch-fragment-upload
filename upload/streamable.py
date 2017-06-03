from io import BytesIO

import requests

from error import UploadingException
from upload.base import BaseUploader, UploadResult


class StreamableUploader(BaseUploader):
    UPLOAD_ENDPOINT = 'https://api.streamable.com/upload'
    URL_TEMPLATE = 'https://streamable.com/e/{code}'

    REQUEST_TIMEOUT = 60 * 3  # 3 minutes

    def __init__(self, client, user, password):
        self.client = client
        self.user = user
        self.password = password

    def upload(self, name, data):
        upload_result = self._upload(name, data)
        print('Upload: ' + upload_result.text)

        json_result = upload_result.json()

        if upload_result.status_code != requests.codes.ok or json_result['status'] != 1:
            raise UploadingException

        return UploadResult(
            url=self.URL_TEMPLATE.format(code=upload_result.json()['shortcode'])
        )

    def _upload(self, name, data):
        return requests.post(
            url=self.UPLOAD_ENDPOINT,
            params=dict(
                title=name
            ),
            files=dict(
                file=BytesIO(data)
            ),
            timeout=self.REQUEST_TIMEOUT,
            auth=self._auth_data()
        )

    def _auth_data(self):
        return (self.user, self.password) \
            if bool(self.user and self.password) \
            else None
