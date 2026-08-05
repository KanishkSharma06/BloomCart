from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, null=True, blank=True)
    
    # Naye fields Prime membership ke liye:
    is_prime = models.BooleanField(default=False)
    subscription_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username

# --- Product & Variants ---
# --- Product & Variants ---
class Product(models.Model):
    uniq_id = models.CharField(max_length=255, primary_key=True)
    product_title = models.TextField() 
    product_description = models.TextField(blank=True, null=True)
    brand = models.TextField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    stock_availability = models.TextField(blank=True, null=True)
    quantity = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=10)
    category = models.CharField(max_length=100, default='General')
    prime_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_exclusive = models.BooleanField(default=False)

    def __str__(self):
        return self.product_title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return sum([review.rating for review in reviews]) / reviews.count()
        return 0

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants') # <-- Yahan se on_database hata diya hai
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    stock = models.IntegerField(default=10)
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    @property
    def get_price(self):
        return self.product.price + self.price_modifier

    def __str__(self):
        return f"{self.product.product_title} - {self.color} {self.size}"

# --- Cart ---
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True) # Yeh line add karein
    quantity = models.IntegerField(default=1)

# --- Review ---
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) # Yahan auto_now_add=True sahi hai

    def __str__(self):
        return f"{self.user.username} - {self.product.product_title}"
    
# --- Wishlist ---
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

# --- Order & OrderItem ---
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
        ('Return_Requested', 'Return Requested'),
        ('Order Placed', 'Order Placed'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Order Placed')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    refund_id = models.CharField(max_length=100, blank=True, null=True)
    return_reason = models.CharField(max_length=255, blank=True, null=True)
    is_cancelled = models.BooleanField(default=False)
    return_requested = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True) # null=True zaroori hai
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True) # Product add karein
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=50, default='Home')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.address_type}"
    
from django.db import models
from django.contrib.auth.models import User
from store.models import Order

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='support_tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, blank=True, null=True)  # <-- Yahan blank=True, null=True add karein
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - Order #{self.order.id} ({self.status})"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True) # Text optional taaki sirf photo bhi bhej sakein
    attachment = models.FileField(upload_to='ticket_attachments/', blank=True, null=True) # Image/File field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} on Ticket #{self.ticket.id}"
from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.IntegerField(help_text="Discount in percentage (e.g. 10 for 10%)")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_order_status_email_task

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if not created and instance.user and instance.user.email:
        # Jab bhi status inme se koi ek ho
        if instance.status in ['Cancelled', 'Refunded', 'Delivered']:
            send_order_status_email_task.delay(
                user_email=instance.user.email,
                username=instance.user.username,
                order_id=instance.id,
                status=instance.status
            )

from django.db import models
from django.contrib.auth.models import User

class EmailVerificationOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"