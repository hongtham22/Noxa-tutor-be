from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.permission import IsAdmin
from application.views.chart_helper import ChartHelper



class StatisticView (APIView):
    #permission_classes = [IsAuthenticated, IsAdmin]
    permission_classes = [AllowAny]
    chart_helper = ChartHelper()
    
    def get(self, request):
        data = {}
        category = request.query_params.get('category', None)
        duration = request.query_params.get('duration', 1)

        if category == 'posts':
            data['data'] = self.get_statistics_posts(duration)
        elif category == 'users':
            data['data'] = self.get_statistics_users(duration)
        elif category == 'classes':
            data['data'] = self.get_statistics_classes(duration)
        else:
            data['data'] = self.get_summary_statistics(duration)

        return JsonResponse(data)
    
    def get_statistics_posts(self, duration):
        data = {}

        data['posts_stat_by_subjects'] = self.chart_helper.get_posts_stat_by_subjects()
        data['posts_stat_by_status'] = self.chart_helper.get_posts_stat_by_status()
        
        return data 
    
    def get_statistics_users(self, duration):
        data = {}

        data['users_stat_by_roles'] = self.chart_helper.get_users_stat_by_roles(duration)

        return data

    def get_statistics_classes(self, duration):
        data = {}

        data['tutors_stat_by_rating'] = self.chart_helper.get_tutors_stat_by_rating()

        return data
    
    def get_summary_statistics(self, duration):
        data = {}
        
        data['summary_stat'] = self.chart_helper.get_summary_stats(duration)

        return data

    