# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from . import plugin_name_lower, plugin_name


class PyScadaFileConfig(AppConfig):
    name = 'pyscada.' + plugin_name_lower
    verbose_name = _("PyScada " + plugin_name)
    path = os.path.dirname(os.path.realpath(__file__))
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from . import signals
