# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from website.models import *

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Event)
admin.site.register(EventDorna)
admin.site.register(Boardgame, BoardgameAdmin)