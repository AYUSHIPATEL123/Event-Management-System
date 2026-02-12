from django import forms
from .models import blog
class UserForm(forms.Form):
    first_name = forms.CharField(label='First Name',max_length=10,help_text="enter the first name")
    last_name = forms.CharField(widget=forms.Textarea,label='Last Name',max_length=10)
    username = forms.CharField(label='Username',max_length = 100)
    password = forms.CharField(widget=forms.PasswordInput(),label='Password',max_length=200)

class BlogForm(forms.ModelForm):
    class Meta:
        model = blog
        fields = ['title','description']
        labels = {'title':'Title','description':'Description'}
        help_texts = {'title':'Enter the title of the blog','description':'Enter the description of the blog'}
        max_lengths = {'title':100,'description':200}
        error_meassages = {'title':{'required':"Enter the title of the blog"},'description':{'required':'Enter the description of the blog'}}
        widget={'description':forms.Textarea}
        