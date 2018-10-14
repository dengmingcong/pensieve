from django.urls import path
from django.views.generic.dates import ArchiveIndexView

from . import views
from .models import Blog


urlpatterns = [
    # Index (home page)
    path('', views.Index.as_view(), name='index'),
    # Archive
    path('archive/', views.BlogArchiveView.as_view(), name='archive'),
    # Archive by tag
    path('archive/<str:tag>/', views.BlogArchivedByTagView.as_view(), name='archived-by-tag'),
    # Blog detail specified by date and slug
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    # Deprecated
    path('blog-author/<int:pk>', views.BlogAuthorDetailView.as_view(), name='blog-author-detail'),
    # Page introducing this blog website
    path('about-this-blog', views.AboutThisBlogView.as_view(), name='about-this-blog'),
    # Page introducing myself
    path('about-me', views.AboutMeView.as_view(), name='about-me'),
]
