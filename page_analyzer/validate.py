from flask import flash
from validators import url


def url_is_correct(ent_url):
    validate_res = url(ent_url) and len(ent_url) < 255
    if not validate_res:
        flash('Некорректный URL', 'error')
    return validate_res
