from wsgiref import simple_server
import json
from datetime import datetime
import pytz
from dateutil import parser


def application(environ, start_response):
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')
    response_headers = [('Content-type', 'application/json; charset=utf-8')]

    if method == 'GET' and (path == '/' or path.startswith('/')):
        tz_name = path[1:] or 'GMT'
        response_headers = [('Content-type', 'text/html; charset=utf-8')]
        response_body = get_current_time(tz_name)
    elif method == 'POST' and path == '/api/v1/convert':
        try:
            request_body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0)))
            response_body = convert_time(request_body)
        except Exception as e:
            response_body = json.dumps({'error': str(e)})
            start_response('400 Bad Request', response_headers)
            return [response_body.encode()]
    elif method == 'POST' and path == '/api/v1/datediff':
        try:
            request_body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0)))
            response_body = date_difference(request_body)
        except Exception as e:
            response_body = json.dumps({'error': str(e)})
            start_response('400 Bad Request', response_headers)
            return [response_body.encode()]
    else:
        start_response('404 Not Found', response_headers)
        return [b'Not Found']

    start_response('200 OK', response_headers)
    return [response_body.encode()]


def get_current_time(tz_name):
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return f'<html><body>Unknown timezone: {tz_name}</body></html>'

    current_time = datetime.now(tz)
    return f'<html><body>Current time in {tz_name} is {current_time.strftime("%Y-%m-%d %H:%M:%S")}</body></html>'


def convert_time(request_body):
    data = json.loads(request_body)
    date_str = data['date']
    from_tz_str = data['tz']
    to_tz_str = data['target_tz']

    from_tz = pytz.timezone(from_tz_str)
    to_tz = pytz.timezone(to_tz_str)

    from_time = parser.parse(date_str)
    from_time = from_tz.localize(from_time)
    to_time = from_time.astimezone(to_tz)

    return json.dumps({'converted_time': to_time.strftime('%Y-%m-%d %H:%M:%S')})


def date_difference(request_body):
    data = json.loads(request_body)
    first_date_str = data['first_date']
    first_tz_str = data['first_tz']
    second_date_str = data['second_date']
    second_tz_str = data['second_tz']

    first_tz = pytz.timezone(first_tz_str)
    second_tz = pytz.timezone(second_tz_str)

    first_date = parser.parse(first_date_str)
    first_date = first_tz.localize(first_date)

    second_date = parser.parse(second_date_str)
    second_date = second_tz.localize(second_date)

    diff_seconds = int((second_date - first_date).total_seconds())

    return json.dumps({'diff_in_seconds': diff_seconds})


if __name__ == '__main__':
    httpd = simple_server.make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
