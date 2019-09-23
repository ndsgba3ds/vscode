from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from user.models import User, Address
from goods.models import GoodsSKU
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_mail
from django.contrib.auth import login, authenticate, logout
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
# Create your views here.

# /user/register


class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([username, password, email]):
            return render(request, 'register.html', {'error': '数据不完整！'})

        if allow != 'on':
            return render(request, 'register.html', {'error': '请勾选同意！'})

        # 检查用户名是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            render(request, 'register.html', {'error': '用户名已存在'})

        user = User.objects.create_user(
            username=username, password=password, email=email, is_active=0)
        user.save()
        # 认证
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode()
        # html_message = '欢迎%s,请点击<a href ="http://127.0.0.1:8000/user/activate/%s">http://127.0.0.1:8000/user/activate/%s</a>激活' % (
        #     username, token, token)
        # send_mail('激活邮件', '', settings.EMAIL_FROM, [
        #     email], html_message=html_message)
        send_register_active_mail.delay(email, username, token)
        return redirect('/')

# /user/aitive


class ActiveView(View):
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect('/user/login')
        except SignatureExpired as e:
            return HttpResponse('激活失败')

# /user/login


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')
        if not all([username, password]):
            return render(request, 'login.html', {'error': '数据不完整！'})
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', '/')
                response = redirect(next_url)
                if remember == 'on':
                    response.set_cookie(
                        'username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return redirect(next_url)
            else:
                return render(request, 'login.html', {'error': '未激活'})
        else:
            return render(request, 'login.html', {'error': '用户不存在'})

# /user/logout


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')


# /user


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        address = Address.objects.get_default_address(user)
        conn = get_redis_connection('default')
        history_key = 'history_%d' % user.id

        # 获取用户最新浏览的5个商品的id
        sku_ids = conn.lrange(history_key, 0, 4)
        goods_list = []
        for id in sku_ids:
            try:
                goods = GoodsSKU.objects.get(id=id)
            except GoodsSKU.DoesNotExist:
                pass
            goods_list.append(goods)

        return render(request, 'user_center_info.html', {'address': address, 'goods_list': goods_list})
# /userorder


class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_order.html')
# /user/address


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html', {'address': address})

    def post(self, request):
        user = request.user
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver, addr, zip_code, phone]):
            return render(request, 'user_center_site.html', {'error': '数据不完整'})

        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        Address.objects.create(user=user, receiver=receiver, addr=addr,
                               zip_code=zip_code, phone=phone, is_default=is_default)
        return redirect('/user/address')
