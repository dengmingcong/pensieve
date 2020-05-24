import collections
import logging
import xml.etree.ElementTree as ET
from datetime import date

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic, View
from django.views.generic.base import TemplateView
from django.views.generic.dates import ArchiveIndexView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import markdown

from .markdown_processor import MarkdownProcessor
from .models import Blog, BlogAuthor, BlogComment, Tag

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger('django')


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
    fields = ['title', 'slug', 'content', 'blog_author', 'post_date', 'tags']
    permission_required = 'blog.add_blog'

    def form_valid(self, form):
        md = MarkdownProcessor(form.instance.content)
        md.to_xml()
        form.instance.content_xml = ET.tostring(md.root, encoding='unicode')
        return super().form_valid(form)


class BlogUpdate(PermissionRequiredMixin, UpdateView):
    """
    Generic class-based view for updating a particular blog.
    """
    model = Blog
    fields = ['content']
    permission_required = 'blog.change_blog'

    def form_valid(self, form):
        md = MarkdownProcessor(form.instance.content)
        md.to_xml()
        form.instance.content_xml = ET.tostring(md.root, encoding='unicode')
        return super().form_valid(form)


class PreviewMarkdownView(View):
    """
    Converts markdown to HTML.
    """
    def post(self, request, *args, **kwargs):
        # Return HTML string transformed from markdown.
        return JsonResponse(
            {
                'html': markdown.markdown(request.POST["origin-markdown"])
            },
            json_dumps_params={'ensure_ascii': False}
        )


class BlogSectionUpdate(PermissionRequiredMixin, View):
    """
    Class-based view for updating only sections.
    """
    permission_required = 'blog.change_blog'

    def get(self, request, *args, **kwargs):
        blog = self.get_blog(**kwargs)
        seqnum = kwargs["seqnum"]
        logger.debug("seqnum: {}".format(seqnum))
        root, section = self.parse_xml(blog, seqnum)

        return JsonResponse(
            {
                'section_text': self.extract_and_join_element_text(section, "\n")
            },
            json_dumps_params={'ensure_ascii': False}
        )

    def post(self, request, *args, **kwargs):
        blog = self.get_blog(**kwargs)
        seqnum = kwargs["seqnum"]
        logger.debug("seqnum: {}".format(seqnum))
        root, old_section = self.parse_xml(blog, seqnum)

        # Convert plain text to XML tree.
        md = MarkdownProcessor(request.POST["section-text"])
        last_id_list = list(map(int, seqnum.split(".")))
        last_id_list[-1] = last_id_list[-1] - 1 if last_id_list[-1] > 0 else last_id_list[-1]
        md.id_list = last_id_list
        md.to_xml()

        # Update section element within XML tree via replacing old section element.
        new_section = md.root.find("h")
        logger.debug("Update element '{}' to '{}'".format(
            ET.tostring(old_section, encoding='unicode'),
            ET.tostring(new_section, encoding='unicode'))
        )
        parent_map = dict((c, p) for p in root.iter() for c in p)
        parent = parent_map[old_section]
        logger.debug("Parent element before replacing child: {}".format(ET.tostring(parent, encoding='unicode')))
        self.replace_child(parent, new_section, old_section)
        logger.debug("XML root after replacing child: {}".format(ET.tostring(md.root, encoding='unicode')))

        # Concatenate inner text of XML elements and update blog's fields 'content' and 'content_xml'.
        blog.content = self.extract_and_join_element_text(root, "\n")
        logger.debug("Update blog's content field to: {}".format(blog.content))
        blog.content_xml = ET.tostring(root, encoding='unicode')
        logger.debug("Update blog's content_xml field to: {}".format(blog.content_xml))
        blog.save()

        # Return HTML string transformed by markdown.
        return JsonResponse(
            {
                'section_html': markdown.markdown(request.POST["section-text"])
            },
            json_dumps_params={'ensure_ascii': False}
        )

    @staticmethod
    def replace_child(parent, new, old):
        """
        Replaces a sub-element.

        :param parent: Parent element whose child would be replaced
        :param new: New XML element
        :param old: Old XML element to be replaced
        :return: None
        """
        parent.insert(list(parent).index(old), new)
        parent.remove(old)

    @staticmethod
    def get_blog(**kwargs):
        """
        Returns blog object identified by post date and slug.

        :param kwargs:
        :return: instance of Blog model
        """
        post_date = "-".join(map(str, [kwargs['year'], kwargs['month'], kwargs['day']]))

        # Find blog by post date and slug.
        blog = Blog.objects.get(post_date=post_date, slug=kwargs['slug'])
        logger.debug("blog title: {}".format(blog.title))

        return blog

    @staticmethod
    def parse_xml(blog, seqnum):
        """
        Parses from blog's field content_xml.

        :param blog: An instance of Blog model
        :param seqnum: specific sequence number
        :return: a tuple of root element and specific section
        """
        # Parses an XML section from string.
        root = ET.fromstring(blog.content_xml)
        logger.debug("root: {}".format(ET.tostring(root, encoding='unicode')))
        section = root.find(".//*[@id='{}']".format(seqnum))
        logger.debug("section: {}".format(ET.tostring(section, encoding='unicode')))

        return root, section

    def extract_and_join_element_text(self, element, sep):
        """
        Join inner text of given element and all of its children.

        :param element: An instance of xml Element.
        :param sep: String as separator.
        :return: The concatenated string.
        """
        logger.debug(sep.join(list(self.itertext(element))))
        return sep.join(list(self.itertext(element)))

    def itertext(self, element):
        """Create text iterator.

        The iterator loops over the element and all subelements in document
        order, returning all inner text.
        """
        tag = element.tag
        if not isinstance(tag, str) and tag is not None:
            return
        t = element.text
        if t:
            yield t
        else:
            yield ""
        for sub_element in element:
            yield from self.itertext(sub_element)
            t = sub_element.tail
            if t:
                yield t


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
