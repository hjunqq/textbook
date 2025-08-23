#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask微服务架构完整示例
===============================================================================
展示Flask框架在企业级微服务场景中的应用实践，包括：
- RESTful API设计与实现
- 数据库集成与ORM操作
- 数据分析与科学计算集成
- 错误处理与日志管理
- 微服务架构模式
===============================================================================
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
import logging
import json
import redis
from functools import wraps
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

# Flask应用初始化和配置
app = Flask(__name__)

# 基础配置
app.config.update({
    'SECRET_KEY': 'your-secret-key-change-in-production',
    'SQLALCHEMY_DATABASE_URI': 'postgresql://user:password@localhost/enterprise_data',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    },
    'REDIS_URL': 'redis://localhost:6379/0',
    'JWT_EXPIRATION_DELTA': timedelta(hours=24),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB max file upload
})

# 扩展初始化
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/api/*": {"origins": "*"}})
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

# Redis连接
redis_client = redis.from_url(app.config['REDIS_URL'])

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# 数据模型定义
# ============================================================================

class User(db.Model):
    """用户模型 - 企业用户管理"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系定义
    data_entries = db.relationship('DataEntry', backref='user', lazy='dynamic')
    
    def set_password(self, password: str):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self) -> str:
        """生成JWT令牌"""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'role': self.role,
            'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'department': self.department,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class DataEntry(db.Model):
    """数据记录模型 - 企业数据管理"""
    __tablename__ = 'data_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)
    value = db.Column(db.Numeric(15, 6))
    unit = db.Column(db.String(20))
    measurement_time = db.Column(db.DateTime, nullable=False, index=True)
    location = db.Column(db.String(100))
    tags = db.Column(db.JSON)
    metadata = db.Column(db.JSON)
    quality_score = db.Column(db.Integer, default=100)
    is_validated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键关系
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'value': float(self.value) if self.value else None,
            'unit': self.unit,
            'measurement_time': self.measurement_time.isoformat() if self.measurement_time else None,
            'location': self.location,
            'tags': self.tags,
            'metadata': self.metadata,
            'quality_score': self.quality_score,
            'is_validated': self.is_validated,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 认证和授权装饰器
# ============================================================================

def token_required(f):
    """JWT令牌验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401
        
        try:
            # 移除 'Bearer ' 前缀
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
            
            if not current_user or not current_user.is_active:
                return jsonify({'error': '无效的用户'}), 401
            
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的令牌'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        if g.current_user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

# ============================================================================
# API路由定义
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password) or not user.is_active:
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成令牌
        token = user.generate_token()
        
        # 记录登录日志
        logger.info(f"用户 {username} 成功登录")
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"登录错误: {str(e)}")
        return jsonify({'error': '登录处理失败'}), 500

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        department = data.get('department', '通用部门')
        
        if not all([username, email, password]):
            return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            department=department,
            role='user'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"新用户注册: {username}")
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"注册错误: {str(e)}")
        return jsonify({'error': '注册处理失败'}), 500

@app.route('/api/data', methods=['GET'])
@token_required
def get_data_entries():
    """获取数据记录列表"""
    try:
        # 解析查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        category = request.args.get('category')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        search = request.args.get('search')
        
        # 构建查询
        query = DataEntry.query
        
        # 非管理员只能查看自己的数据
        if g.current_user.role != 'admin':
            query = query.filter_by(user_id=g.current_user.id)
        
        # 应用过滤条件
        if category:
            query = query.filter(DataEntry.category == category)
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(DataEntry.measurement_time >= start_dt)
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(DataEntry.measurement_time <= end_dt)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    DataEntry.title.ilike(search_pattern),
                    DataEntry.description.ilike(search_pattern),
                    DataEntry.location.ilike(search_pattern)
                )
            )
        
        # 执行分页查询
        pagination = query.order_by(DataEntry.measurement_time.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"获取数据错误: {str(e)}")
        return jsonify({'error': '数据查询失败'}), 500

@app.route('/api/data', methods=['POST'])
@token_required
def create_data_entry():
    """创建数据记录"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['title', 'category', 'measurement_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 创建数据记录
        entry = DataEntry(
            title=data['title'],
            description=data.get('description'),
            category=data['category'],
            value=data.get('value'),
            unit=data.get('unit'),
            measurement_time=datetime.fromisoformat(data['measurement_time'].replace('Z', '+00:00')),
            location=data.get('location'),
            tags=data.get('tags'),
            metadata=data.get('metadata'),
            user_id=g.current_user.id
        )
        
        db.session.add(entry)
        db.session.commit()
        
        logger.info(f"用户 {g.current_user.username} 创建数据记录: {entry.title}")
        
        return jsonify({
            'success': True,
            'message': '数据记录创建成功',
            'data': entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建数据记录错误: {str(e)}")
        return jsonify({'error': '数据记录创建失败'}), 500

@app.route('/api/data/<int:entry_id>', methods=['PUT'])
@token_required
def update_data_entry(entry_id: int):
    """更新数据记录"""
    try:
        entry = DataEntry.query.get_or_404(entry_id)
        
        # 权限检查
        if g.current_user.role != 'admin' and entry.user_id != g.current_user.id:
            return jsonify({'error': '没有权限修改此数据记录'}), 403
        
        data = request.get_json()
        
        # 更新字段
        updatable_fields = [
            'title', 'description', 'category', 'value', 'unit',
            'location', 'tags', 'metadata', 'quality_score', 'is_validated'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'measurement_time':
                    setattr(entry, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                else:
                    setattr(entry, field, data[field])
        
        entry.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"用户 {g.current_user.username} 更新数据记录: {entry.title}")
        
        return jsonify({
            'success': True,
            'message': '数据记录更新成功',
            'data': entry.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新数据记录错误: {str(e)}")
        return jsonify({'error': '数据记录更新失败'}), 500

@app.route('/api/analytics/summary', methods=['GET'])
@token_required
def get_analytics_summary():
    """获取数据分析摘要"""
    try:
        # 解析参数
        days = int(request.args.get('days', 30))
        category = request.args.get('category')
        
        # 时间范围
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # 构建查询
        query = DataEntry.query.filter(
            DataEntry.measurement_time >= start_time,
            DataEntry.measurement_time <= end_time
        )
        
        # 非管理员只能查看自己的数据
        if g.current_user.role != 'admin':
            query = query.filter_by(user_id=g.current_user.id)
        
        if category:
            query = query.filter(DataEntry.category == category)
        
        # 获取数据
        entries = query.all()
        
        if not entries:
            return jsonify({
                'success': True,
                'message': '没有找到符合条件的数据',
                'data': {}
            })
        
        # 转换为DataFrame进行分析
        data_list = []
        for entry in entries:
            if entry.value is not None:
                data_list.append({
                    'measurement_time': entry.measurement_time,
                    'value': float(entry.value),
                    'category': entry.category,
                    'quality_score': entry.quality_score,
                    'location': entry.location
                })
        
        if not data_list:
            return jsonify({
                'success': True,
                'message': '没有有效的数值数据进行分析',
                'data': {}
            })
        
        df = pd.DataFrame(data_list)
        
        # 统计分析
        value_stats = calculate_statistics(df['value'])
        quality_stats = calculate_statistics(df['quality_score'])
        
        # 按类别分组分析
        category_stats = {}
        for cat in df['category'].unique():
            cat_data = df[df['category'] == cat]
            category_stats[cat] = {
                'count': len(cat_data),
                'value_stats': calculate_statistics(cat_data['value']),
                'avg_quality': float(cat_data['quality_score'].mean())
            }
        
        # 时间趋势分析
        trend_analysis = analyze_trend(df)
        
        # 数据质量分析
        quality_analysis = analyze_data_quality(df)
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_entries': len(entries),
                    'valid_numeric_entries': len(data_list),
                    'categories': len(df['category'].unique()),
                    'locations': len(df['location'].unique())
                },
                'value_statistics': value_stats,
                'quality_statistics': quality_stats,
                'category_analysis': category_stats,
                'trend_analysis': trend_analysis,
                'quality_analysis': quality_analysis
            }
        })
        
    except Exception as e:
        logger.error(f"分析数据错误: {str(e)}")
        return jsonify({'error': '数据分析失败'}), 500

# ============================================================================
# 数据分析辅助函数
# ============================================================================

def calculate_statistics(series: pd.Series) -> Dict[str, float]:
    """计算统计指标"""
    if series.empty:
        return {'error': '没有有效数据'}
    
    return {
        'count': int(len(series)),
        'mean': float(series.mean()),
        'median': float(series.median()),
        'std': float(series.std()),
        'min': float(series.min()),
        'max': float(series.max()),
        'q25': float(series.quantile(0.25)),
        'q75': float(series.quantile(0.75)),
        'variance': float(series.var())
    }

def analyze_trend(df: pd.DataFrame) -> Dict[str, Any]:
    """分析时间趋势"""
    if len(df) < 2:
        return {'error': '数据点不足，无法进行趋势分析'}
    
    # 按时间排序
    df_sorted = df.sort_values('measurement_time')
    
    # 线性回归分析
    x = np.arange(len(df_sorted))
    y = df_sorted['value'].values
    
    try:
        slope, intercept = np.polyfit(x, y, 1)
        correlation = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0
        
        # 判断趋势方向
        if abs(slope) < np.std(y) * 0.01:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        # 计算趋势强度
        strength = abs(correlation)
        if strength > 0.7:
            strength_desc = 'strong'
        elif strength > 0.4:
            strength_desc = 'moderate'
        else:
            strength_desc = 'weak'
        
        return {
            'direction': direction,
            'slope': float(slope),
            'correlation': float(correlation),
            'strength': strength_desc,
            'strength_value': float(strength)
        }
        
    except Exception as e:
        return {'error': f'趋势分析失败: {str(e)}'}

def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """分析数据质量"""
    total_count = len(df)
    
    # 质量分数分析
    quality_scores = df['quality_score']
    high_quality = len(quality_scores[quality_scores >= 90])
    medium_quality = len(quality_scores[(quality_scores >= 70) & (quality_scores < 90)])
    low_quality = len(quality_scores[quality_scores < 70])
    
    # 数据完整性分析
    complete_records = len(df.dropna())
    completeness_rate = complete_records / total_count if total_count > 0 else 0
    
    # 异常值检测（使用IQR方法）
    values = df['value']
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    outliers = len(values[(values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)])
    
    return {
        'quality_distribution': {
            'high_quality': high_quality,
            'medium_quality': medium_quality,
            'low_quality': low_quality,
            'high_quality_rate': high_quality / total_count if total_count > 0 else 0
        },
        'completeness': {
            'complete_records': complete_records,
            'total_records': total_count,
            'completeness_rate': completeness_rate
        },
        'outliers': {
            'count': outliers,
            'rate': outliers / len(values) if len(values) > 0 else 0
        },
        'overall_score': (
            (high_quality * 1.0 + medium_quality * 0.7 + low_quality * 0.3) / total_count * 100
        ) if total_count > 0 else 0
    }

# ============================================================================
# 错误处理
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '请求的资源不存在'}), 404

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': '请求格式错误'}), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"内部错误: {str(error)}")
    return jsonify({'error': '内部服务器错误'}), 500

@app.errorhandler(429)
def rate_limit_error(error):
    return jsonify({'error': '请求过于频繁，请稍后再试'}), 429

# ============================================================================
# 应用启动
# ============================================================================

@app.before_first_request
def create_tables():
    """创建数据库表"""
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)