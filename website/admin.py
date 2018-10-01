# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from website.models import *

admin.site.register(Category)
admin.site.register(Boardgame)
admin.site.register(Tag)
admin.site.register(Event)