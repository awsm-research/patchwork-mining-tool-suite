from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from msr.models import *
from msr.serializers import *
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET', 'POST', 'DELETE'])
def msr_people_list(request):
    # GET list of people, POST a new person, DELETE all people
    if request.method == 'GET':
        people = People.objects.all()
        
        username = request.GET.get('username', None)
        if username is not None:
            people = people.filter(username__icontains=username)
            
        # email = request.GET.get('email', None)
        # if username is not None:
        #     people = people.filter(email__icontains=email)
        
        people_serializer = PeopleSerializer(people, many=True)
        return JsonResponse(people_serializer.data, safe=False)
        # 'safe=False' for objects serialization
        
    elif request.method == 'POST':
        people_data = JSONParser().parse(request)
        people_serializer = PeopleSerializer(data=people_data)
        if people_serializer.is_valid():
            people_serializer.save()
            return JsonResponse(people_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(people_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = People.objects.all().delete()
        return JsonResponse({'message': '{} people were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST', 'DELETE'])
def msr_project_list(request):
    # GET list of projects, POST a new project, DELETE all projects
    if request.method == 'GET':
        projects = Project.objects.all()
        
        project_name = request.GET.get('name', None)
        if project_name is not None:
            projects = projects.filter(project_name__icontains=project_name)
        
        project_serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(project_serializer.data, safe=False)
        # 'safe=False' for objects serialization
        
    elif request.method == 'POST':
        project_data = JSONParser().parse(request)
        project_serializer = ProjectSerializer(data=project_data)
        if project_serializer.is_valid():
            project_serializer.save()
            return JsonResponse(project_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Project.objects.all().delete()
        return JsonResponse({'message': '{} projects were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST', 'DELETE'])
def msr_series_list(request):
    # GET list of series, POST a new series, DELETE all series
    if request.method == 'GET':
        series = Series.objects.all()
        
        series_name = request.GET.get('name', None)
        if series_name is not None:
            series = series.filter(series_name__icontains=series_name)
        
        series_serializer = SeriesSerializer(series, many=True)
        return JsonResponse(series_serializer.data, safe=False)
        # 'safe=False' for objects serialization
        
    elif request.method == 'POST':
        series_data = JSONParser().parse(request)
        series_serializer = SeriesSerializer(data=series_data)
        if series_serializer.is_valid():
            series_serializer.save()
            return JsonResponse(series_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(series_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Series.objects.all().delete()
        return JsonResponse({'message': '{} series were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST', 'DELETE'])
def msr_change_list(request):
    # GET list of changes, POST a new change, DELETE all changes
    if request.method == 'GET':
        changes = Change.objects.all()
        
        change_serializer = ChangeSerializer(changes, many=True)
        return JsonResponse(change_serializer.data, safe=False)
        # 'safe=False' for objects serialization
        
    elif request.method == 'POST':
        change_data = JSONParser().parse(request)
        change_serializer = ChangeSerializer(data=change_data)
        if change_serializer.is_valid():
            change_serializer.save()
            return JsonResponse(change_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(change_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Change.objects.all().delete()
        return JsonResponse({'message': '{} changes were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST', 'DELETE'])
def msr_mailing_list_list(request):
    # GET list of mailing_lists, POST a new mailing_list, DELETE all mailing_lists
    if request.method == 'GET':
        mailing_lists = MailingList.objects.all()
        
        mailing_list_serializer = MailingListSerializer(mailing_lists, many=True)
        return JsonResponse(mailing_list_serializer.data, safe=False)
        # 'safe=False' for objects serialization
        
    elif request.method == 'POST':
        mailing_list_data = JSONParser().parse(request)
        mailing_list_serializer = MailingListSerializer(data=mailing_list_data)
        if mailing_list_serializer.is_valid():
            mailing_list_serializer.save()
            return JsonResponse(mailing_list_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(mailing_list_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = MailingList.objects.all().delete()
        return JsonResponse({'message': '{} mailing list were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST', 'DELETE'])
def msr_patch_list(request):
    # GET list of patches, POST a new patch, DELETE all patches
    if request.method == 'GET':
        patches = Patch.objects.all()
        
        patch_name = request.GET.get('name', None)
        if patch_name is not None:
            patches = projects.filter(patch_name__icontains=project_name)
        
        patch_serializer = PatchSerializer(patches, many=True)
        return JsonResponse(patch_serializer.data, safe=False)
        # 'safe=False' for objects serialization
        
    elif request.method == 'POST':
        patch_data = JSONParser().parse(request)
        patch_serializer = PatchSerializer(data=patch_data)
        if patch_serializer.is_valid():
            patch_serializer.save()
            return JsonResponse(patch_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Patch.objects.all().delete()
        return JsonResponse({'message': '{} patches were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST', 'DELETE'])
def msr_comment_list(request):
    # GET list of comments, POST a new comment, DELETE all comments
    if request.method == 'GET':
        comments = Comment.objects.all()
        
        comment_serializer = CommentSerializer(comments, many=True)
        return JsonResponse(comment_serializer.data, safe=False)
        # 'safe=False' for objects serialization
        
    elif request.method == 'POST':
        comment_data = JSONParser().parse(request)
        comment_serializer = CommentSerializer(data=comment_data)
        if comment_serializer.is_valid():
            comment_serializer.save()
            return JsonResponse(comment_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Comment.objects.all().delete()
        return JsonResponse({'message': '{} comments were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def msr_people_detail(request, pk):
    # find people by pk (id)
    try: 
        people = People.objects.get(pk=pk) 
    except People.DoesNotExist: 
        return JsonResponse({'message': 'The person does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # GET / PUT / DELETE people
    if request.method == 'GET': 
        people_serializer = PeopleSerializer(people) 
        return JsonResponse(people_serializer.data)
    
    elif request.method == 'PUT': 
        people_data = JSONParser().parse(request) 
        people_serializer = PeopleSerializer(people, data=people_data) 
        if people_serializer.is_valid(): 
            people_serializer.save() 
            return JsonResponse(people_serializer.data) 
        return JsonResponse(people_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE': 
        people.delete() 
        return JsonResponse({'message': 'The person was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def msr_project_detail(request, pk):
    # find project by pk (id)
    try: 
        project = Project.objects.get(pk=pk) 
    except Project.DoesNotExist: 
        return JsonResponse({'message': 'The project does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # GET / PUT / DELETE project
    if request.method == 'GET': 
        project_serializer = ProjectSerializer(project) 
        return JsonResponse(project_serializer.data)
    
    elif request.method == 'PUT': 
        project_data = JSONParser().parse(request) 
        project_serializer = ProjectSerializer(project, data=project_data) 
        if project_serializer.is_valid(): 
            project_serializer.save() 
            return JsonResponse(project_serializer.data) 
        return JsonResponse(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE': 
        project.delete() 
        return JsonResponse({'message': 'Project was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def msr_series_detail(request, pk):
    # find series by pk (id)
    try: 
        series = Series.objects.get(pk=pk) 
    except Series.DoesNotExist: 
        return JsonResponse({'message': 'The series does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # GET / PUT / DELETE series
    if request.method == 'GET': 
        series_serializer = SeriesSerializer(series) 
        return JsonResponse(series_serializer.data)
    
    elif request.method == 'PUT': 
        series_data = JSONParser().parse(request) 
        series_serializer = SeriesSerializer(series, data=series_data) 
        if series_serializer.is_valid(): 
            series_serializer.save() 
            return JsonResponse(series_serializer.data) 
        return JsonResponse(series_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE': 
        series.delete() 
        return JsonResponse({'message': 'Series was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def msr_change_detail(request, pk):
    # find change by pk (id)
    try: 
        change = Change.objects.get(pk=pk) 
    except Change.DoesNotExist: 
        return JsonResponse({'message': 'The change does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # GET / PUT / DELETE change
    if request.method == 'GET': 
        change_serializer = ChangeSerializer(change) 
        return JsonResponse(change_serializer.data)
    
    elif request.method == 'PUT': 
        change_data = JSONParser().parse(request) 
        change_serializer = ChangeSerializer(change, data=change_data) 
        if change_serializer.is_valid(): 
            change_serializer.save() 
            return JsonResponse(change_serializer.data) 
        return JsonResponse(change_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE': 
        change.delete() 
        return JsonResponse({'message': 'Change was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def msr_mailing_list_detail(request, pk):
    # find mailing_list by pk (id)
    try: 
        mailing_list = MailingList.objects.get(pk=pk) 
    except MailingList.DoesNotExist: 
        return JsonResponse({'message': 'The mailing list does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # GET / PUT / DELETE mailing_list
    if request.method == 'GET': 
        mailing_list_serializer = MailingListSerializer(mailing_list) 
        return JsonResponse(mailing_list_serializer.data)
    
    elif request.method == 'PUT': 
        mailing_list_data = JSONParser().parse(request) 
        mailing_list_serializer = MailingListSerializer(mailing_list, data=mailing_list_data) 
        if mailing_list_serializer.is_valid(): 
            mailing_list_serializer.save() 
            return JsonResponse(mailing_list_serializer.data) 
        return JsonResponse(mailing_list_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE': 
        mailing_list.delete() 
        return JsonResponse({'message': 'Mailing list was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def msr_patch_detail(request, pk):
    # find patch by pk (id)
    try: 
        patch = Patch.objects.get(pk=pk) 
    except Patch.DoesNotExist: 
        return JsonResponse({'message': 'The patch does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # GET / PUT / DELETE patch
    if request.method == 'GET': 
        patch_serializer = PatchSerializer(patch) 
        return JsonResponse(patch_serializer.data)
    
    elif request.method == 'PUT': 
        patch_data = JSONParser().parse(request) 
        patch_serializer = PatchSerializer(patch, data=patch_data) 
        if patch_serializer.is_valid(): 
            patch_serializer.save() 
            return JsonResponse(patch_serializer.data) 
        return JsonResponse(patch_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE': 
        patch.delete() 
        return JsonResponse({'message': 'Patch was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'PUT', 'DELETE'])
def msr_comment_detail(request, pk):
    # find comment by pk (id)
    try: 
        comment = Comment.objects.get(pk=pk) 
    except Comment.DoesNotExist: 
        return JsonResponse({'message': 'The comment does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    # GET / PUT / DELETE comment
    if request.method == 'GET': 
        comment_serializer = CommentSerializer(comment) 
        return JsonResponse(comment_serializer.data)
    
    elif request.method == 'PUT': 
        comment_data = JSONParser().parse(request) 
        comment_serializer = CommentSerializer(comment, data=comment_data) 
        if comment_serializer.is_valid(): 
            comment_serializer.save() 
            return JsonResponse(comment_serializer.data) 
        return JsonResponse(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE': 
        comment.delete() 
        return JsonResponse({'message': 'Comment was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)