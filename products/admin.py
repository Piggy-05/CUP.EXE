from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
# 从我们刚才写的文件里，把“饮料(Drink)”的设计图纸拿过来
from .models import Drink, Order, UserProfile, Coupon

# 1. 定义一个内联扩展，告诉后台：“把 UserProfile 作为附属品展示出来”
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '📞 客户额外资料 (电话号码)'

# 2. 卸载掉 Django 默认那个死板的 User 后台
admin.site.unregister(User)

# 3. 重新组装一个包含“电话号码扩展”的豪华版 User 后台
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# 4. 把豪华版注册回系统！
admin.site.register(User, CustomUserAdmin)

# 告诉 Django 后台：请在管理页面里加上“饮料”这个商品
admin.site.register(Drink)


# 给 Order 定制一个高级显示面板
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 1. 魔法：定义一个假字段，专门用来把 ID 包装成取餐码！
    def pickup_code(self, obj):
        return f"#CUP-{obj.id}"

    pickup_code.short_description = '🔑 取餐码 (Pickup Code)'  # 这是后台显示的列名

    # 2. 告诉后台：把这些列整整齐齐地排出来！
    list_display = ('id', 'user', 'total_amount', 'payment_method', 'status', 'created_at')

    # 3. 在右侧加一个“状态过滤器”，方便你一键查看“待制作”的订单
    list_filter = ('payment_method', 'status',)

    # 4. 增加一个搜索框，可以搜顾客名字或者饮料名字
    search_fields = ('user__username', 'items_summary')


# 🌟 2. 打造老板专属的优惠券核销控制台
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    # 后台列表显示的列：顾客名字 | 优惠券名称 | 面额 | 是否已使用 | 抽中时间
    list_display = ['user', 'name', 'amount', 'is_used', 'drawn_at']

    # 右侧快速筛选栏：可以一键过滤出“所有未使用的券”或“已使用的券”
    list_filter = ['is_used', 'drawn_at']

    # 顶部搜索框：顾客来结账时，直接在这里搜他的“用户名”，瞬间调出他名下所有的券
    search_fields = ['user__username', 'name']

    # 🔥 核心外挂：允许在列表页面“直接打勾核销”，不需要点进详情页，效率翻倍！
    list_editable = ['is_used']



