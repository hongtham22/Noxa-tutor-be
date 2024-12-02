from django.db import models
import uuid

from accounts.models import JobPost, User


# Create your models here.
class JobPostComment(models.Model):
    comment_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    post_id = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_parent_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.comment)
    
class JobPostReact(models.Model):
    REACTION_CHOICES = (
        (1, "Like"),
        (0, "Unlike"),
    )
    reaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    post_id = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    reaction_type = models.IntegerField(choices=REACTION_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "post_id",
            "user_id",
        )  # User chỉ được like 1 lần vào mỗi bài đăng

    def __str__(self):
        return f"{self.user_id} - {self.post_id} - {self.reaction_type}"