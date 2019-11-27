from django.shortcuts import render, redirect
from django.views.generic import View
from goods.models import GoodsSKU
from user.models import Address
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from django.http import JsonResponse
from order.models import OrderInfo, OrderGoods
from datetime import datetime
from django.db import transaction
from alipay import AliPay
import os
from django.conf import settings
# Create your views here.


class OrderPlaceView(LoginRequiredMixin, View):
    def post(self, request):
        sku_ids = request.POST.getlist('sku_ids')
        if not sku_ids:
            return redirect('/cart/show')

        user = request.user
        conn = get_redis_connection('default')

        cart_key = 'cart_%d' % user.id
        skus = []
        total_count = 0
        total_price = 0
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            count = conn.hget(cart_key, sku_id)
            amount = sku.price*int(count)
            sku.amount = amount
            sku.count = int(count)
            skus.append(sku)
            total_count += int(count)
            total_price += amount
        transit_price = 12
        total_pay = total_price+transit_price
        address = Address.objects.filter(user=user)
        sku_ids = ','.join(sku_ids)
        context = {'skus': skus, 'total_count': total_count, 'total_price': total_price,
                   'total_pay': total_pay, 'transit_price': transit_price, 'address': address, 'sku_ids': sku_ids}
        return render(request, 'place_order.html', context)


class OrderCommitView(View):
    @transaction.atomic
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登陆'})
        addr_id = request.POST.get('addr_id')
        pay_style = request.POST.get('pay_style')
        sku_ids = request.POST.get('sku_ids')
        if not all([addr_id, pay_style, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})
        if pay_style not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist():
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})

        order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(user.id)
        transit_price = 12
        total_count = 0
        total_price = 0
        save_id = transaction.savepoint()
        try:
            order = OrderInfo.objects.create(order_id=order_id, user=user, addr=addr, pay_method=pay_style,
                                             total_count=total_count, total_price=total_price, transit_price=transit_price)
            sku_ids = sku_ids.split(',')
            conn = get_redis_connection('default')

            cart_key = 'cart_%d' % user.id

            for sku_id in sku_ids:
                try:
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                except:
                    return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
                count = conn.hget(cart_key, sku_id)
                if int(count) > sku.stock:
                    return JsonResponse({'res': 6, 'errmsg': '库存不足'})
                OrderGoods.objects.create(
                    order=order, sku=sku, count=count, price=sku.price)
                sku.stock-+int(count)
                sku.sales += int(count)
                sku.save()
                amount = sku.price*int(count)
                total_count += int(count)
                total_price += amount

            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
        transaction.savepoint_commit(save_id)
        conn.hdel(cart_key, *sku_ids)
        return JsonResponse({'res': 5, 'message': '创建成功'})


class OrderPayView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '订单id无效'})
        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=user, pay_method=3, order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        alipay = AliPay(
            appid="2016091300501408",
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(
                settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            alipay_public_key_path=os.path.join(
                settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=True  # 默认False
        )
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        total_pay = order.total_price+order.transit_price
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(total_pay),
            subject='天天生鲜%s' % order_id,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


class OrderCheckView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '订单id无效'})
        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=user, pay_method=3, order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        alipay = AliPay(
            appid="2016091300501408",
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(
                settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            alipay_public_key_path=os.path.join(
                settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=True  # 默认False
        )
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            code = response.get('code')
            trade_status = response.get('trade_status')
            if code == '10000' and trade_status == 'TRADE_SUCCESS':
                order.trade_no = response.get('trade_no')
                order.order_status = 4
                order.save()
                return JsonResponse({'res': 3, 'msg': '支付成功'})
            elif code == '40004' or (code == '10000' and trade_status == 'WAIT_BUYER_PAY'):
                import time
                time.sleep(5)
                continue
            else:
                return JsonResponse({'res': 4, 'errmsg': '用户未登录'})
