from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Quote, Favorite, Follower
from sqlalchemy import desc

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    quotes = Quote.query.filter_by(user_id=user.id, approved=True).order_by(
        desc(Quote.created_at)).paginate(page=page, per_page=12, error_out=False)
    is_following = False
    if current_user.is_authenticated and current_user.id != user.id:
        is_following = current_user.is_following(user.id)
    return render_template('profile.html', profile_user=user, quotes=quotes,
                           is_following=is_following)


@user_bp.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    fav_ids = [f.quote_id for f in Favorite.query.filter_by(
        user_id=current_user.id).order_by(desc(Favorite.created_at)).all()]
    quotes = Quote.query.filter(Quote.id.in_(fav_ids), Quote.approved == True).paginate(
        page=page, per_page=12, error_out=False)
    return render_template('favorites.html', quotes=quotes)


@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    existing = Follower.query.filter_by(
        user_id=user.id, follower_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
        following = False
    else:
        follow = Follower(user_id=user.id, follower_id=current_user.id)
        db.session.add(follow)
        following = True
    db.session.commit()
    return jsonify({'following': following,
                    'followers_count': user.followers_count})


@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()[:300]
        current_user.bio = bio
        db.session.commit()
        flash('Profile updated! ✅', 'success')
        return redirect(url_for('user.profile', username=current_user.username))
    return render_template('edit_profile.html')
