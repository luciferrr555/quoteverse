from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re

db = SQLAlchemy()


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text[:80]


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_pic = db.Column(db.String(255), default='default_avatar.png')
    bio = db.Column(db.String(300), default='')
    is_admin = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    streak = db.Column(db.Integer, default=0)
    last_visit = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships — distinct backref names to avoid conflicts
    submitted_quotes = db.relationship('Quote', backref='quote_author', lazy='dynamic',
                                       foreign_keys='Quote.user_id')
    user_likes = db.relationship('Like', backref='like_owner', lazy='dynamic')
    user_favorites = db.relationship('Favorite', backref='fav_owner', lazy='dynamic')
    user_comments = db.relationship('Comment', backref='comment_owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_liked(self, quote_id):
        return Like.query.filter_by(user_id=self.id, quote_id=quote_id).first() is not None

    def has_favorited(self, quote_id):
        return Favorite.query.filter_by(user_id=self.id, quote_id=quote_id).first() is not None

    def is_following(self, user_id):
        return Follower.query.filter_by(follower_id=self.id, user_id=user_id).first() is not None

    @property
    def followers_count(self):
        return Follower.query.filter_by(user_id=self.id).count()

    @property
    def following_count(self):
        return Follower.query.filter_by(follower_id=self.id).count()

    def __repr__(self):
        return f'<User {self.username}>'


class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), default='Unknown')
    category = db.Column(db.String(50), nullable=False, index=True)
    slug = db.Column(db.String(120), unique=True, index=True)
    likes_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    quote_likes = db.relationship('Like', backref='parent_quote', lazy='dynamic',
                                  cascade='all, delete-orphan')
    quote_favorites = db.relationship('Favorite', backref='parent_quote_fav', lazy='dynamic',
                                      cascade='all, delete-orphan')
    quote_comments = db.relationship('Comment', backref='parent_quote_comment', lazy='dynamic',
                                     cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.text and not self.slug:
            base_slug = slugify(self.text[:60])
            self.slug = f"{base_slug}-{self.id or 0}"

    def generate_slug(self):
        base_slug = slugify(self.text[:60])
        self.slug = f"{base_slug}-{self.id}"

    @property
    def trending_score(self):
        now = datetime.utcnow()
        age_hours = max(1, (now - self.created_at).total_seconds() / 3600)
        return (self.likes_count * 3 + self.views * 0.1) / (age_hours ** 1.5)

    @property
    def comments_count(self):
        return Comment.query.filter_by(quote_id=self.id).count()

    def __repr__(self):
        return f'<Quote {self.id}: {self.text[:30]}>'


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'quote_id', name='unique_like'),)


class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'quote_id', name='unique_fav'),)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Follower(db.Model):
    __tablename__ = 'followers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'follower_id', name='unique_follow'),)


class DailyVisit(db.Model):
    __tablename__ = 'daily_visits'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    visit_count = db.Column(db.Integer, default=0)
