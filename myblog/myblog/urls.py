from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include("django.contrib.auth.urls")),
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
