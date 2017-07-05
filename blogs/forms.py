from django import forms

class PostForm(forms.Form):
    header = forms.CharField(max_length=255, label='Введите заголовок')
    text = forms.CharField(widget=forms.Textarea, label='Введите содержимое поста')


class SubscribeForm(forms.Form):
    author = forms.IntegerField()
    is_subscribe = forms.BooleanField()


class MarkreadForm(forms.Form):
    post = forms.IntegerField()
