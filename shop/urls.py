from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store.views import index

from shop import settings

#..._user pour différencier des fonctions Django

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
    path('boutique/', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
