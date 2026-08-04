from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home and Products
    path('', views.home, name='home'),
    
    # Yeh line confirm karein
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search_results, name='search_results'),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('verify-otp/', views.otp_verify, name='otp_verify'),
    
    # Cart Management
    path('cart/', views.cart_detail, name='cart_detail'),
    # urls.py mein change karein
    path('add-to-cart/product/<str:product_id>/', views.add_to_cart, name='add_to_cart_product'),
    path('add-to-cart/variant/<int:variant_id>/', views.add_to_cart, name='add_to_cart_variant'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-review/<str:product_id>/', views.add_review, name='add_review'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('api/chatbot/', views.rag_chatbot_view, name='rag_chatbot_view'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('track-orders/', views.track_orders_view, name='track_orders'),
    path('help-faq/', views.help_faq_view, name='help_faq'),
    # Payment and Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'), # YE LINE MISSING HAI
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<str:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('order/refund/<int:order_id>/', views.request_refund, name='request_refund'),
    path('order/<int:order_id>/support/create/', views.create_support_ticket, name='create_support_ticket'),
    path('support/ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),  # Coupon apply karne ka URL
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),  # Coupon remove karne ka URL
    path('create-subscription/', views.create_subscription_flow, name='create_subscription'),
    path('register/', views.signup, name='register'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='store/password_reset.html'), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='store/password_reset_done.html'), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='store/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='store/password_reset_complete.html'), 
         name='password_reset_complete'),

   path('tools/scraper/', views.scrape_view, name='scraper_view'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)