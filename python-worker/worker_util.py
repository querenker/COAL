import hashlib


def get_cache_filename(url):
    base_path = 'cache/'
    base_ext = '.ttl'
    hash = hashlib.md5()
    hash.update(url.encode('utf-8'))
    return base_path + hash.hexdigest()[:32] + base_ext
