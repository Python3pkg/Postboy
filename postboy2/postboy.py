# coding=utf-8
import pycurl
from io import BytesIO
from urllib.parse import urlencode
import re


class PostBoy:
    ZONE_PATTERN = r"((https?|ftp)://)?(?P<zone>[a-zA-Z0-9.\-]+[a-zA-Z0-9\-])/?(.*)"
    TITLE_PATTERN = r"<title.*?>\s*(?P<title>[\s\S]*?)\s*</title>"
    HEAD_PATTERN = r"<head.*?>\s*(?P<head>[\s\S]*?)\s*</head>"
    BODY_PATTERN = r"<body.*?>\s*(?P<body>[\s\S]*?)\s*</body>"

    def __init__(self, url, codec='utf-8', con_timeout=5, timeout=10, followlocation=True, maxredirs=10):
        self._url = url
        self._codec = codec
        self._con_timeout = con_timeout
        self._timeout = timeout
        self._maxredirs = maxredirs
        self._followlocation = followlocation
        self._header = BytesIO()
        self._data = BytesIO()

    def _curl_for_get(self, parameters):
        self._header.truncate(0)
        self._data.truncate(0)
        curl = self._basic_curl()
        querymeters = '' if len(parameters) == 0 else '?' + urlencode(parameters)
        curl.setopt(pycurl.URL, self._url + querymeters)
        return curl

    def _curl_for_post(self, parameters):
        self._header.truncate(0)
        self._data.truncate(0)
        curl = self._basic_curl()
        postfields = urlencode(parameters)
        curl.setopt(pycurl.POSTFIELDS, postfields)
        curl.setopt(pycurl.URL, self._url)
        return curl

    def _basic_curl(self):
        curl = pycurl.Curl()
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.CONNECTTIMEOUT, self._con_timeout)
        curl.setopt(pycurl.TIMEOUT, self._timeout)
        curl.setopt(pycurl.FOLLOWLOCATION, self._followlocation)
        curl.setopt(pycurl.MAXREDIRS, self._maxredirs)
        curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0)
        curl.setopt(pycurl.USERAGENT,
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36')
        curl.setopt(pycurl.WRITEHEADER, self._header)
        curl.setopt(pycurl.WRITEDATA, self._data)
        return curl

    def get(self, parameters={}):
        curl = self._curl_for_get(parameters)
        return self._perform(curl)

    def post(self, parameters={}):
        curl = self._curl_for_post(parameters)
        return self._perform(curl)

    def _perform(self, curl):
        try:
            curl.perform()
        except pycurl.error as e:
            return {
                'error': {
                    'pycurl-code': e.args[0],
                    'description': e.args[1]
                }
            }
        status = self._get_status_info(curl)
        header = self._get_header_info()
        data = self._get_data_info()
        result = {}
        result.update(status)
        result.update(header)
        result.update(data)
        return result

    def _get_status_info(self, curl):
        code = curl.getinfo(pycurl.HTTP_CODE)
        url = curl.getinfo(pycurl.EFFECTIVE_URL)
        zone_result = re.match(self.ZONE_PATTERN, url, re.IGNORECASE)
        zone = zone_result and zone_result.group('zone')
        return {
            'status': {
                'http-code': code,
                'url': url,
                'zone': zone
            }
        }

    def _get_header_info(self):
        header = self._header.getvalue()
        decoded_header = header.decode(encoding=self._codec)
        return {
            'header': self._splitted_header(decoded_header)
        }

    def _splitted_header(self, decoded_header):
        result = {'raw': decoded_header}
        splitted_header = decoded_header.split('\r\n')
        part = 0
        for i, line in enumerate(splitted_header):
            if line is '':
                part += 1
            else:
                p = result.get(part, None)
                if not p:
                    result[part] = {}
                    protocol, status_code = line.split(' ', 1)
                    result[part]['protocol'] = protocol
                    result[part]['status-code'] = status_code
                    continue
                key, value = line.split(':', 1)
                item = result[part].get(key, None)
                if item:
                    if type(item) == str:
                        result[part][key] = [result[part][key]]
                    result[part][key].append(value[1:])
                else:
                    result[part][key] = value[1:]
        result['parts'] = part - 1
        return result

    def _get_data_info(self):
        data = self._data.getvalue()
        decoded_data = data.decode(encoding=self._codec)
        title_result = re.search(self.TITLE_PATTERN, decoded_data, re.IGNORECASE)
        title = title_result and title_result.group('title')
        head_result = re.search(self.HEAD_PATTERN, decoded_data, re.IGNORECASE)
        head = head_result and head_result.group('head')
        body_result = re.search(self.BODY_PATTERN, decoded_data, re.IGNORECASE)
        body = body_result and body_result.group('body')
        return {
            'data': {
                'raw': decoded_data,
                'title': title,
                'head': head,
                'body': body,
            }
        }


if __name__ == '__main__':
    result = PostBoy('http://www.baidu.com').get()

    error = result.get('error')
    if error:
        print((error.get('pycurl-code')))
        print((error.get('description')))
    header = result.get('header')
    if header:
        parts = header.get('parts')
        for i in range(parts):
            print((header.get(i)))

    data = result.get('data')
    if data:
        print((data.get('title')))

    print(('-' * 40))
    result = PostBoy('http://www.douban.com').get()

    error = result.get('error')
    if error:
        print((error.get('pycurl-code')))
        print((error.get('description')))
    header = result.get('header')
    if header:
        parts = header.get('parts')
        for i in range(parts):
            print((header.get(i)))

    data = result.get('data')
    if data:
        print((data.get('title')))

    print(('-' * 40))
    result = PostBoy('http://127.0.0.1:5000/post_test').post({'username': 'meng'})

    error = result.get('error')
    if error:
        print((error.get('pycurl-code')))
        print((error.get('description')))
    header = result.get('header')
    if header:
        parts = header.get('parts')
        for i in range(parts):
            print((header.get(i)))

    data = result.get('data')
    print(data)
