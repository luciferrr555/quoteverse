from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Quote, DailyVisit
from datetime import date, timedelta
from sqlalchemy import desc, func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('quotes.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_quotes = Quote.query.filter_by(approved=True).count()
    pending_quotes = Quote.query.filter_by(approved=False).count()
    today = date.today()
    visits_today = DailyVisit.query.filter_by(date=today).first()
    visit_count = visits_today.visit_count if visits_today else 0

    # Last 7 days visits for chart
    visits_chart = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        v = DailyVisit.query.filter_by(date=d).first()
        visits_chart.append({'date': d.strftime('%d %b'), 'count': v.visit_count if v else 0})

    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
    pending = Quote.query.filter_by(approved=False).order_by(desc(Quote.created_at)).all()
    top_quotes = Quote.query.filter_by(approved=True).order_by(desc(Quote.likes_count)).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users, total_quotes=total_quotes,
                           pending_quotes=pending_quotes, visit_count=visit_count,
                           visits_chart=visits_chart, recent_users=recent_users,
                           pending=pending, top_quotes=top_quotes)


@admin_bp.route('/approve/<int:quote_id>', methods=['POST'])
@login_required
@admin_required
def approve_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    quote.approved = True
    if not quote.slug:
        quote.generate_slug()
    db.session.commit()
    return jsonify({'status': 'approved', 'slug': quote.slug})


@admin_bp.route('/reject/<int:quote_id>', methods=['POST'])
@login_required
@admin_required
def reject_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    db.session.delete(quote)
    db.session.commit()
    return jsonify({'status': 'rejected'})


@admin_bp.route('/delete-quote/<int:quote_id>', methods=['POST'])
@login_required
@admin_required
def delete_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    db.session.delete(quote)
    db.session.commit()
    flash('Quote deleted.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users_list = User.query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users_list)


@admin_bp.route('/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot modify yourself'}), 400
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'is_admin': user.is_admin})
