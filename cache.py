import redis
import json
import xmltodict

cache = redis.Redis()
random_fields = ['salt', 'id']


def clean_content(dict_content: dict):
    content = {}
    for key in dict_content:
        if key not in random_fields:
            content[key] = dict_content[key]
    return content


def content_to_dict(raw_content: str, content_type: str):
    if content_type == 'application/json':
        # print(json.loads(raw_content))
        return json.loads(raw_content)
    elif content_type == 'application/xml':
        return xmltodict.parse(raw_content)
    else:
        pass


def is_in_db(service_url: str, request: str):
    if cache.hget(service_url, request):
        return True
    return False


def del_old(service_url: str):
    cache.delete(service_url)


def add_to_db(service_url: str, request: str, response: str):
    cache.hset(service_url, request, response)
