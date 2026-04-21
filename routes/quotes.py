from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from models import db, Quote, Like, Favorite, Comment, DailyVisit
from datetime import datetime, date
from sqlalchemy import desc

quotes_bp = Blueprint('quotes', __name__)

CATEGORIES = ['Success', 'Study', 'Gym', 'Love', 'Breakup', 'Money', 'Discipline', 'Life', 'Mindset', 'Hinglish']
CATEGORY_ICONS = {
    'Success': '🏆', 'Study': '📚', 'Gym': '💪', 'Love': '❤️',
    'Breakup': '💔', 'Money': '💰', 'Discipline': '🎯', 'Life': '🌱',
    'Mindset': '🧠', 'Hinglish': '🇮🇳'
}
CATEGORY_COLORS = {
    'Success': '#f59e0b', 'Study': '#3b82f6', 'Gym': '#ef4444', 'Love': '#ec4899',
    'Breakup': '#8b5cf6', 'Money': '#10b981', 'Discipline': '#f97316', 'Life': '#06b6d4',
    'Mindset': '#6366f1', 'Hinglish': '#84cc16'
}


@quotes_bp.route('/')
def index():
    _track_visit()
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    query = Quote.query.filter_by(approved=True)
    if category:
        query = query.filter_by(category=category)
    quotes = query.order_by(desc(Quote.created_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('index.html', quotes=quotes, categories=CATEGORIES,
                           category_icons=CATEGORY_ICONS, category_colors=CATEGORY_COLORS,
                           active_category=category)


@quotes_bp.route('/api/quotes')
def api_quotes():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    per_page = 10
    query = Quote.query.filter_by(approved=True)
    if category:
        query = query.filter_by(category=category)
    quotes = query.order_by(desc(Quote.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    data = []
    for q in quotes.items:
        data.append({
            'id': q.id,
            'text': q.text,
            'author': q.author,
            'category': q.category,
            'slug': q.slug,
            'likes_count': q.likes_count,
            'views': q.views,
            'comments_count': q.comments_count,
            'liked': current_user.has_liked(q.id) if current_user.is_authenticated else False,
            'favorited': current_user.has_favorited(q.id) if current_user.is_authenticated else False,
            'created_at': q.created_at.strftime('%b %d, %Y'),
            'color': CATEGORY_COLORS.get(q.category, '#6366f1')
        })
    return jsonify({
        'quotes': data,
        'has_next': quotes.has_next,
        'next_page': quotes.next_num if quotes.has_next else None,
        'total': quotes.total
    })


@quotes_bp.route('/categories')
def categories():
    cats = []
    for cat in CATEGORIES:
        count = Quote.query.filter_by(category=cat, approved=True).count()
        cats.append({'name': cat, 'icon': CATEGORY_ICONS.get(cat, '📝'),
                     'count': count, 'color': CATEGORY_COLORS.get(cat, '#6366f1')})
    return render_template('categories.html', categories=cats)


@quotes_bp.route('/category/<name>')
def category(name):
    if name not in CATEGORIES:
        flash('Category not found.', 'danger')
        return redirect(url_for('quotes.categories'))
    page = request.args.get('page', 1, type=int)
    quotes = Quote.query.filter_by(category=name, approved=True).order_by(
        desc(Quote.created_at)).paginate(page=page, per_page=12, error_out=False)
    return render_template('index.html', quotes=quotes, categories=CATEGORIES,
                           category_icons=CATEGORY_ICONS, category_colors=CATEGORY_COLORS,
                           active_category=name, page_title=f'{name} Quotes')


@quotes_bp.route('/trending')
def trending():
    all_quotes = Quote.query.filter_by(approved=True).all()
    sorted_quotes = sorted(all_quotes, key=lambda q: q.trending_score, reverse=True)[:50]
    return render_template('trending.html', quotes=sorted_quotes,
                           category_colors=CATEGORY_COLORS, category_icons=CATEGORY_ICONS)


@quotes_bp.route('/latest')
def latest():
    page = request.args.get('page', 1, type=int)
    quotes = Quote.query.filter_by(approved=True).order_by(
        desc(Quote.created_at)).paginate(page=page, per_page=20, error_out=False)
    return render_template('latest.html', quotes=quotes,
                           category_colors=CATEGORY_COLORS, category_icons=CATEGORY_ICONS)


@quotes_bp.route('/quote/<slug>')
def quote_detail(slug):
    quote = Quote.query.filter_by(slug=slug, approved=True).first_or_404()
    quote.views += 1
    db.session.commit()
    from sqlalchemy.orm import joinedload
    comments = Comment.query.options(joinedload(Comment.comment_owner)).filter_by(
        quote_id=quote.id).order_by(desc(Comment.created_at)).all()
    related = Quote.query.filter_by(category=quote.category, approved=True).filter(
        Quote.id != quote.id).order_by(desc(Quote.likes_count)).limit(6).all()
    liked = current_user.has_liked(quote.id) if current_user.is_authenticated else False
    favorited = current_user.has_favorited(quote.id) if current_user.is_authenticated else False
    return render_template('quote_detail.html', quote=quote, comments=comments,
                           related=related, liked=liked, favorited=favorited,
                           color=CATEGORY_COLORS.get(quote.category, '#6366f1'))


@quotes_bp.route('/api/like/<int:quote_id>', methods=['POST'])
@login_required
def like_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    existing = Like.query.filter_by(user_id=current_user.id, quote_id=quote_id).first()
    if existing:
        db.session.delete(existing)
        quote.likes_count = max(0, quote.likes_count - 1)
        liked = False
    else:
        like = Like(user_id=current_user.id, quote_id=quote_id)
        db.session.add(like)
        quote.likes_count += 1
        liked = True
    db.session.commit()
    return jsonify({'liked': liked, 'count': quote.likes_count})


@quotes_bp.route('/api/favorite/<int:quote_id>', methods=['POST'])
@login_required
def favorite_quote(quote_id):
    Quote.query.get_or_404(quote_id)
    existing = Favorite.query.filter_by(user_id=current_user.id, quote_id=quote_id).first()
    if existing:
        db.session.delete(existing)
        favorited = False
    else:
        fav = Favorite(user_id=current_user.id, quote_id=quote_id)
        db.session.add(fav)
        favorited = True
    db.session.commit()
    return jsonify({'favorited': favorited})


@quotes_bp.route('/api/comment/<int:quote_id>', methods=['POST'])
@login_required
def post_comment(quote_id):
    Quote.query.get_or_404(quote_id)
    text = request.json.get('text', '').strip()
    if not text or len(text) > 500:
        return jsonify({'error': 'Invalid comment'}), 400
    comment = Comment(user_id=current_user.id, quote_id=quote_id, text=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'id': comment.id,
        'text': comment.text,
        'username': current_user.username,
        'profile_pic': current_user.profile_pic,
        'created_at': comment.created_at.strftime('%b %d, %Y')
    })


@quotes_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_quote():
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        author = request.form.get('author', 'Unknown').strip()
        category = request.form.get('category', '').strip()
        if not text or len(text) < 10:
            flash('Quote must be at least 10 characters.', 'danger')
            return render_template('submit.html', categories=CATEGORIES)
        if category not in CATEGORIES:
            flash('Please select a valid category.', 'danger')
            return render_template('submit.html', categories=CATEGORIES)
        quote = Quote(text=text, author=author, category=category,
                      user_id=current_user.id, approved=current_user.is_admin)
        db.session.add(quote)
        db.session.flush()
        quote.generate_slug()
        db.session.commit()
        if current_user.is_admin:
            flash('Quote published successfully! 🎉', 'success')
        else:
            flash('Quote submitted for review. We\'ll notify you once approved! ✅', 'success')
        return redirect(url_for('quotes.index'))
    return render_template('submit.html', categories=CATEGORIES, category_icons=CATEGORY_ICONS)


@quotes_bp.route('/about')
def about():
    return render_template('about.html')


@quotes_bp.route('/sitemap.xml')
def sitemap():
    quotes = Quote.query.filter_by(approved=True).all()
    pages = []
    for q in quotes:
        pages.append({
            'loc': url_for('quotes.quote_detail', slug=q.slug, _external=True),
            'lastmod': q.created_at.strftime('%Y-%m-%d'),
            'priority': '0.8'
        })
    pages.append({'loc': url_for('quotes.index', _external=True), 'priority': '1.0'})
    pages.append({'loc': url_for('quotes.trending', _external=True), 'priority': '0.9'})
    xml = render_template('sitemap.xml', pages=pages)
    return Response(xml, mimetype='application/xml')


def _track_visit():
    today = date.today()
    visit = DailyVisit.query.filter_by(date=today).first()
    if not visit:
        visit = DailyVisit(date=today, visit_count=1)
        db.session.add(visit)
    else:
        visit.visit_count += 1
    db.session.commit()
