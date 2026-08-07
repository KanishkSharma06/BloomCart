# 🌸 BloomCart - AI-Powered E-Commerce Platform

BloomCart is a modern, feature-rich e-commerce web application built with **Django**. It goes beyond standard online shopping by integrating advanced AI features, smart product recommendations, secure checkout flows, and robust admin management.

---

## 🚀 Key Features

* **🤖 AI-Powered Integrations:** Smart product recommendations and AI assistant features powered by Google GenAI and ChromaDB.
* **🛍️ Complete E-Commerce Workflow:** User registration, product catalog, dynamic cart, wishlist, and secure order placement.
* **📦 Order Management & Tracking:** Real-time order status updates, cancellation, returns, and support ticket systems.
* **💳 Secure Payments & Subscriptions:** Razorpay integration for seamless transactions and prime membership features.
* **🛠️ Admin Dashboard:** Fully customizable Django admin panel with data import/export capabilities.

---

## 🛠️ Tech Stack

* **Backend:** Python, Django, Celery
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
* **Database:** SQLite / PostgreSQL
* **AI & Search:** Google GenAI, ChromaDB, Typesense

---

## ⚙️ Getting Started & Installation

Follow these steps to set up and run the project locally on your machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/KanishkSharma06/BloomCart.git](https://github.com/KanishkSharma06/BloomCart.git)
cd BloomCart
2. Create and Activate a Virtual Environment
Bash
python -m venv myenv
# On Windows:
myenv\Scripts\activate
# On macOS/Linux:
source myenv/bin/activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Set Up Environment Variables
Create a .env file in the root directory of the project and add your confidential keys:

Code snippet
GEMINI_API_KEY=your_actual_gemini_api_key_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True
5. Run Database Migrations
Bash
python manage.py makemigrations
python manage.py migrate
6. Run the Development Server
Bash
python manage.py runserver
Open your browser and visit: https://bloomcart-30cs.onrender.com/
👨‍💻 Author
Kanishk Sharma

GitHub: @KanishkSharma06