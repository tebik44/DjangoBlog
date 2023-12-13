from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from django.db.models import Count

from .models import Post

from .forms import EmailPostForm, CommentForm


def post_detail(request, year, month, day, slug):
    """работа с отображением деталей поста"""
    # post = get_object_or_404(Post, id=id,
    #                          status=Post.Status.PUBLISHED)
    try:
        post = Post.published.get(publish__year=year, 
                                  publish__month=month, 
                                  publish__day=day, 
                                  slug=slug)
        comments = post.comments.filter(active=True)
        form = CommentForm()
        
        post_tags = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags'))

    except Post.DoesNotExist as er:
        return HttpResponseBadRequest(er)
    return render(request, 'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):
    """работа с отправкой на почту"""
    post = get_object_or_404(Post, id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s ({cd['email']}) comments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER,
                      [cd['to']])
            sent = True
        else:
            return HttpResponseBadRequest("""Ошибка валидации данных, 
                                          проверьте правильность написания""")
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


def post_list(request, tag_slug=None):
    post_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 1)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'tag': tag})

# class PostListView(ListView):
#     model = Post
#     template_name = 'blog/post/list.html'
#     context_object_name = 'posts'
#     paginate_by = 2

#     def get_queryset(self):
#         tag_slug = self.kwargs.get('tag_slug')
#         queryset = Post.published.all()

#         if tag_slug:
#             tag = get_object_or_404(Tag, slug=tag_slug)
#             queryset = queryset.filter(tags__in=[tag])

#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         tag_slug = self.kwargs.get('tag_slug')
#         if tag_slug:
#             context['tag'] = get_object_or_404(Tag, slug=tag_slug)
#         return context


@require_POST
def post_comment(request, post_id):
    """Работа с коментраием"""
    post = get_object_or_404(Post, 
                             id=post_id, 
                             status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})
    
    
