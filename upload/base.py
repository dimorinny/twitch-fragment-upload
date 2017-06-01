from concurrent.futures import ThreadPoolExecutor

from tornado import httpclient

from config import config
from upload.streamable import StreamableUploader
from upload.vk import VkUploader


class UploadResult(object):
    INVALID_ID = -1

    def __init__(self, url):
        self.status = 'success'
        self.url = url


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


def resolve_uploader():
    providers = {
        'vk': lambda: VkUploader(
            client=httpclient.AsyncHTTPClient(),
            token=config['VK_OAUTH'],
            group_id=config['VK_GROUP_ID']
        ),
        'streamable': lambda: StreamableUploader(
            client=httpclient.AsyncHTTPClient()
        )
    }

    if config['UPLOAD_BACKEND'] not in providers:
        raise Exception('''
        Upload backend is not specified.
        Allowed backends: {backends}'''.format(
            backends=', '.join(providers.keys())
        ))

    return providers[config['UPLOAD_BACKEND']]()
