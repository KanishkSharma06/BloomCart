from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Sabse pehle aapka store app aana chahiye!
    path('', include('store.urls')),  
    
    # 2. Allauth ya baaki ke accounts baad mein aane chahiye
    path('accounts/', include('allauth.urls')), 
]

# Ye static lines sabse last mein honi chahiye
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)