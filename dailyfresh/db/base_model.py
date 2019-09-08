from django.db import models

class BaseModel(models.Model):
    """Model definition for MODELNAME."""

    # TODO: Define fields here

    create_time = models.DateTimeField(auto_now_add = True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now = True , verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        """Meta definition for MODELNAME."""
        abstract = True

