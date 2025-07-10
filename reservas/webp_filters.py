from django import template

register = template.Library()

@register.filter
def webp(url):
    return url.replace('.jpg', '.webp').replace('.jpeg', '.webp').replace('.png', '.webp')
