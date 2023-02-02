# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from .models import FileDevice, FileVariable, ExtendedFileDevice, \
    ExtendedFileVariable

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=FileDevice)
@receiver(post_save, sender=FileVariable)
@receiver(post_save, sender=ExtendedFileDevice)
@receiver(post_save, sender=ExtendedFileVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is FileDevice:
        post_save.send_robust(sender=Device, instance=instance.file_device)
    elif type(instance) is FileVariable:
        post_save.send_robust(sender=Variable, instance=instance.file_variable)
    elif type(instance) is ExtendedFileVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedFileDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
