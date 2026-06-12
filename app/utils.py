from app import db
from app.models import User
from config import Config


def init_admin_user():
    """初始化管理员账号"""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username=Config.ADMIN_USERNAME,
            email=Config.ADMIN_EMAIL,
            role='admin',
            is_active=True
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f'管理员账号已创建: {Config.ADMIN_USERNAME}')
