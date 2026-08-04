from pathlib import Path
import os
from dotenv import load_dotenv
from celery.schedules import crontab

# Path sahi set karo agar file nahi mil रही
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env')) 

RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
print(f"DEBUG: Key ID is: {RAZORPAY_KEY_ID}")
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

SECRET_KEY = 'django-insecure-&jg4u2q!me)7g^z6rt9f5aoqxx%g3k17)3vgdv(o7v@=_s^e)s'
DEBUG = True
ALLOWED_HOSTS = ['*']

# ==============================================================================
# APPS & MIDDLEWARE
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    'import_export',
    
    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # Your store app
    'store',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Allauth requirement
]

# ==============================================================================
# DATABASE & URLS (Optimized connection persistence)
# ==============================================================================
import dj_database_url

# ==============================================================================
# DATABASE & URLS (Auto-switch between Local and Render Production)
# ==============================================================================
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f"postgres://postgres:Kanishk@13@localhost:5432/bloomcart_db"),
        conn_max_age=60
    )
}
ROOT_URLCONF = 'bloomcart_project.urls'

# ==============================================================================
# AUTHENTICATION SETTINGS
# ==============================================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# AllAuth Configuration
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_QUERY_EMAIL = True

ACCOUNT_SIGNUP_FIELDS = ['email', 'username']

# Google Only Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# ==============================================================================
# STATIC & MEDIA
# ==============================================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,                
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',
            ],
        },
    },
]

# ==============================================================================
# TYPESENSE CONFIGURATION (Reduced timeout to prevent page hanging)
# ==============================================================================
TYPESENSE = {
    'API_KEY': 'dtOFl3ANkvNJr7DUrOAmIWTZO2AQSVNR',  # Admin API Key
    'HOST': 'fas0pie5tckr6g2hp-1.a2.typesense.net', # Cloud URL
    'PORT': '443',
    'PROTOCOL': 'https',
    'CONNECTION_TIMEOUT_SECONDS': 3,  # <-- REDUCED from 15 to 3 seconds so page won't freeze if cloud is slow
}

# ==============================================================================
# EMAIL CONFIGURATION (Gmail SMTP Inbox Delivery)
# ==============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kanishkmeenakshisharma06@gmail.com'         
EMAIL_HOST_PASSWORD = 'zsetfvslumjjpdrj'   
DEFAULT_FROM_EMAIL = 'BloomCart <kanishkmeenakshisharma06@gmail.com>'

# ==============================================================================
# CELERY & REDIS CONFIGURATION
# ==============================================================================
# Celery Configuration
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

CELERY_BEAT_SCHEDULE = {
    'send-daily-morning-essentials': {
        'task': 'store.tasks.send_daily_promotional_notifications',
        'schedule': crontab(hour=8, minute=0), 
    },
    'send-alternate-pantry-deals': {
        'task': 'store.tasks.send_daily_promotional_notifications',
        'schedule': crontab(hour=12, minute=0, day_of_week='mon,wed,fri'),
    },
    'send-weekly-household-sale': {
        'task': 'store.tasks.send_daily_promotional_notifications',
        'schedule': crontab(hour=10, minute=0, day_of_week='sun'),
    },
}