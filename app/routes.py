from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, TutorProfile, JobOrder, Application, Certificate
from app.forms import (JobOrderForm, ApplicationForm, ProfileForm, 
                       TutorProfileForm, CertificateForm)
import os

bp = Blueprint('main', __name__)


# ───────────────── 首页 ─────────────────

@bp.route('/')
def index():
    recent_orders = JobOrder.query.filter_by(status='open').order_by(
        JobOrder.created_at.desc()).limit(6).all()
    teachers = TutorProfile.query.filter_by(status='approved').order_by(
        TutorProfile.created_at.desc()).limit(6).all()
    return render_template('index.html', orders=recent_orders, teachers=teachers)


# ───────────────── 师资列表与详情 ─────────────────

@bp.route('/teachers')
def teachers():
    page = request.args.get('page', 1, type=int)
    subject = request.args.get('subject', '')
    location = request.args.get('location', '')

    query = TutorProfile.query.filter_by(status='approved')

    if subject:
        query = query.filter(TutorProfile.subjects.contains(subject))
    if location:
        query = query.filter(TutorProfile.location.contains(location))

    teachers = query.order_by(TutorProfile.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)

    return render_template('teachers.html', teachers=teachers,
                           subject=subject, location=location)


@bp.route('/teacher/<int:id>')
def teacher_detail(id):
    profile = TutorProfile.query.filter_by(id=id, status='approved').first_or_404()
    return render_template('teacher_detail.html', profile=profile)


# ───────────────── 家教大厅 ─────────────────

@bp.route('/orders')
def orders():
    page = request.args.get('page', 1, type=int)
    subject = request.args.get('subject', '')
    grade = request.args.get('grade', '')
    location = request.args.get('location', '')
    form_type = request.args.get('form', '')
    time_type = request.args.get('time', '')
    gender_pref = request.args.get('gender', '')
    teacher_type = request.args.get('teacher_type', '')
    sort = request.args.get('sort', 'latest')
    city = request.args.get('city', '')

    query = JobOrder.query.filter_by(status='open')

    if subject:
        query = query.filter_by(subject=subject)
    if grade:
        query = query.filter_by(grade=grade)
    if location:
        query = query.filter(JobOrder.location.contains(location))
    if city:
        query = query.filter(JobOrder.city.contains(city))
    if form_type:
        query = query.filter_by(form_type=form_type)
    if gender_pref:
        query = query.filter(
            (JobOrder.gender_pref == gender_pref) | 
            (JobOrder.gender_pref == '不限') |
            (JobOrder.gender_pref == '男女不限')
        )
    if teacher_type:
        query = query.filter(
            (JobOrder.teacher_type == teacher_type) | 
            (JobOrder.teacher_type == '不限')
        )
    if time_type == '周末':
        query = query.filter(JobOrder.schedule.contains('周末'))
    elif time_type == '周内':
        query = query.filter(~JobOrder.schedule.contains('周末'))

    if sort == 'latest':
        query = query.order_by(JobOrder.created_at.desc())
    else:
        query = query.order_by(JobOrder.created_at.desc())

    # 获取所有城市列表
    cities = db.session.query(JobOrder.city).distinct().filter(JobOrder.city != '').all()
    cities = [c[0] for c in cities if c[0]]

    orders = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('orders.html', orders=orders, 
                          subject=subject, grade=grade, location=location,
                          form_type=form_type, time_type=time_type,
                          gender_pref=gender_pref, teacher_type=teacher_type,
                          sort=sort, city=city, cities=cities)


