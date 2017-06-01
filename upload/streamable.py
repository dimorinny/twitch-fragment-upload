from io import BytesIO

import requests

from error import UploadingException


class StreamableUploader(object):
    UPLOAD_ENDPOINT = 'https://api.streamable.com/upload'
    URL_TEMPLATE = 'https://streamable.com/e/{code}'

    REQUEST_TIMEOUT = 60 * 3  # 3 minutes

    def __init__(self, client):
        self.client = client

    def upload(self, name, data):
        upload_result = self._upload(name, data)
        json_result = upload_result.json()

        print('Upload: ' + upload_result.text)

        if upload_result.status_code != requests.codes.ok or json_result['status'] != 1:
            raise UploadingException

        from upload.base import UploadResult
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
            timeout=self.REQUEST_TIMEOUT
        )
