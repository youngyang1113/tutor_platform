from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """用户表：统一账号，角色区分"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='parent')  # admin / tutor / parent
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    job_orders = db.relationship('JobOrder', backref='parent', lazy='dynamic',
                                 foreign_keys='JobOrder.parent_id')
    applications = db.relationship('Application', backref='tutor', lazy='dynamic',
                                   foreign_keys='Application.tutor_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_tutor(self):
        return self.role == 'tutor'

    def is_parent(self):
        return self.role == 'parent'

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class TutorProfile(db.Model):
    """教师简历表：与 User 一对一"""
    __tablename__ = 'tutor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    id_card = db.Column(db.String(18))
    avatar = db.Column(db.String(200))
    gender = db.Column(db.String(10))  # 男/女
    introduction = db.Column(db.Text)  # 自我介绍
    teaching_style = db.Column(db.Text)  # 教学特色
    achievements = db.Column(db.Text)  # 教学成果
    education = db.Column(db.String(100))
    school = db.Column(db.String(100))  # 毕业院校
    major = db.Column(db.String(100))  # 专业
    experience = db.Column(db.Integer, default=0)
    subjects = db.Column(db.String(200))       # 逗号分隔
    hourly_rate = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending / approved / rejected
    is_profile_complete = db.Column(db.Boolean, default=False)  # 资料是否完善
    is_platform_certified = db.Column(db.Boolean, default=False)  # 平台认证
    is_verified = db.Column(db.Boolean, default=False)  # 资质已验
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('tutor_profile', uselist=False, lazy='joined'))
    applications = db.relationship('Application', backref='tutor_profile', lazy='dynamic',
                                   foreign_keys='Application.tutor_profile_id')
    certificates = db.relationship('Certificate', backref='tutor_profile', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def get_subjects_list(self):
        return [s.strip() for s in self.subjects.split(',')] if self.subjects else []

    def check_complete(self):
        """检查资料是否完善"""
        required_fields = [self.real_name, self.phone, self.education, self.subjects, self.location]
        self.is_profile_complete = all(required_fields)
        return self.is_profile_complete

    def generate_resume(self):
        """生成简历数据"""
        resume = {
            'name': self.real_name,
            'gender': self.gender,
            'phone': self.phone,
            'education': self.education,
            'school': self.school,
            'major': self.major,
            'experience': self.experience,
            'subjects': self.get_subjects_list(),
            'hourly_rate': self.hourly_rate,
            'location': self.location,
            'introduction': self.introduction,
            'teaching_style': self.teaching_style,
            'achievements': self.achievements,
            'certificates': [c.to_dict() for c in self.certificates.all()],
        }
        return resume

    def __repr__(self):
        return f'<TutorProfile {self.real_name} ({self.status})>'


class Certificate(db.Model):
    """证书表（单图）"""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    tutor_profile_id = db.Column(db.Integer, db.ForeignKey('tutor_profiles.id'), nullable=False)
    cert_type = db.Column(db.String(50), nullable=False)  # 证书类型
    cert_name = db.Column(db.String(100), nullable=False)  # 证书名称
    image_path = db.Column(db.String(200))  # 证书图片路径
    status = db.Column(db.String(20), default='pending')  # pending / approved / rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'cert_type': self.cert_type,
            'cert_name': self.cert_name,
            'image_path': self.image_path,
            'status': self.status,
        }

    def __repr__(self):
        return f'<Certificate {self.cert_name} ({self.status})>'


class JobOrder(db.Model):
    """家教需求订单：家长发布"""
    __tablename__ = 'job_orders'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    subject = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), default='')
    budget = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer, default=2)
    frequency = db.Column(db.String(50), default='1次/周')
    form_type = db.Column(db.String(20), default='上门')      # 上门/网课
    gender_pref = db.Column(db.String(20), default='不限')    # 男老师/女老师/不限
    teacher_type = db.Column(db.String(20), default='不限')   # 在读学生/专职/不限
    contact_phone = db.Column(db.String(20))   # 家长联系方式，前台隐藏
    status = db.Column(db.String(20), default='open')  # open / filled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    applications = db.relationship('Application', backref='job_order', lazy='dynamic',
                                   cascade='all, delete-orphan')

    def applications_count(self):
        return self.applications.count()

    def __repr__(self):
        return f'<JobOrder {self.id} ({self.status})>'


class Application(db.Model):
    """抢单表：教师对订单的申请"""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_order_id = db.Column(db.Integer, db.ForeignKey('job_orders.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tutor_profile_id = db.Column(db.Integer, db.ForeignKey('tutor_profiles.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)  # 自我推荐
    proposed_rate = db.Column(db.Integer)  # 报价
    status = db.Column(db.String(20), default='pending')  # pending(待处理) / success(撮合成功) / failed(未匹配)
    admin_note = db.Column(db.Text)  # 管理员跟进备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 唯一约束：同一老师对同一需求只能抢单一次
    __table_args__ = (
        db.UniqueConstraint('job_order_id', 'tutor_id', name='uq_job_tutor'),
    )

    def __repr__(self):
        return f'<Application job={self.job_order_id} tutor={self.tutor_id} ({self.status})>'
