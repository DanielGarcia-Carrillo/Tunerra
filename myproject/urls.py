from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
admin.autodiscover()
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tunerra.views.index', name='home'),
    url(r'^accounts$', 'tunerra.views.login_signup'),
    url(r'^accounts/welcome$', 'tunerra.views.welcome'),
    url(r'^accounts/logout$', 'tunerra.views.logout'),
    url(r'^sign out$', 'tunerra.views.logout'),
    # url(r'^myproject/', include('myproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
