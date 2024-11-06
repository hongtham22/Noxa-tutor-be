from datetime import datetime, timedelta, timezone
from accounts.enums import Role, Status, Subject
from accounts.models import Feedback, JobPost, User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import Avg

class ChartHelper():
    def get_posts_stat_by_subjects(self):
        data = {subject : {'posts': 0} for subject in Subject.values}
        result = JobPost.objects.values('subject').annotate(count=Count('subject'))
        for item in result:
            data[item['subject']] = {'posts': item['count']}

        return data
    
    def get_posts_stat_by_status(self):
        data = {status: {'posts': 0} for status in Status.values}
        result = JobPost.objects.values('status').annotate(count=Count('status'))
        for item in result:
            data[item['status']] = {'posts': item['count']}

        return data
    
    def get_users_stat_by_roles(self, duration=1):
        data = {}
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=duration * 30)  # Assuming 1 month = 30 days
        result = User.objects.filter(date_joined__range=(start_date, end_date)).exclude(role=Role.ADMIN).annotate(month=TruncMonth('date_joined')).values('month', 'role').annotate(count=Count('role')).order_by('month')
        for item in result:
            month = item['month'].strftime('%Y-%m')
            if month not in data:
                data[month] = {'tutor': 0, 'parent': 0}
            data[month][item['role']] = item['count']

        return data
    
    def get_tutors_stat_by_rating(self):
        data = {'0-1': 0, '1-2': 0, '2-3': 0, '3-4': 0, '4-5': 0}
        
        avg_rating_per_tutor = Feedback.objects.values('tutor_id').annotate(avg_rating=Avg('rating')).order_by('tutor_id')
        print (avg_rating_per_tutor)

        for item in avg_rating_per_tutor:
            if (item['avg_rating'] >= 0 and item['avg_rating'] < 1):
                data['0-1'] += 1
            elif (item['avg_rating'] >= 1 and item['avg_rating'] < 2):
                data['1-2'] += 1
            elif (item['avg_rating'] >= 2 and item['avg_rating'] < 3):
                data['2-3'] += 1
            elif (item['avg_rating'] >= 3 and item['avg_rating'] < 4):
                data['3-4'] += 1
            elif (item['avg_rating'] >= 4):
                data['4-5'] += 1

        return data
    
    def get_summary_stats(self, duration):
        data = {}

        tutors_total = User.objects.filter(role=Role.TUTOR).count()
        parents_total = User.objects.filter(role=Role.PARENT).count()   
        posts_total = JobPost.objects.exclude(status=Status.CLOSED or Status.CANCELLED).count()
        queue = JobPost.objects.filter(status=Status.PENDING_APPROVAL).count()

        data['tutors_total'] = tutors_total
        data['parents_total'] = parents_total
        data['posts_total'] = posts_total
        data['queue'] = queue

        return data