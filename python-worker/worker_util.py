import hashlib

def get_cache_filename(url):
    base_path = 'cache/'
    base_ext = '.ttl'
    hash_value = hashlib.pbkdf2_hmac('md5', url, 16)
    return base_path + hash_value + base_ext
