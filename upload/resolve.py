from tornado import httpclient

from config import config
from upload.streamable import StreamableUploader
from upload.vk import VkUploader


def resolve_uploader():
    providers = {
        'vk': lambda: VkUploader(
            client=httpclient.AsyncHTTPClient(),
            token=config['VK_OAUTH'],
            group_id=config['VK_GROUP_ID']
        ),
        'streamable': lambda: StreamableUploader(
            client=httpclient.AsyncHTTPClient(),
            user=config['STREAMABLE_USER'],
            password=config['STREAMABLE_PASSWORD']
        )
    }

    if config['UPLOAD_BACKEND'] not in providers:
        raise Exception('''
        Upload backend is not specified.
        Allowed backends: {backends}'''.format(
            backends=', '.join(providers.keys())
        ))

    return providers[config['UPLOAD_BACKEND']]()
