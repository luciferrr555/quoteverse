# QuoteVerse — Motivational Quotes Platform

A fully functional, production-ready Flask-based motivational quotes platform with AI tools, admin dashboard, user auth, infinite scroll, and PWA support.

## Quick Start (Local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file
copy .env.example .env

# 3. Seed the database (50+ quotes + admin account)
python seed_data.py

# 4. Run the server
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

**Admin login:** `admin@quotesplatform.com` / `admin123`
**Demo login:** `demo@quotesplatform.com` / `demo123`

---

## Features

| Feature | Details |
|---|---|
| 🔐 Auth | Register, Login, Logout, Password hashing, Streak tracking |
| ♾️ Infinite Scroll | Instagram-style feed with Intersection Observer API |
| ❤️ Like / ⭐ Save | Toggle-based like and favorite system |
| 💬 Comments | Post comments on any quote |
| 👥 Follow | Follow/unfollow other users |
| 🤖 AI Tools | Generate quotes by mood, rewrite in 4 styles, Instagram caption generator |
| 📸 Download | Save any quote as a beautiful image (html2canvas) |
| 📤 Share | WhatsApp, Twitter/X, Instagram caption copy |
| 🔥 Trending | Algorithm-ranked by likes + views + recency |
| 📂 Categories | 10 categories: Success, Study, Gym, Love, Breakup, Money, Discipline, Life, Mindset, Hinglish |
| ⚙️ Admin Panel | Approve/reject quotes, manage users, Chart.js analytics |
| 🌙 Dark/Light Mode | Toggle with localStorage persistence |
| 📱 PWA | Installable as mobile app, offline cache via Service Worker |
| 🗺️ Sitemap | Auto-generated `/sitemap.xml` for SEO |

---

## Folder Structure

```
quotes-platform/
├── app.py              # Flask app factory
├── models.py           # SQLAlchemy models (6 tables)
├── config.py           # Dev/Prod configuration
├── seed_data.py        # Database seeder
├── requirements.txt
├── .env.example
├── routes/
│   ├── auth.py         # Login, register, logout
│   ├── quotes.py       # Home, API, like, fav, comment, sitemap
│   ├── ai.py           # Generate, rewrite, caption, daily quote
│   ├── user.py         # Profile, favorites, follow
│   └── admin.py        # Dashboard, approve, users
├── templates/
│   ├── base.html       # Nav, footer, toasts, dark mode
│   ├── index.html      # Home + infinite scroll
│   ├── categories.html
│   ├── trending.html
│   ├── latest.html
│   ├── quote_detail.html
│   ├── ai_tools.html
│   ├── submit.html
│   ├── profile.html
│   ├── favorites.html
│   ├── about.html
│   ├── edit_profile.html
│   ├── partials/
│   │   └── quote_card.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── admin/
│       ├── dashboard.html
│       └── users.html
└── static/
    ├── css/style.css   # Full design system (dark/light, glassmorphism)
    ├── js/main.js      # Infinite scroll, likes, toasts, modals
    ├── js/quote-image.js # html2canvas poster download
    ├── manifest.json   # PWA manifest
    └── sw.js           # Service Worker (offline cache)
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/quotes?page=N&category=X` | Paginated quotes JSON |
| POST | `/api/like/<id>` | Toggle like |
| POST | `/api/favorite/<id>` | Toggle favorite |
| POST | `/api/comment/<id>` | Post comment |
| POST | `/ai/generate` | Generate quotes by mood |
| POST | `/ai/rewrite` | Rewrite quote in style |
| POST | `/ai/caption` | Instagram caption |
| GET | `/ai/daily?mood=X` | Daily personalized quote |
| GET | `/sitemap.xml` | SEO sitemap |

---

## Monetization Ready

- **Google AdSense** placeholders in `base.html` and `index.html`
- **Premium membership** flag (`user.is_premium`) in database
- **Affiliate links** section in footer
- **Print-on-Demand** integration point in quote detail page

---

## Deploy to Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set these:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add Environment Variables:
   - `SECRET_KEY` = `your-very-secret-key`
   - `FLASK_ENV` = `production`
6. Click Deploy!

---

## Adding a Real Gemini API Key (Optional)

1. Get a free key at [aistudio.google.com](https://aistudio.google.com)
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`
3. Update `routes/ai.py` to call the Gemini API instead of the template system
