from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, TutorProfile, JobOrder, Application

bp = Blueprint('manage', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('您没有权限访问管理后台', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ───────────────── 仪表盘 ─────────────────

@bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_tutors': TutorProfile.query.count(),
        'pending_tutors': TutorProfile.query.filter_by(status='pending').count(),
        'approved_tutors': TutorProfile.query.filter_by(status='approved').count(),
        'total_orders': JobOrder.query.count(),
        'open_orders': JobOrder.query.filter_by(status='open').count(),
        'filled_orders': JobOrder.query.filter_by(status='filled').count(),
        'total_applications': Application.query.count(),
        'pending_applications': Application.query.filter_by(status='pending').count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    pending_teachers = TutorProfile.query.filter_by(status='pending').order_by(
        TutorProfile.created_at.desc()).limit(5).all()
    recent_orders = JobOrder.query.order_by(JobOrder.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_users=recent_users,
                           pending_teachers=pending_teachers,
                           recent_orders=recent_orders)


# ───────────────── 用户管理 ─────────────────

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', '')
    query = User.query
    if role:
        query = query.filter_by(role=role)
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users, role=role)


@bp.route('/user/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.role == 'admin':
        flash('不能禁用管理员账号', 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = '启用' if user.is_active else '禁用'
        flash(f'已{status}用户 {user.username}', 'success')
    return redirect(url_for('manage.users'))


@bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.role == 'admin':
        flash('不能删除管理员账号', 'danger')
        return redirect(url_for('manage.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'已删除用户 {user.username}', 'success')
    return redirect(url_for('manage.users'))


# ───────────────── 教师审核 ─────────────────

@bp.route('/teachers')
@login_required
@admin_required
def teachers():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = TutorProfile.query
    if status:
        query = query.filter_by(status=status)
    teachers = query.order_by(TutorProfile.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/teachers.html', teachers=teachers, status=status)


@bp.route('/teacher/<int:id>')
@login_required
@admin_required
def teacher_detail(id):
    profile = TutorProfile.query.get_or_404(id)
    applications = Application.query.filter_by(tutor_profile_id=id).order_by(
        Application.created_at.desc()).all()
    return render_template('admin/teacher_detail.html',
                           profile=profile, applications=applications)


@bp.route('/teacher/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_teacher(id):
    profile = TutorProfile.query.get_or_404(id)
    profile.status = 'approved'
    db.session.commit()
    flash(f'已通过 {profile.real_name} 的审核', 'success')
    return redirect(url_for('manage.teacher_detail', id=id))


@bp.route('/teacher/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_teacher(id):
    profile = TutorProfile.query.get_or_404(id)
    profile.status = 'rejected'
    db.session.commit()
    flash(f'已拒绝 {profile.real_name} 的审核', 'warning')
    return redirect(url_for('manage.teacher_detail', id=id))


@bp.route('/teacher/<int:id>/reset', methods=['POST'])
@login_required
@admin_required
def reset_teacher(id):
    profile = TutorProfile.query.get_or_404(id)
    profile.status = 'pending'
    db.session.commit()
    flash(f'已将 {profile.real_name} 的状态重置为待审核', 'info')
    return redirect(url_for('manage.teacher_detail', id=id))


@bp.route('/teacher/<int:id>/certify', methods=['POST'])
@login_required
@admin_required
def certify_teacher(id):
    """平台认证"""
    profile = TutorProfile.query.get_or_404(id)
    profile.is_platform_certified = not profile.is_platform_certified
    db.session.commit()
    status = '已获得' if profile.is_platform_certified else '已取消'
    flash(f'{profile.real_name} {status}平台认证', 'success')
    return redirect(url_for('manage.teacher_detail', id=id))


@bp.route('/teacher/<int:id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_teacher(id):
    """资质已验"""
    profile = TutorProfile.query.get_or_404(id)
    profile.is_verified = not profile.is_verified
    db.session.commit()
    status = '已获得' if profile.is_verified else '已取消'
    flash(f'{profile.real_name} {status}资质验证', 'success')
    return redirect(url_for('manage.teacher_detail', id=id))


# ───────────────── 需求管理 ─────────────────

@bp.route('/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = JobOrder.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(JobOrder.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/orders.html', orders=orders, status=status)


@bp.route('/order/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_order():
    """管理员新增需求"""
    from app.forms import JobOrderForm
    parents = User.query.filter_by(role='parent', is_active=True).order_by(User.username).all()
    form = JobOrderForm()
    if form.validate_on_submit():
        parent_id = request.form.get('parent_id', type=int)
        if not parent_id:
            flash('请选择家长', 'warning')
            return render_template('admin/add_order.html', form=form, parents=parents)
        order = JobOrder(
            parent_id=parent_id,
            subject=form.subject.data,
            grade=form.grade.data,
            description=form.description.data,
            location=form.location.data,
            city=form.city.data,
            budget=form.budget.data,
            schedule=form.schedule.data,
            duration=form.duration.data,
            frequency=form.frequency.data,
            form_type=form.form_type.data,
            gender_pref=form.gender_pref.data,
            teacher_type=form.teacher_type.data,
            contact_phone=form.contact_phone.data,
            status='open'
        )
        db.session.add(order)
        db.session.commit()
        flash(f'需求 #{order.id} 创建成功！', 'success')
        return redirect(url_for('manage.order_detail', id=order.id))
    return render_template('admin/add_order.html', form=form, parents=parents)


@bp.route('/order/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_order(id):
    """管理员编辑需求"""
    from app.forms import JobOrderForm
    order = JobOrder.query.get_or_404(id)
    form = JobOrderForm()
    if form.validate_on_submit():
        order.subject = form.subject.data
        order.grade = form.grade.data
        order.description = form.description.data
        order.location = form.location.data
        order.city = form.city.data
        order.budget = form.budget.data
        order.schedule = form.schedule.data
        order.duration = form.duration.data
        order.frequency = form.frequency.data
        order.form_type = form.form_type.data
        order.gender_pref = form.gender_pref.data
        order.teacher_type = form.teacher_type.data
        order.contact_phone = form.contact_phone.data
        db.session.commit()
        flash(f'需求 #{order.id} 已更新', 'success')
        return redirect(url_for('manage.order_detail', id=order.id))
    elif request.method == 'GET':
        form.subject.data = order.subject
        form.grade.data = order.grade
        form.description.data = order.description
        form.location.data = order.location
        form.city.data = order.city
        form.budget.data = order.budget
        form.schedule.data = order.schedule
        form.duration.data = order.duration
        form.frequency.data = order.frequency
        form.form_type.data = order.form_type
        form.gender_pref.data = order.gender_pref
        form.teacher_type.data = order.teacher_type
        form.contact_phone.data = order.contact_phone
    return render_template('admin/add_order.html', form=form, parents=[], order=order, editing=True)


@bp.route('/order/<int:id>')
@login_required
@admin_required
def order_detail(id):
    order = JobOrder.query.get_or_404(id)
    applications = Application.query.filter_by(job_order_id=id).order_by(
        Application.created_at.desc()).all()
    return render_template('admin/order_detail.html',
                           order=order, applications=applications)


@bp.route('/order/<int:id>/close', methods=['POST'])
@login_required
@admin_required
def close_order(id):
    order = JobOrder.query.get_or_404(id)
    order.status = 'filled'
    db.session.commit()
    flash('需求已关闭', 'success')
    return redirect(url_for('manage.order_detail', id=id))


@bp.route('/order/<int:id>/reopen', methods=['POST'])
@login_required
@admin_required
def reopen_order(id):
    order = JobOrder.query.get_or_404(id)
    order.status = 'open'
    db.session.commit()
    flash('需求已重新开放', 'success')
    return redirect(url_for('manage.order_detail', id=id))


@bp.route('/order/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_order(id):
    """管理员删除需求"""
    order = JobOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash(f'需求 #{id} 已删除', 'success')
    return redirect(url_for('manage.orders'))


# ───────────────── 抢单管理 ─────────────────

@bp.route('/applications')
@login_required
@admin_required
def applications():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Application.query
    if status:
        query = query.filter_by(status=status)
    applications = query.order_by(Application.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/applications.html',
                           applications=applications, status=status)


@bp.route('/application/<int:id>/note', methods=['POST'])
@login_required
@admin_required
def update_note(id):
    app = Application.query.get_or_404(id)
    note = request.form.get('admin_note', '').strip()
    app.admin_note = note
    db.session.commit()
    flash('跟进备注已更新', 'success')
    return redirect(request.referrer or url_for('manage.applications'))


@bp.route('/application/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_app_status(id):
    app = Application.query.get_or_404(id)
    new_status = request.form.get('status', '')
    if new_status in ('pending', 'success', 'failed'):
        app.status = new_status
        db.session.commit()
        flash('状态已更新', 'success')
    return redirect(request.referrer or url_for('manage.applications'))
