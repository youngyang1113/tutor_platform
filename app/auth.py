from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User, TutorProfile
from app.forms import LoginForm, TutorRegisterForm

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('账号已被禁用，请联系管理员', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        next_page = request.args.get('next')
        flash(f'欢迎回来，{user.username}！', 'success')
        # 教师登录后直接跳转到家教大厅
        if user.is_tutor():
            return redirect(next_page or url_for('main.orders'))
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form)


@bp.route('/register/tutor', methods=['GET', 'POST'])
def register_tutor():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = TutorRegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='tutor')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # 拿到 user.id

        # 创建基础教师资料
        profile = TutorProfile(
            user_id=user.id,
            real_name=form.real_name.data,
            phone=form.phone.data,
            subjects='',  # 后续完善
            location='',  # 后续完善
            status='pending'
        )
        db.session.add(profile)
        db.session.commit()
        
        # 注册成功后自动登录
        login_user(user)
        flash('注册成功！请完善您的个人资料以开始接单', 'success')
        return redirect(url_for('main.orders'))

    return render_template('auth/register_tutor.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('main.index'))
