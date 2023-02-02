# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pyscada

__version__ = '0.7.1rc1'
__author__ = 'Camille Lavayssière'

plugin_name = "File"
plugin_name_lower = plugin_name.lower()

PROTOCOL_ID = 14

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.' + plugin_name_lower,
                        'process_class': 'pyscada.' + plugin_name_lower + '.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]
