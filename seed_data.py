# -*- coding: utf-8 -*-
"""
渊博家教平台 - 测试数据生成脚本
运行方式：python seed_data.py
功能：清空旧数据，生成管理员、30位教师、30个家教订单
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from random import sample, randint
from app import create_app, db
from app.models import User, TutorProfile, JobOrder, Application

app = create_app()

with app.app_context():
    # ───────── 删除旧表并重建 ─────────
    db.drop_all()
    db.create_all()
    print('✓ 数据库表已重建')

    # ───────── 1. 管理员账号 ─────────
    admin = User(username='admin', email='admin@yuanbo.com', role='admin', is_active=True)
    admin.set_password('admin123')
    db.session.add(admin)
    print('✓ 管理员账号创建完成 (admin / admin123)')

    # ───────── 2. 30位通过审核的教师 ─────────
    teachers_data = [
        {'username':'tutor01', 'email':'tutor01@test.com', 'real_name':'刘洋', 'phone':'13800001001', 'id_card':'110101199203150011', 'education':'北京大学硕士', 'experience':8, 'subjects':'数学,物理', 'hourly_rate':280, 'location':'海淀区', 'introduction':'8年教学经验，擅长高考数学和物理竞赛辅导，曾培养多名学生考入985高校。'},
        {'username':'tutor02', 'email':'tutor02@test.com', 'real_name':'王鑫', 'phone':'13800001002', 'id_card':'110101199506200022', 'education':'清华大学本科', 'experience':5, 'subjects':'英语,语文', 'hourly_rate':260, 'location':'朝阳区', 'introduction':'英语专八，雅思8分。5年中小学英语和语文教学经验。'},
        {'username':'tutor03', 'email':'tutor03@test.com', 'real_name':'张梅', 'phone':'13800001003', 'id_card':'110101199008100033', 'education':'北京师范大学博士', 'experience':10, 'subjects':'化学,生物', 'hourly_rate':320, 'location':'西城区', 'introduction':'北师大博士，10年高中化学和生物教学经验。'},
        {'username':'tutor04', 'email':'tutor04@test.com', 'real_name':'陈伟', 'phone':'13800001004', 'id_card':'110101199312050044', 'education':'中国人民大学硕士', 'experience':6, 'subjects':'历史,地理,政治', 'hourly_rate':240, 'location':'东城区', 'introduction':'文科全能型教师，6年教学经验。擅长文综答题技巧。'},
        {'username':'tutor05', 'email':'tutor05@test.com', 'real_name':'赵磊', 'phone':'13800001005', 'id_card':'110101199801180055', 'education':'北京航空航天大学本科', 'experience':3, 'subjects':'数学,物理,化学', 'hourly_rate':200, 'location':'昌平区', 'introduction':'年轻有活力的理工科教师，3年教学经验。'},
        {'username':'tutor06', 'email':'tutor06@test.com', 'real_name':'孙丽', 'phone':'13800001006', 'id_card':'110101199106220066', 'education':'首都师范大学硕士', 'experience':7, 'subjects':'语文,英语', 'hourly_rate':250, 'location':'丰台区', 'introduction':'7年中小学语文和英语教学经验，注重阅读和写作能力培养。'},
        {'username':'tutor07', 'email':'tutor07@test.com', 'real_name':'黄海', 'phone':'13800001007', 'id_card':'110101199405030077', 'education':'北京理工大学硕士', 'experience':4, 'subjects':'物理,数学', 'hourly_rate':220, 'location':'石景山区', 'introduction':'4年教学经验，擅长初中和高中物理、数学。'},
        {'username':'tutor08', 'email':'tutor08@test.com', 'real_name':'李雪', 'phone':'13800001008', 'id_card':'110101199703120088', 'education':'北京外国语大学本科', 'experience':4, 'subjects':'英语', 'hourly_rate':230, 'location':'海淀区', 'introduction':'北外英语专业，专八优秀。4年少儿英语教学经验。'},
        {'username':'tutor09', 'email':'tutor09@test.com', 'real_name':'吴东', 'phone':'13800001009', 'id_card':'110101199208150099', 'education':'北京师范大学硕士', 'experience':6, 'subjects':'数学', 'hourly_rate':270, 'location':'海淀区', 'introduction':'6年数学教学经验，专注于小学到高中数学辅导。'},
        {'username':'tutor10', 'email':'tutor10@test.com', 'real_name':'周燕', 'phone':'13800001010', 'id_card':'110101199601090100', 'education':'中央民族大学硕士', 'experience':3, 'subjects':'生物,化学', 'hourly_rate':190, 'location':'海淀区', 'introduction':'3年教学经验，擅长初高中生物和化学。'},
        {'username':'tutor11', 'email':'tutor11@test.com', 'real_name':'杨帆', 'phone':'13800001011', 'id_card':'110101199305150011', 'education':'复旦大学硕士', 'experience':5, 'subjects':'英语', 'hourly_rate':290, 'location':'海淀区', 'introduction':'海归硕士，托福112分。5年出国考试培训经验。'},
        {'username':'tutor12', 'email':'tutor12@test.com', 'real_name':'刘娜', 'phone':'13800001012', 'id_card':'110101199408200022', 'education':'中央美术学院本科', 'experience':6, 'subjects':'绘画,书法', 'hourly_rate':260, 'location':'朝阳区', 'introduction':'央美毕业，6年美术教学经验。擅长素描、水彩、国画。'},
        {'username':'tutor13', 'email':'tutor13@test.com', 'real_name':'张伟', 'phone':'13800001013', 'id_card':'110101199109250033', 'education':'北京体育大学硕士', 'experience':7, 'subjects':'体育', 'hourly_rate':200, 'location':'丰台区', 'introduction':'国家二级运动员，7年体育教学经验。'},
        {'username':'tutor14', 'email':'tutor14@test.com', 'real_name':'王丽', 'phone':'13800001014', 'id_card':'110101199602140044', 'education':'中国音乐学院本科', 'experience':5, 'subjects':'音乐,钢琴', 'hourly_rate':300, 'location':'西城区', 'introduction':'中央音乐学院考级优秀辅导教师，5年钢琴教学经验。'},
        {'username':'tutor15', 'email':'tutor15@test.com', 'real_name':'李强', 'phone':'13800001015', 'id_card':'110101199207300055', 'education':'北京大学博士', 'experience':9, 'subjects':'数学,物理', 'hourly_rate':350, 'location':'海淀区', 'introduction':'北大博士，9年教学经验。曾获全国数学奥林匹克竞赛金牌。'},
        {'username':'tutor16', 'email':'tutor16@test.com', 'real_name':'陈雪', 'phone':'13800001016', 'id_card':'110101199504180066', 'education':'北京师范大学硕士', 'experience':4, 'subjects':'语文', 'hourly_rate':240, 'location':'东城区', 'introduction':'北师大中文系硕士，4年语文教学经验。'},
        {'username':'tutor17', 'email':'tutor17@test.com', 'real_name':'孙鹏', 'phone':'13800001017', 'id_card':'110101199311080077', 'education':'浙江大学本科', 'experience':5, 'subjects':'编程', 'hourly_rate':280, 'location':'海淀区', 'introduction':'前大厂程序员，5年编程教学经验。擅长Python、C++。'},
        {'username':'tutor18', 'email':'tutor18@test.com', 'real_name':'赵燕', 'phone':'13800001018', 'id_card':'110101199806120088', 'education':'中国人民大学硕士', 'experience':3, 'subjects':'政治,历史', 'hourly_rate':210, 'location':'海淀区', 'introduction':'人大法学硕士，3年文科教学经验。'},
        {'username':'tutor19', 'email':'tutor19@test.com', 'real_name':'王军', 'phone':'13800001019', 'id_card':'110101199005220099', 'education':'清华大学博士', 'experience':12, 'subjects':'物理', 'hourly_rate':380, 'location':'海淀区', 'introduction':'清华博士，12年高中物理教学经验。'},
        {'username':'tutor20', 'email':'tutor20@test.com', 'real_name':'李梅', 'phone':'13800001020', 'id_card':'110101199708150100', 'education':'首都师范大学本科', 'experience':4, 'subjects':'数学,英语', 'hourly_rate':220, 'location':'通州区', 'introduction':'4年小学全科辅导经验，擅长幼小衔接。'},
        {'username':'tutor21', 'email':'tutor21@test.com', 'real_name':'郑浩', 'phone':'13800001021', 'id_card':'110101199104250011', 'education':'武汉大学硕士', 'experience':6, 'subjects':'数学', 'hourly_rate':260, 'location':'朝阳区', 'introduction':'武大数学系硕士，6年高中数学教学经验，善于总结解题方法。'},
        {'username':'tutor22', 'email':'tutor22@test.com', 'real_name':'林芳', 'phone':'13800001022', 'id_card':'110101199308160022', 'education':'北京语言大学本科', 'experience':5, 'subjects':'英语', 'hourly_rate':240, 'location':'海淀区', 'introduction':'英语专业八级，5年少儿英语和成人英语教学经验。'},
        {'username':'tutor23', 'email':'tutor23@test.com', 'real_name':'何明', 'phone':'13800001023', 'id_card':'110101199509270033', 'education':'中国政法大学硕士', 'experience':4, 'subjects':'政治,历史,地理', 'hourly_rate':230, 'location':'昌平区', 'introduction':'法大硕士，4年高中文科综合教学经验。'},
        {'username':'tutor24', 'email':'tutor24@test.com', 'real_name':'马琳', 'phone':'13800001024', 'id_card':'110101199702180044', 'education':'北京协和医学院博士', 'experience':3, 'subjects':'生物,化学', 'hourly_rate':310, 'location':'东城区', 'introduction':'协和博士，3年高中生物和化学教学经验。'},
        {'username':'tutor25', 'email':'tutor25@test.com', 'real_name':'高峰', 'phone':'13800001025', 'id_card':'110101199205090055', 'education':'同济大学本科', 'experience':7, 'subjects':'物理,数学', 'hourly_rate':250, 'location':'丰台区', 'introduction':'同济毕业，7年初高中物理和数学教学经验。'},
        {'username':'tutor26', 'email':'tutor26@test.com', 'real_name':'宋佳', 'phone':'13800001026', 'id_card':'110101199608300066', 'education':'上海音乐学院本科', 'experience':5, 'subjects':'钢琴,音乐', 'hourly_rate':320, 'location':'西城区', 'introduction':'上音毕业，5年钢琴教学经验，学生考级通过率98%。'},
        {'username':'tutor27', 'email':'tutor27@test.com', 'real_name':'谢斌', 'phone':'13800001027', 'id_card':'110101199406210077', 'education':'哈尔滨工业大学硕士', 'experience':5, 'subjects':'编程,数学', 'hourly_rate':270, 'location':'海淀区', 'introduction':'哈工大硕士，前华为工程师，5年编程和数学教学经验。'},
        {'username':'tutor28', 'email':'tutor28@test.com', 'real_name':'韩梅', 'phone':'13800001028', 'id_card':'110101199803120088', 'education':'华东师范大学硕士', 'experience':3, 'subjects':'语文,英语', 'hourly_rate':220, 'location':'朝阳区', 'introduction':'华师大硕士，3年语文和英语教学经验，注重素质教育。'},
        {'username':'tutor29', 'email':'tutor29@test.com', 'real_name':'罗强', 'phone':'13800001029', 'id_card':'110101199101030099', 'education':'北京体育大学硕士', 'experience':8, 'subjects':'体育', 'hourly_rate':210, 'location':'石景山区', 'introduction':'国家一级运动员，8年体育教学经验，擅长中考体育提分。'},
        {'username':'tutor30', 'email':'tutor30@test.com', 'real_name':'唐敏', 'phone':'13800001030', 'id_card':'110101199507140100', 'education':'中央民族大学硕士', 'experience':4, 'subjects':'英语,语文', 'hourly_rate':230, 'location':'通州区', 'introduction':'民大硕士，4年英语和语文教学经验，教学风格亲切。'},
    ]

    for td in teachers_data:
        u = User(username=td['username'], email=td['email'], role='tutor', is_active=True)
        u.set_password('123456')
        db.session.add(u)
        db.session.flush()

        profile = TutorProfile(
            user_id=u.id,
            real_name=td['real_name'],
            phone=td['phone'],
            id_card=td['id_card'],
            education=td['education'],
            experience=td['experience'],
            subjects=td['subjects'],
            hourly_rate=td['hourly_rate'],
            location=td['location'],
            introduction=td['introduction'],
            status='approved',
            is_profile_complete=True,
            is_platform_certified=True,
            is_verified=True,
        )
        db.session.add(profile)

    print('✓ 30位教师账号创建完成 (密码均为 123456)')

    # ───────── 3. 30个不同科目的家教订单 ─────────
    orders_data = [
        {'subject':'数学', 'grade':'高三', 'location':'海淀区中关村', 'city':'北京', 'budget':300, 'schedule':'周六上午 9:00-11:00', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001001', 'description':'孩子高三冲刺阶段，数学成绩在110分左右，目标140分。需要经验丰富的老师，重点突破导数、解析几何压轴题。'},
        {'subject':'英语', 'grade':'初二', 'location':'朝阳区望京', 'city':'北京', 'budget':220, 'schedule':'周日下午 2:00-4:00', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'女老师优先', 'teacher_type':'不限', 'contact_phone':'13900001002', 'description':'初二学生，英语基础薄弱，单词量不足，语法混乱。希望老师能系统补习，培养学习兴趣。'},
        {'subject':'物理', 'grade':'高二', 'location':'西城区西直门', 'city':'北京', 'budget':280, 'schedule':'工作日晚上 7:00-9:00', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'男老师优先', 'teacher_type':'专职', 'contact_phone':'13900001003', 'description':'高二学生，物理力学部分学得不好，电学还可以。希望老师帮忙梳理力学知识体系。'},
        {'subject':'化学', 'grade':'高三', 'location':'丰台区方庄', 'city':'北京', 'budget':260, 'schedule':'周六下午 3:00-5:00', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'女老师', 'teacher_type':'专职', 'contact_phone':'13900001004', 'description':'高三学生，化学有机化学部分比较薄弱，希望找一位有经验的女老师进行专项突破。'},
        {'subject':'语文', 'grade':'初三', 'location':'东城区东直门', 'city':'北京', 'budget':200, 'schedule':'周末上午 10:00-12:00', 'duration':2, 'frequency':'1次/周', 'form_type':'网课', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001005', 'description':'初三学生，阅读理解和作文是弱项。希望老师能指导文言文阅读技巧和议论文写作。'},
        {'subject':'数学', 'grade':'小学', 'location':'海淀区五道口', 'city':'北京', 'budget':180, 'schedule':'周三、周五下午', 'duration':1, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'女老师优先', 'teacher_type':'在读学生', 'contact_phone':'13900001006', 'description':'五年级学生，数学思维不错但计算粗心。希望老师帮忙培养良好的计算习惯。'},
        {'subject':'英语', 'grade':'高中', 'location':'朝阳区国贸', 'city':'北京', 'budget':300, 'schedule':'周六上午', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001007', 'description':'高三学生，英语成绩在110分左右，目标冲刺140分。需要提升阅读理解和完形填空。'},
        {'subject':'钢琴', 'grade':'小学', 'location':'西城区金融街', 'city':'北京', 'budget':350, 'schedule':'周末', 'duration':1, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'女老师优先', 'teacher_type':'不限', 'contact_phone':'13900001008', 'description':'8岁孩子，零基础学钢琴，希望能培养音乐兴趣，考取中央音乐学院等级考试。'},
        {'subject':'编程', 'grade':'初中', 'location':'海淀区西二旗', 'city':'北京', 'budget':280, 'schedule':'周末', 'duration':2, 'frequency':'1次/周', 'form_type':'网课', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001009', 'description':'初一学生，对编程感兴趣，想学习Python编程和信息学竞赛相关内容。'},
        {'subject':'全科', 'grade':'小学', 'location':'东城区崇文门', 'city':'北京', 'budget':200, 'schedule':'周一至周五晚上', 'duration':2, 'frequency':'5次/周', 'form_type':'上门', 'gender_pref':'女老师优先', 'teacher_type':'在读学生', 'contact_phone':'13900001010', 'description':'四年级学生，需要一位大学生陪读，辅导完成作业并预习复习功课。'},
        {'subject':'数学', 'grade':'初三', 'location':'朝阳区三里屯', 'city':'北京', 'budget':220, 'schedule':'周六下午', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001011', 'description':'初三学生，数学成绩中等，几何证明题经常丢分。希望老师帮助梳理几何解题思路。'},
        {'subject':'英语', 'grade':'小学', 'location':'海淀区上地', 'city':'北京', 'budget':180, 'schedule':'周二、周四下午', 'duration':1, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'女老师', 'teacher_type':'不限', 'contact_phone':'13900001012', 'description':'三年级学生，刚开始学英语，希望找一位有耐心的老师培养英语学习兴趣。'},
        {'subject':'物理', 'grade':'初中', 'location':'丰台区丽泽', 'city':'北京', 'budget':230, 'schedule':'周末', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001013', 'description':'初二学生，物理刚开始学，电学部分不太理解。希望老师用实验方式讲解。'},
        {'subject':'美术', 'grade':'小学', 'location':'西城区什刹海', 'city':'北京', 'budget':250, 'schedule':'周末', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001014', 'description':'10岁孩子，喜欢画画，想系统学习素描和水彩，为以后考艺术特长生做准备。'},
        {'subject':'数学', 'grade':'高一', 'location':'昌平区回龙观', 'city':'北京', 'budget':240, 'schedule':'周日下午', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001015', 'description':'高一学生，数学成绩下滑严重，从初中到高中的衔接不好。需要帮助补习。'},
        {'subject':'体育', 'grade':'初三', 'location':'朝阳区大望路', 'city':'北京', 'budget':200, 'schedule':'周末', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'男老师', 'teacher_type':'不限', 'contact_phone':'13900001016', 'description':'初三学生，中考体育成绩不理想，需要老师帮助制定训练计划。'},
        {'subject':'英语', 'grade':'高二', 'location':'海淀区学院路', 'city':'北京', 'budget':280, 'schedule':'工作日晚上', 'duration':2, 'frequency':'2次/周', 'form_type':'网课', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001017', 'description':'高二学生，准备出国留学，需要老师帮助备考雅思，目标分数7分。'},
        {'subject':'化学', 'grade':'初三', 'location':'东城区建国门', 'city':'北京', 'budget':210, 'schedule':'周六上午', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001018', 'description':'初三学生，化学方程式配平和计算题经常出错，需要帮助巩固基础。'},
        {'subject':'数学', 'grade':'小学', 'location':'通州区梨园', 'city':'北京', 'budget':160, 'schedule':'周末', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'在读学生', 'contact_phone':'13900001019', 'description':'六年级学生，准备小升初，需要系统复习小学数学知识。'},
        {'subject':'语文', 'grade':'高三', 'location':'海淀区清华园', 'city':'北京', 'budget':260, 'schedule':'周六下午', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001020', 'description':'高三学生，语文作文分数不稳定，希望帮助提升议论文写作水平。'},
        {'subject':'英语', 'grade':'初一', 'location':'朝阳区安贞', 'city':'北京', 'budget':200, 'schedule':'周末上午', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'女老师优先', 'teacher_type':'不限', 'contact_phone':'13900001021', 'description':'初一学生，英语发音不标准，口语表达能力弱。希望老师帮助纠正发音。'},
        {'subject':'数学', 'grade':'高二', 'location':'西城区德胜门', 'city':'北京', 'budget':270, 'schedule':'周六上午', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001022', 'description':'高二学生，数学概率统计部分学得不好，希望老师针对性辅导。'},
        {'subject':'物理', 'grade':'高三', 'location':'海淀区知春路', 'city':'北京', 'budget':300, 'schedule':'工作日晚上', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001023', 'description':'高三学生，物理电磁学部分薄弱，需要老师帮助突破高考物理难点。'},
        {'subject':'历史', 'grade':'高三', 'location':'东城区雍和宫', 'city':'北京', 'budget':250, 'schedule':'周日下午', 'duration':2, 'frequency':'1次/周', 'form_type':'网课', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001024', 'description':'高三文科生，历史时间线混乱，需要老师帮助梳理知识框架。'},
        {'subject':'生物', 'grade':'高二', 'location':'朝阳区双井', 'city':'北京', 'budget':240, 'schedule':'周六下午', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001025', 'description':'高二学生，生物遗传学部分理解困难，希望老师用通俗方式讲解。'},
        {'subject':'地理', 'grade':'高一', 'location':'丰台区草桥', 'city':'北京', 'budget':220, 'schedule':'周末', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001026', 'description':'高一学生，地理气候和地形部分学得不好，需要老师帮助理解。'},
        {'subject':'编程', 'grade':'小学', 'location':'海淀区中关村', 'city':'北京', 'budget':260, 'schedule':'周末', 'duration':2, 'frequency':'1次/周', 'form_type':'网课', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001027', 'description':'五年级学生，对Scratch和Python编程感兴趣，希望系统学习。'},
        {'subject':'语文', 'grade':'初一', 'location':'西城区月坛', 'city':'北京', 'budget':190, 'schedule':'周六上午', 'duration':2, 'frequency':'1次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001028', 'description':'初一学生，文言文阅读困难，希望老师帮助掌握文言文翻译技巧。'},
        {'subject':'数学', 'grade':'初二', 'location':'昌平区天通苑', 'city':'北京', 'budget':200, 'schedule':'周末', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'不限', 'contact_phone':'13900001029', 'description':'初二学生，数学函数部分理解困难，成绩下滑明显。需要针对性辅导。'},
        {'subject':'英语', 'grade':'初三', 'location':'东城区北新桥', 'city':'北京', 'budget':240, 'schedule':'周六下午', 'duration':2, 'frequency':'2次/周', 'form_type':'上门', 'gender_pref':'不限', 'teacher_type':'专职', 'contact_phone':'13900001030', 'description':'初三学生，中考英语冲刺，需要提升听力和写作能力。'},
    ]

    for od in orders_data:
        order = JobOrder(
            parent_id=None,
            subject=od['subject'],
            grade=od['grade'],
            description=od['description'],
            location=od['location'],
            city=od['city'],
            budget=od['budget'],
            schedule=od['schedule'],
            duration=od['duration'],
            frequency=od['frequency'],
            form_type=od['form_type'],
            gender_pref=od['gender_pref'],
            teacher_type=od['teacher_type'],
            contact_phone=od['contact_phone'],
            status='open',
        )
        db.session.add(order)

    db.session.commit()
    print('✓ 30个家教订单创建完成')

    # ───────── 4. 为订单生成抢单记录 ─────────
    tutors = TutorProfile.query.filter_by(status='approved').all()
    orders = JobOrder.query.all()

    for order in orders:
        chosen = sample(tutors, min(3, len(tutors)))
        for t in chosen:
            app = Application(
                job_order_id=order.id,
                tutor_id=t.user_id,
                tutor_profile_id=t.id,
                message=f'您好！我是{t.real_name}，{t.experience}年教学经验，擅长{t.subjects}。看到您的需求非常感兴趣，希望能有机会帮助孩子提升成绩！',
                proposed_rate=t.hourly_rate,
                status='pending',
            )
            db.session.add(app)

    db.session.commit()
    print('✓ 抢单记录创建完成')

    # ───────── 统计 ─────────
    print('\n' + '=' * 40)
    print('📊 数据统计：')
    print(f'   用户总数：{User.query.count()}')
    print(f'   管理员：{User.query.filter_by(role="admin").count()}')
    print(f'   教师（已审核）：{TutorProfile.query.filter_by(status="approved").count()}')
    print(f'   家教订单：{JobOrder.query.count()}')
    print(f'   抢单记录：{Application.query.count()}')
    print('=' * 40)
    print('\n✅ 测试数据生成完成！')
    print('📌 管理员登录：admin / admin123')
    print('📌 教师登录：tutor01 / 123456')
