from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blog/<int:pk>', views.BlogDetailView.as_view(), name='blog-detail'),
    path('blog-authors/', views.BlogAuthorListView.as_view(),
        name='blog-authors'),
    path('blog-author/<int:pk>', views.BlogAuthorDetailView.as_view(),
        name='blog-author-detail'),
]