@bp.route('/orders/matched')
def matched_orders():
    """智能匹配 - 根据筛选条件显示匹配订单（无需登录）"""
    page = request.args.get('page', 1, type=int)
    
    # 从URL参数获取筛选条件
    subjects = request.args.get('subjects', '').split(',')
    location = request.args.get('location', '')
    experience = request.args.get('experience', '3')  # 默认3年教龄
    
    query = JobOrder.query.filter_by(status='open')
    
    # 匹配科目
    if subjects and subjects[0]:
        subject_conditions = [JobOrder.subject.contains(s.strip()) for s in subjects if s.strip()]
        if subject_conditions:
            query = query.filter(db.or_(*subject_conditions))
    
    # 匹配地区
    if location:
        query = query.filter(
            db.or_(
                JobOrder.location.contains(location),
                JobOrder.city.contains(location)
            )
        )
    
    # 根据教龄匹配老师类型
    try:
        exp = int(experience)
    except:
        exp = 3
    
    is_full_time = exp >= 3
    if is_full_time:
        query = query.filter(
            db.or_(
                JobOrder.teacher_type == '不限',
                JobOrder.teacher_type == '专职'
            )
        )
    else:
        query = query.filter(
            db.or_(
                JobOrder.teacher_type == '不限',
                JobOrder.teacher_type == '在读学生'
            )
        )
    
    orders = query.order_by(JobOrder.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # 构建筛选信息
    filter_info = {
        'subjects': [s for s in subjects if s.strip()],
        'location': location,
        'experience': exp,
        'is_full_time': is_full_time
    }
    
    return render_template('orders.html', orders=orders, 
                          matched=True, filter_info=filter_info)


@bp.route('/order/<int:id>')
def order_detail(id):
    order = JobOrder.query.get_or_404(id)
    # 老师只能看到自己的抢单状态，家长看不到任何抢单详情
    my_app = None
    if current_user.is_authenticated and current_user.is_tutor():
        my_app = Application.query.filter_by(
            job_order_id=id, tutor_id=current_user.id).first()
    return render_template('order_detail.html', order=order, my_app=my_app)


# ───────────────── 家长发单 ─────────────────

@bp.route('/order/new', methods=['GET', 'POST'])
@login_required
def new_order():
    if not current_user.is_parent():
        flash('只有家长可以发布家教需求', 'warning')
        return redirect(url_for('main.index'))

    form = JobOrderForm()
    if form.validate_on_submit():
        order = JobOrder(
            parent_id=current_user.id,
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
            contact_phone=form.contact_phone.data
        )
        db.session.add(order)
        db.session.commit()
        flash('需求发布成功！', 'success')
        return redirect(url_for('main.order_detail', id=order.id))

    return render_template('new_order.html', form=form)


# ───────────────── 老师抢单（极简流程）─────────────────

@bp.route('/order/<int:id>/apply', methods=['GET', 'POST'])
@login_required
def apply_order(id):
    order = JobOrder.query.get_or_404(id)

    # 检查老师身份与认证状态
    if not current_user.is_tutor():
        flash('只有老师可以抢单', 'warning')
        return redirect(url_for('main.order_detail', id=id))

    if not current_user.tutor_profile or current_user.tutor_profile.status != 'approved':
        flash('您的账号尚未通过审核，暂不能抢单。请等待管理员审核通过后再试。', 'warning')
        return redirect(url_for('main.order_detail', id=id))

    if order.status != 'open':
        flash('该需求已关闭，无法抢单', 'warning')
        return redirect(url_for('main.order_detail', id=id))

    # 检查是否重复投递
    existing = Application.query.filter_by(
        job_order_id=id, tutor_id=current_user.id).first()
    if existing:
        flash('您已对该需求提交过申请，请勿重复提交。', 'info')
        return redirect(url_for('main.order_detail', id=id))

    form = ApplicationForm()
    if form.validate_on_submit():
        app = Application(
            job_order_id=id,
            tutor_id=current_user.id,
            tutor_profile_id=current_user.tutor_profile.id,
            message=form.message.data,
            proposed_rate=form.proposed_rate.data,
            status='pending'  # 待管理员线下处理
        )
        db.session.add(app)
        db.session.commit()
        flash('申请成功！请保持手机畅通，管理员将致电与您确认匹配事宜。', 'success')
        return redirect(url_for('main.my_applications'))

    return render_template('apply_order.html', form=form, order=order)


# ───────────────── 我的需求（家长） ─────────────────

@bp.route('/my-orders')
@login_required
def my_orders():
    if not current_user.is_parent():
        flash('只有家长可以查看我的需求', 'warning')
        return redirect(url_for('main.index'))

    orders = JobOrder.query.filter_by(parent_id=current_user.id).order_by(
        JobOrder.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)


# ───────────────── 我的抢单（教师） ─────────────────

@bp.route('/my-applications')
@login_required
def my_applications():
    if not current_user.is_tutor():
        flash('只有老师可以查看抢单记录', 'warning')
        return redirect(url_for('main.index'))

    apps = Application.query.filter_by(tutor_id=current_user.id).order_by(
        Application.created_at.desc()).all()
    return render_template('my_applications.html', applications=apps)


# ───────────────── 账号设置 ─────────────────

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    # 预填教师简历
    if current_user.is_tutor() and current_user.tutor_profile:
        p = current_user.tutor_profile
        if request.method == 'GET':
            form.real_name.data = p.real_name
            form.phone.data = p.phone
            form.education.data = p.education
            form.experience.data = p.experience
            form.subjects.data = p.subjects
            form.hourly_rate.data = p.hourly_rate
            form.location.data = p.location

    if form.validate_on_submit():
        if current_user.is_tutor() and current_user.tutor_profile:
            p = current_user.tutor_profile
            p.real_name = form.real_name.data
            p.phone = form.phone.data
            p.education = form.education.data
            p.experience = form.experience.data
            p.subjects = form.subjects.data
            p.hourly_rate = form.hourly_rate.data
            p.location = form.location.data
            db.session.commit()
            flash('个人信息更新成功！', 'success')
        else:
            flash('您暂无可编辑的个人信息', 'info')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', form=form)


# ───────────────── 我的页面 ─────────────────

@bp.route('/mine')
@login_required
def mine():
    """我的页面 - 个人中心主页"""
    profile = None
    resume_data = None
    
    if current_user.is_tutor():
        profile = current_user.tutor_profile
        if profile:
            profile.check_complete()
            resume_data = profile.generate_resume()
    
    return render_template('mine.html', profile=profile, resume_data=resume_data)


@bp.route('/mine/edit', methods=['GET', 'POST'])
@login_required
def mine_edit():
    """编辑教师资料"""
    if not current_user.is_tutor():
        flash('仅教师可访问此页面', 'warning')
        return redirect(url_for('main.mine'))
    
    profile = current_user.tutor_profile
    if not profile:
        profile = TutorProfile(user_id=current_user.id, real_name=current_user.username)
        db.session.add(profile)
        db.session.commit()
    
    form = TutorProfileForm(obj=profile)
    
    if form.validate_on_submit():
        form.populate_obj(profile)
        profile.check_complete()
        db.session.commit()
        flash('资料更新成功！', 'success')
        return redirect(url_for('main.mine'))
    
    return render_template('mine_edit.html', form=form, profile=profile)


@bp.route('/mine/resume')
@login_required
def mine_resume():
    """预览简历"""
    if not current_user.is_tutor():
        flash('仅教师可访问此页面', 'warning')
        return redirect(url_for('main.mine'))
    
    profile = current_user.tutor_profile
    if not profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('main.mine_edit'))
    
    resume_data = profile.generate_resume()
    certificates = profile.certificates.all()
    
    return render_template('mine_resume.html', profile=profile, 
                          resume_data=resume_data, certificates=certificates)


