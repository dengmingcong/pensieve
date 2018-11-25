from django.urls import path
from django.views.generic.dates import ArchiveIndexView, YearArchiveView

from . import views
from .models import Blog


urlpatterns = [
    # Index (home page)
    path('', views.Index.as_view(), name='index'),
    # Archive
    path('archive/', views.BlogArchiveView.as_view(), name='archive'),
    # Archive by tag
    path('category/<str:tag>/', views.TagArchiveView.as_view(), name='blog-tag-archive'),
    # Archive by year
    path('<int:year>/', YearArchiveView.as_view(model=Blog, date_field="post_date", make_object_list=True), name="blog-year-archive"),
    # Blog detail specified by date and slug
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    # Deprecated
    path('blog-author/<int:pk>', views.BlogAuthorDetailView.as_view(), name='blog-author-detail'),
    # Page introducing this blog website
    path('about-this-blog', views.AboutThisBlogView.as_view(), name='about-this-blog'),
    # Page introducing myself
    path('about-me', views.AboutMeView.as_view(), name='about-me'),
]
