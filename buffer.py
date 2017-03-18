from collections import deque
from itertools import chain
from threading import Lock


class RingBuffer(object):
    def __init__(self, buffer_size=8192 * 4, chunk_size=1024):
        self.buffer_size = buffer_size
        self.chunk_size = chunk_size
        self.buffer = deque(
            maxlen=buffer_size // chunk_size
        )
        self._lock = Lock()

    def write(self, data):
        with self._lock:
            for chunk in self._get_chunks(data):
                self.buffer.append(chunk)

    def read_all(self):
        with self._lock:
            return self._dump()

    def clear(self):
        with self._lock:
            self.buffer.clear()

    def _dump(self):
        return bytes(chain(*list(self.buffer)))

    def _get_chunks(self, data):
        for i in range(0, len(data), self.chunk_size):
            yield data[i:i + self.chunk_size]
