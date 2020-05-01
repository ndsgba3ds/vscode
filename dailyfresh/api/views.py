from django.shortcuts import render
from django.conf import settings
import requests
import json
from django.http import JsonResponse, HttpResponse
from api import models
from django.views.decorators.csrf import csrf_exempt
from rest_framework_jwt.settings import api_settings
from django.core.files import File
from io import BytesIO
from urllib.request import urlopen, urlretrieve
import os
from django.core import serializers
import datetime
from pyecharts.charts import Bar, Line, Timeline
from pyecharts import options as opts

from random import randrange
from django.views.generic import View
# Create your views here.


@csrf_exempt
def wx_login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        nickName = data['nickName']
        code = data['code']
        url = data['avatarUrl']
        result = urlretrieve(url)
        if not code or len(code) < 1:
            result = {
                'code': data,
                'msg': '需要微信授权',
                'data': ''
            }
            return JsonResponse(result)
        openId = getWeChatOpenId(code)
        if openId is None:
            result = {
                'code': 202,
                'msg': '调用微信出错',
                'data': ''
            }
            return JsonResponse(result)
        user = models.TB_USER.objects.filter(open_ID=openId).first()
        if not user:
            user = models.TB_USER(open_ID=openId, username=nickName)
            user.user_image.save(os.path.basename(
                url), File(open(result[0], 'rb')))
            user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        result = {
            'code': 200,
            'msg': '登录成功',
            'data': {
                'userInfo': {
                    'userId': user.id,
                    'openId': user.open_ID,
                    # 'avatarUrl':user.user_image
                }

            },
            'token': token
        }
        return JsonResponse(result)
    else:
        return ''


def getWeChatOpenId(code):
    url = str("https://api.weixin.qq.com/sns/jscode2session?appid=" + settings.APPID +
              "&secret=" + settings.SECRET + "&js_code=" + code + "&grant_type=authorization_code")
    r = requests.get(url)
    openid = r.json()['openid']
    return openid


def get_employees(request):
    if request.method == 'GET':
        employees = models.TB_EMPLOYEE.objects.all().values()
        if employees.count() == 0:
            result = {
                'code': 201,
                'msg': '没有数据',
                'data': ''
            }
        else:
            result = {
                'code': 200,
                'msg': '查询成功',
                'data': list(employees)
                # 'data': json.loads(serializers.serialize('json',employees))
            }

        return JsonResponse(result)


def get_employee_by_id(request):
    if request.method == 'GET':
        employee_id = request.GET.get('employee_id')
        # data = json.loads(request.body.decode())
        employee = models.TB_EMPLOYEE.objects.get(id=employee_id)
        if not employee:
            result = {
                'code': 201,
                'msg': '没有数据',
                'data': ''
            }
        else:
            result = {
                'code': 200,
                'msg': '查询成功',
                'data': object_to_json(employee)
                # 'data': json.loads(serializers.serialize('json',employee))
            }

        return JsonResponse(result)

# model转json


def object_to_json(obj):
    return dict([(kk, obj.__dict__[kk]) for kk in obj.__dict__.keys() if kk != "_state"])


@csrf_exempt
def add_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        open_Id = data['openId']
        employee_id = data['employeeId']
        content = data['content']
        score = data['score']
        if open_Id is None:
            result = {
                'code': 202,
                'msg': '调用微信出错',
                'data': ''
            }
            return JsonResponse(result)
        employee = models.TB_EMPLOYEE.objects.get(id=employee_id)
        user = models.TB_USER.objects.get(open_ID=open_Id)
        comment = models.TB_COMMENT.objects.filter(
            user=user, add_time=datetime.datetime.now())
        if not comment:
            comment = models.TB_COMMENT(
                employee=employee, user=user, content=content, score=score)
            comment.save()
            result = {
                'code': 200,
                'msg': '评价成功',
                'data': {
                    'userInfo': {
                        'userId': comment.id,
                    }
                },
                'time': datetime.datetime.now()
            }
        else:
            result = {
                'code': 201,
                'msg': '今天已评论',
                'data': '',
                'time': datetime.datetime.now()
            }
        return JsonResponse(result)
    else:
        return ''


def get_comment_by_openId(request):
    if request.method == 'GET':
        open_Id = request.GET.get('openId')
        user = models.TB_USER.objects.get(open_ID=open_Id)
        comment = models.TB_COMMENT.objects.filter(
            user=user, add_time=datetime.datetime.now())
        if not comment:
            result = {
                'code': 201,
                'msg': '没有数据',
            }
        else:
            result = {
                'code': 200,
                'msg': '查询成功',
            }

        return JsonResponse(result)


def day_get(d):
    for i in range(0, 7):
        oneday = datetime.timedelta(days=i)
        day = d - oneday
        date_to = datetime.datetime(day.year, day.month, day.day)
        yield str(date_to)[:10]


def line_base():
    d = datetime.datetime.now()
    list_day = []
    for obj in day_get(d):
        list_day.append(obj)
    list_week_day = list_day[::-1]
    employees = models.TB_EMPLOYEE.objects.all()
    employee_names = models.TB_EMPLOYEE.objects.values_list("name")
    names = [i[0] for i in employee_names]
    count = len(names)
    names.insert(0, 'project')
    list = []
    for day in list_week_day:
        counts_list = []
        date = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        for employee in employees:
            counts = models.TB_COMMENT.objects.filter(
                employee=employee, add_time=date).count()
            counts_list.append(counts)
        counts_list.insert(0, day)
        list.append(counts_list)
    list.insert(0, names)

    return {'xdata': list_week_day, 'ydata': list, 'count': count}


def bar_base():
    employees = models.TB_EMPLOYEE.objects.all()
    employee_names = models.TB_EMPLOYEE.objects.values_list("name")
    names = [i[0] for i in employee_names]
    count = len(names)
    list = []
    for employee in employees:
        data = []
        for i in range(1, 6):
            counts = models.TB_COMMENT.objects.filter(
                employee=employee, score=i).count()
            data.append({'value': counts,'name': str(i)+'星'})
        list.append(data)

    return {'names': names, 'list': list, 'count': count}


class LineView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(line_base()))


class BarView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(bar_base()))


class IndexView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/index.html").read())
