from django import template
from django.views.generic.dates import ArchiveIndexView

from ..models import Blog, Tag

register = template.Library()

@register.simple_tag
def sidebar_context():
    blog_list = Blog.objects.all()
    date_list = Blog.objects.dates('post_date', 'year', 'DESC')
    tag_list = Tag.objects.exclude(blog__isnull=True).order_by('tag')
    context = {
        'blog_list': blog_list,
        'date_list': date_list,
        'tag_list': tag_list,
    }
    return context
