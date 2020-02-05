from django import forms

from .models import Blog


class BlogModelForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'slug', 'content', 'blog_author', 'post_date', 'tags']

        #widgets = {
        #    'content': forms.Textarea(attrs={'cols': '120', 'rows': '40'}),
        #}
