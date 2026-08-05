from decimal import Decimal
import json
import random
import typesense
import os
import google.generativeai as gen
import os

# API key configure karein
gen.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model ko call karne ke liye yeh tarika use karein:
model = gen.GenerativeModel('gemini-pro')

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
import razorpay
from xhtml2pdf import pisa

# Models & Forms Import
from .forms import RegisterForm
from .models import (
    Address,
    Cart,
    CartItem,
    EmailVerificationOTP,
    Order,
    OrderItem,
    Product,
    ProductVariant,
    Profile,
    Review,
    SupportTicket,
    TicketMessage,
    Wishlist,
)
from .recommender import get_recommendations

# LangChain & Gemini Imports
import google.generativeai as genai
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- Client Setup ---
client = typesense.Client(
    {
        "nodes": [
            {
                "host": "fas0pie5tckr6g2hp-1.a2.typesense.net",
                "port": "443",
                "protocol": "https",
            }
        ],
        "api_key": "dtOFl3ANkvNJr7DUrOAmIWTZO2AQSVNR",
        "connection_timeout_seconds": 60,
    }
)


def get_razorpay_client():
  return razorpay.Client(
      auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
  )


import os
import google.generativeai as genai
from django.conf import settings

# Gemini API ko properly configure karein
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', ''))

def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Sorry, I am unable to process this request right now."

# --- Products ---
def home(request):
  trending = Product.objects.all().order_by("?")[:6]
  recommendations = []

  if request.user.is_authenticated:
    try:
      all_product_ids = list(Product.objects.values_list("uniq_id", flat=True))
      rec_ids = get_recommendations(request.user.id, all_product_ids)

      if rec_ids:
        model_recommendations = list(Product.objects.filter(uniq_id__in=rec_ids))
        random_fillers = list(Product.objects.all().order_by("?")[:6])

        combined = model_recommendations + random_fillers
        seen = set()
        recommendations = []
        for p in combined:
          if p.uniq_id not in seen:
            seen.add(p.uniq_id)
            recommendations.append(p)

        recommendations = recommendations[:6]
      else:
        recommendations = list(Product.objects.all().order_by("?")[:6])
    except Exception as e:
      recommendations = list(Product.objects.all().order_by("?")[:6])
  else:
    recommendations = list(Product.objects.all().order_by("?")[:6])

  context = {"trending": trending, "recommendations": recommendations}
  return render(request, "store/home.html", context)


def product_detail(request, product_id):
  product = get_object_or_404(Product, uniq_id=product_id)
  random_limit = random.randint(4, 20)

  similar_products = (
      Product.objects.filter(category=product.category)
      .exclude(uniq_id=product.uniq_id)
      .order_by("?")[:random_limit]
  )

  context = {
      "product": product,
      "similar_products": similar_products,
  }
  return render(request, "store/product_detail.html", context)


# --- Cart Logic ---
@login_required
def cart_detail(request):
  cart, _ = Cart.objects.get_or_create(user=request.user)
  cart_items = CartItem.objects.filter(cart=cart)

  total_price = 0
  for item in cart_items:
    if item.variant:
      total_price += (
          item.variant.product.price + item.variant.price_modifier
      ) * item.quantity
    elif item.product:
      total_price += item.product.price * item.quantity

  return render(
      request,
      "store/cart.html",
      {"cart_items": cart_items, "total_price": total_price},
  )


@login_required
def add_to_cart(request, product_id=None, variant_id=None):
  cart, _ = Cart.objects.get_or_create(user=request.user)
  referer_url = request.META.get("HTTP_REFERER", "home")

  if variant_id:
    item = get_object_or_404(ProductVariant, id=variant_id)
    if item.stock <= 0:
      messages.error(request, "Product is out of stock!")
      return redirect(referer_url)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=item)

  elif product_id:
    item = get_object_or_404(Product, uniq_id=product_id)
    if item.stock <= 0:
      messages.error(request, "Product is out of stock!")
      return redirect(referer_url)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item)

  if not created:
    if cart_item.quantity < item.stock:
      cart_item.quantity += 1
      cart_item.save()
      messages.success(request, "Item quantity updated in cart.")
    else:
      messages.warning(request, "Maximum available stock reached!")
      return redirect(referer_url)
  else:
    messages.success(request, "Added to cart successfully!")

  return redirect(referer_url)


