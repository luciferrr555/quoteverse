"""
Seed the database with sample data.
Run: python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, User, Quote

QUOTES = [
    # SUCCESS
    ("The secret of getting ahead is getting started.", "Mark Twain", "Success"),
    ("Success is not final, failure is not fatal. It is the courage to continue that counts.", "Winston Churchill", "Success"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson", "Success"),
    ("Opportunities don't happen. You create them.", "Chris Grosser", "Success"),
    ("Dream big. Start small. Act now.", "Robin Sharma", "Success"),
    ("Hustle in silence and let your success make the noise.", "Unknown", "Success"),
    ("The harder you work for something, the greater you'll feel when you achieve it.", "Unknown", "Success"),
    ("Winners are not people who never fail, but people who never quit.", "Edwin Louis Cole", "Success"),
    # STUDY
    ("Education is the most powerful weapon you can use to change the world.", "Nelson Mandela", "Study"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin", "Study"),
    ("The expert in anything was once a beginner.", "Helen Hayes", "Study"),
    ("Study while others are sleeping.", "William A. Ward", "Study"),
    ("Genius is 1% inspiration and 99% perspiration.", "Thomas Edison", "Study"),
    ("The beautiful thing about learning is nobody can take it away from you.", "B.B. King", "Study"),
    # GYM
    ("Your body can stand almost anything. It's your mind you have to convince.", "Unknown", "Gym"),
    ("The only bad workout is the one that didn't happen.", "Unknown", "Gym"),
    ("Push harder than yesterday if you want a different tomorrow.", "Unknown", "Gym"),
    ("No pain, no gain. Shut up and train.", "Unknown", "Gym"),
    ("The body achieves what the mind believes.", "Unknown", "Gym"),
    ("Fall in love with the process and the results will follow.", "Unknown", "Gym"),
    # LOVE
    ("The best thing to hold onto in life is each other.", "Audrey Hepburn", "Love"),
    ("Love is not about how many days, weeks, or months you've been together. It is about how much you love each other every day.", "Unknown", "Love"),
    ("You don't love someone for their looks or clothes or cars. You love them because they sing a song that only you can hear.", "Oscar Wilde", "Love"),
    ("In love, one and one are one.", "Jean Paul Sartre", "Love"),
    # BREAKUP
    ("Sometimes good things fall apart so better things can fall together.", "Marilyn Monroe", "Breakup"),
    ("Never allow someone to be your priority while allowing yourself to be their option.", "Mark Twain", "Breakup"),
    ("Your value doesn't decrease based on someone's inability to see your worth.", "Unknown", "Breakup"),
    ("You survived everything before this. You will survive this too.", "Unknown", "Breakup"),
    ("Stop looking for happiness in the same place you lost it.", "Unknown", "Breakup"),
    # MONEY
    ("Don't work for money. Make money work for you.", "Robert Kiyosaki", "Money"),
    ("Financial freedom is not about being rich, it's about having choices.", "Unknown", "Money"),
    ("The goal is not more money. The goal is living life on your terms.", "Chris Brogan", "Money"),
    ("Every rupee you save is a soldier fighting for your freedom.", "Unknown", "Money"),
    ("Build assets that work while you sleep.", "Unknown", "Money"),
    # DISCIPLINE
    ("Discipline is the bridge between goals and accomplishment.", "Jim Rohn", "Discipline"),
    ("We must all suffer from one of two pains: the pain of discipline or the pain of regret.", "Jim Rohn", "Discipline"),
    ("Motivation gets you going. Discipline keeps you growing.", "John C. Maxwell", "Discipline"),
    ("Without self-discipline, success is impossible, period.", "Lou Holtz", "Discipline"),
    # LIFE
    ("Life is what happens when you're busy making other plans.", "John Lennon", "Life"),
    ("In the end, it's not the years in your life that count. It's the life in your years.", "Abraham Lincoln", "Life"),
    ("You only live once, but if you do it right, once is enough.", "Mae West", "Life"),
    # MINDSET
    ("Your mindset is your most powerful weapon.", "Unknown", "Mindset"),
    ("The mind is everything. What you think, you become.", "Buddha", "Mindset"),
    ("Change your thoughts and you change your world.", "Norman Vincent Peale", "Mindset"),
    ("Whether you think you can, or you think you can't — you're right.", "Henry Ford", "Mindset"),
    # HINGLISH
    ("Sapne dekh nahi, sapne mein jee. Tab jaake zindagi badlegi.", "Unknown", "Hinglish"),
    ("Log kya kahenge yeh soch ke apni life mat rok.", "Unknown", "Hinglish"),
    ("Ek din aisa aayega jab teri story dusron ko inspire karegi.", "Unknown", "Hinglish"),
    ("Apni mehnat pe trust kar, baaki sab time pe chhod.", "Unknown", "Hinglish"),
    ("Thoda aur ruk. Kamiyabi door nahi.", "Unknown", "Hinglish"),
]


def seed():
    with app.app_context():
        # Create admin user
        admin = User.query.filter_by(email='admin@quotesplatform.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@quotesplatform.com',
                is_admin=True,
                bio='QuoteVerse founder. Bringing daily motivation to the world.'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.flush()
            print('[OK] Admin user created.')
        else:
            print('[OK] Admin user already exists.')

        # Create sample user
        demo = User.query.filter_by(email='demo@quotesplatform.com').first()
        if not demo:
            demo = User(username='inspiredhuman', email='demo@quotesplatform.com', bio='Just living. Just learning.')
            demo.set_password('demo123')
            db.session.add(demo)
            db.session.flush()

        # Add quotes
        added = 0
        for text, author, category in QUOTES:
            existing = Quote.query.filter_by(text=text).first()
            if not existing:
                q = Quote(text=text, author=author, category=category,
                          user_id=admin.id, approved=True,
                          likes_count=0, views=0)
                db.session.add(q)
                db.session.flush()
                q.generate_slug()
                added += 1

        db.session.commit()
        print(f'[OK] Added {added} quotes to the database.')
        print(f'[OK] Total quotes: {Quote.query.count()}')
        print('')
        print('Database seeded successfully!')
        print('  Admin login: admin@quotesplatform.com / admin123')
        print('  Demo login:  demo@quotesplatform.com / demo123')


if __name__ == '__main__':
    seed()
