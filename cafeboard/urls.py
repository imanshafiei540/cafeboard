from django.conf.urls import url
from django.contrib import admin
from website import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^enterallproducts', views.enter_bg_data),
    url(r'^addboardgame', views.add_boardgame),
    url(r'^getproducts', views.getproducts),
    url(r'^getallboardgames', views.getallboardgames),
    url(r'^getbgscategory', views.get_bg_ctaegory),
    url(r'^admin/', admin.site.urls),
    url(r'^public/media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^', views.index),
]

urlpatterns += staticfiles_urlpatterns()
