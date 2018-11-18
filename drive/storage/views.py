# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from drive.storage.models import Folder, Data


class FolderView(View):

    def __init__(self, *args, **kwargs):
        self.user = User.objects.first()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FolderView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        folder_type = kwargs['folder_type']
        folder_id = kwargs.get('folder_id') or ''
        try:
            if folder_type.lower() == 'bin':
                is_deleted = True
            elif folder_type.lower() == 'home':
                is_deleted = False
            else:
                raise Http404
            if folder_id and folder_id.strip():
                folder = get_object_or_404(Folder, owner=self.user, pk=folder_id.strip(), is_deleted=is_deleted)
                folder_contents = folder.get_folder_contents()
            else:
                folder_contents = Folder.get_bin_contents_of_user(self.user) if is_deleted else \
                    Folder.get_root_contents_of_user(self.user)
            data = {
                'folders': [each.get_folder_details() for each in folder_contents.get_folders()],
                'files': [each.get_file_details() for each in folder_contents.get_files()]
            }
            return JsonResponse(data, status=200)
        except Http404:
            return JsonResponse({'message': 'Not found'}, status=404)
        except BaseException:
            return JsonResponse({'message': 'Error'}, status=500)

    def post(self, request, *args, **kwargs):
        folder_type = kwargs['folder_type']
        folder_id = kwargs.get('folder_id')
        name = request.POST.get('name')
        uploaded_file = request.FILES.get('data')
        try:
            if folder_type.lower() == 'home':
                parent = get_object_or_404(Folder, owner=self.user, pk=folder_id.strip(), is_deleted=False
                                           ) if (folder_id and folder_id.strip()) else None
                if uploaded_file:
                    data = Data.create_or_update(user=self.user, uploaded_file=uploaded_file)
                    name = data.name
                else:
                    data = None
                folder = Folder.create_or_update(name=name, parent=parent, owner=self.user, data=data)
                return JsonResponse(folder.get_details(), status=200)
            else:
                raise Http404
        except Http404:
            return JsonResponse({'message': 'Not found'}, status=404)
        except ValidationError as ex:
            return JsonResponse({'message': str(ex[0])}, status=422)
        except BaseException:
            return JsonResponse({'message': 'Error'}, status=500)

    def delete(self, request, *args, **kwargs):
        folder_type = kwargs['folder_type']
        folder_id = kwargs['folder_id']
        action = kwargs['action']
        try:
            if folder_type.strip().lower() == 'home' and action.strip().lower() == 'delete':
                is_deleted = False
            elif folder_type.strip().lower() == 'bin' and action.strip().lower() == 'restore':
                is_deleted = True
            else:
                raise Http404
            folder = get_object_or_404(Folder, owner=self.user, pk=folder_id.strip(), is_deleted=is_deleted)
            folder.restore() if is_deleted else folder.softdelete()
            return JsonResponse({'message': '{}d successfully'.format(action.title())}, status=200)
        except Http404:
            return JsonResponse({'message': 'Not found'}, status=404)
        except BaseException:
            return JsonResponse({'message': 'Error'}, status=500)


class FolderUpdateView(View):

    def __init__(self, *args, **kwargs):
        self.user = User.objects.first()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FolderUpdateView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        folder_id = kwargs.get('folder_id')
        name = request.POST.get('name')
        move_to_folder_id = request.POST.get('move_to_folder_id')
        import ipdb; ipdb.set_trace()
        try:
            folder = get_object_or_404(Folder, owner=self.user, pk=folder_id.strip(), is_deleted=False)
            remove_parent = False
            parent = None
            if move_to_folder_id and move_to_folder_id.strip().lower() == 'root':
                remove_parent = True
            elif move_to_folder_id and move_to_folder_id.strip():
                parent = get_object_or_404(Folder, owner=self.user, pk=move_to_folder_id.strip(), is_deleted=False)
            if folder.is_file() and name:
                folder.get_file().update_name(name)
            folder = Folder.create_or_update(pk=folder.pk, name=name, parent=parent, remove_parent=remove_parent)
            return JsonResponse(folder.get_details(), status=200)
        except Http404:
            return JsonResponse({'message': 'Not found'}, status=404)
        except ValidationError as ex:
            return JsonResponse({'message': str(ex[0])}, status=422)
        except BaseException:
            return JsonResponse({'message': 'Error'}, status=500)

    def delete(self, request, *args, **kwargs):
        folder_type = kwargs['folder_type']
        folder_id = kwargs['folder_id']
        action = kwargs['action']
        try:
            if folder_type.strip().lower() == 'home' and action.strip().lower() == 'delete':
                is_deleted = False
            elif folder_type.strip().lower() == 'bin' and action.strip().lower() == 'restore':
                is_deleted = True
            else:
                raise Http404
            folder = get_object_or_404(Folder, owner=self.user, pk=folder_id.strip(), is_deleted=is_deleted)
            folder.restore() if is_deleted else folder.softdelete()
            return JsonResponse({'message': '{}d successfully'.format(action.title())}, status=200)
        except Http404:
            return JsonResponse({'message': 'Not found'}, status=404)
        except BaseException:
            return JsonResponse({'message': 'Error'}, status=500)


def get_file(request, file_id):
    file = get_object_or_404(Data, user=User.objects.first(), pk=file_id.strip())
    return file.get_file()

