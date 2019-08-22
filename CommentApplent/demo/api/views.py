from django.shortcuts import render
from django.conf import settings
import requests
import json
from django.http import JsonResponse
from api import models
from django.views.decorators.csrf import csrf_exempt
from rest_framework_jwt.settings import api_settings
from django.core.files import File
from io import BytesIO
from urllib.request import urlopen, urlretrieve
import os
from django.core import serializers
import datetime
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
        if employees.count() ==0:
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
                #'data': json.loads(serializers.serialize('json',employees))
            }

        return JsonResponse(result)


def get_employee_by_id(request):
    if request.method == 'GET':
        employee_id = request.GET.get('employee_id')
        #data = json.loads(request.body.decode())
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
                #'data': json.loads(serializers.serialize('json',employee))
            }

        return JsonResponse(result)

#model转json
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
        employee = models.TB_EMPLOYEE.objects.get(id = employee_id)
        user = models.TB_USER.objects.get(open_ID=open_Id)
        comment = models.TB_COMMENT.objects.filter(user=user,add_time=datetime.datetime.now())
        if not comment:
            comment = models.TB_COMMENT(employee=employee, user=user,content=content,score=score)
            comment.save()
            result = {
                'code': 200,
                'msg': '评价成功',
                'data': {
                    'userInfo': {
                        'userId': comment.id,
                    }
                },
                'time':datetime.datetime.now()
            }
        else:
            result = {
                'code': 201,
                'msg': '今天已评论',
                'data':'',
                'time':datetime.datetime.now()
            }
        return JsonResponse(result)
    else:
        return ''