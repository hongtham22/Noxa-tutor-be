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
    
def convert_to_unicode(text):
    conversion_dict = {
        'toan': 'math',
        'van hoc': 'literature',
        'ngu van': 'literature',
        'van': 'literature',
        'vat ly': 'physics',
        'ly': 'physics',
        'hoa hoc': 'chemistry',
        'hoa': 'chemistry',
        'sinh hoc': 'biology',
        'sinh': 'biology',
        'tieng anh': 'english',
        'anh van': 'english',
        'anh': 'english',
        'lich su': 'history',
        'su': 'history',
        'dia ly': 'geography',
        'dia': 'geography',
        'kinh te': 'economy',
        'khoa hoc may tinh' : 'computer_science',
        'khoa hoc': 'computer_science',
        'kh': 'computer_science',
        'may tinh': 'computer_science',
    }
    return conversion_dict.get(text)


def convert_to_unicode_bg(text):
    conversion_dict = {
        'tot nghiep': ['graduate', 'high_school_diploma'],
        'tot nghiep dai hoc': 'university_graduate',
        'thpt': 'high_school_diploma',
        'trung hoc pho thong': 'high_school_diploma',
        'pho thong': 'high_school_diploma',
        'trung hoc': 'high_school_diploma',
        'sinh vien': 'student',
        'sv': 'student',
        'dai hoc': 'university',
        'su pham': 'education',
        'dai hoc su pham': 'education',
    }
    # return conversion_dict.get(text)
    matched_values = []

    # Duyệt qua từng key trong từx điển để kiểm tra
    for key, value in conversion_dict.items():
        if key in text:
            matched_values.append(value)  
    print('matched_values', matched_values)
    return matched_values if matched_values else None  
def is_substring(a, b):
    print("============", a,b)
    return a in b

# def getPostId(dict, word):
#     print("word",word)
#     list = []
#     for di in dict:
#         description = di.get('description', '')
#         address = di.get('address', '')
#         # print(description, address)
#         if description:
#             if is_substring(word, description):
#                 list.append (di['id'])
#         if address:
#             if is_substring(word, address):
#                  list.append (di['id'])
#     return list

def getPostId(dict, word):
    print("word:", word)
    ids = []
    for di in dict:
        description = di.get('description', '')
        address = di.get('address', '')
        if description and is_substring(word, description):
            ids.append(di['id'])
        if address and is_substring(word, address):
            ids.append(di['id'])
    return ids

class SearchView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes]
    

    def get(self, request):
        query = request.query_params.get('query', None)
        print('query:', query)
        filters = Q()
        results = {}
        posts = JobPost.objects.all()

        # pattern
        pattern_grade = r'cap\s+(\d+)'
        pattern_student_number = r'(\d+)\s*(hoc sinh|sinh vien|sv|hoc tro|em|be)'
        pattern_session = r'(\d+)\s*(buoi|ngay)'
        pattern_duration = r'(\d+)\s*(tuan|thang)'
        # pattern_subject = r'(Toan|Vanhoc|Van|Nguvan|Vatly|Ly|Hoahoc|Hoa|Sinhhoc|TiengAnh|Anhvan|Lichsu|Su|Dialy|Dia|Kinhte|Khoahocmaytinh|Khoahoc)'
        pattern_subject = r'(?:mon|lop)?\s*(toan|van hoc|ngu van|van|vat ly|ly|hoa hoc|hoa|sinh hoc|sinh|tieng anh|anh van|anh|lich su|su|dia ly|dia|kinh te|khoa hoc|kh|khoa hoc may tinh|may tinh)'
        pattern_background = r'(tot nghiep|tot nghiep dai hoc|thpt|trung hoc pho thong|pho thong|trung hoc|sinh vien|sv|dai hoc|su pham|dai hoc su pham)'
        
        # xử lý query:
        # cắt chuỗi query thành các từ đơn để match
        normalized_query = [word.strip() for word in unidecode(query).lower().split(',')]


        # 1: tìm cấp grade
        for word in normalized_query:
            match = re.search(pattern_grade, word)
            if match:
                grade_number = match.group(1) 
                filters |= Q(grade=grade_number)


        #2: tìm số học sinh
        for word in normalized_query:
            match = re.search(pattern_student_number, word)
            if match:
                student_number = match.group(1) 
                print('student_number', student_number)
                filters |= Q(student_number=student_number)

        #3: tìm số buổi học
        for word in normalized_query:
            match = re.search(pattern_session, word)
            if match:
                session_number = match.group(1) 
                print('session_number', session_number)
                filters |= Q(session_per_week=session_number)

        #4: tìm thời gian duration
        for word in normalized_query:
            match = re.search(pattern_duration, word)
            if match:
                duration = match.group(1) 
                print('duration', duration)
                filters |= Q(duration=duration)

        #5: subject
        subject = ''
        sbj_convert = ''
        for word in normalized_query:
            match = re.search(pattern_subject, word)
            if match:
                subject = match.group(1) 
                sbj_convert = convert_to_unicode(subject)
                filters |= Q(subject=sbj_convert)

        #6: background
        bg_convert = ""
        for word in normalized_query:
            match = re.search(pattern_background, word)
            if match:
                background = match.group(1) 
                bg_convert = convert_to_unicode_bg(background)
                print('bg_convert', bg_convert)  # This should print the list, e.g., ['graduate', 'high_school_diploma']
                if len(bg_convert) == 1:
                    filters |= Q(background_desired__icontains=bg_convert[0])
                else:    
                    for bground in bg_convert:
                        for i in range(len(bground)):
                            print("bground",bground[i])
                            filters |= Q(background_desired__icontains=bground[i])

        #7: ........
        filtered_posts = [
            {'id': post.post_id, 
             'description': unidecode(post.description).lower() if post.description else None, 
             'address': unidecode(post.address).lower() if post.address else None}
            for post in posts
        ]
        postid = []
        for word in normalized_query:
            id = getPostId(filtered_posts, word)
            print("id:",id)
            postid.append(id)

        print('postid', postid)   
        for pid in postid:
            print(pid)
            filters |= Q(post_id=pid)

        # for word in normalized_query:
        #     # if word 
        #     filtered_posts = [
        #         post for post in filtered_posts
        #         if word in post['description'] or word in post['address']
        #     ]
        #     filters |= Q(post_id=word)



        posts = JobPost.objects.filter(filters) 
        serializer = PostSerializer(posts, many=True)

        return Response({
            "query": normalized_query if normalized_query else None,
            "posts": serializer.data,
            "subject": subject if subject else None,
            "sbj_convert": sbj_convert if sbj_convert else None,
            "bg_convert": bg_convert if bg_convert else None
            # "check": next_word if next_word else None
        })

class testhah(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes]

    def get(self, request):
        query = request.query_params.get('query', None)
        posts = JobPost.objects.all()
        # print(posts)

        # # Lọc các bài đăng
        # filtered_posts = [
        #     {'id': post.post_id, 'description': post.description}
        #     for post in posts
        # ]
        # for fil_port in filtered_posts:
        #     fil_port_unicode = unidecode(fil_port['description'])

        #     print("I: ", fil_port_unicode)
        # print(filtered_posts)  # In ra filtered_posts

        # Thay đổi ở đây để sử dụng filtered_posts
        return Response({
            "posts": filtered_posts,  # Trả về filtered_posts
        })
