from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, \
    IntegerField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, \
    NumberRange, Optional, ValidationError
from app.models import User


# ───────────────── 认证表单 ─────────────────

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class TutorRegisterForm(FlaskForm):
    """简化版教师注册 - 只需基本信息"""
    username = StringField('用户名', validators=[
        DataRequired(), Length(min=3, max=20, message='用户名长度3-20个字符')])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(min=6, message='密码至少6个字符')])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(), EqualTo('password', message='两次密码不一致')])
    real_name = StringField('真实姓名', validators=[DataRequired()])
    phone = StringField('手机号', validators=[
        DataRequired(), Length(min=11, max=11, message='请输入11位手机号')])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')


class TutorProfileForm(FlaskForm):
    """教师资料编辑表单 - 完善个人信息"""
    real_name = StringField('真实姓名', validators=[DataRequired()])
    phone = StringField('手机号', validators=[
        DataRequired(), Length(min=11, max=11, message='请输入11位手机号')])
    id_card = StringField('身份证号', validators=[
        Optional(), Length(min=18, max=18, message='请输入18位身份证号')])
    gender = SelectField('性别', choices=[
        ('', '请选择'), ('男', '男'), ('女', '女')])
    education = SelectField('最高学历', choices=[
        ('', '请选择'), ('高中', '高中'), ('大专', '大专'), 
        ('本科', '本科'), ('硕士', '硕士'), ('博士', '博士')])
    school = StringField('毕业院校', validators=[Optional()])
    major = StringField('专业', validators=[Optional()])
    experience = IntegerField('教龄（年）', validators=[
        Optional(), NumberRange(min=0, max=50)])
    subjects = StringField('擅长科目（逗号分隔，如：数学,物理）', validators=[DataRequired()])
    hourly_rate = IntegerField('期望时薪（元/小时）', validators=[
        Optional(), NumberRange(min=1)])
    location = StringField('所在地区', validators=[DataRequired()])
    introduction = TextAreaField('自我介绍', validators=[
        Optional(), Length(max=1000)], 
        description='介绍您的教学经历、教学风格、教学成果等')
    teaching_style = TextAreaField('教学特色', validators=[
        Optional(), Length(max=500)],
        description='描述您的教学方法和特点')
    achievements = TextAreaField('教学成果', validators=[
        Optional(), Length(max=500)],
        description='如：学生成绩提升案例、获奖经历等')
    submit = SubmitField('保存资料')


class CertificateForm(FlaskForm):
    """证书上传表单（单图）"""
    cert_type = SelectField('证书类型', choices=[
        ('教师资格证', '教师资格证'), 
        ('学历证书', '学历证书'),
        ('学位证书', '学位证书'),
        ('普通话证书', '普通话证书'),
        ('英语等级证书', '英语等级证书'),
        ('专业技能证书', '专业技能证书'),
        ('获奖证书', '获奖证书'),
        ('其他', '其他')])
    cert_name = StringField('证书名称', validators=[DataRequired()])
    cert_image = FileField('上传证书图片', validators=[DataRequired()])
    submit = SubmitField('上传证书')


class ParentRegisterForm(FlaskForm):
    """家长注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(), Length(min=3, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(), EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')


# ───────────────── 业务表单 ─────────────────

class JobOrderForm(FlaskForm):
    """发布需求表单"""
    subject = SelectField('科目', validators=[DataRequired()], choices=[
        ('数学', '数学'), ('语文', '语文'), ('英语', '英语'),
        ('物理', '物理'), ('化学', '化学'), ('生物', '生物'),
        ('历史', '历史'), ('地理', '地理'), ('政治', '政治'),
        ('全科', '全科'), ('体育', '体育'), ('音乐', '音乐'),
        ('绘画', '绘画'), ('编程', '编程'), ('其他', '其他')])
    grade = SelectField('年级', validators=[DataRequired()], choices=[
        ('小学', '小学'), ('初一', '初一'), ('初二', '初二'), ('初三', '初三'),
        ('高一', '高一'), ('高二', '高二'), ('高三', '高三'),
        ('大学', '大学'), ('其他', '其他')])
    description = TextAreaField('需求描述', validators=[
        DataRequired(), Length(min=10, max=500, message='描述10-500字')])
    location = StringField('上课地点', validators=[DataRequired()])
    city = StringField('城市', default='')
    budget = IntegerField('预算（元/小时）', validators=[
        DataRequired(), NumberRange(min=1)])
    schedule = StringField('时间安排', validators=[DataRequired()])
    duration = IntegerField('每次课时（小时）', validators=[
        DataRequired(), NumberRange(min=1, max=8)], default=2)
    frequency = SelectField('频次', choices=[
        ('1次/周', '1次/周'), ('2次/周', '2次/周'), ('3次/周', '3次/周'),
        ('每天', '每天'), ('短期', '短期')])
    form_type = SelectField('授课形式', choices=[
        ('上门', '上门'), ('网课', '网课')])
    gender_pref = SelectField('老师性别要求', choices=[
        ('不限', '不限'), ('男老师', '男老师'), ('女老师', '女老师'),
        ('男老师优先', '男老师优先'), ('女老师优先', '女老师优先')])
    teacher_type = SelectField('老师类型', choices=[
        ('不限', '不限'), ('在读学生', '在读学生'), ('专职', '专职')])
    contact_phone = StringField('联系电话（仅管理员可见）', validators=[
        Optional(), Length(min=11, max=11)])
    submit = SubmitField('发布需求')


class ApplicationForm(FlaskForm):
    """抢单表单"""
    message = TextAreaField('自我推荐', validators=[
        DataRequired(), Length(min=10, max=300, message='10-300字')])
    proposed_rate = IntegerField('报价（元/小时，可选）', validators=[
        Optional(), NumberRange(min=1)])
    submit = SubmitField('提交抢单')


class ProfileForm(FlaskForm):
    """账号设置表单"""
    real_name = StringField('真实姓名')
    phone = StringField('手机号')
    education = StringField('学历')
    experience = IntegerField('教龄', validators=[Optional(), NumberRange(min=0)])
    subjects = StringField('擅长科目')
    hourly_rate = IntegerField('时薪', validators=[Optional(), NumberRange(min=1)])
    location = StringField('所在地区')
    submit = SubmitField('保存修改')
