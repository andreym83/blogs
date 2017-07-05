from django.shortcuts import render, render_to_response
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, JsonResponse, HttpResponseNotAllowed
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView, ListView, TemplateView
from django.views.decorators.http import require_http_methods
from django.template import loader, Context, RequestContext
from blogs.forms import *
from blogs.models import *


class MainView(TemplateView):
    def get_context_data(self, **kwargs):
        return {}


class AuthorsView(TemplateView):

    def get_context_data(self, **kwargs):

        users = User.objects.raw('''SELECT auth_user.id, username
            FROM auth_user
            JOIN blogs_subscriber ON blogs_subscriber.author_id = auth_user.id
            WHERE subscriber_id = %s AND auth_user.id != %s''', [self.request.user.id, self.request.user.id])

        users_not_subscribe = User.objects.raw('''SELECT auth_user.id, username
            FROM auth_user
            LEFT JOIN blogs_subscriber ON blogs_subscriber.author_id = auth_user.id AND subscriber_id = %s
            WHERE author_id IS NULL AND auth_user.id != %s''', [self.request.user.id, self.request.user.id])

        return {'users' : users, 'users_not_subscribe' : users_not_subscribe}


def add_paginator(posts, page):

    paginator = Paginator(posts, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return posts


class BlogView(TemplateView):

    def get_context_data(self, **kwargs):

        username = self.kwargs['username']
        if not User.objects.filter(username=username).exists():
            raise Http404

        posts = Post.objects.filter(user__username=username)
        posts = add_paginator(posts, self.request.GET.get('page'))
        return {'join' : False, 'username' : username, 'posts' : posts}


class NewsView(TemplateView):

    def get_context_data(self, **kwargs):

        posts = Post.objects.raw('''SELECT header, text, time, username, blogs_post.id, auth_user.id AS user_id,
            blogs_read.post_id AS readed
            FROM blogs_post
            JOIN auth_user ON blogs_post.user_id = auth_user.id
            JOIN blogs_subscriber ON blogs_subscriber.author_id = blogs_post.user_id
            LEFT JOIN blogs_read ON blogs_read.post_id = blogs_post.id AND blogs_read.reader_id = %s
            WHERE subscriber_id = %s
            ORDER BY blogs_post.id DESC''', [self.request.user.id, self.request.user.id])

        posts = add_paginator(list(posts), self.request.GET.get('page'))
        return {'join' : True, 'posts' : posts}


class AddPostView(TemplateView):

    form_class = PostForm

    def get(self, request, *args, **kwargs):
        form = PostForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            post = Post(header = data['header'],
                        text = data['text'],
                        user_id = self.request.user.id)
            post.save()
            messages.success(request, "Ваш пост размещён в блоге")

            users = User.objects.filter(subscriber__author = self.request.user.id)
            for user in users:
                user.email_user('User ' + self.request.user.username + ' add new post', 'User ' + self.request.user.username + ' add new post')

            return HttpResponseRedirect('/blog/' + self.request.user.username + '/')


class SubscribeView(TemplateView):

    form_class = SubscribeForm

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            if form.data['is_subscribe'] == '1':
                Subscriber(author_id = str(data['author']), subscriber_id = self.request.user.id).save()
                return JsonResponse({'result' : 'ok'})
            else:
                Subscriber.objects.filter(author_id = data['author'], subscriber_id = self.request.user.id).delete()
                Read.objects.filter(reader_id = self.request.user.id, post__user = data['author']).delete()
                return JsonResponse({'result' : 'ok'})
        else:
            return JsonResponse({'result' : 'error'})


class MarkreadView(TemplateView):

    form_class = MarkreadForm

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        if form.is_valid():
            Read(post_id = str(form.cleaned_data['post']), reader_id = self.request.user.id).save()
            return JsonResponse({'result' : 'ok'})
        else:
            return JsonResponse({'result' : 'error'})


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')
