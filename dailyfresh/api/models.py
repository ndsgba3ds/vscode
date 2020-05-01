from django.db import models

# Create your models here.

# 员工表(TB_EMPLOYEE)


class TB_EMPLOYEE(models.Model):
    name = models.CharField(max_length=11, verbose_name="姓名")
    header_image = models.ImageField(
        verbose_name='头像', null=True, upload_to='images')

    def __str__(self): 
        return self.name

    class Meta:
        db_table = "TB_EMPLOYEE"
        verbose_name = '员工'
        verbose_name_plural = verbose_name


# 用户表（TB_USER）
class TB_USER(models.Model):
    open_ID = models.CharField(max_length=64, verbose_name='微信唯一标识')
    username = models.CharField(max_length=32, verbose_name='用户微信名称')
    user_image = models.ImageField(verbose_name='用户头像',null=True, upload_to='images')

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'TB_USER'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

# 用户评论(TB_COMMENT)


class TB_COMMENT(models.Model):
    employee = models.ForeignKey(
        TB_EMPLOYEE, on_delete=models.CASCADE, related_name='employeeName', verbose_name='员工')
    user = models.ForeignKey(
        TB_USER, on_delete=models.CASCADE, related_name='userName', verbose_name='用户')
    content = models.TextField(verbose_name='评论内容', null=True)
    score = models.IntegerField(verbose_name='评分', default=1)
    add_time = models.DateField(verbose_name='评论时间', auto_now=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'TB_COMMENT'
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def short_content(self):
        if len(str(self.content))>50:
            return '{}...'.format(str(self.content)[0:50])
        else:
            return str(self.content)
    short_content.allow_tags = True

    short_content.short_description = '评论'
