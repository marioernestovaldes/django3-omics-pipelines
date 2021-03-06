
import os
import hashlib
import shutil
import zipfile

from pathlib import Path as P

from django.db import models
from django_currentuser.db.models import CurrentUserField
from django.template.defaultfilters import slugify
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings 
from uuid import uuid4


DATALAKE_ROOT = settings.DATALAKE_ROOT
COMPUTE_ROOT = settings.COMPUTE_ROOT
COMPUTE = settings.COMPUTE



class MaxQuantExecutable(models.Model):
    filename = models.FileField(upload_to='software/MaxQuant',
                                storage = COMPUTE)
    
    created = models.DateField(default = timezone.now)
        
    def __str__(self):
        return os.path.basename(str(self.filename).replace('.zip', ''))
    
    @property
    def path(self): 
        fn = str(self.filename)
        return COMPUTE_ROOT / 'software' / 'MaxQuant' / P( fn ).name
    
    def save(self, *args, **kwargs):
        print('Save MQ bin')
        super(MaxQuantExecutable, self).save(*args, **kwargs)
        

@receiver(models.signals.post_save, sender=MaxQuantExecutable)
def unzip_maxquant(sender, instance, created, *args, **kwargs):
    'Unzip MaxQuant.zip'
    mq_bin = instance
    name = mq_bin.path
    tmp = mq_bin.path.with_suffix('')

    assert name.is_file(), name

    with zipfile.ZipFile(name, 'r') as zip_ref:
        print('Extracting zip archive:', name, tmp)
        zip_ref.extractall(tmp)

    os.remove(name)
    os.rename(tmp, name)


@receiver(models.signals.post_delete, sender=MaxQuantExecutable)
def remove_maxquant(sender, instance, *args, **kwargs):
    'Remove MaxQuant directory'
    mq_bin = instance
    path = mq_bin.path
    if path.is_dir():
        shutil.rmtree(mq_bin.path)