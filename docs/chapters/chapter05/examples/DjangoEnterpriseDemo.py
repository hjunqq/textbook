#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django企业级应用完整示例
===============================================================================
展示Django框架在大型企业级应用开发中的完整实践，包括：
- Django项目结构与应用组织
- 模型设计与数据库关系
- 视图层与URL路由配置
- Django REST Framework API实现
- 用户认证与权限管理
- 中间件与信号处理
- 缓存策略与性能优化
===============================================================================
"""

# ============================================================================
# Django项目配置 (settings.py)
# ============================================================================

import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# 基础配置
SECRET_KEY = 'your-secret-key-change-in-production'
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 应用定义
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'celery',
    'redis',
]

LOCAL_APPS = [
    'core',
    'users',
    'data_management',
    'analytics',
    'reporting',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RequestLoggingMiddleware',
    'core.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'enterprise_platform.urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'enterprise_platform'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 600,
    }
}

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# JWT配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'enterprise_platform',
        'TIMEOUT': 300,
    }
}

# Celery配置
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# ============================================================================
# 用户管理应用 (users/models.py)
# ============================================================================

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class Department(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name="部门名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="部门代码")
    description = models.TextField(blank=True, verbose_name="部门描述")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="上级部门"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"
        ordering = ['code']
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    """扩展用户模型"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('manager', '经理'),
        ('analyst', '分析师'),
        ('operator', '操作员'),
        ('viewer', '查看者'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="手机号格式不正确"
    )
    
    # 基础信息
    chinese_name = models.CharField(max_length=50, verbose_name="中文姓名")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name="手机号")
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="工号")
    
    # 组织关系
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="所属部门"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer', verbose_name="角色")
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name="直属上级"
    )
    
    # 状态信息
    is_active = models.BooleanField(default=True, verbose_name="账户激活状态")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="最后登录IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
    
    def __str__(self):
        return f"{self.chinese_name}({self.username})"
    
    def get_full_display_name(self):
        """获取完整显示名称"""
        return f"{self.chinese_name} - {self.department.name if self.department else '无部门'}"

