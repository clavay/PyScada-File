# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device
from pyscada.models import Variable
from . import PROTOCOL_ID

from django.db import models

import logging

from django.forms.models import BaseInlineFormSet
from django import forms

logger = logging.getLogger(__name__)


class FileDevice(models.Model):
    file_device = models.OneToOneField(Device, null=True, blank=True, on_delete=models.CASCADE)
    protocol_choices = ((0, 'local'), (1, 'ssh'), (2, 'ftp'))
    protocol = models.PositiveSmallIntegerField(choices=protocol_choices)
    file_path = models.CharField(default="", blank=True, help_text="For example : /dir/file.txt", max_length=100)
    timeout = models.PositiveSmallIntegerField(default=5, help_text="in seconds")

    # SSH and FTP
    host = models.CharField(default="test.com", max_length=200)
    port = models.PositiveSmallIntegerField(default=21)
    username = models.CharField(default="", blank=True, max_length=50)
    password = models.CharField(default="", blank=True, max_length=50)

    # FTP
    ftp_passive_mode = models.BooleanField(default=True)
    local_temporary_file_copy_path = models.CharField(default="", blank=True, help_text="For example : /tmp/file.txt",
                                                      max_length=100)

    protocol_id = PROTOCOL_ID

    class FormSet(BaseInlineFormSet):
        def add_fields(self, form, index):
            super().add_fields(form, index)
            form.fields['protocol'].widget.attrs = {
                    # all hidden by default
                    "--hideshow-fields": "host, port, username, password, ftp_passive_mode, local_temporary_file_copy_path",
                    # host, port, username, password visible when "1" (ssh) is selected
                    "--show-on-1": "host, port, username, password",
                    # host, port, username, password, ftp_passive_mode, local_temporary_file_copy_path visible when "2" (ftp) is selected
                    "--show-on-2": "host, port, username, password, ftp_passive_mode, local_temporary_file_copy_path",
                }

    def parent_device(self):
        try:
            return self.file_device
        except:
            return None

    def __str__(self):
        return self.file_device.short_name


class FileVariable(models.Model):
    file_variable = models.OneToOneField(Variable, null=True, blank=True, on_delete=models.CASCADE)
    program_choices = (('awk', 'awk'), ('sed', 'sed'),)
    program = models.CharField(default='awk', choices=program_choices, max_length=25)
    command = models.CharField(default="NR==1{ print; exit }", blank=True, max_length=500,
                               help_text="Look at https://www.gnu.org/software/gawk/manual/gawk.html"
                                         "<br> To write, use $value$ where the variable value should be placed.")

    protocol_id = PROTOCOL_ID

    def __str__(self):
        return self.id.__str__() + "-" + self.file_variable.short_name


class ExtendedFileDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'File Device'
        verbose_name_plural = 'File Devices'


class ExtendedFileVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'File Variable'
        verbose_name_plural = 'File Variables'
