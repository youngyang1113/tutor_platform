from flask import redirect, url_for, flash, request
from flask_login import current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from app import db
from app.models import User, TutorProfile, JobOrder, Application


# ───────────────── 安全基类 ─────────────────

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('您没有权限访问管理后台', 'danger')
        return redirect(url_for('auth.login'))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin():
            return redirect(url_for('auth.login'))
        return super().index()

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('您没有权限访问管理后台', 'danger')
        return redirect(url_for('auth.login'))


# ───────────────── 用户管理 ─────────────────

class UserAdmin(SecureModelView):
    column_list = ['id', 'username', 'email', 'role', 'is_active', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['role', 'is_active', 'created_at']
    column_labels = {
        'id': 'ID', 'username': '用户名', 'email': '邮箱',
        'role': '角色', 'is_active': '激活', 'created_at': '注册时间'
    }
    form_columns = ['username', 'email', 'role', 'is_active']

    def delete_model(self, model):
        if model.role == 'admin':
            flash('不能删除管理员账号', 'error')
            return False
        return super().delete_model(model)


# ───────────────── 教师简历管理（含行内审核） ─────────────────

class TutorProfileAdmin(SecureModelView):
    column_list = ['id', 'user', 'real_name', 'phone', 'education',
                   'subjects', 'hourly_rate', 'location', 'status', 
                   'is_platform_certified', 'is_verified', 'created_at']
    column_searchable_list = ['real_name', 'phone', 'subjects']
    column_filters = ['status', 'is_platform_certified', 'is_verified', 'education', 'created_at']
    column_editable_list = ['status', 'is_platform_certified', 'is_verified']  # 行内编辑
    column_labels = {
        'id': 'ID', 'user': '账号', 'real_name': '真实姓名',
        'phone': '手机号', 'id_card': '身份证', 'education': '学历',
        'experience': '教龄', 'subjects': '科目', 'hourly_rate': '时薪',
        'location': '地区', 'status': '审核状态', 'introduction': '简介',
        'is_platform_certified': '平台认证', 'is_verified': '资质已验',
        'created_at': '提交时间'
    }
    form_columns = ['user', 'real_name', 'phone', 'id_card', 'gender', 'education',
                    'school', 'major', 'experience', 'subjects', 'hourly_rate', 
                    'location', 'introduction', 'teaching_style', 'achievements',
                    'status', 'is_platform_certified', 'is_verified', 'avatar']
    column_formatters = {
        'phone': lambda v, c, m, p: m.phone[:3] + '****' + m.phone[7:]
                    if m.phone and len(m.phone) == 11 else (m.phone or ''),
        'id_card': lambda v, c, m, p: m.id_card[:4] + '**********' + m.id_card[14:]
                    if m.id_card and len(m.id_card) == 18 else (m.id_card or ''),
        'is_platform_certified': lambda v, c, m, p: '✅' if m.is_platform_certified else '❌',
        'is_verified': lambda v, c, m, p: '✅' if m.is_verified else '❌'
    }


# ───────────────── 需求管理 ─────────────────

class JobOrderAdmin(SecureModelView):
    column_list = ['id', 'parent', 'subject', 'grade', 'location',
                   'budget', 'status', 'created_at']
    column_searchable_list = ['subject', 'grade', 'location']
    column_filters = ['subject', 'grade', 'status', 'created_at']
    column_labels = {
        'id': 'ID', 'parent': '家长', 'subject': '科目', 'grade': '年级',
        'location': '地点', 'city': '城市', 'budget': '预算', 'status': '状态',
        'description': '描述', 'schedule': '时间', 'duration': '课时',
        'frequency': '频率', 'form_type': '授课方式', 'gender_pref': '性别偏好',
        'teacher_type': '老师类型', 'contact_phone': '家长电话', 'created_at': '发布时间'
    }
    form_columns = ['subject', 'grade', 'description', 'location', 'city',
                    'budget', 'schedule', 'duration', 'frequency', 'form_type',
                    'gender_pref', 'teacher_type', 'contact_phone', 'status']
    column_formatters = {
        'contact_phone': lambda v, c, m, p: m.contact_phone[:3] + '****' + m.contact_phone[7:]
                         if m.contact_phone and len(m.contact_phone) == 11 else (m.contact_phone or '')
    }


# ───────────────── 抢单管理（线索管理）─────────────────

class ApplicationAdmin(SecureModelView):
    column_list = ['id', 'job_order_id', 'parent_phone', 'tutor_real_name',
                   'tutor_phone', 'proposed_rate', 'status', 'admin_note', 'created_at']
    column_searchable_list = ['tutor_profile.real_name', 'tutor_profile.phone']
    column_filters = ['status', 'created_at']
    column_editable_list = ['status', 'admin_note']
    column_labels = {
        'id': 'ID', 'job_order_id': '需求编号', 'parent_phone': '家长手机',
        'tutor_real_name': '老师姓名', 'tutor_phone': '老师手机',
        'tutor': '老师账号', 'tutor_profile': '教师简历',
        'proposed_rate': '报价(元/h)', 'message': '留言',
        'status': '状态', 'admin_note': '跟进备注',
        'created_at': '抢单时间'
    }
    column_formatters = {
        'parent_phone': lambda v, c, m, p: (
            m.job_order.contact_phone[:3] + '****' + m.job_order.contact_phone[7:]
            if m.job_order and m.job_order.contact_phone
            and len(m.job_order.contact_phone) == 11
            else (m.job_order.contact_phone if m.job_order else '')
        ),
        'tutor_real_name': lambda v, c, m, p: (
            m.tutor_profile.real_name if m.tutor_profile else ''
        ),
        'tutor_phone': lambda v, c, m, p: (
            m.tutor_profile.phone[:3] + '****' + m.tutor_profile.phone[7:]
            if m.tutor_profile and m.tutor_profile.phone
            and len(m.tutor_profile.phone) == 11
            else (m.tutor_profile.phone if m.tutor_profile else '')
        ),
    }
    form_columns = ['job_order', 'tutor', 'tutor_profile', 'message',
                    'proposed_rate', 'status', 'admin_note']
    column_choices = {
        'status': [
            ('pending', '待处理'),
            ('success', '撮合成功'),
            ('failed', '未匹配'),
        ]
    }


# ───────────────── 初始化 ─────────────────

def init_admin(app):
    admin = Admin(
        app,
        name='渊博家教 · 管理后台',
        template_mode='bootstrap4',
        index_view=MyAdminIndexView()
    )
    admin.add_view(UserAdmin(User, db.session, name='用户管理'))
    admin.add_view(TutorProfileAdmin(TutorProfile, db.session, name='教师审核'))
    admin.add_view(JobOrderAdmin(JobOrder, db.session, name='需求管理'))
    admin.add_view(ApplicationAdmin(Application, db.session, name='抢单管理'))
