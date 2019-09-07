from django.db import models
from django.contrib.auto.models import AbstractUser
from db.base_model import BaseModel

# Create your models heer.


class User(AbstractUser, BaseModel):
    # 用户模型类

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Address(BaseModel):
    # 地址模型类

    User = models.ForeignKey(
        'User', on_delete=models.CASCADE, verbose_name='所属用户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, verbose_name='邮政编号')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        db_table = 'db_address'
        verbose_name = '收获地址'
        verbose_name_plural = '收获地址'
