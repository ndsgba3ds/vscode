from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.cache import cache
from django.core.paginator import Paginator
from django_redis import get_redis_connection
from goods.models import GoodsType, GoodsSKU, Goods, GoodsImage, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner

# Create your views here.


class IndexView(View):
    def get(self, request):

        context = cache.get('index_data')
        if context is None:
            # 获取商品分类
            types = GoodsType.objects.all()
            # 获取轮播图片
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')
            # 获取促销活动
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
            # 获取商品分类推荐
            for type in types:
                image_goods = IndexTypeGoodsBanner.objects.filter(
                    type=type, display_type=1).order_by('index')
                title_goods = IndexTypeGoodsBanner.objects.filter(
                    type=type, display_type=0).order_by('index')
                type.image_goods = image_goods
                type.title_goods = title_goods

            context = {'types': types, 'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners}
            cache.set('index_data', context, 3600)
        # 获取购物车数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
        context.update(cart_count=cart_count)
        return render(request, 'index.html', context)


class DetailView(View):
    def get(self, request, goods_id):

        try:
            goods_sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect('/')

        types = GoodsType.objects.all()

        new_goods = GoodsSKU.objects.filter(
            type=goods_sku.type).order_by('create_time')[:2]

        # 获取购物车数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)

        context = {'types': types, 'goods_sku': goods_sku,
                   'new_goods': new_goods, 'cart_count': cart_count}

        return render(request, 'detail.html', context)


class ListView(View):
    def get(self, request, type_id, page):
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect('/')
        types = GoodsType.objects.all()
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 分页
        paginator = Paginator(skus, 1)
        if page is None:
            page = 1
        if page > paginator.count:
            page = 1
        skus_page = paginator.get_page(page)
        num_pages = skus_page.num_pages
        if num_pages < 5:
            pages = range(1, num_pages+1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages-4, num_pages+1)
        else:
            pages = range(page-2, page+3)

        new_goods = GoodsSKU.objects.filter(
            type=type).order_by('create_time')[:2]
        # 获取购物车数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
        context = {'type': type, 'types': types, 'skus_page': skus_page,
                   'new_goods': new_goods, 'cart_count': cart_count, 'sort': sort, 'pages': pages}
        return render(request, 'list.html', context)
