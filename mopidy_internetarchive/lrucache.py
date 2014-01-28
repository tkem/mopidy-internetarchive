from __future__ import unicode_literals
import logging

from time import time

logger = logging.getLogger(__name__)


class LRUCache(dict):

    def __init__(self, size, ttl=3600):
        self.size = size
        self.ttl = ttl
        self.root = root = []
        root[:] = [root, root, None, 0]
        self.map = {}

    def __contains__(self, key):
        self._expire(time() - self.ttl)
        return super(LRUCache, self).__contains__(key)

    def __iter__(self):
        self._expire(time() - self.ttl)
        return super(LRUCache, self).__iter__()

    def __getitem__(self, key):
        self._expire(time() - self.ttl)
        return super(LRUCache, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key not in self:
            logger.debug('inserting new key %s', key)
            if len(self) == self.size:
                logger.debug('removing oldest key %s', self.root[0][2])
                del self[self.root[0][2]]
            root = self.root
            last = root[0]
            last[1] = root[0] = self.map[key] = [last, root, key, time()]
        else:
            logger.debug('updating key %s', key)
            root = self.root
            last = root[0]
            curr = self.map[key]
            curr[0][1] = curr[1]
            curr[1][0] = curr[0]
            curr[0] = last
            curr[1] = root
            last[1] = root[0] = curr
            curr[3] = time()
        return super(LRUCache, self).__setitem__(key, value)

    def __delitem__(self, key):
        super(LRUCache, self).__delitem__(key)
        logger.debug('removing key %s', key)
        prev, next, _, _ = self.map.pop(key)
        prev[1] = next
        next[0] = prev

    def _expire(self, t):
        root = self.root
        curr = root[1]
        while curr is not root and curr[3] < t:
            logger.debug('expiring key %s', curr[2])
            del self[curr[2]]
            curr = curr[1]
