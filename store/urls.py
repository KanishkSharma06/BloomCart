from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search_results, name='search_results'),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.signup, name='register'),
    path('verify-otp/', views.otp_verify, name='otp_verify'),
    
    # Cart & Checkout
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/product/<str:product_id>/', views.add_to_cart, name='add_to_cart_product'),
    path('add-to-cart/variant/<int:variant_id>/', views.add_to_cart, name='add_to_cart_variant'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('order-success/', views.order_success, name='order_success'),
    
    # Orders, Wishlist & Profile
    path('my-orders/', views.my_orders, name='my_orders'),
    path('track-orders/', views.track_orders_view, name='track_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/reorder/', views.reorder, name='reorder'),
    path('order/<int:order_id>/invoice/', views.download_invoice, name='download_invoice'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<str:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('add-review/<str:product_id>/', views.add_review, name='add_review'),
    
    # Support & Tools
    path('order/refund/<int:order_id>/', views.request_refund, name='request_refund'),
    path('order/<int:order_id>/support/create/', views.create_support_ticket, name='create_support_ticket'),
    path('support/ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('help-faq/', views.help_faq_view, name='help_faq'),
    path('tools/scraper/', views.scrape_view, name='scraper_view'),
    path('api/chatbot/', views.rag_chatbot_view, name='rag_chatbot_view'),
    path('create-subscription/', views.create_subscription_flow, name='create_subscription'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='store/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='store/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='store/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='store/password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)