"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from helloword import userInfo as userview
from helloword import initadd as initview

from helloword import wordlist as listview
from helloword import word as wordview
from helloword import chat
import os
from django.urls import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),

    # media
    re_path(r'^media/user_avatar/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.MEDIA_ROOT, 'user_avatar/')}),
    re_path(r'^media/user_file/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.MEDIA_ROOT, 'user_file/')}),

    # user
    path("login/", userview.login),
    path("register/", userview.register),

    path("submit_image/",userview.submit_image),

    # wordlist
    path("get_user_wordlists/",listview.get_user_wordlists),
    path("get_wordlist_info/",listview.get_wordlist_info),
    path("get_words_info/",listview.get_words_info),
    path("edit_wordlists/",listview.edit_wordlists),
    path("get_wordlists/",listview.get_wordlists),
    path("get_official_wordlists/",listview.get_official_wordlists),
    path("get_wordList_from_file/",listview.get_wordList_from_file),

    # learn word
    path("get_word_releation/",wordview.get_word_releation),
    path("group_word_learn_save/",wordview.group_word_learn_save),
    path("get_group_words_in_list/",wordview.get_group_words_in_list),

    # init mysql
    path("add_word/",initview.add_word),
    path("add_public_list/",initview.add_public_list),
    path("add_studylist_from_public/",initview.add_studylist_from_public),
    path("add_relation/",initview.add_relation),
    path("add_example/",initview.add_example),

    # chat
    path("user_send/", chat.user_send),
    path("get_log_history/", chat.get_log_history)

    
]
