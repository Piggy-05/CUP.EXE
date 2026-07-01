# 从我们之前写的模型里，把“饮料(Drink)”的设计图纸拿过来
from django.shortcuts import render, redirect  # 额外请来一个 redirect（跳转页面）功能
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required # 【核心】：门禁装饰器
from .models import Drink, Order, UserProfile, Coupon
import random



@login_required(login_url='/login/')
def mode_selection(request):
    # 这里不需要去数据库拿饮料，只展示两个选择按钮
    return render(request, 'selection.html')


@login_required(login_url='/login/')
def transition_view(request, mode):
    # 如果用户选了 1（官方饮品）
    if mode == 'classic':
        context = {
            'title': 'LOADING CLASSIC DATABASE...',
            'message': 'SYSTEM TIP: Official recipes are strictly balanced for optimal taste.', # 给客户的留言1
            'next_url': '/menu/'  # 动画结束去大厅
        }
    # 如果用户选了 2（DIY 调配）
    elif mode == 'diy':
        context = {
            'title': 'BOOTING CUSTOM LAB ENV...',
            'message': 'WARNING: Unstable flavor combinations may occur in the lab.', # 给客户的留言2（带点警告的酷炫感）
            'next_url': '/diy/'   # 动画结束去 DIY 页面
        }
    else:
        return redirect('/') # 如果有人乱输网址，踢回模式选择

    # 把带有不同留言和终点站的包裹（context），发给唯一的过场网页
    return render(request, 'transition.html', context)


# 定义一个功能，叫“饮料首页”
@login_required(login_url='/login/')  # 意思是：没登录的人，通通给我滚去 /login/ 网址
def standard_menu(request):
    # 1. 去数据库仓库里，把所有的饮料【全部拿出来】
    # Drink.objects.all() 就像一条去仓库搬货的指令
    all_drinks = Drink.objects.exclude(name__contains='[').exclude(name__startswith='DIY:')
    return render(request, 'drink_list.html', {'drinks': all_drinks})


@login_required(login_url='/login/')
def diy_menu(request):
    return render(request, 'diy_list.html')


# 功能 2：处理“加入购物车”的动作
@login_required(login_url='/login/')
def add_to_cart(request):
    if request.method == 'POST':
        drink_id = request.POST.get('drink_id')

        # 1. 去仓库查一下这杯饮料叫啥、多少钱
        drink = Drink.objects.get(id=drink_id)

        # 2. 🌟 核心升级：打包成一个小字典（临时包裹）
        item = {
            'name': drink.name,
            'price': drink.price
        }

        # 3. 把包裹放进小账本（Session内存）
        cart = request.session.get('cart', [])
        cart.append(item)
        request.session['cart'] = cart

        return redirect('/menu/')
    return redirect('/')


# 功能 3：专门用来看购物车里有什么的页面
# ================= 3. 修改：显示购物车 =================
def show_cart(request):
    # 直接从小账本里拿出所有的包裹（不用再去数据库 filter 搜索了！）
    cart_items = request.session.get('cart', [])

    # 算一下总价
    total_price = 0
    for item in cart_items:
        total_price += item['price'] # 从字典里抓出价格来相加

    user_coupons = Coupon.objects.filter(user=request.user, is_used=False)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total_price,
        'coupons': user_coupons
    }) # 传给前端渲染


# 功能 4：取消订单（清空购物车）
def clear_cart(request):
    if request.method == 'POST':
        # 核心逻辑：直接把小账本（session）里的 'cart' 重新设置成一个【空列表 []】
        # 这样里面之前存的所有饮料 ID 就全部被抹掉了
        request.session['cart'] = []

        # 擦干净账本后，让网页重新刷新一下购物车页面
        return redirect('/cart/')


# 功能 5：用户注册
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid(): # 检查名字是否重复、密码是否一致
            user = form.save() # 存入数据库

            phone = request.POST.get('phone_number', '')  # 从网页抓取用户填写的电话号码
            full_phone = f"+60 {phone}"  # 组合出完整的号码（+60 加上 用户填的数字）并帮这个新用户创建一个资料包
            UserProfile.objects.create(user=user, phone_number=full_phone)

            login(request, user) # 注册成功直接帮他登录
            return redirect('/register_loading/') # 跳回首页看奶茶
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# 功能 6：用户登录
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) # 验证成功，登录
            return redirect('/register_loading/') # 跳回首页
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# 功能 6.5 ： 退出登录
def logout_view(request):
    logout(request) # 撕掉通行证
    return redirect('/login/') # 踢回登录页


# 功能 7：确认下单并保存到数据库
from django.contrib.auth.decorators import login_required

# 功能 7：确认下单并保存到数据库（TNG 专属版 + 优惠券核销）
@login_required(login_url='/login/')
def checkout(request):
    if request.method == 'POST':
        # ==================== 第一步：先算出购物车的【原本总价】 ====================
        cart_items = request.session.get('cart', [])
        if not cart_items:
            return redirect('/cart/')

        total_price = 0.0
        names_list = []

        # 从包裹里提取数据，把原本要多少钱算清楚
        for item in cart_items:
            total_price += float(item['price'])  # 统一转成小数计算防报错
            names_list.append(item['name'])

        items_summary = ", ".join(names_list)

        # ==================== 第二步：读取优惠券，计算【最终折扣价】 ====================
        chosen_coupon_id = request.POST.get('selected_coupon_id')
        final_total_price = total_price  # 先让最终价格 = 原本总价

        if chosen_coupon_id and chosen_coupon_id != 'none':
            try:
                # 安全门禁：必须是当前用户没用过的券
                coupon = Coupon.objects.get(id=chosen_coupon_id, user=request.user, is_used=False)

                # 真实扣钱！总价减去优惠券的面额
                final_total_price -= float(coupon.amount)
                if final_total_price < 0:
                    final_total_price = 0.0  # 保底，防止减成负数

                # 🔥 核心核销：原地将这张券作废，打上已使用标记，永久锁死！
                coupon.is_used = True
                coupon.save()

            except Coupon.DoesNotExist:
                # 乱传ID或者券不存在就直接忽略，不给打折
                pass

        # ==================== 第三步：用【最终折扣价】生成付款订单 ====================
        new_order = Order.objects.create(
            user=request.user,
            items_summary=items_summary,
            total_amount=final_total_price,  # 🌟 必须存入抵扣后的 final_total_price！
            payment_method='TNG',
            status='PENDING'
        )

        # 4. 账算清了，撕掉临时的购物车便利贴
        request.session['cart'] = []

        # 5. 踢去扫码界面，让他扫码给钱！
        return render(request, 'tng_qr.html', {'order': new_order})

    return redirect('/cart/')


