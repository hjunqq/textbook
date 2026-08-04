#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python框架性能对比与选型指南
===============================================================================
对比Flask和Django在不同企业应用场景下的性能表现，包括：
- 基准测试对比
- 内存使用分析
- 并发处理能力
- 数据库操作性能
- 缓存策略效果
- 部署和扩展性对比
===============================================================================
"""

import time
import psutil
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
import statistics
from dataclasses import dataclass
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import pandas as pd

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    response_time: float
    memory_usage: float
    cpu_usage: float
    concurrent_requests: int
    success_rate: float
    throughput: float

class FrameworkBenchmark:
    """框架性能测试类"""
    
    def __init__(self, base_url: str, framework_name: str):
        self.base_url = base_url
        self.framework_name = framework_name
        self.results = []
    
    def simple_request_test(self, endpoint: str, num_requests: int = 100):
        """简单请求测试"""
        url = f"{self.base_url}{endpoint}"
        response_times = []
        success_count = 0
        
        print(f"开始测试 {self.framework_name} - {endpoint}")
        start_time = time.time()
        
        for i in range(num_requests):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    success_count += 1
                response_times.append(response.elapsed.total_seconds())
            except Exception as e:
                print(f"请求失败: {e}")
        
        total_time = time.time() - start_time
        
        return {
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'success_rate': (success_count / num_requests) * 100,
            'throughput': num_requests / total_time,
            'total_time': total_time
        }
    
    def concurrent_request_test(self, endpoint: str, concurrent_users: int = 50, requests_per_user: int = 10):
        """并发请求测试"""
        url = f"{self.base_url}{endpoint}"
        all_response_times = []
        success_count = 0
        total_requests = concurrent_users * requests_per_user
        
        def user_requests():
            nonlocal success_count
            user_response_times = []
            
            for _ in range(requests_per_user):
                try:
                    start = time.time()
                    response = requests.get(url, timeout=10)
                    end = time.time()
                    
                    if response.status_code == 200:
                        success_count += 1
                    
                    user_response_times.append(end - start)
                except Exception as e:
                    pass
            
            return user_response_times
        
        print(f"开始并发测试 {self.framework_name} - {concurrent_users} 并发用户")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_requests) for _ in range(concurrent_users)]
            
            for future in futures:
                user_times = future.result()
                all_response_times.extend(user_times)
        
        total_time = time.time() - start_time
        
        return {
            'avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
            'p95_response_time': statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) > 20 else 0,
            'p99_response_time': statistics.quantiles(all_response_times, n=100)[98] if len(all_response_times) > 100 else 0,
            'success_rate': (success_count / total_requests) * 100,
            'throughput': total_requests / total_time,
            'concurrent_users': concurrent_users
        }
    
    def memory_usage_test(self, duration: int = 60):
        """内存使用测试"""
        memory_samples = []
        
        def monitor_memory():
            start_time = time.time()
            while time.time() - start_time < duration:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_samples.append(memory_info.rss / 1024 / 1024)  # MB
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor_memory)
        monitor_thread.start()
        
        # 在监控期间发送请求
        for _ in range(duration * 2):  # 每秒2个请求
            try:
                requests.get(f"{self.base_url}/api/health", timeout=5)
            except:
                pass
            time.sleep(0.5)
        
        monitor_thread.join()
        
        return {
            'avg_memory_usage': statistics.mean(memory_samples) if memory_samples else 0,
            'max_memory_usage': max(memory_samples) if memory_samples else 0,
            'min_memory_usage': min(memory_samples) if memory_samples else 0
        }

def compare_frameworks():
    """框架对比测试"""
    
    # 测试配置
    flask_benchmark = FrameworkBenchmark("http://localhost:5000", "Flask")
    django_benchmark = FrameworkBenchmark("http://localhost:8000", "Django")
    
    test_scenarios = [
        {
            'name': 'API健康检查',
            'endpoint': '/api/health',
            'description': '简单的健康检查端点'
        },
        {
            'name': '数据列表查询',
            'endpoint': '/api/data',
            'description': '分页数据列表查询'
        },
        {
            'name': '数据统计分析',
            'endpoint': '/api/analytics/summary',
            'description': '复杂的数据分析计算'
        }
    ]
    
    comparison_results = {}
    
    for scenario in test_scenarios:
        print(f"\n{'='*50}")
        print(f"测试场景: {scenario['name']}")
        print(f"描述: {scenario['description']}")
        print(f"{'='*50}")
        
        # Flask测试
        flask_simple = flask_benchmark.simple_request_test(scenario['endpoint'])
        flask_concurrent = flask_benchmark.concurrent_request_test(scenario['endpoint'])
        
        # Django测试
        django_simple = django_benchmark.simple_request_test(scenario['endpoint'])
        django_concurrent = django_benchmark.concurrent_request_test(scenario['endpoint'])
        
        comparison_results[scenario['name']] = {
            'Flask': {
                'simple_test': flask_simple,
                'concurrent_test': flask_concurrent
            },
            'Django': {
                'simple_test': django_simple,
                'concurrent_test': django_concurrent
            }
        }
    
    return comparison_results

def analyze_performance_data(results: Dict[str, Any]) -> Dict[str, Any]:
    """分析性能测试数据"""
    
    analysis = {
        'summary': {},
        'detailed_comparison': {},
        'recommendations': []
    }
    
    # 汇总分析
    flask_avg_response = []
    django_avg_response = []
    flask_throughput = []
    django_throughput = []
    
    for scenario, data in results.items():
        flask_resp = data['Flask']['simple_test']['avg_response_time']
        django_resp = data['Django']['simple_test']['avg_response_time']
        
        flask_avg_response.append(flask_resp)
        django_avg_response.append(django_resp)
        
        flask_throughput.append(data['Flask']['simple_test']['throughput'])
        django_throughput.append(data['Django']['simple_test']['throughput'])
    
    analysis['summary'] = {
        'Flask平均响应时间': statistics.mean(flask_avg_response),
        'Django平均响应时间': statistics.mean(django_avg_response),
        'Flask平均吞吐量': statistics.mean(flask_throughput),
        'Django平均吞吐量': statistics.mean(django_throughput)
    }
    
    # 详细对比
    for scenario, data in results.items():
        flask_data = data['Flask']
        django_data = data['Django']
        
        analysis['detailed_comparison'][scenario] = {
            '响应时间对比': {
                'Flask更快': flask_data['simple_test']['avg_response_time'] < django_data['simple_test']['avg_response_time'],
                '性能差异倍数': django_data['simple_test']['avg_response_time'] / flask_data['simple_test']['avg_response_time']
            },
            '吞吐量对比': {
                'Flask更高': flask_data['simple_test']['throughput'] > django_data['simple_test']['throughput'],
                '性能差异倍数': flask_data['simple_test']['throughput'] / django_data['simple_test']['throughput']
            },
            '并发性能对比': {
                'Flask P95响应时间': flask_data['concurrent_test']['p95_response_time'],
                'Django P95响应时间': django_data['concurrent_test']['p95_response_time']
            }
        }
    
    # 生成推荐
    if analysis['summary']['Flask平均响应时间'] < analysis['summary']['Django平均响应时间']:
        analysis['recommendations'].append("在响应时间方面，Flask表现更优")
    
    if analysis['summary']['Flask平均吞吐量'] > analysis['summary']['Django平均吞吐量']:
        analysis['recommendations'].append("在吞吐量方面，Flask表现更优")
    
    return analysis

def generate_performance_report(results: Dict[str, Any]):
    """生成性能测试报告"""
    
    analysis = analyze_performance_data(results)
    
    print("\n" + "="*80)
    print("Flask vs Django 性能对比报告")
    print("="*80)
    
    print(f"\n【总体性能摘要】")
    for metric, value in analysis['summary'].items():
        print(f"{metric}: {value:.4f}")
    
    print(f"\n【详细场景对比】")
    for scenario, comparison in analysis['detailed_comparison'].items():
        print(f"\n场景: {scenario}")
        print(f"  响应时间: {'Flask更优' if comparison['响应时间对比']['Flask更快'] else 'Django更优'}")
        print(f"  性能差异: {comparison['响应时间对比']['性能差异倍数']:.2f}倍")
        print(f"  吞吐量: {'Flask更优' if comparison['吞吐量对比']['Flask更高'] else 'Django更优'}")
    
    print(f"\n【性能优化建议】")
    for recommendation in analysis['recommendations']:
        print(f"• {recommendation}")
    
    # 额外的选型建议
    print(f"\n【框架选型建议】")
    print("• 如果项目注重快速原型开发和高性能API，推荐Flask")
    print("• 如果项目需要完整的企业级功能和快速开发，推荐Django")
    print("• 对于数据分析和机器学习集成，两个框架都有良好支持")
    print("• 考虑团队技能水平和项目维护需求")

class ScalabilityAnalyzer:
    """扩展性分析器"""
    
    @staticmethod
    def analyze_horizontal_scaling():
        """水平扩展分析"""
        return {
            'Flask': {
                '扩展难度': '简单',
                '负载均衡': '需要外部工具(Nginx/HAProxy)',
                '状态管理': '无状态，天然支持扩展',
                '数据库连接': '需要连接池管理',
                '推荐部署': 'Docker容器 + K8s'
            },
            'Django': {
                '扩展难度': '中等',
                '负载均衡': '需要外部工具或Django配置',
                '状态管理': '支持无状态和有状态应用',
                '数据库连接': '内置连接池管理',
                '推荐部署': 'Gunicorn + Docker + K8s'
            }
        }
    
    @staticmethod
    def analyze_vertical_scaling():
        """垂直扩展分析"""
        return {
            'Flask': {
                'CPU利用率': '高效，轻量级框架',
                '内存占用': '低，最小化依赖',
                '数据库性能': '依赖ORM选择',
                '缓存策略': '需要手动实现'
            },
            'Django': {
                'CPU利用率': '中等，功能丰富',
                '内存占用': '较高，完整功能集',
                '数据库性能': '优化的Django ORM',
                '缓存策略': '内置多层缓存'
            }
        }

def main():
    """主函数 - 执行完整的性能分析"""
    
    print("Python Web框架性能分析工具")
    print("="*50)
    
    # 注意：实际运行需要启动Flask和Django服务
    print("注意: 此脚本需要Flask(localhost:5000)和Django(localhost:8000)服务运行")
    print("建议使用示例代码启动服务后再运行此分析工具")
    
    # 模拟数据展示分析功能
    mock_results = {
        'API健康检查': {
            'Flask': {
                'simple_test': {'avg_response_time': 0.002, 'throughput': 1250, 'success_rate': 100},
                'concurrent_test': {'p95_response_time': 0.015, 'success_rate': 99.8}
            },
            'Django': {
                'simple_test': {'avg_response_time': 0.008, 'throughput': 800, 'success_rate': 100},
                'concurrent_test': {'p95_response_time': 0.045, 'success_rate': 99.5}
            }
        },
        '数据列表查询': {
            'Flask': {
                'simple_test': {'avg_response_time': 0.025, 'throughput': 400, 'success_rate': 100},
                'concurrent_test': {'p95_response_time': 0.120, 'success_rate': 98.5}
            },
            'Django': {
                'simple_test': {'avg_response_time': 0.035, 'throughput': 285, 'success_rate': 100},
                'concurrent_test': {'p95_response_time': 0.180, 'success_rate': 98.0}
            }
        }
    }
    
    generate_performance_report(mock_results)
    
    # 扩展性分析
    print("\n" + "="*80)
    print("扩展性分析报告")
    print("="*80)
    
    analyzer = ScalabilityAnalyzer()
    horizontal = analyzer.analyze_horizontal_scaling()
    vertical = analyzer.analyze_vertical_scaling()
    
    print("\n【水平扩展对比】")
    for framework, metrics in horizontal.items():
        print(f"\n{framework}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
    
    print("\n【垂直扩展对比】")
    for framework, metrics in vertical.items():
        print(f"\n{framework}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")

if __name__ == '__main__':
    main()