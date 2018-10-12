from datetime import date
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Tag(models.Model):
    """
    Model representing a tag.

    One blog can have multi tags, one tag can be used for multi blogs.
    """

    tag = models.CharField(max_length=20, help_text="Define a tag.")

    def __str__(self):
        """
        String represent the model object.
        """
        return self.tag


class BlogAuthor(models.Model):
    """
    Model representing a blog author.
    """

    name = models.ForeignKey(User,on_delete=models.PROTECT) 
    biography = models.TextField()

    def __str__(self):
        """
        String representing the Model object.
        """
        return self.name.username

    def get_absolute_url(self):
        """
        Return the url to access a particular blog-author instance.
        """
        return reverse('blog-author-detail', args=[str(self.id)]) 


class Blog(models.Model):
    """
    Model representing a blog.
    """

    blog_author = models.ForeignKey(BlogAuthor, on_delete=models.PROTECT)
    post_date = models.DateField(default=date.today)
    tags = models.ManyToManyField(Tag)
    title = models.CharField(max_length=50, help_text="Title of this blog.")
    slug = models.CharField(max_length=50, unique_for_date="post_date", help_text="Short for title, used as the URL slug.")
    content = models.TextField()

    class Meta:
        ordering = ['-post_date']

    def __str__(self):
        """
        String representing the blog instance.
        """
        return self.title

    def get_absolute_url(self):
        """
        Return the url to access a particular blog instance.
        """
        return reverse(
            'blog-detail', 
            kwargs={
                'year': self.post_date.year,
                'month': self.post_date.month,
                'day': self.post_date.day,
                'slug': self.slug
            }
        )


class BlogComment(models.Model):
    """
    Model representing a comment against a blog post.
    """

    comment_author = models.ForeignKey(User, on_delete=models.SET_NULL,
            null=True)
    post_date = models.DateTimeField(auto_now_add=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)

    def __str__(self):
        """
        String representing the Model object.
        """
        title_len = 75
        if len(self.content) > title_len:
            title_string = self.content[:title_len] + "..."
        else:
            title_string = self.content
        return title_string
