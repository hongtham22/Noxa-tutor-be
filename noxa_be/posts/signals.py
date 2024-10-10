# posts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import JobPost
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=JobPost)
def notify_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_instance = JobPost.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'jobpost_group',
                {
                    'type': 'send_status_change',
                    'post_id': str(instance.post_id),
                    'status': instance.status,
                }
            )