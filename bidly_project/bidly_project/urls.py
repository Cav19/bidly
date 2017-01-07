"""bidly_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from bidly_app import views as bidly_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', bidly_views.login, name="login"),
    url(r'^register/$', bidly_views.no_auction_register, name="no_auction_register"),
    url(r'^register/(?P<auction_name>[\w]+)/$', bidly_views.register, name="register"),
    url(r'^user_login/$', bidly_views.no_auction_user_login, name="no_auction_user_login"),
    url(r'^user_login/(?P<auction_name>[\w]+)/$', bidly_views.user_login, name="user_login"),
    url(r'^profile/', bidly_views.profile, name="profile"),
    url(r'^item_page/$', bidly_views.item, name="item_page"),
    url(r'^make_bid/$', bidly_views.make_bid, name="make_bid"),
    url(r'^get_top_bid/$', bidly_views.get_top_bid, name="get_top_bid"),
    url(r'^changepw/$', bidly_views.changepw, name="change_password"),
    url(r'^change_profile/$', bidly_views.change_profile, name="change_profile"),
    url(r'^get_profile_info/$', bidly_views.get_profile_info, name="get_profile_info"),
    url(r'^search/$', bidly_views.search, name="search"),
    url(r'^create_auction/$', bidly_views.create_auction, name="create_auction"),
    url(r'^begin_auction/$', bidly_views.begin_auction, name="begin_auction"),
    url(r'^image_test/$', bidly_views.image_test, name="image_test"),
    url(r'^home/$', bidly_views.generic_home, name="generic_home"),
    url(r'^home/(?P<auction_name>[\w]+)/$', bidly_views.home, name="home"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
