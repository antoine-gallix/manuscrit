from pprint import pformat
import inspect
import os
from jinja2 import Template
import os.path

request_template_file = 'request_template'


def load_template(template_name):
    filepath = os.path.join(os.path.dirname(__file__), template_name)
    return Template(open(filepath).read())


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


def format_response(response, title=''):
    template = load_template(request_template_file)
    try:
        response_body = response.json()
    except ValueError:
        response_body = None
    return template.render(
        title=title,
        response=response,
        response_body=response_body)


def log_state(n=0):
    """log the name of the function, it's file and the local variables
    """

    # caller level
    caller_frame, calling_file, calling_line, calling_function, _, _ = inspect.stack()[
        1 + n]
    calling_file_name = os.path.basename(calling_file)
    caller_locals = pformat(caller_frame.f_locals)

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
    # dict version
    # for k, v in caller_frame.f_locals.iteritems():
    #     template.append('{} : {}'.format(k, v))
    # simple version
    template.append('{caller_locals}')
    template.append('\n')
    template.append('-----calling function\n')
    template.append(
        '{calling_function_2}() in {calling_file_name_2}\n({calling_file_2}:{calling_line_2})')

    template = '\n'.join(template)

    rendered = template.format(**locals())
    return rendered
