from urllib.parse import urlparse

urls = 'https://www.yandex'
url = urlparse(urls)
print(url)
print('://'.join([url.scheme, url.netloc]))