import json
import logging
import time

import requests


class JsonHttpClient(object):

    def __init__(self, host: str):
        self.host = host

    def get_json(self, path: str, retry: int = -1, method: str = 'GET', **kwargs) -> dict:
        url = join_url(self.host, path)
        retry_times = 0
        while retry_times != retry:
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                if retry_times:
                    logging.warning(f'Succeed after retry {retry_times} times, URL: {url}')
                return json.loads(response.text)
            except Exception as e:
                logging.debug(e)
                retry_times += 1
                if retry_times % 100 == 0:
                    logging.error(e)
                time.sleep(0.1)


def join_url(lhs, rhs):
    if len(rhs) and rhs[0] != '/':
        rhs = '/' + rhs
    return lhs + rhs
