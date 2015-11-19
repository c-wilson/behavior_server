from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<mouse_number>[0-9]+)/$', views.mouse, name='mouse'),
    url(r'^(?P<mouse_number>[0-9]+)/(?P<session_num>[0-9]+)/$', views.session, name='session'),
    url(r'^mouse_adder/$', views.mouse_adder, name='mouse_adder'),
    url(r'^(?P<mouse_number>[0-9]+)/editor/$', views.edit_mouse, name='edit_mouse'),
    url(r'^_add_session/$', views.add_session, name='add_session'),
    url(r'^(?P<mouse_number>[0-9]+)/(?P<session_num>[0-9]+)/notes$', views.session_notes, name='session_notes')
]
