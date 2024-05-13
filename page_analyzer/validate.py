from validators import url


def is_correct(ent_url):
    return url(ent_url)
