from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404, HttpResponseBadRequest
from django.core.paginator import Paginator


def post_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except Exception:
        posts = paginator.page(1)
    return render(request, 'blog/post/list.html',
                  {'posts': posts})


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

