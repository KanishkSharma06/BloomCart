from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User

# 1. Daily Promotional Deals Task (Full of Energy & Warmth)
@shared_task
def send_daily_promotional_notifications_task():
    users = User.objects.filter(is_active=True, email__isnull=False).exclude(email='')
    
    for user in users:
        subject = "🍫 Sweet Treats, Fragrances & Daily Munchies Loot! Check Today's Specials! 🎁"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #fdf2f2; padding: 20px; margin: 0;">
            <div style="max-width: 600px; background: #ffffff; margin: 0 auto; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(241,39,17,0.1);">
                
                <!-- Header Banner -->
                <div style="background: linear-gradient(135deg, #ff416c, #ff4b2b); color: white; text-align: center; padding: 35px 20px;">
                    <h1 style="margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 0.5px;">✨ BLOOMCART GENERAL STORE ✨</h1>
                    <p style="margin: 12px 0 0 0; font-size: 16px; font-weight: 500;">Hello {user.username or 'Shopper'}! We have brought amazing treats to sweeten up your day! 🛍️💖</p>
                </div>

                <!-- Banner Image -->
                <div style="text-align: center; padding: 20px;">
                    <img src="https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=600&auto=format&fit=crop&q=80" alt="Chocolates and Treats" style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 12px;">
                </div>

                <!-- Body Highlights -->
                <div style="padding: 25px 35px; color: #2d3748;">
                    <h3 style="color: #ff416c; margin-top: 0; font-size: 18px;">🔥 Today's Super-Duper Special Picks For You:</h3>
                    <ul style="line-height: 2.1; padding-left: 20px; font-size: 15px;">
                        <li>🍫 <b>Chocolates & Munchies:</b> Satisfy your sweet tooth! Exciting offers on imported chocolates and yummy snacks.</li>
                        <li>🧴 <b>Shampoos & Personal Care:</b> Keep your daily self-care routine super fresh! Up to 25% OFF on top-brand body washes & shampoos.</li>
                        <li>🌸 <b>Perfumes & Deos:</b> Smell amazing all day long with long-lasting fragrances and body sprays that instantly lift your mood.</li>
                        <li>🍓 <b>Jams, Spreads & Drinks:</b> Stock up your pantry with delicious spreads and refreshing drinks!</li>
                    </ul>
                    <p style="font-size: 15px; color: #4a5568; text-align: center; margin-top: 25px; font-weight: bold;">Hurry up, grab your favorites before the stock runs out! 🏃‍♂️💨✨</p>
                </div>

                <!-- Call to Action Button -->
                <div style="text-align: center; padding: 10px 35px 35px 35px;">
                    <a href="http://127.0.0.1:8000/" target="_blank" style="background: linear-gradient(135deg, #ff416c, #ff4b2b); color: white; padding: 16px 35px; text-decoration: none; font-size: 17px; font-weight: bold; border-radius: 35px; display: inline-block; box-shadow: 0 6px 20px rgba(255, 65, 108, 0.4);">
                        🛍️ SHOP TREATS & ESSENTIALS NOW 🚀
                    </a>
                </div>

                <!-- Footer -->
                <div style="background-color: #1a202c; color: #cbd5e0; text-align: center; padding: 20px; font-size: 13px;">
                    <p style="margin: 0;">Made with ❤️ by BloomCart Store. Visit us anytime at <a href="http://127.0.0.1:8000/" style="color: #ff4b2b; text-decoration: none; font-weight: bold;">BloomCart</a></p>
                    <p style="margin: 8px 0 0 0;"><a href="http://127.0.0.1:8000/" style="color: #a0aec0; text-decoration: underline;">Unsubscribe</a></p>
                </div>

            </div>
        </body>
        </html>
        """
        
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body="Hey! Check out today's sweet treats and essentials on BloomCart: http://127.0.0.1:8000/",
                from_email=None,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
        except Exception as e:
            print(f"Failed to send promo email to {user.email}: {e}")


# 2. Order Status Update Task (With Product Images, Details & Total Price)
@shared_task
def send_order_status_email_task(user_email, username, order_id, status, items_data):
    if status == "Placed":
        subject = f"Order Placed Successfully! 🎉 (Order #{order_id})"
        status_message = f"Your order #{order_id} has been placed successfully and is being processed right now."
        badge_color = "#3182ce"  # Blue
    elif status == "Cancelled":
        subject = f"Order Cancelled (Order #{order_id})"
        status_message = f"Your order #{order_id} has been successfully cancelled as per your request."
        badge_color = "#e53e3e"  # Red
    elif status == "Refunded":
        subject = f"Refund Initiated for Order #{order_id}"
        status_message = f"Your refund for order #{order_id} has been initiated and will reflect in your account within 5-7 business days."
        badge_color = "#d69e2e"  # Yellow/Gold
    elif status == "Delivered":
        subject = f"Order Delivered! 🚀 (Order #{order_id})"
        status_message = f"Your order #{order_id} has been delivered successfully. We hope you love your products!"
        badge_color = "#38a169"  # Green
    else:
        return

    # --- Generate Items HTML Table ---
    items_html = ""
    total_amount = 0
    
    for item in items_data:
        item_total = item['price'] * item['quantity']
        total_amount += item_total
        
        items_html += f"""
        <tr style="border-bottom: 1px solid #edf2f7;">
            <td style="padding: 12px 10px; text-align: left;">
                <img src="{item.get('image_url', '')}" alt="{item['name']}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 1px solid #e2e8f0;">
            </td>
            <td style="padding: 12px 10px; text-align: left; color: #2d3748; font-size: 14px;">
                <b>{item['name']}</b><br>
                <span style="color: #718096; font-size: 12px;">Qty: {item['quantity']}</span>
            </td>
            <td style="padding: 12px 10px; text-align: right; color: #2d3748; font-size: 14px; font-weight: bold;">
                ₹{item_total}
            </td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Order Update</title>
    </head>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f7f6; padding: 20px 0;">
            <tr>
                <td align="center">
                    <table border="0" cellpadding="0" cellspacing="0" width="600" style="background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
                        
                        <!-- Header Section -->
                        <tr>
                            <td align="center" style="background: linear-gradient(135deg, #1a202c, #2d3748); padding: 30px 20px; color: #ffffff;">
                                <h1 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 0.5px;">✨ BLOOMCART STORE ✨</h1>
                                <p style="margin: 8px 0 0 0; font-size: 14px; color: #a0aec0;">Order Status: <span style="color: {badge_color}; font-weight: bold; text-transform: uppercase;">{status}</span></p>
                            </td>
                        </tr>

                        <!-- Body Content -->
                        <tr>
                            <td style="padding: 30px 30px 20px 30px; color: #2d3748;">
                                <h2 style="margin-top: 0; font-size: 20px; color: #1a202c;">Hello {username or 'Shopper'}! 👋</h2>
                                <p style="font-size: 15px; line-height: 1.6; color: #4a5568; margin-bottom: 25px;">{status_message}</p>
                                
                                <!-- Order Details Box -->
                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;">
                                    <tr>
                                        <td>
                                            <p style="margin: 0 0 15px 0; font-size: 14px; color: #4a5568;"><b>Order ID:</b> #{order_id}</p>
                                            
                                            <!-- Items Table -->
                                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
                                                <thead>
                                                    <tr style="border-bottom: 2px solid #cbd5e0;">
                                                        <th style="padding: 10px 0; text-align: left; font-size: 12px; color: #718096; text-transform: uppercase;">Item</th>
                                                        <th style="padding: 10px 0; text-align: left; font-size: 12px; color: #718096; text-transform: uppercase;">Details</th>
                                                        <th style="padding: 10px 0; text-align: right; font-size: 12px; color: #718096; text-transform: uppercase;">Price</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {items_html}
                                                </tbody>
                                            </table>
                                            
                                            <!-- Total Amount -->
                                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 15px; border-top: 2px solid #e2e8f0;">
                                                <tr>
                                                    <td style="padding-top: 15px; text-align: right; font-size: 16px; color: #1a202c; font-weight: bold;">
                                                        Total Amount: <span style="color: #e53e3e;">₹{total_amount}</span>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Call To Action Button -->
                        <tr>
                            <td align="center" style="padding: 10px 30px 30px 30px;">
                                <a href="http://127.0.0.1:8000/" target="_blank" style="background: linear-gradient(135deg, #ff416c, #ff4b2b); color: #ffffff; padding: 14px 30px; text-decoration: none; font-size: 15px; font-weight: bold; border-radius: 30px; display: inline-block; box-shadow: 0 4px 15px rgba(255, 65, 108, 0.4);">
                                    🛍️ VIEW ORDER ON SITE 🚀
                                </a>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="background-color: #edf2f7; color: #718096; padding: 20px; font-size: 12px;">
                                <p style="margin: 0;">With lots of love and warmth, Team BloomCart ❤️</p>
                                <p style="margin: 6px 0 0 0;"><a href="http://127.0.0.1:8000/" style="color: #ff4b2b; text-decoration: none; font-weight: bold;">Explore Store</a></p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Hello {username}, your order #{order_id} status is now: {status}. Visit us at http://127.0.0.1:8000/",
            from_email=None,
            to=[user_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Failed to send order status email to {user_email}: {e}")


# 3. Account Verification OTP Task
@shared_task
def send_otp_email_task(user_email, username, otp):
    subject = "🔐 Your BloomCart Account Verification OTP"
    message = f"Hi {username},\n\nYour OTP for account verification is: {otp}\n\nThis OTP is valid for a few minutes. Do not share it with anyone."
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f7fafc; padding: 20px; margin: 0;">
        <div style="max-width: 600px; background: #ffffff; margin: 0 auto; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.08);">
            <div style="background: linear-gradient(135deg, #1a202c, #2d3748); color: white; text-align: center; padding: 30px 20px;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 900;">✨ BLOOMCART STORE ✨</h1>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: #cbd5e0;">Account Verification 🛡️</p>
            </div>
            <div style="padding: 30px; color: #2d3748; text-align: center;">
                <h3 style="margin-top: 0; font-size: 20px;">Hello {username or 'Shopper'}! 👋</h3>
                <p style="font-size: 16px; color: #4a5568;">Use the verification code below to activate your account:</p>
                
                <div style="background: #edf2f7; display: inline-block; padding: 15px 30px; border-radius: 12px; margin: 20px 0;">
                    <span style="font-size: 28px; font-weight: bold; letter-spacing: 4px; color: #ff4b2b;">{otp}</span>
                </div>
                
                <p style="font-size: 14px; color: #718096;">If you didn't request this, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    try:
        email = EmailMultiAlternatives(subject=subject, body=message, from_email=None, to=[user_email])
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Failed to send OTP email: {e}")