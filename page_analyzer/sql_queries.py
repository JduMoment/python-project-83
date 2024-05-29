def get_url_id(url_name):
    return f"""
            SELECT id FROM urls
            WHERE name ='{url_name}';
            """


def get_url_name(url_id):
    return f"""
            SELECT name FROM urls
            WHERE id ='{url_id}';
            """


def get_url_list():
    return """
           SELECT DISTINCT
           urls.id,
           urls.name AS ulr,
           url_checks.created_at AS last_check,
           url_checks.status_code
           FROM urls
           LEFT JOIN url_checks ON urls.id = url_checks.url_id
           ORDER BY url_checks.created_at DESC;
           """


def get_url_name_and_date(url_id):
    return f"""
            SELECT name, created_at FROM urls
            WHERE id ='{url_id}';
            """


def get_url_info(url_id):
    return f"""
            SELECT id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id ='{url_id}'
            ORDER BY created_at DESC;
            """


def insert_url(name, created_at):
    return f"""
            INSERT INTO urls (name, created_at)
            VALUES ('{name}', '{created_at}');
            """


def insert_url_check(url_id, status_code, h1, title, description, created_at):
    return f"""
            INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at)
            VALUES ('{url_id}', '{status_code}', '{h1}', '{title}', '{description}', '{created_at}');
            """