@login_required
def remove_from_cart(request, item_id):
  get_object_or_404(CartItem, id=item_id).delete()
  return redirect("cart_detail")


# --- Coupon & Subscription Logic ---
@login_required
def apply_coupon(request):
  if request.method == "POST":
    coupon_code = request.POST.get("coupon_code", "").strip().upper()
    if coupon_code == "DISCOUNT10":
      request.session["discount_percentage"] = 10
      messages.success(request, "Coupon applied successfully! 10% discount added.")
    elif coupon_code == "DISCOUNT20":
      request.session["discount_percentage"] = 20
      messages.success(request, "Coupon applied successfully! 20% discount added.")
    else:
      messages.error(request, "Invalid coupon code.")
  return redirect("checkout")


@login_required
def remove_coupon(request):
  if "discount_percentage" in request.session:
    del request.session["discount_percentage"]
    messages.success(request, "Coupon removed successfully.")
  return redirect("checkout")


@login_required
def create_subscription_flow(request):
  client = razorpay.Client(
      auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
  )
  try:
    subscription_data = {
        "plan_id": "plan_TGsPzyMl4oNM1W",
        "total_count": 12,
        "customer_notify": 1,
        "quantity": 1,
    }
    razorpay_subscription = client.subscription.create(subscription_data)
    subscription_id = razorpay_subscription["id"]
  except Exception as e:
    print("Razorpay Error:", e)
    subscription_id = None

  context = {
      "razorpay_key_id": settings.RAZORPAY_KEY_ID,
      "subscription_id": subscription_id,
  }
  return render(request, "store/subscription_checkout.html", context)


# --- Checkout & Payment ---
@login_required(login_url="/login/")
def checkout(request):
  user = request.user
  cart = Cart.objects.get(user=user)
  cart_items = CartItem.objects.filter(cart=cart)
  total = sum(
      item.product.price * item.quantity for item in cart_items if item.product
  )

  profile, created = Profile.objects.get_or_create(user=user)
  saved_addresses = Address.objects.filter(user=user)
  default_address = saved_addresses.first()

  discount_amount = Decimal("0.00")
  final_total = Decimal(str(total))

  if "discount_percentage" in request.session:
    discount_percentage = Decimal(str(request.session["discount_percentage"]))
    discount_amount = (final_total * discount_percentage) / Decimal("100")
    final_total = final_total - discount_amount

  razorpay_amount = int(float(final_total) * 100)

  razorpay_order = get_razorpay_client().order.create(
      {"amount": razorpay_amount, "currency": "INR", "payment_capture": 1}
  )

  context = {
      "cart_items": cart_items,
      "total_price": total,
      "discount_amount": discount_amount,
      "final_total": final_total,
      "razorpay_key": settings.RAZORPAY_KEY_ID,
      "razorpay_order_id": razorpay_order["id"],
      "amount": razorpay_amount,
      "profile": profile,
      "saved_addresses": saved_addresses,
      "default_address": default_address,
  }

  if request.method == "POST":
    request.session["order_details"] = {
        "full_name": request.POST.get("full_name"),
        "address": request.POST.get("address_line"),
        "phone": request.POST.get("phone"),
        "city": request.POST.get("city"),
        "pincode": request.POST.get("pincode"),
    }
    return render(request, "store/checkout.html", context)

  return render(request, "store/checkout.html", context)


@csrf_exempt
def verify_payment(request):
  if request.method == "POST":
    body = json.loads(request.body)
    params = {
        "razorpay_order_id": body.get("razorpay_order_id"),
        "razorpay_payment_id": body.get("razorpay_payment_id"),
        "razorpay_signature": body.get("razorpay_signature"),
    }

    if get_razorpay_client().utility.verify_payment_signature(params):
      cart = Cart.objects.get(user=request.user)
      cart_items = CartItem.objects.filter(cart=cart)
      details = request.session.get("order_details", {})

      order = Order.objects.create(
          user=request.user,
          total_amount=sum(
              item.product.price * item.quantity
              for item in cart_items
              if item.product
          ),
          status="Paid",
          full_name=details.get("full_name", "User"),
          address=details.get("address", "No Address"),
          phone=details.get("phone", "0000000000"),
          razorpay_payment_id=body.get("razorpay_payment_id"),
      )

      # Order items create karein aur saath hi items_data list bhi taiyar karein
      items_data = []
      for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant if hasattr(item, "variant") else None,
            quantity=item.quantity,
            price=item.product.price if item.product else 0,
        )
        
        # Celery task ke liye data format
        if item.product:
            items_data.append({
                "name": item.product.product_title,
                "quantity": item.quantity,
                "price": float(item.product.price),
                "image_url": item.product.image_url.split('|')[0] if item.product.image_url else ""
            })

      cart_items.delete()

      from store.tasks import send_order_status_email_task

      # Ab yahan items_data bhi pass kar diya gaya hai
      send_order_status_email_task.delay(
          user_email=request.user.email,
          username=request.user.username,
          order_id=order.id,
          status="Placed",
          items_data=items_data,
      )

      return JsonResponse({"status": "Success"})

  return JsonResponse({"status": "Failed"}, status=400)

