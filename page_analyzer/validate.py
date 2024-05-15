from validators import url


def url_is_correct(ent_url):
    return url(ent_url) and len(ent_url) < 255
