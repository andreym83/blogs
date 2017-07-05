from django.conf.urls import *
from django.contrib.auth.views import login, logout
from django.contrib.auth.decorators import login_required
from blogs import views
from blogs.views import *

urlpatterns=[
    url(r'^$', login_required(MainView.as_view(template_name='main.html'))),
    url(r'^blog/(?P<username>\S+)/$', login_required(BlogView.as_view(template_name='blog.html'))),
    url(r'^authors/$', login_required(AuthorsView.as_view(template_name='authors.html'))),
    url(r'^news/$', login_required(NewsView.as_view(template_name='blog.html'))),
    url(r'^add_post/$', login_required(AddPostView.as_view(template_name='add_post.html'))),
    url(r'^subscribe/$', login_required(SubscribeView.as_view())),
    url(r'^markread/$', login_required(MarkreadView.as_view())),
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', LogoutView.as_view()),
]
