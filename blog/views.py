from django.shortcuts import render
from django.views import generic

from .models import Blog, BlogAuthor



def index(request):
    """
    View function for home page of site.
    """
    
    blog_num = Blog.objects.all().count()
    blog_author_num = BlogAuthor.objects.all().count()

    return render(
        request,
        'index.html',
        context={
            'blog_num': blog_num,
            'blog_author_num': blog_author_num
        }
    )


class BlogListView(generic.ListView):
    """
    The generic class-based view for list of all blogs.
    """

    model = Blog
    paginate_by = 10


class BlogDetailView(generic.DetailView):
    """
    Class-based view for one particular blog.
    """

    model = Blog


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
