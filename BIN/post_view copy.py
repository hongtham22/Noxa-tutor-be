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

class PostSearchView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes]
    
    # def get(self, request):
    #     query = request.query_params.get('query', None)
        
    #     if query:
    #         # Kiểm tra số buổi học (ví dụ: "3 buổi")
    #         pattern_buoi = r'\d+\s+buổi'
    #         if re.search(pattern_buoi, query):  # Tìm nếu 'query' chứa mẫu này
    #             posts = JobPost.objects.filter(
    #                 Q(session_per_week=query) 
    #             )

    #             return Response({"message": f"Query contains buổi pattern: {query}"})
            
    #         # Kiểm tra môn học (ví dụ: toán, văn, sinh,...)
    #         subjects = ["toán", "văn", "sinh", "lý", "hóa", "anh"]
    #         if any(subject in query.lower() for subject in subjects):
    #             return Response({"message": f"Query contains subject: {query}"})
            
    #         # Kiểm tra cấp học (ví dụ: cấp 1, cấp 2, cấp 3)
    #         pattern_cap = r'cấp\s+[123]'
    #         if re.search(pattern_cap, query):  # Tìm nếu 'query' chứa cấp học
    #             return Response({"message": f"Query contains cấp pattern: {query}"})
            
    #     # In ra query nếu không khớp với điều kiện nào
    #     print(f"Query: {query}")
    #     return Response({'query': query})
    

    def get(self, request):
        query = request.query_params.get('query', None)
        pattern_session = r'(\d+)\s*([buoi|ngay|tiet])'
        pattern_student_number = r'(\d+)\s*([hocsinh|sinhvien|sv|hoctro|be]+)'
        pattern_grade = r'([cap])\s*(\d+)'
        pattern_duration = r'(\d+)\s*([tuan|thang])'
        subjects_enum = Subject.choices  # Dùng thuộc tính choices của enum
        #Toán|Văn học|Vật lý|Hóa học|Sinh học|Tiếng Anh|Lịch sử|Địa lý|Kinh tế|Khoa học máy tính
        pattern_subject = '|'.join(unidecode(subject[1].strip().replace(' ', '')) for subject in subjects_enum[:-1]) 
        print(pattern_subject)

        if query: 
            normalized_query = unidecode(query.replace(' ', ''))

            # session
            match = re.search(pattern_session, normalized_query)
            if match:
                number_session = match.group(1) 
                return Response({"message": f": {number_session}"})

            # student
            match_student = re.search(pattern_student_number, normalized_query)
            if match_student:
                student_number = match_student.group(1)
                print(f"Number student: {student_number}")
               
                return Response({"message": f"Number of student: {student_number}"})
            

            # grade
            match_grade = re.search(pattern_grade, normalized_query)
            if match_grade:
                grade = match_grade.group(2)
                print(f"grade: {grade}")
               
                return Response({"message": f"grade: {grade}"})
            

            # duration
            match_duration = re.search(pattern_duration, normalized_query)
            if match_duration:
                duration = match_duration.group(1)
                print(f"match_duration: {duration}")
               
                return Response({"message": f"match_duration: {duration}"})

            # subject
            match_subject = re.search(pattern_subject, normalized_query, re.IGNORECASE)
            if match_subject:
                print(f'Tìm thấy từ: "{match_subject.group()}" trong query.')
                return Response({"message": f"Number of student: {match_subject.group()}"})
            
        return Response({"message": "No query provided"})

        # if query:
            # match = re.search(pattern_session, query)
            # if match:
            #     number_session = match.group(1) 
            #     posts = JobPost.objects.filter(
            #         Q(session_per_week__icontains=number_session)
            #     )

            # match_student = re.search(pattern_student_number, query)
            # if match_student:
            #     student_number = match_student.group(1)
            #     print(f"Number student: {student_number}")
               
            #     return Response({"message": f"Number of student: {student_number}"})
            
            # match_grade = re.search(pattern_grade, query)
            # if match_grade:
            #     grade = match_grade.group(2)
            #     print(f"grade: {grade}")
               
            #     return Response({"message": f"grade: {grade}"})
            
            # match_duration = re.search(pattern_duration, query)
            # if match_duration:
            #     duration = match_duration.group(1)
            #     print(f"match_duration: {duration}")
               
            #     return Response({"message": f"match_duration: {duration}"})



        # serializer = PostSerializer(posts, many=True)
        # return Response(serializer.data)


        
    
