from django.shortcuts import render, redirect
from django.views import View
from user.models import User, Address

# Create your views here.


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

        user = User.objects.create(
            username=username, password=password, email=email, is_active=0)
        user.save()
        return redirect('/')
