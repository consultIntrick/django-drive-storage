# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mimetypes
import re
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
# from django.contrib.postgres.fields import ArrayField


class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       abstract = True

    def save(self, *args, **kwargs):
        super(AuditModel, self).save(*args, **kwargs)


def validate_name(value):
    if not (value or bool(re.match('^[a-zA-Z0-9_\-.()]+$', value))):
        raise ValidationError(
            _("%(value)s - should contain only alphabets, numbers, '.', '(', ')', '_' and '-' in it"),
            params={'value': value},
        )


class FolderQuerySet(QuerySet):

    def available(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def get_files(self):
        return self.filter(data__isnull=False)

    def get_folders(self):
        return self.filter(data__isnull=True)


class FolderManager(models.Manager):

    def get_queryset(self):
        return FolderQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().available()

    def deleted(self):
        return self.get_queryset().deleted()

    def get_files(self):
        return self.get_queryset().get_files()

    def get_folders(self):
        return self.get_queryset().get_folders()


class Folder(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256, validators=[validate_name])
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='child_folders')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    deleted_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                     related_name='deleted_child_folders')
    data = models.ForeignKey('storage.Data', on_delete=models.CASCADE, null=True, blank=True)

    objects = FolderManager()

    def __str__(self):
        return '{} {}'.format(self.name, self.id)

    def is_folder(self):
        return True if not self.data else False

    def is_file(self):
        return True if self.data else False

    def get_file(self):
        return self.data

    def is_root(self):
        return True if not self.parent else False

    def get_file_details(self):
        if self.data:
            response = self.data.get_details()
            if self.is_deleted:
                response['restore_url'] = reverse('folder_content_action', kwargs={'folder_id': self.id,
                                                                                   'folder_type': 'bin',
                                                                                   'action': 'restore'})
            else:
                response['delete_url'] = reverse('folder_content_action', kwargs={'folder_id': self.id,
                                                                                  'folder_type': 'home',
                                                                                  'action': 'delete'})
                response['update_url'] = reverse('folder_update_content', kwargs={'folder_id': self.id})
        else:
            response = self.get_folder_details()
        return response

    def get_folder_details(self):
        from pytz import timezone
        from django.conf import settings
        x = timezone(settings.TIME_ZONE)
        response =  {
            'id': self.id,
            'name': self.name,
            'url': reverse('folder_content', kwargs={'folder_id': self.id,
                                                     'folder_type': 'bin' if self.is_deleted else 'home'}),
            'created_at': self.created_at.astimezone(x).strftime("%d-%m-%Y %H:%M:%S %Z"),
            'type': 'folder'
        }
        if self.is_deleted:
            response['restore_url'] = reverse('folder_content_action', kwargs={'folder_id': self.id,
                                                                               'folder_type': 'bin',
                                                                               'action': 'restore'})
        else:
            response['delete_url'] = reverse('folder_content_action', kwargs={'folder_id': self.id,
                                                                               'folder_type': 'home',
                                                                               'action': 'delete'})
            response['update_url'] = reverse('folder_update_content', kwargs={'folder_id': self.id})
        return response

    def get_details(self):
        return self.get_file_details() if self.is_file() else self.get_folder_details()

    def get_folder_contents(self, sort_by='name'):
        if not sort_by in ['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']:
            sort_by = 'name'
        return self.child_folders.available().order_by(sort_by)

    def softdelete(self, user_deleted=True):
        if user_deleted:
            self.deleted_from = self.parent
            self.parent = None
            self.is_deleted = True
            self.save()
        qs = self.child_folders.available()
        if qs.exists():
            qs.update(is_deleted=True)
            for each in qs:
                each.softdelete(user_deleted=False)

    def restore(self):
        if self.deleted_from and not self.deleted_from.is_deleted:
            self.parent = self.deleted_from
        self.deleted_from = None
        self.is_deleted = False
        self.save()
        qs = self.child_folders.deleted()
        if qs.exists():
            qs.update(is_deleted=False, deleted_from=None)
            for each in qs:
                each.restore()

    @staticmethod
    def get_root_contents_of_user(user, sort_by='name'):
        if not sort_by in ['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']:
            sort_by = 'name'
        return Folder.objects.filter(owner=user, parent__isnull=True).available().order_by(sort_by)

    @staticmethod
    def get_bin_contents_of_user(user, sort_by='name'):
        if not sort_by in ['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']:
            sort_by = 'name'
        return user.folder_set.filter(parent__isnull=True).deleted().order_by(sort_by)

    @staticmethod
    def create_or_update(pk=None, name=None, parent=None, owner=None, data=None, remove_parent=False, remove_file=False):
        if pk:
            obj = get_object_or_404(Folder, pk=pk)
            if Folder.objects.filter(parent=parent or obj.parent, owner=owner or obj.owner,
                                     name=name or obj.name).exclude(pk=pk).exists():
                raise ValidationError('Folder/file with the same name already exists in the current folder')
        else:
            obj = Folder()
            if not (name and owner):
                raise ValidationError('Name and Owner are mandatory for a folder creation')
            if parent and parent.is_deleted:
                raise ValidationError('Creation is not allowed in a deleted folder')
            if Folder.objects.filter(parent=parent, owner=owner, name=name).exists():
                raise ValidationError('Folder/file with the same name already exists in the current folder')
        if name and name.strip():
            obj.name = name
        elif data:
            obj.name = data.name
        if remove_parent:
            obj.parent = None
        elif parent:
            if isinstance(parent, Folder):
                obj.parent = parent
            else:
                raise ValidationError('Invalid parent object supplied')
        if owner:
            obj.owner = owner
        if remove_file:
            obj.data = None
        elif data:
            if data and isinstance(data, Data):
                obj.data = data
            else:
                raise ValidationError('Invalid file object supplied')
        obj.save()
        return obj


def generate_path(self, filename):
    file_extension = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(), file_extension)
    return "{0}/{1}".format(self.user.username, filename)

class Data(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    type = models.CharField(max_length=256)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.FileField(max_length=2048, upload_to=generate_path)
    # tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return '{} {}'.format(self.name, self.id)

    def generate_id(self):
        id = uuid.uuid4().hex
        while Data.objects.filter(id=self.id).exists():
            id = uuid.uuid4().hex
        return id

    def get_file(self):
        response = HttpResponse(
            self.url.file.read(), content_type=self.type)
        response['Content-Disposition'] = 'inline; filename=' + self.name
        return response

    def get_details(self):
        from pytz import timezone
        from django.conf import settings
        x = timezone(settings.TIME_ZONE)
        return {
            'id': self.id,
            'name': self.name,
            'url': reverse('get_file', kwargs={'file_id': self.id}),
            'created_at': self.created_at.astimezone(x).strftime("%d-%m-%Y %H:%M:%S %Z"),
            'type': 'file'
            # 'tags': self.tags
        }

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_id()
        if not self.name:
            self.name = self.url.name
        self.type = mimetypes.guess_type(self.url.name)[0]
        return super(Data, self).save(*args, **kwargs)

    @staticmethod
    def create_or_update(pk=None, name=None, user=None, uploaded_file=None):
        if pk:
            obj = get_object_or_404(Data, pk=pk)
        else:
            obj = Data()
            if not (user and uploaded_file):
                raise ValidationError('User and File are mandatory for a file creation')
        if name and name.strip():
            obj.name = name
        if user:
            obj.user = user
        if uploaded_file:
            obj.url = uploaded_file
        obj.save()
        return obj

    def update_name(self, name):
        if name and name.strip():
            self.name = name.strip()
            self.save()
