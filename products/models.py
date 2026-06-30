from django.db import models
from django.contrib.auth.models import User # 引入Django自带的用户表格


# -------------------------------------------------------------------
# 第一步：定义“饮料”这个商品
# 你可以把 class Drink 想象成我们在 Excel 里新建了一个叫“饮料”的表格
# -------------------------------------------------------------------
class Drink(models.Model):
    # 第 1 列：饮料名字
    # CharField 专门用来存比较短的一句话。max_length=100 限制名字最多 100 个字。
    name = models.CharField(max_length=100)

    # 第 2 列：饮料介绍
    # TextField 用来存长篇大论。blank=True 表示如果老板懒得写介绍，留空也可以，系统不会报错。
    description = models.TextField(blank=True)

    # 第 3 列：价格
    # FloatField 用来存带小数点的数字（比如 12.5 元）。
    # (注：其实商业项目严格来说会用 DecimalField，但需要设置各种参数。为了新手不报错，我们先用最简单的 Float)
    price = models.FloatField()

    # -------------------------------------------------------------------
    # 这个特殊的功能非常实用：
    # 以后你在商家后台看到这杯饮料时，它会直接显示名字（比如“珍珠奶茶”），
    # 如果不写这三行代码，后台只会冷冰冰地显示 "Drink object (1)"，那老板肯定看不懂。
    # -------------------------------------------------------------------
    def __str__(self):
        return self.name


class Order(models.Model):
    # 1. 关联用户
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # 2. 购买内容
    items_summary = models.TextField()

    # 3. 总金额
    total_amount = models.IntegerField()

    # 4. 下单时间
    created_at = models.DateTimeField(auto_now_add=True)

    # 🌟 5. 整合后的状态选项（合并了你之前写的）
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed/Paid'),
        ('COMPLETED', 'Delivered')
    ]

    # 🌟 6. 新增的支付方式
    PAYMENT_CHOICES = [
        ('TNG', 'TNG e-Wallet')
    ]

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='TNG')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"订单 #{self.id} - 顾客: {self.user.username}"


class Coupon(models.Model):
    # 1. 绑定用户：这张券属于哪个幸运儿
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # 2. 优惠券面额（例如：减 2 🪙，或者减 5 🪙）
    amount = models.FloatField()

    # 3. 酷炫的名字（例如："[CRITICAL_HIT] 🪙2 OFF COUPON"）
    name = models.CharField(max_length=50)

    # 4. 核心状态：是否已使用（默认是 False，即未使用）
    is_used = models.BooleanField(default=False)

    # 5. 抽中时间
    drawn_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status_text = "❌ 已核销/使用" if self.is_used else "🔥 未使用"
        return f"顾客: {self.user.username} - {self.name} ({status_text})"


class UserProfile(models.Model):
    # 用 OneToOneField 和默认的 User 一对一绑定
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 用来存电话号码
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} 的资料"