# --- Other Pages ---
def register(request):
  form = RegisterForm(request.POST or None)
  if form.is_valid():
    username = form.cleaned_data.get("username")

    if User.objects.filter(username=username).exists():
      form.add_error("username", "A user with this username already exists.")
    else:
      user = form.save(commit=False)
      user.set_password(form.cleaned_data["password"])
      user.save()
      messages.success(request, "Registration successful! Please login.")
      return redirect("login")

  return render(request, "store/register.html", {"form": form})


@login_required
def my_orders(request):
  status_filter = request.GET.get("status")
  orders = Order.objects.filter(user=request.user).order_by("-created_at")

  if status_filter:
    orders = orders.filter(status=status_filter)

  context = {"orders": orders, "active_status": status_filter}
  return render(request, "store/my_orders.html", context)


def search_results(request):
  raw_query = request.GET.get("query") or request.GET.get("q") or ""
  query = raw_query.encode("ascii", "ignore").decode("utf-8").strip()

  selected_category = request.GET.get("category")
  selected_brand = request.GET.get("brand")
  min_price = request.GET.get("min_price")
  max_price = request.GET.get("max_price")
  availability = request.GET.get("availability")
  sort_by = request.GET.get("sort")

  products = Product.objects.none()
  hit_ids = []

  if query:
    try:
      search_response = client.collections["products"].documents.search({
          "q": query,
          "query_by": "title,description,brand,category",
          "prefix": True,
      })
      hit_ids = [
          hit["document"]["id"] for hit in search_response.get("hits", [])
      ]
    except Exception as e:
      hit_ids = []

  if query and hit_ids:
    products = Product.objects.filter(uniq_id__in=hit_ids)
    if not sort_by or sort_by == "featured":
      preserved_order = models.Case(
          *(models.When(uniq_id=pk, then=pos) for pos, pk in enumerate(hit_ids))
      )
      products = products.order_by(preserved_order)
  elif query:
    q_object = Q()
    for word in query.split():
      q_object &= (
          Q(product_title__icontains=word)
          | Q(brand__icontains=word)
          | Q(category__icontains=word)
      )
    products = Product.objects.filter(q_object)
  else:
    products = Product.objects.all()

  if selected_category:
    products = products.filter(category=selected_category)
  if selected_brand:
    products = products.filter(brand=selected_brand)
  if min_price:
    products = products.filter(price__gte=min_price)
  if max_price:
    products = products.filter(price__lte=max_price)
  if availability == "in_stock":
    products = products.filter(stock__gt=0)

  results = []
  sizes = [
      "320g Jar",
      "500g Economy Pack",
      "1 kg Family Mega Pack",
      "Combo Pack (Pack of 2)",
  ]
  price_multipliers = [1.0, 1.45, 2.2, 3.0]

  for index, product in enumerate(products):
    variant_index = index % len(sizes)
    product.dynamic_size = sizes[variant_index]
    base_price = float(product.price) if product.price else 120.0
    product.dynamic_price = round(
        base_price * price_multipliers[variant_index], 2
    )
    product.dynamic_mrp = round(product.dynamic_price * 1.3, 2)
    results.append(product)

  if sort_by == "price_low":
    results = sorted(results, key=lambda x: x.dynamic_price)
  elif sort_by == "price_high":
    results = sorted(results, key=lambda x: x.dynamic_price, reverse=True)
  elif sort_by == "newest":
    results = sorted(results, key=lambda x: x.uniq_id, reverse=True)

  paginator = Paginator(results, 12)
  page_number = request.GET.get("page")
  page_obj = paginator.get_page(page_number)

  context = {
      "page_obj": page_obj,
      "results": page_obj,
      "query": query,
      "categories": Product.objects.values_list(
          "category", flat=True
      ).distinct(),
      "brands": Product.objects.exclude(brand__isnull=True)
      .values_list("brand", flat=True)
      .distinct(),
      "selected_category": selected_category,
      "selected_brand": selected_brand,
      "min_price": min_price,
      "max_price": max_price,
      "availability": availability,
      "sort_by": sort_by,
  }
  return render(request, "store/search_results.html", context)


