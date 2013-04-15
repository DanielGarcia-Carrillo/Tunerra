from django.conf.urls import patterns, include, url
from tunerra.social_views import facebook_connect
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tunerra.views.index', name='home'),
    url(r'^search$', 'tunerra.views.search'),

    url(r'^accounts$', 'tunerra.views.login_signup'),
    url(r'^accounts/welcome$', 'tunerra.views.welcome'),
    url(r'^accounts/logout$', 'tunerra.views.logout_user'),
    url(r'^accounts/profile/(?P<username>[A-Z|a-z|0-9|+|\-|_|.|@]{1,30})$', 'tunerra.views.user_profile'),
    url(r'^login_error$', 'tunerra.views.login_error'),
    url(r'^accounts/settings$', 'tunerra.views.settings'),
    url(r'^accounts/facebook_connect', facebook_connect.as_view),
    url(r'^map', 'tunerra.views.map_page'),

    url(r'^channel.html$', 'tunerra.views.facebook_api'),

    # Insert RESTful url here for accounts (accounts/[id] or profile/[id]) perhaps?
    # url(r'^myproject/', include('myproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
