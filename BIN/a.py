from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsParent, IsTutor
from accounts.models import * 
from application.serializers.post_serializer import PostSerializer, ClassTimeSerializer
import re
from unidecode import unidecode
from accounts.enums import Subject 

from .patterns import pattern_subject2

"""
PostView API endpoint for JobPost model. Use for parent to CRUD their job posts.
"""

class PostView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes] 
    
    def get(self, request, pk=None):
        if pk:
            if User.objects.filter(user_id=pk).exists():
                user = get_object_or_404(User, user_id=pk)
                posts = JobPost.objects.filter(parent_id=user)
                post_serializer = PostSerializer(posts, many=True, context={'request_type': 'detail'})
            else:
                post = get_object_or_404(JobPost, post_id=pk)
                post_serializer = PostSerializer(post, context={'request_type': 'detail'})
        else:
            posts = JobPost.objects.all()
            post_serializer = PostSerializer(posts, many=True, context={'request_type': 'detail'})
        return Response(post_serializer.data)
    
    def post(self, request):
        post_serializer = PostSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        post = get_object_or_404(JobPost, post_id=pk)
        post_serializer = PostSerializer(post, data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_object_or_404(JobPost, post_id=pk)
        post.delete()

        # check deleted in class_time
        class_times = ClassTime.objects.filter(post_id=pk)
        if not class_times:
            print ('Logic works perfectly')
        for class_time in class_times:
            class_time.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# class PostView(APIView):
#     def get_permissions(self):
#         if self.request.method == 'GET':
#             return [AllowAny()]  # Không yêu cầu xác thực cho GET
#         return [permission() for permission in self.permission_classes] 

#     def get(self, request, pk=None):
#         filters = {key: request.query_params.get(key) for key in ['subject', 'status', 'grade', 'background_desired'] if request.query_params.get(key) is not None}

#         if pk:
#             post = get_object_or_404(JobPost, post_id=pk)
#             serializer = PostSerializer(post)
#         else:
#             posts = JobPost.objects.filter(**filters)
#             serializer = PostSerializer(posts, many=True)
        
#         return Response(serializer.data)
    
# class PostSearchView(APIView):
#     def get_permissions(self):
#         if self.request.method == 'GET':
#             return [AllowAny()]  # Không yêu cầu xác thực cho GET
#         return [permission() for permission in self.permission_classes]
    
    
#     def get(self, request):
#         query = request.query_params.get('query', None)
#         filters = {key: request.query_params.get(key) for key in ['subject', 'status', 'grade', 'background_desired'] if request.query_params.get(key) is not None}
#         posts = JobPost.objects.all()

#         if query:
#             posts = JobPost.objects.filter(
#                 Q(subject__icontains=query) |
#                 Q(status__icontains=query) |
#                 Q(grade__icontains=query) | 
#                 Q(background_desired__icontains=query) |
#                 Q(duration__icontains=query) | 
#                 Q(session_per_week__icontains=query) |
#                 Q(wage_per_hour__icontains=query) | 
#                 Q(student_number__icontains=query)
#             )

#         if filters:
#             posts = posts.filter(**filters)


#         serializer = PostSerializer(posts, many=True)
        
#         return Response(serializer.data)
def convert_to_unicode(text):
    print("text", text)
    text = text.lower()
    conversion_dict = {
        'toan': 'math',
        'van': 'literature',
        'vanhoc': 'literature',
        'nguvan': 'literature',
        'hoa': 'chemistry',
        'hoahoc': 'chemistry',
        'vatly': 'physics',
        'ly': 'physics',
        'anhvan': 'english',
        'tienganh': 'english',
        'lichsu': 'history',
        'su': 'history',
        'dialy': 'geography',
        'dia': 'geography',
        'kinhte': 'economy',
        'hoahocmaytinh' : 'computer_science',
        'khoahoc': 'computer_science',
    }
    print("test: ", conversion_dict.get(text))
    return conversion_dict.get(text)

class PostSearchView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes]
    

    def get(self, request):
        query = request.query_params.get('query', None)
        filters = Q()
        # filters = {key: request.query_params.get(key) for key in ['subject', 'status', 'grade', 'background_desired'] if request.query_params.get(key) is not None}

        # Extract filters from query params
        extracted_filters = {key: request.query_params.get(key) for key in ['subject', 'status', 'grade', 'background_desired'] if request.query_params.get(key) is not None}
        filters |= Q(**extracted_filters)


        pattern_session = r'(\d+)(buoi|ngay)'
        pattern_student_number = r'(\d+)(hocsinh|sinhvien|sv|hoctro|em|be)'
        pattern_grade = r'(cap)(\d+)'
        pattern_duration = r'(\d+)(tuan|thang)'
        subjects_enum = Subject.choices  # Dùng thuộc tính choices của enum
        pattern_subject = r'(Toan|Vanhoc|Van|Nguvan|Vatly|Ly|Hoahoc|Hoa|Sinhhoc|Sinh|TiengAnh|Anhvan|Lichsu|Su|Dialy|Dia|Kinhte|Khoahocmaytinh|Khoahoc)'
        print('pattern_subject', pattern_subject)
        # pattern_subject
        # pattern_subject = '|'.join(unidecode(subject[1].strip().replace(' ', '')) for subject in subjects_enum[:-1])
        # pattern_subject = pattern_subject.join(r'(|toan|van|ly|hoa|sinh|anh|su|dia|khoahoc|)')
        # pattern_subject = f"{pattern_subject}|toan|van|ly|hoa|sinh|anh|su|dia|khoahoc"
        # pattern_subject = pattern_subject.join(unidecode(subject[1].strip().replace(' ', '')) for subject in subjects_enum[:-1])
        # pattern_subject = pattern_subject.join(unidecode(subject[1].strip().replace(' ', '')) for subject in subjects_enum[:-1])
        # print('pattern_subject', pattern_subject)

        if query:
            normalized_query = unidecode(query.replace(' ', ''))
            print('normalized_query', normalized_query)

            # Khởi tạo một dictionary để lưu trữ kết quả
            results = {}
            # posts = JobPost.objects.all() 
            # filters = Q()
            
            
            # session
            match = re.search(pattern_session, normalized_query)
            if match:
                number_session = match.group(1)
                results['number_session'] = number_session
                # posts = posts.filter(session_per_week=number_session)
                filters |= Q(session_per_week=number_session)

            # student
            match_student = re.search(pattern_student_number, normalized_query)
            if match_student:
                student_number = match_student.group(1)  # Lấy số học sinh
                results['student_number'] = student_number
                # posts = posts.filter(student_number=student_number)
                filters |= Q(student_number=student_number)


            # grade
            match_grade = re.search(pattern_grade, normalized_query)
            if match_grade:
                grade = match_grade.group(2)
                results['grade_pattern'] = grade
                # posts = posts.filter(grade=grade)
                filters |= Q(grade=grade)


            # duration
            match_duration = re.search(pattern_duration, normalized_query)
            if match_duration:
                duration = match_duration.group(1)
                results['duration_pattern'] = duration
                # posts = posts.filter(duration=duration)
                filters |= Q(duration=duration)

            # subject
            match_subject = re.search(pattern_subject, normalized_query, re.IGNORECASE)
            if match_subject:
                subject = convert_to_unicode(match_subject.group())
                results['subject_pattern'] = subject
                print(type(subject))
                print(">>>>: ", results['subject_pattern'])
                print(">>>>: ", subject)
                # Toan
                # posts = posts.filter(subject=subject)
                filters |= Q(subject=results['subject_pattern'])

        
        # Lọc posts với tất cả các điều kiện đã được xác định
        print('filters', filters)
        posts = JobPost.objects.filter(filters) 
        serializer = PostSerializer(posts, many=True)
        return Response({
            "message": "Kết quả tìm kiếm",
            # "data": results,
            # "data": results if results else "type",
            "posts": serializer.data
            })

