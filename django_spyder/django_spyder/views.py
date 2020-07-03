# /usr/bin/python
# -*- coding=utf-8 -*-
from django.http import HttpResponse


def hello(request):
    return HttpResponse(content="hello")