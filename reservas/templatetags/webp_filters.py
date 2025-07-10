from django import template

register = template.Library()

@register.filter
def webp(url):
    if url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".png"):
        return url.rsplit('.', 1)[0] + ".webp"
    return url