def otp_verify(request):
  if request.method == "POST":
    entered_otp = request.POST.get("otp")
    user_id = request.session.get("verify_user_id")

    if not user_id:
      messages.error(request, "Session expired. Please signup again.")
      return redirect("signup")

    try:
      otp_record = EmailVerificationOTP.objects.filter(user_id=user_id).latest(
          "created_at"
      )
      if otp_record.otp == entered_otp:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()

        EmailVerificationOTP.objects.filter(user_id=user_id).delete()
        del request.session["verify_user_id"]

        messages.success(request, "Account verified successfully! Please login.")
        return redirect("login")
      else:
        messages.error(request, "Invalid OTP. Please try again.")
    except EmailVerificationOTP.DoesNotExist:
      messages.error(request, "OTP expired or not found.")

  return render(request, "store/otp_verify.html")


@login_required
def update_cart(request, item_id, action):
  cart_item = get_object_or_404(CartItem, id=item_id)
  if action == "increase":
    cart_item.quantity += 1
    cart_item.save()
  elif action == "decrease":
    if cart_item.quantity > 1:
      cart_item.quantity -= 1
      cart_item.save()
    else:
      cart_item.delete()
  return redirect("cart_detail")


def payment_success(request):
  return render(request, "store/success.html")


def order_success(request):
  return render(request, "store/order_success.html")


@login_required
def wishlist(request):
  items = Wishlist.objects.filter(user=request.user)
  return render(request, "store/wishlist.html", {"wishlist_items": items})


@login_required
def add_to_wishlist(request, product_id):
  product = get_object_or_404(Product, uniq_id=product_id)
  Wishlist.objects.get_or_create(user=request.user, product=product)
  return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def remove_from_wishlist(request, wishlist_id):
  item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
  item.delete()
  return redirect("wishlist")


@login_required
def add_review(request, product_id):
  product = get_object_or_404(Product, uniq_id=product_id)
  if request.method == "POST":
    rating = request.POST.get("rating")
    comment = request.POST.get("comment")
    Review.objects.create(
        product=product, user=request.user, rating=rating, comment=comment
    )
    return redirect("product_detail", product_id=product_id)
  return redirect("product_detail", product_id=product_id)


