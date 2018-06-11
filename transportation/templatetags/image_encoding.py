from django import template
from django.contrib.staticfiles.finders import find as find_static_file
from django.conf import settings

register = template.Library()

@register.simple_tag
def encode_static(path, encoding='base64', file_type='image'):
    """
    a template tag that returns a encoded string representation of a staticfile
    Usage::
        {% encode_static path [encoding] %}
    Examples::
        <img src="{% encode_static 'path/to/img.png' %}">
    """
    file_path = find_static_file(path)
    ext = file_path.split('.')[-1]
    file_str = get_file_data(file_path).encode(encoding)
    return u"data:{0}/{1};{2},{3}".format(file_type, ext, encoding, file_str)

def get_file_data(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
        return data