# ============================================================================
# 数据管理应用 (data_management/models.py)
# ============================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class DataCategory(models.Model):
    """数据分类模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="分类代码")
    description = models.TextField(blank=True, verbose_name="分类描述")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="父分类"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "数据分类"
        verbose_name_plural = "数据分类"
    
    def __str__(self):
        return self.name

class DataSource(models.Model):
    """数据源模型"""
    SOURCE_TYPES = [
        ('manual', '手动录入'),
        ('api', 'API接口'),
        ('file_upload', '文件上传'),
        ('sensor', '传感器'),
        ('database', '数据库'),
        ('external_system', '外部系统'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="数据源名称")
    type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name="数据源类型")
    description = models.TextField(blank=True, verbose_name="描述")
    configuration = models.JSONField(default=dict, verbose_name="配置信息")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "数据源"
        verbose_name_plural = "数据源"
    
    def __str__(self):
        return self.name

class DataRecord(models.Model):
    """数据记录模型"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    QUALITY_LEVELS = [
        (1, '差'),
        (2, '一般'),
        (3, '良好'),
        (4, '优秀'),
        (5, '完美'),
    ]
    
    # 基础信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="标题")
    description = models.TextField(blank=True, verbose_name="描述")
    category = models.ForeignKey(DataCategory, on_delete=models.CASCADE, verbose_name="数据分类")
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, verbose_name="数据源")
    
    # 数据内容
    value = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True, verbose_name="数值")
    unit = models.CharField(max_length=20, blank=True, verbose_name="单位")
    text_content = models.TextField(blank=True, verbose_name="文本内容")
    json_content = models.JSONField(default=dict, verbose_name="JSON内容")
    
    # 元数据
    tags = models.JSONField(default=list, verbose_name="标签")
    metadata = models.JSONField(default=dict, verbose_name="元数据")
    location = models.CharField(max_length=200, blank=True, verbose_name="位置")
    coordinates = models.JSONField(default=dict, blank=True, verbose_name="坐标信息")
    
    # 质量和状态
    quality_score = models.IntegerField(
        choices=QUALITY_LEVELS,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="质量评分"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    is_validated = models.BooleanField(default=False, verbose_name="是否已验证")
    
    # 时间信息
    measurement_time = models.DateTimeField(verbose_name="测量时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 用户关系
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_records',
        verbose_name="创建者"
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_records',
        verbose_name="验证者"
    )
    
    class Meta:
        verbose_name = "数据记录"
        verbose_name_plural = "数据记录"
        ordering = ['-measurement_time']
        indexes = [
            models.Index(fields=['category', 'measurement_time']),
            models.Index(fields=['data_source', 'status']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.measurement_time}"

# ============================================================================
# REST API视图 (data_management/views.py)
# ============================================================================

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataRecordViewSet(viewsets.ModelViewSet):
    """数据记录视图集"""
    queryset = DataRecord.objects.select_related('category', 'data_source', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'data_source', 'status', 'quality_score', 'is_validated']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['measurement_time', 'created_at', 'quality_score']
    ordering = ['-measurement_time']
    
    def get_queryset(self):
        """根据用户权限过滤数据"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # 管理员可以查看所有数据
        if user.role == 'admin':
            return queryset
        
        # 经理可以查看本部门数据
        if user.role == 'manager' and user.department:
            department_users = User.objects.filter(department=user.department)
            return queryset.filter(created_by__in=department_users)
        
        # 其他用户只能查看自己创建的数据
        return queryset.filter(created_by=user)
    
    def perform_create(self, serializer):
        """创建时自动设置创建者"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取数据统计信息"""
        try:
            queryset = self.get_queryset()
            
            # 基础统计
            total_count = queryset.count()
            validated_count = queryset.filter(is_validated=True).count()
            
            # 按分类统计
            category_stats = queryset.values('category__name').annotate(
                count=Count('id'),
                avg_quality=Avg('quality_score')
            ).order_by('-count')
            
            # 按状态统计
            status_stats = queryset.values('status').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 时间范围统计（最近30天）
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            recent_records = queryset.filter(measurement_time__gte=start_date)
            
            # 质量分析
            quality_analysis = {
                'average_quality': queryset.aggregate(avg=Avg('quality_score'))['avg'] or 0,
                'quality_distribution': queryset.values('quality_score').annotate(
                    count=Count('id')
                ).order_by('quality_score')
            }
            
            return Response({
                'success': True,
                'data': {
                    'overview': {
                        'total_records': total_count,
                        'validated_records': validated_count,
                        'validation_rate': (validated_count / total_count * 100) if total_count > 0 else 0,
                        'recent_records_count': recent_records.count()
                    },
                    'category_statistics': list(category_stats),
                    'status_statistics': list(status_stats),
                    'quality_analysis': quality_analysis,
                    'time_range': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"统计分析错误: {str(e)}")
            return Response(
                {'error': '统计分析失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """高级数据分析"""
        try:
            # 获取查询参数
            days = int(request.query_params.get('days', 30))
            category_id = request.query_params.get('category_id')
            
            # 构建查询
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            queryset = self.get_queryset().filter(
                measurement_time__gte=start_date,
                measurement_time__lte=end_date
            )
            
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            
            # 数据有效性检查
            if not queryset.exists():
                return Response({
                    'success': True,
                    'message': '指定时间范围内没有数据',
                    'data': {}
                })
            
            # 转换为DataFrame进行分析
            data_list = []
            for record in queryset.values(
                'measurement_time', 'value', 'quality_score',
                'category__name', 'location'
            ):
                if record['value'] is not None:
                    data_list.append({
                        'measurement_time': record['measurement_time'],
                        'value': float(record['value']),
                        'quality_score': record['quality_score'],
                        'category': record['category__name'],
                        'location': record['location']
                    })
            
            if not data_list:
                return Response({
                    'success': True,
                    'message': '没有有效的数值数据进行分析',
                    'data': {}
                })
            
            df = pd.DataFrame(data_list)
            
            # 执行各种分析
            trend_analysis = self._analyze_trend(df)
            distribution_analysis = self._analyze_distribution(df)
            quality_analysis = self._analyze_data_quality(df)
            location_analysis = self._analyze_by_location(df)
            
            return Response({
                'success': True,
                'data': {
                    'analysis_period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'days': days
                    },
                    'data_summary': {
                        'total_records': len(queryset),
                        'valid_numeric_records': len(data_list),
                        'categories': df['category'].nunique(),
                        'locations': df['location'].nunique()
                    },
                    'trend_analysis': trend_analysis,
                    'distribution_analysis': distribution_analysis,
                    'quality_analysis': quality_analysis,
                    'location_analysis': location_analysis
                }
            })
            
        except Exception as e:
            logger.error(f"数据分析错误: {str(e)}")
            return Response(
                {'error': '数据分析失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _analyze_trend(self, df):
        """趋势分析"""
        if len(df) < 2:
            return {'error': '数据点不足，无法进行趋势分析'}
        
        # 按时间排序
        df_sorted = df.sort_values('measurement_time')
        
        # 线性回归分析
        import numpy as np
        x = np.arange(len(df_sorted))
        y = df_sorted['value'].values
        
        try:
            slope, intercept = np.polyfit(x, y, 1)
            correlation = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0
            
            # 趋势方向判断
            std_threshold = np.std(y) * 0.01
            if abs(slope) < std_threshold:
                direction = 'stable'
            elif slope > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            return {
                'direction': direction,
                'slope': float(slope),
                'correlation': float(correlation),
                'strength': 'strong' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.4 else 'weak'
            }
            
        except Exception as e:
            return {'error': f'趋势分析计算失败: {str(e)}'}
    
    def _analyze_distribution(self, df):
        """分布分析"""
        values = df['value']
        
        return {
            'descriptive_statistics': {
                'mean': float(values.mean()),
                'median': float(values.median()),
                'std': float(values.std()),
                'min': float(values.min()),
                'max': float(values.max()),
                'q25': float(values.quantile(0.25)),
                'q75': float(values.quantile(0.75))
            },
            'distribution_shape': {
                'skewness': float(values.skew()),
                'kurtosis': float(values.kurtosis())
            }
        }
    
    def _analyze_data_quality(self, df):
        """数据质量分析"""
        quality_scores = df['quality_score']
        
        return {
            'average_quality': float(quality_scores.mean()),
            'quality_distribution': {
                'excellent': len(quality_scores[quality_scores >= 4]),
                'good': len(quality_scores[quality_scores == 3]),
                'fair': len(quality_scores[quality_scores == 2]),
                'poor': len(quality_scores[quality_scores == 1])
            }
        }
    
    def _analyze_by_location(self, df):
        """按位置分析"""
        if 'location' not in df.columns:
            return {'error': '缺少位置信息'}
        
        location_stats = df.groupby('location').agg({
            'value': ['count', 'mean', 'std'],
            'quality_score': 'mean'
        }).round(3)
        
        # 转换为字典格式
        result = {}
        for location in location_stats.index:
            result[location] = {
                'count': int(location_stats.loc[location, ('value', 'count')]),
                'mean_value': float(location_stats.loc[location, ('value', 'mean')]),
                'std_value': float(location_stats.loc[location, ('value', 'std')]) if pd.notna(location_stats.loc[location, ('value', 'std')]) else 0,
                'avg_quality': float(location_stats.loc[location, ('quality_score', 'mean')])
            }
        
        return result

# ============================================================================
# URL配置 (enterprise_platform/urls.py)
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# API路由配置
api_router = DefaultRouter()
api_router.register(r'data-records', DataRecordViewSet)

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),
    
    # API认证
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API路由
    path('api/v1/', include(api_router.urls)),
    
    # 应用URL
    path('api/users/', include('users.urls')),
    path('api/data/', include('data_management.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/reports/', include('reporting.urls')),
]

# ============================================================================
# 自定义中间件 (core/middleware.py)
# ============================================================================

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """请求日志中间件"""
    
    def process_request(self, request):
        """处理请求开始"""
        request.start_time = time.time()
        
        # 记录请求信息
        logger.info(f"请求开始: {request.method} {request.path}")
        return None
    
    def process_response(self, request, response):
        """处理响应"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # 记录响应信息
            logger.info(f"请求完成: {request.method} {request.path} - "
                       f"状态码: {response.status_code} - 耗时: {duration:.3f}秒")
        
        return response

class TimezoneMiddleware:
    """时区处理中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 从请求头获取时区信息
        timezone_header = request.META.get('HTTP_X_TIMEZONE')
        if timezone_header:
            try:
                timezone.activate(timezone_header)
            except Exception:
                pass
        
        response = self.get_response(request)
        
        # 重置时区
        timezone.deactivate()
        
        return response

# ============================================================================
# Celery异步任务 (core/tasks.py)
# ============================================================================

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_data_record(record_id):
    """异步处理数据记录"""
    try:
        from data_management.models import DataRecord
        
        record = DataRecord.objects.get(id=record_id)
        record.status = 'processing'
        record.save()
        
        # 模拟数据处理逻辑
        import time
        time.sleep(2)  # 模拟处理时间
        
        # 更新状态
        record.status = 'completed'
        record.save()
        
        logger.info(f"数据记录 {record_id} 处理完成")
        return f"记录 {record_id} 处理成功"
        
    except Exception as e:
        logger.error(f"处理数据记录 {record_id} 时发生错误: {str(e)}")
        return f"记录 {record_id} 处理失败: {str(e)}"

@shared_task
def send_notification_email(recipient_list, subject, message):
    """发送通知邮件"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info(f"邮件发送成功: {subject}")
        return "邮件发送成功"
        
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return f"邮件发送失败: {str(e)}"

if __name__ == '__main__':
    print("Django企业级应用示例")
    print("运行命令:")
    print("python manage.py runserver")