from django.conf.urls import patterns, include, url
from tunerra import search_views, social_views, views, feed_views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tunerra.views.index', name='home'),
    url(r'^search$', search_views.search.as_view(), name='search'),

    url(r'^accounts$', 'tunerra.views.login_signup', name='login_signup'),
    url(r'^accounts/welcome$', 'tunerra.views.welcome', name='welcome'),
    url(r'^accounts/logout$', 'tunerra.views.logout_user', name='logout'),
    url(r'^accounts/feed/(?P<username>[A-Z|a-z|0-9|+|\-|_|.|@]{1,30})$', feed_views.FeedPage.as_view()),
    url(r'^login_error$', 'tunerra.views.login_error'),
    url(r'^accounts/settings$', 'tunerra.views.settings', name='settings'),
    url(r'^accounts/facebook_connect', social_views.facebook_connect.as_view()),
    url(r'^map', 'tunerra.views.map_page', name='map'),
    
    url(r'^channel.html$', 'tunerra.social_views.facebook_api'),
    # Insert RESTful url here for accounts (accounts/[id] or profile/[id]) perhaps?
    # url(r'^myproject/', include('myproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
