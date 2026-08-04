from django.contrib import admin
from .models import (
    Product, ProductVariant, Cart, CartItem, 
    Order, OrderItem, SupportTicket, TicketMessage, Coupon
)

# --- Product & Variants ---
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = ('product_title', 'price', 'brand')
    search_fields = ('product_title',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'stock', 'price_modifier')
    list_filter = ('product', 'color')


# --- Cart ---
admin.site.register(Cart)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'variant', 'quantity')


# --- Orders ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at', 'return_reason')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'razorpay_payment_id', 'refund_id', 'full_name')
    readonly_fields = ('razorpay_payment_id', 'refund_id', 'return_reason', 'created_at')
    inlines = [OrderItemInline]


# --- Support Tickets & Messages ---
class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1  
    
    # Purane messages readonly rahenge, naye reply ke liye message box editable rahega
    def get_readonly_fields(self, request, obj=None):
        if obj:  
            return ('sender', 'attachment', 'created_at') 
        return ('created_at',)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'subject')
    inlines = [TicketMessageInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if not obj.pk:  # Naya reply/message hai toh sender current admin ban jayega
                obj.sender = request.user
            obj.save()
        formset.save_m2m()

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'attachment', 'created_at')
    list_filter = ('created_at', 'sender')


# --- Coupons ---
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'valid_from', 'valid_to', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']