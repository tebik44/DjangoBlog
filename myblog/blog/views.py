from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.core.paginator import Paginator
from django.views.generic import ListView

from .forms import EmailPostForm

from django.core.mail import send_mail
from django.conf import settings


def post_detail(request, year, month, day, slug):
    # post = get_object_or_404(Post, id=id,
    #                          status=Post.Status.PUBLISHED)
    try:
        post = Post.published.get(publish__year=year, 
                                  publish__month=month, 
                                  publish__day=day, 
                                  slug=slug)
    except Post.DoesNotExist as er:
        return HttpResponseBadRequest(er)
    return render(request, 'blog/post/detail.html',
                  {'post': post})


def post_share(request, post_id):
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

#############
# def post_list(request):
#     posts = Post.objects.all()
#     paginator = Paginator(posts, 2)
#     page_number = request.GET.get('page', 1)
#     posts = paginator.get_page(page_number)
#     return render(request, 'blog/post/list.html',
#                   {'posts': posts})

# сверху пример того, как можно написать без использования представления, логика та же самая
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 1
    template_name = 'blog/post/list.html'
    
    
    
