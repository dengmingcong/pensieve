from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('blog-author/<int:pk>', views.BlogAuthorDetailView.as_view(), name='blog-author-detail'),
    path('about-this-blog', views.AboutThisBlogView.as_view(), name='about-this-blog'),
    path('about-me', views.AboutMeView.as_view(), name='about-me'),
]
