from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
# Create your views here.


class CartAddView(View):
    def post(self, request):
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 4, 'error': '请登录'})

        if not all([sku_id, count]):
            return JsonResponse({'res': 0, 'error': '数据不完整'})

        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 1, 'error': '商品数量出错'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'error': '商品不存在'})

        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        cart_count = conn.hget(cart_key, sku_id)

        if cart_count:
            count += int(cart_count)
        if count > sku.stock:
            return JsonResponse({'res': 3, 'error': '商品库存不足'})
        conn.hset(cart_key, sku_id, count)

        total_count = conn.hlen(cart_key)
        return JsonResponse({'res': 5, 'message': '商品数量出错', 'total_count': total_count})


class CartInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取用户购物车信息
        user = request.user
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        cart_dict = conn.hgetall(cart_key)
        skus = []
        total_count = 0
        total_price = 0
        # 遍历获取的商品信息
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            amount = sku.price*int(count)
            sku.count = int(count)
            sku.amount = amount
            total_count += int(count)
            total_price += amount
            skus.append(sku)

        # 组织上下文
        context = {'total_count': total_count,
                   'total_price': total_price, 'skus': skus}
        return render(request, 'cart.html', context)


class CartUpdateView(View):
    def post(self, request):
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 4, 'error': '请登录'})

        if not all([sku_id, count]):
            return JsonResponse({'res': 0, 'error': '数据不完整'})

        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 1, 'error': '商品数量出错'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'error': '商品不存在'})

        if count > sku.stock:
            return JsonResponse({'res': 6, 'error': '商品库存不足'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        conn.hset(cart_key, sku_id, count)
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        return JsonResponse({'res': 5, 'message': '更新成功', 'total_count': total_count})


class CartDeleteView(View):
    def post(self, request):
        sku_id = request.POST.get('sku_id')
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 4, 'error': '请登录'})
        if not sku_id:
            return JsonResponse({'res': 0, 'error': '数据不完整'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'error': '商品不存在'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        conn.hdel(cart_key, sku_id)
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        return JsonResponse({'res': 3, 'message': '删除成功', 'total_count': total_count})
