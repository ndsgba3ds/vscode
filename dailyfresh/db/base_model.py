from django.db import models

class MODELNAME(models.Model):
    """Model definition for MODELNAME."""

    # TODO: Define fields here

    create_time = models.DateTimeField(auto_now_add = True,verbose_name="创建时间")
    

    class Meta:
        """Meta definition for MODELNAME."""
        abstract = True

    def __str__(self):
        """Unicode representation of MODELNAME."""
        pass

