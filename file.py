import requests


def zapros(url):
    response = requests.get(url)
    return response


print(zapros('https://stub.com'))
