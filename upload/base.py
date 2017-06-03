import abc
from concurrent.futures import ThreadPoolExecutor


class BaseUploader(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def upload(self, name, data):
        pass


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


class UploadResult(object):
    INVALID_ID = -1

    def __init__(self, url):
        self.status = 'success'
        self.url = url