# 跳转中间页
def loading_view(request):
    return render(request, 'register_loading.html')


# 功能 8：处理 DIY 饮料合成与加入购物车
@login_required(login_url='/login/')
def add_diy_to_cart(request):
    if request.method == 'POST':
        # 1. 🌟 【核心升级】用 getlist 抓取用户在网页上选的【所有基底】
        bases_info = request.POST.getlist('base')
        flavors_info = request.POST.getlist('flavor')
        touch_info = request.POST.getlist('touch')
        hardware_info = request.POST.get('hardware_cup')

        total_price = 0.0

        # 2. 🌟 循环拆解所有的基底，累加价格和提取名字
        base_names = []
        for base in bases_info:
            b_name, b_price = base.split('|')
            total_price += float(b_price)  # 把每个勾选的基底价格加上去
            base_names.append(b_name)

        # 把名字拼起来，比如 "DIY: Classic Milk Tea + Cyber Coffee"
        diy_drink_name = f"DIY: {' + '.join(base_names)}"

        # 3. 循环拆解配料，把名字加上去，价格也叠加上去
        for flavor in flavors_info:
            f_name, f_price = flavor.split('|')
            total_price += float(f_price)
            diy_drink_name += f" + {f_name}"

        for touch in touch_info:
            touch_name, touch_price = touch.split('|')
            total_price += float(touch_price)
            diy_drink_name += f" + {touch_name}"

        # 4. 在最后面加上杯子/硬件标签
        if hardware_info:
            cup_name, cup_price = hardware_info.split('|')
            total_price += float(cup_price)
            diy_drink_name += f" + [{cup_name}]"
        else:
            # 门禁保底
            total_price += 1
            diy_drink_name += " + [STANDARD CUP]"

        # 5. 直接现场捏造并保存一杯新饮料！
        item = {
            'name': diy_drink_name,
            'price': total_price
        }

        # 6. 放进购物车小账本
        cart = request.session.get('cart', [])
        cart.append(item)
        request.session['cart'] = cart

        # 7. 合成完毕，踢去购物车页面结账！
        return redirect('/cart/')

    return redirect('/diy/')


def tng_qr_view(request):
    return render(request, 'tng_qr.html')


# 功能 8：订单成功与赛博盲盒抽奖中心
@login_required(login_url='/login/')
def success_view(request):
    drawn_coupon = None  # 默认还没抽到任何券

    if request.method == 'POST':
        # 🎲 老板的暗箱操作：设置爆率池 (1出现的概率最高，5出现的概率最低)
        pool = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2.0, 2.0, 2.0, 2.0, 2.0, 2.5, 2.5, 2.5, 3.0]
        amount = random.choice(pool)

        # 根据抽中的金额，生成酷炫的名字
        name_map = {
            1.0: "[COMMON] 🪙1.0 OFF TICKET",
            1.5: "[UNCOMMON] 🪙1.5 OFF TOKEN",
            2.0: "[RARE] 🪙2.0 OFF COUPON",
            2.5: "[EPIC] 🪙2.5 OFF VOUCHER",
            3.0: "[LEGENDARY] 🪙3.0 OFF PASS"
        }
        coupon_name = name_map[amount]

        # 🌟 直接把券写进数据库，永久绑定给当前这个顾客！
        Coupon.objects.create(
            user=request.user,
            amount=amount,
            name=coupon_name
        )
        drawn_coupon = coupon_name  # 把抽到的券名字传给前端炫耀

    return render(request, 'order_success.html', {'drawn_coupon': drawn_coupon})


# 功能 9：赛博钱包 / 顾客优惠券资产查看
@login_required(login_url='/login/')
def user_wallet(request):
    # 去数据库里，把当前登录用户的所有优惠券全部搜出来
    my_coupons = Coupon.objects.filter(user=request.user, is_used=False)

    # 算一下顾客一共拥有多少张券
    coupon_count = my_coupons.count()

    return render(request, 'wallet.html', {
        'coupons': my_coupons,
        'count': coupon_count
    })


def remove_item(request):
    if request.method == 'POST':
        # 获取顾客想要删除的那个物品的索引号（第几个）
        item_index = request.POST.get('item_index')

        # 拿出当前的购物车数据
        cart = request.session.get('cart', [])

        # 如果索引是有效的，就从列表里把它“踢出去”
        if item_index is not None and cart:
            try:
                item_index = int(item_index)
                if 0 <= item_index < len(cart):
                    cart.pop(item_index)  # 踢出列表
                    request.session['cart'] = cart  # 把更新后的购物车存回去
                    request.session.modified = True
            except ValueError:
                pass

    # 删完之后，让页面重新刷新回到购物车
    return redirect('/cart/')