@login_required
def order_detail(request, order_id):
  order = get_object_or_404(Order, id=order_id, user=request.user)
  context = {
      "order": order,
  }
  return render(request, "store/order_detail.html", context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order
from .tasks import send_order_status_email_task

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order
from .tasks import send_order_status_email_task

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ["Pending", "Paid"]:
        order.status = "Cancelled"
        order.save()
        
        # Task ke signature ke mutabiq items data prepare karein
        items_data = [
            {
                "name": item.product.product_title,
                "quantity": item.quantity,
                "price": float(item.price),
                "image_url": item.product.image_url.split('|')[0] if item.product.image_url else ""
            }
            for item in order.items.all() # Agar aapke relation ka naam alag hai toh use adjust kar lein
        ]
        
        # Sahi positional arguments pass karein: user_email, username, order_id, status, items_data
        send_order_status_email_task.delay(
            user_email=request.user.email,
            username=request.user.username,
            order_id=order.id,
            status="Cancelled",
            items_data=items_data
        )
        
        messages.success(
            request, f"Order #{order.id} has been cancelled successfully."
        )
    else:
        messages.error(request, "This order cannot be cancelled.")
        
    return redirect("my_orders")

@login_required
def reorder(request, order_id):
  order = get_object_or_404(Order, id=order_id, user=request.user)
  cart, _ = Cart.objects.get_or_create(user=request.user)
  for item in order.items.all():
    if item.product:
      CartItem.objects.create(
          cart=cart, product=item.product, quantity=item.quantity
      )
  return redirect("cart_detail")


@login_required
def download_invoice(request, order_id):
  order = get_object_or_404(Order, id=order_id, user=request.user)
  grand_total = sum(item.price * item.quantity for item in order.items.all())

  context = {"order": order, "grand_total": grand_total, "customer": request.user}

  template = get_template("store/invoice.html")
  html = template.render(context)

  response = HttpResponse(content_type="application/pdf")
  response["Content-Disposition"] = (
      f'attachment; filename="Invoice_{order.id}.pdf"'
  )

  pisa_status = pisa.CreatePDF(html, dest=response)
  if pisa_status.err:
    return HttpResponse("PDF generation error")
  return response


import time

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from store.models import Product  # Aapka Django model

@csrf_exempt
def rag_chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("message", "").strip()

            if not user_query:
                return JsonResponse({"reply": "Please ask a valid question."}, status=400)

            ai_reply = None

            # --- Try Heavy AI/RAG Locally, fallback safely on Render to prevent RAM crash ---
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                from langchain_chroma import Chroma
                from langchain_ollama import ChatOllama
                from langchain_core.messages import HumanMessage

                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                vectorstore = Chroma(
                    persist_directory="./chroma_db", embedding_function=embeddings
                )
                docs = vectorstore.similarity_search(user_query, k=6)

                if docs:
                    context_list = []
                    for doc in docs:
                        title = doc.metadata.get("title", "Product")
                        price = doc.metadata.get("price", "N/A")
                        context_list.append(f"- {title} | Price: ₹{price}")

                    context_text = "\n".join(context_list)

                    prompt = f"""
                    You are a helpful and friendly e-commerce personal shopper assistant for BloomCart.
                    Customer Query: "{user_query}"
                    Available Store Products Retrieved:
                    {context_text}
                    Instructions:
                    - Start with a warm, friendly greeting using emojis (e.g., 🍫, ✨).
                    - List ALL products provided above.
                    - Format neatly using bullet points with title and price.
                    """

                    llm = ChatOllama(model="phi3", temperature=0.1)
                    ai_message = llm.invoke([HumanMessage(content=prompt)])
                    ai_reply = ai_message.content
            except Exception:
                # Agar Render par heavy AI load fail hua, toh yeh fallback chal jayega (Zero Crash!)
                ai_reply = None

            # --- Fallback to Django ORM Database Search if AI is unavailable ---
            if not ai_reply:
                products = Product.objects.filter(title__icontains=user_query)[:6]
                if not products:
                    return JsonResponse({"reply": "I couldn't find any matching items in our store right now. 😔"})

                context_list = []
                for product in products:
                    context_list.append(f"- {product.title} | Price: ₹{product.price}")

                context_text = "\n".join(context_list)
                ai_reply = f"✨ Hello! Here are some items I found for you based on '{user_query}':\n\n{context_text}\n\n🛒 You can add them to your cart right away!"

            return JsonResponse({"reply": ai_reply})

        except Exception as e:
            return JsonResponse({"reply": f"Error: {str(e)}"}, status=500)
@login_required(login_url="/login/")
def user_profile_view(request):
  user = request.user
  profile, created = Profile.objects.get_or_create(user=user)
  addresses = Address.objects.filter(user=user)

  if request.method == "POST":
    form_type = request.POST.get("form_type")

    if form_type == "personal_info":
      user.first_name = request.POST.get("first_name")
      user.last_name = request.POST.get("last_name")
      user.email = request.POST.get("email")
      user.save()

      profile.phone = request.POST.get("phone")
      profile.save()
      messages.success(request, "Personal information updated successfully!")
      return redirect("user_profile")

    elif form_type == "add_address":
      Address.objects.create(
          user=user,
          address_type=request.POST.get("address_type"),
          full_name=request.POST.get("full_name"),
          phone=request.POST.get("phone"),
          address_line=request.POST.get("address_line"),
          city=request.POST.get("city"),
          pincode=request.POST.get("pincode"),
      )
      messages.success(request, "New address added successfully!")
      return redirect("user_profile")

    elif form_type == "update_address":
      address_id = request.POST.get("address_id")
      address_obj = get_object_or_404(Address, id=address_id, user=user)

      address_obj.address_type = request.POST.get("address_type")
      address_obj.full_name = request.POST.get("full_name")
      address_obj.phone = request.POST.get("phone")
      address_obj.address_line = request.POST.get("address_line")
      address_obj.city = request.POST.get("city")
      address_obj.pincode = request.POST.get("pincode")
      address_obj.save()

      messages.success(request, "Address updated successfully!")
      return redirect("user_profile")

  context = {
      "profile": profile,
      "addresses": addresses,
  }
  return render(request, "store/profile.html", context)


@login_required
def request_refund(request, order_id):
  order = get_object_or_404(Order, id=order_id, user=request.user)

  if request.method == "POST":
    selected_reason = request.POST.get("return_reason")
    custom_reason = request.POST.get("custom_reason", "").strip()
    final_reason = (
        custom_reason if selected_reason == "Others" else selected_reason
    )

    if not final_reason:
      messages.error(request, "Please select or provide a reason for return.")
      return redirect("my_orders")

    if order.razorpay_payment_id and order.status in [
        "Paid",
        "Return_Requested",
    ]:
      try:
        razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        refund_amount = int(order.total_amount * 100)

        refund_response = razorpay_client.payment.refund(
            order.razorpay_payment_id,
            {
                "amount": refund_amount,
                "speed_optimum": "optimum",
                "notes": {"reason_for_refund": final_reason},
            },
        )

        order.status = "Refunded"
        order.refund_id = refund_response.get("id")
        order.return_reason = final_reason
        order.save()

        subject = f"Refund Initiated for Order #{order.id} - BloomCart"
        message = f"""Hi {order.full_name},

Your return request for Order #{order.id} has been successfully processed.
Reason: {final_reason}
Refund ID: {order.refund_id}
Total Refund Amount: ₹{order.total_amount}

The amount will reflect in your original payment source within 5-7 business days.

Thank you for shopping with BloomCart!
"""
        try:
          send_mail(
              subject,
              message,
              settings.EMAIL_HOST_USER,
              [order.user.email],
              fail_silently=True,
          )
        except Exception:
          pass

        messages.success(
            request, "Return request accepted & refund initiated successfully!"
        )
      except Exception as e:
        messages.error(request, f"Razorpay Error: {str(e)}")
    else:
      messages.error(request, "This order is not eligible for a refund.")

  return redirect("my_orders")

from django.shortcuts import get_object_or_404, redirect, render
from .models import Order, SupportTicket

from django.shortcuts import get_object_or_404, redirect, render
from .models import Order, SupportTicket, TicketMessage # Jo bhi models required ho

@login_required
def create_support_ticket(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message') # Form se message liya
        
        # 1. Pehle SupportTicket create karein (Isme sirf order, user, subject aur status hota hai)
        ticket = SupportTicket.objects.create(
            order=order,
            user=request.user,
            subject=subject,
            status='Open'
        )
        
        # 2. Phir pehla message 'TicketMessage' model mein save karein
        if message_text:
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=message_text
            )
        
        return redirect('ticket_detail', ticket_id=ticket.id)
        
    return render(request, 'store/create_support_ticket.html', {'order': order})
        

@login_required
def ticket_detail(request, ticket_id):
  ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
  messages_list = ticket.messages.all().order_by("created_at")

  if request.method == "POST":
    reply_text = request.POST.get("message")
    if reply_text:
      TicketMessage.objects.create(
          ticket=ticket, sender=request.user, message=reply_text
      )
      messages.success(request, "Reply sent successfully!")
      return redirect("ticket_detail", ticket_id=ticket.id)

  context = {
      "ticket": ticket,
      "messages_list": messages_list,
  }
  return render(request, "store/ticket_detail.html", context)

import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import EmailVerificationOTP
from .tasks import send_otp_email_task

def signup(request):
    otp_sent = request.session.get('otp_sent', False)
    email = request.session.get('reg_email', '')

    if request.method == "POST":
        action = request.POST.get('action')

        # --- STEP 1: Email aane par OTP generate karke task ko bhejna ---
        if action == 'send_otp':
            email = request.POST.get('email', '').strip()
            
            if not email:
                messages.error(request, "Please enter a valid email address.")
                return render(request, 'store/signup.html', {'otp_sent': False, 'email': ''})

            # Check if an active account already exists with this email
            if User.objects.filter(email=email, is_active=True).exists():
                messages.error(request, "An account with this email already exists.")
                return render(request, 'store/signup.html', {'otp_sent': False, 'email': ''})

            # 6-digit random OTP generate karein
            otp_code = str(random.randint(100000, 999999))
            
            # Temporary username create karein
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            
            while User.objects.filter(username=username, is_active=True).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Temporary inactive user create ya reuse karein
            temp_user, created = User.objects.get_or_create(
                email=email, 
                is_active=False, 
                defaults={'username': username}
            )
            if not created:
                temp_user.username = username
                temp_user.save()

            # Purane OTPs hata kar naya save karein
            EmailVerificationOTP.objects.filter(user=temp_user).delete()
            EmailVerificationOTP.objects.create(user=temp_user, otp=otp_code)

            # --- Celery Task Trigger with exact 3 arguments ---
            send_otp_email_task.delay(email, temp_user.username, otp_code)

            # Session values set karein taaki step 2 khul jaye
            request.session['otp_sent'] = True
            request.session['reg_email'] = email
            request.session['verify_user_id'] = temp_user.id

            messages.success(request, "OTP has been sent to your email! Please check your inbox.")
            return redirect('signup')

        # --- STEP 2: OTP, Username aur Password verify karke account active karna ---
        elif action == 'register':
            entered_otp = request.POST.get('otp', '').strip()
            new_username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            # Fallback to session email if hidden/readonly field didn't send
            email = request.POST.get('email', '').strip() or request.session.get('reg_email', '')
            user_id = request.session.get('verify_user_id')

            if not user_id:
                messages.error(request, "Session expired. Please start again.")
                return redirect('signup')

            try:
                temp_user = User.objects.get(id=user_id)
                otp_record = EmailVerificationOTP.objects.filter(user=temp_user).latest('created_at')

                if otp_record.otp == entered_otp:
                    # Username update karein agar user ne naya dala hai
                    if new_username and new_username != temp_user.username:
                        if User.objects.filter(username=new_username).exists():
                            messages.error(request, "This username is already taken. Please choose another.")
                            return render(request, 'store/signup.html', {'otp_sent': True, 'email': email})
                        temp_user.username = new_username
                    
                    # Password set karein aur account active karein
                    temp_user.set_password(password)
                    temp_user.is_active = True
                    temp_user.save()

                    # Session aur OTP records saaf karein
                    EmailVerificationOTP.objects.filter(user=temp_user).delete()
                    request.session.pop('otp_sent', None)
                    request.session.pop('reg_email', None)
                    request.session.pop('verify_user_id', None)

                    messages.success(request, "Account verified and created successfully! Please login.")
                    return redirect('login')
                else:
                    messages.error(request, "Invalid OTP. Please try again.")
            except (User.DoesNotExist, EmailVerificationOTP.DoesNotExist):
                messages.error(request, "OTP expired or invalid session. Please request a new OTP.")

            otp_sent = True

    return render(request, 'store/signup.html', {
        'otp_sent': otp_sent,
        'email': email
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order # Agar orders fetch karne hain toh

@login_required
def track_orders_view(request):
    """User ke saare orders fetch karke tracking status dikhayega"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'store/track_orders.html', context)

def help_faq_view(request):
    """Help & FAQ page render karega"""
    return render(request, 'store/help_faq.html')

import uuid  # 👈 Yeh import sabse upar add karein
from django.shortcuts import render, redirect
from django.contrib import messages
from .scraper import scrape_product_data
from .models import Product

def scrape_view(request):
    scraped_data = request.session.get('scraped_data', None)

    if request.method == 'POST':
        if 'start_scraping' in request.POST:
            target_url = request.POST.get('target_url')
            if target_url:
                scraped_data = scrape_product_data(target_url)
                request.session['scraped_data'] = scraped_data
                
        elif 'save_to_db' in request.POST:
            if scraped_data and scraped_data.get('success'):
                # Database mein unique ID ke sath product create karein
                Product.objects.create(
                    uniq_id=str(uuid.uuid4()),  # 👈 Yeh unique key error ko khatam kar dega
                    product_title=scraped_data['title'],
                    price=scraped_data['price'],
                    image_url=scraped_data['image_url'],
                    category="Scraped Items",
                    stock=10
                )
                if 'scraped_data' in request.session:
                    del request.session['scraped_data']
                
                messages.success(request, "Product successfully saved to database!")
                return redirect('scraper_view')

    return render(request, 'store/scraper_tool.html', {'scraped_data': scraped_data})