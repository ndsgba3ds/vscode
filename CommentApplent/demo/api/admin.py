from django.contrib import admin

# Register your models here.

from api import models
from django.utils.safestring import mark_safe

# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    list_display=['name','image']
    list_per_page=10
    

    def image(self,obj):
        return mark_safe('<img src="/media/%s" style="width:64px;height:64px;border-radius:32px" />' % obj.header_image)

    image.allow_tags = True

    image.short_description = '头像'



class UserAdmin(admin.ModelAdmin):
    list_display=['open_ID','username','image']
    list_per_page=10
    def image(self,obj):
        return mark_safe('<img src="/media/%s" style="width:64px;height:64px;border-radius:32px" />' % obj.user_image)

    image.allow_tags = True

    image.short_description = '头像'

class CommentAdmin(admin.ModelAdmin):
    list_display=['user','short_content','score_image','add_time']
    list_per_page=10

    def score_image(self,obj):
        count=0
        str_image = ''
        while count <obj.score:
            str_image +='<span class="el-icon-star-on"></span> '
            count +=1
        return mark_safe(str_image)

    score_image.allow_tags = True

    score_image.short_description = '评分'



admin.site.register(models.TB_EMPLOYEE,EmployeeAdmin)
admin.site.register(models.TB_USER,UserAdmin)
admin.site.register(models.TB_COMMENT,CommentAdmin)

