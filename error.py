class ApiException(Exception):
    MESSAGE = None
    CODE = None

    def __init__(self):
        assert self.MESSAGE is not None
        assert self.CODE is not None

        super(ApiException, self).__init__(self.MESSAGE)

    def to_response(self):
        return {
            'code': self.CODE,
            'message': self.MESSAGE
        }


class StreamBufferIsEmptyException(ApiException):
    MESSAGE = 'Stream buffer is empty'
    CODE = 100


class UploadingException(ApiException):
    MESSAGE = 'Upload video error'
    CODE = 101
