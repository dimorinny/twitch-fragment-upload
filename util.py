import mimetypes

from tornado import gen


async def multipart_producer(boundary, filename, data, write):
    boundary_bytes = boundary.encode()

    filename_bytes = filename.encode()
    write(b'--%s\r\n' % (boundary_bytes,))
    write(b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' %
          (filename_bytes, filename_bytes))

    mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    write(b'Content-Type: %s\r\n' % (mime_type.encode(),))
    write(b'\r\n')
    write(data)

    write(b'\r\n')
    await gen.moment
    write(b'--%s--\r\n' % (boundary_bytes,))
