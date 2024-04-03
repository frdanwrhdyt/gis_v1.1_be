from django.db import models
from django.utils import timezone


class PermanentDeletionManager(models.Manager):
    def expired_records(self):
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        return self.get_queryset().filter(is_deleted=True, updated_at__gte=thirty_days_ago)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = models.Manager()
    permanent_deletion_objects = PermanentDeletionManager()

    class Meta:
        abstract = True