@bp.route('/mine/certificate', methods=['GET', 'POST'])
@login_required
def mine_certificate():
    """上传证书（单图）"""
    if not current_user.is_tutor():
        flash('仅教师可访问此页面', 'warning')
        return redirect(url_for('main.mine'))
    
    profile = current_user.tutor_profile
    if not profile:
        flash('请先完善个人资料', 'warning')
        return redirect(url_for('main.mine_edit'))
    
    form = CertificateForm()
    
    if form.validate_on_submit():
        cert = Certificate(
            tutor_profile_id=profile.id,
            cert_type=form.cert_type.data,
            cert_name=form.cert_name.data
        )
        
        # 保存单张图片
        file = form.cert_image.data
        if file and file.filename:
            filename = f'cert_{profile.id}_{file.filename}'
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            cert.image_path = f'uploads/certificates/{filename}'
        
        db.session.add(cert)
        db.session.commit()
        flash('证书上传成功！', 'success')
        return redirect(url_for('main.mine_certificate'))
    
    certificates = profile.certificates.all()
    return render_template('mine_certificate.html', form=form, 
                          profile=profile, certificates=certificates)


@bp.route('/mine/certificate/<int:id>/delete', methods=['POST'])
@login_required
def delete_certificate(id):
    """删除证书"""
    cert = Certificate.query.get_or_404(id)
    if cert.tutor_profile_id != current_user.tutor_profile.id:
        abort(403)
    
    # 删除图片文件
    if cert.image_path:
        filepath = os.path.join(current_app.static_folder, cert.image_path)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(cert)
    db.session.commit()
    flash('证书已删除', 'success')
    return redirect(url_for('main.mine_certificate'))
