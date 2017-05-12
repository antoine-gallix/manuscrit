from pprint import pformat
import inspect
import json
import os

def format_object(o, show_all=False, show_values=False):
    """Return a string describing an object

    options:
    "show_all" : also show "__xxxx__" attributes
    "show_values" : show attributes values, else show types
    """

    # analyse
    info = {}
    info['name'] = getattr(o, "__name__", "")
    info['type'] = str(type(o))
    info['attributes'] = []
    info['functions'] = []
    info['errors'] = []
    for att_name in dir(o):
        if att_name[0:2] == "__" and not show_all:
            continue
        try:  # skip problematic attributes
            att = getattr(o, att_name)
        except Exception:
            info['errors'].append(att_name)
            continue
        if callable(att):
            info['functions'].append(att_name)
        else:
            info['attributes'].append(att_name)

    # build output
    output = []
    output.append("-" * 30)
    if info['name']:
        output.append('name : {}'.format(info['name']))
    output.append('type : {}'.format(info['type']))

    if info['attributes']:
        output.append("-" * 10 + 'attributes' + "-" * 10)
        for a in info['attributes']:
            if show_values:
                output.append("{:20s}{:40s}".format(
                    a, str(getattr(o, a, None))))
            else:
                output.append("{:20s}{:40s}".format(
                    a, type(getattr(o, a, None))))

    if info['functions']:
        output.append("-" * 10 + 'functions' + "-" * 11)
        for a in info['functions']:
            output.append(a + '()')

    if info['errors']:
        output.append("-" * 12 + 'errors' + "-" * 12)
        for a in info['errors']:
            output.append(a)

    if info['attributes'] or info['functions'] or info['errors']:
        output.append("-" * 30)

    return '\n'.join(output)


def format_request(r, **kwargs):
    """Format a Requests request object for nicer debugging.

    Print request method, url, status code, errors, payload, and response.
    """
    sep = '-' * 10
    query = kwargs.get('query', False)
    # ----| gather information
    if query:  # query only
        body = pformat(json.loads(r.body)) if r.body else ''
        method = r.method
        path_url = r.path_url
        status = None
        json_content = pformat(r.json)
        request_headers = pformat(dict(r.headers))
        content = None
        request_body = None
    else:  # query + response
        request_body = pformat(json.loads(r.request.body)
                               ) if r.request.body else ''
        method = r.request.method
        path_url = r.request.path_url
        status = r.status_code
        if not r.ok:
            reason = r.reason
        try:
            json_content = pformat(r.json())
        except ValueError:
            json_content = None
        request_headers = pformat(dict(r.request.headers))
        response_headers = pformat(dict(r.headers))

    # ----| build template
    template = ''
    template += '{sep}' * 3
    template += '\n'
    template += '{sep}QUERY'
    template += '\n\n'
    template += '{method} {url}'
    template += '\n'
    if kwargs.get('show_headers',False):
        template += '\n'
        template += '{sep}HEADERS'
        template += '\n\n'
        template += '{request_headers}'
        template += '\n'
    if request_body:
        template += '\n'
        template += '{sep}CONTENT'
        template += '\n\n'
        template += '{request_body}'
        template += '\n'
    template += '\n\n'
    if not query:
        template += '{sep}RESPONSE\n'
        if r.ok:
            template += 'OK : {status}'
        else:
            template += 'Error : {status} {reason}'
    if json_content:
        template += '\n{json_content}'
    template += '\n\n'
    template += '{sep}' * 3

    # ----| format
    return template.format(
        url=r.url,
        **locals())


def log_state(n=0):
    """log the name of the function, it's file and the local variables
    """

    # caller level
    caller_frame, calling_file, calling_line, calling_function, _, _ = inspect.stack()[
        1 + n]
    calling_file_name = os.path.basename(calling_file)
    # caller_locals = pformat(caller_frame.f_locals)

    # over caller level
    (caller_frame_2, calling_file_2, calling_line_2,
     calling_function_2, _, _) = inspect.stack()[2 + n]
    calling_file_name_2 = os.path.basename(calling_file_2)

    # build template
    template = []

    template.append('function : {calling_function}()')
    template.append('file : {calling_file_name}')
    template.append('location : {calling_file}:{calling_line}')
    template.append('\n')
    template.append('----| arguments')
    template.append('\n')
    for k,v in caller_frame.f_locals.iteritems():
        template.append('{} : {}'.format(k,v))
    # template.append('{caller_locals}')
    template.append('\n')
    template.append('-----calling function\n')
    template.append(
        '{calling_function_2}() in {calling_file_name_2}\n({calling_file_2}:{calling_line_2})')
    template = '\n'.join(template)

    rendered = template.format(**locals())
    return rendered
