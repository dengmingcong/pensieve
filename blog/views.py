import collections
from datetime import date

from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.generic.dates import ArchiveIndexView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import BlogModelForm
from .models import Blog, BlogAuthor, BlogComment, Tag


class Index(ArchiveIndexView):
    """
    Class-based view for home.

    Get all blogs ordered by date in descending order.
    In the template, comments detail won't be displayed.
    """

    allow_empty = True
    date_field = "post_date"
    model = Blog
    template_name = 'index.html'


class BlogArchiveView(ArchiveIndexView):
    """
    Archive blogs by dates and tag.
    """

    allow_empty = True
    date_field = "post_date"
    model = Blog

    def get_context_data(self, **kwargs):
        """
        Extends context by adding data grouped by date and tag to context.
        """
        context = super().get_context_data(**kwargs)
        object_dict_sorted_by_year = {}
        for date in context['date_list']:
            year = date.year
            object_dict_sorted_by_year[year] = Blog.objects.filter(post_date__year=year)
        ordered_object_dict_sorted_by_year = collections.OrderedDict(sorted(object_dict_sorted_by_year.items(), reverse=True))
        context['object_dict_sorted_by_year'] = ordered_object_dict_sorted_by_year
        
        object_dict_sorted_by_tag = {}
        for tag in Tag.objects.all():
            related_objects = tag.blog_set.all()
            if related_objects:
                object_dict_sorted_by_tag[tag.tag] = related_objects
        ordered_object_dict_sorted_by_tag = collections.OrderedDict(sorted(object_dict_sorted_by_tag.items()))
        context['object_dict_sorted_by_tag'] = ordered_object_dict_sorted_by_tag

        return context


class TagArchiveView(generic.ListView):
    """
    Archive by tag.

    The URL should be 'category/<str:tag>/'.
    """

    model = Blog
    template_name = "blog/blog_archive_tag.html"

    def get_queryset(self):
        tag = get_object_or_404(Tag, tag=self.kwargs['tag'])
        blog_with_tag = Blog.objects.filter(tags=tag)
        return blog_with_tag

    def get_context_data(self, **kwargs):
        """
        Add the tag name to context.
        """
        context = super().get_context_data(**kwargs)
        context['tag'] = self.kwargs['tag']
        return context


class BlogDetailView(generic.DetailView):
    """
    Class-based view for one particular blog.
    """

    context_object_name = "blog"

    def get_queryset(self):
        post_date = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        return Blog.objects.filter(post_date=post_date, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """
        Add extra data ('comment number') to context.

        BETTER WAY:
            In template, use 'blog.blogcomment_set.all.count' to get the count.
        """
        context = super().get_context_data(**kwargs)
        post_date = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        blog = get_object_or_404(Blog, post_date=post_date, slug=self.kwargs['slug'])
        comment_number = BlogComment.objects.filter(blog=blog).count()
        context['comment_number'] = comment_number
        return context


class BlogCreate(PermissionRequiredMixin, CreateView):
    """
    Generic class-based view for adding a new blog.
    """
    model = Blog
    form_class = BlogModelForm
    permission_required = 'blog.add_blog'


class BlogUpdate(PermissionRequiredMixin, UpdateView):
    """
    Generic class-based view for updating a particular blog.
    """
    model = Blog
    form_class = BlogModelForm
    permission_required = 'blog.change_blog'


class BlogDelete(PermissionRequiredMixin, DeleteView):
    """
    Generic class-based view for deleting a particular blog.
    """
    model = Blog
    success_url = reverse_lazy("index")
    permission_required = 'blog.delete_blog'


class BlogAuthorListView(generic.ListView):
    """
    The generic class-based view for list of all blog-authors.
    """

    model = BlogAuthor


class BlogAuthorDetailView(generic.DetailView):
    """
    Class-based detail view for one particular blog-author.
    """

    model = BlogAuthor


class AboutThisBlogView(TemplateView):
    """
    Template view for the template of blog website introduction.
    """

    template_name = 'about_this_blog.html'



class AboutMeView(TemplateView):
    """
    Template view for the template of self-introduction.
    """

    template_name = 'about_me.html'
