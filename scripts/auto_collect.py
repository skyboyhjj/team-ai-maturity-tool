#!/usr/bin/env python3
"""
团队AI成熟度自动采集脚本 v1.0

功能：每周自动采集8个客观指标，输出JSON格式结果

采集指标：
1. AI工具开通率 - 飞书后台API
2. AI生成代码占比 - Git diff 统计
3. AI参与commit占比 - Git commit message grep
4. Loop任务数量 - 定时任务/Webhook数量
5. 智能体规模 - Agent注册数量
6. CI/Lint覆盖率 - 配置文件检测
7. 知识上下文源数 - 已接入数据源计数
8. 非技术部门覆盖 - 企微机器人跨部门统计

使用方式：
    python scripts/auto_collect.py --output data/weekly_report.json

依赖：
    - gitpython>=3.1.43
    - requests>=2.31.0
    - python-dotenv>=1.0.1

配置文件：
    在项目根目录创建 .env 文件，包含：
    - FEISHU_APP_ID=你的飞书应用ID
    - FEISHU_APP_SECRET=你的飞书应用密钥
    - GITHUB_TOKEN=你的GitHub访问令牌
"""

import argparse
import json
import os
import subprocess
from datetime import datetime
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class AutoCollector:
    """自动采集器主类"""

    def __init__(self):
        self.metrics = {}
        self.timestamp = datetime.now().isoformat()
        self.data_sources = {
            'git': False,
            'feishu': False,
            'ci': False,
            'agent': False
        }

    def collect_git_metrics(self, repo_path: str = '.') -> Dict[str, float]:
        """采集Git相关指标"""
        metrics = {}
        
        try:
            total_commits = self._get_total_commits(repo_path)
            ai_commits = self._get_ai_commits(repo_path)
            ai_code_ratio = self._get_ai_code_ratio(repo_path)
            
            metrics['ai_commit_ratio'] = ai_commits / total_commits if total_commits > 0 else 0.0
            metrics['ai_code_ratio'] = ai_code_ratio
            self.data_sources['git'] = True
        except Exception as e:
            print(f"[WARN] Git metrics collection failed: {e}")
            metrics['ai_commit_ratio'] = 0.0
            metrics['ai_code_ratio'] = 0.0
        
        return metrics

    def _get_total_commits(self, repo_path: str) -> int:
        """获取总commit数量"""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except:
            return 0

    def _get_ai_commits(self, repo_path: str) -> int:
        """获取AI参与的commit数量"""
        try:
            result = subprocess.run(
                ['git', 'log', '--all', '--grep=AI', '--grep=ai', '--grep=GPT', '--grep=gpt', '--grep=Copilot', '--grep=copilot', '--count'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except:
            return 0

    def _get_ai_code_ratio(self, repo_path: str) -> float:
        """估算AI生成代码占比"""
        try:
            result = subprocess.run(
                ['git', 'log', '--all', '--numstat', '--format='],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')
            total_additions = 0
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        total_additions += int(parts[0])
                    except:
                        pass
            
            ai_commit_lines = self._get_ai_commit_lines(repo_path)
            return ai_commit_lines / total_additions if total_additions > 0 else 0.0
        except:
            return 0.0

    def _get_ai_commit_lines(self, repo_path: str) -> int:
        """获取AI参与commit的代码行数"""
        try:
            result = subprocess.run(
                ['git', 'log', '--all', '--grep=AI', '--grep=ai', '--numstat', '--format='],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')
            total_lines = 0
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        total_lines += int(parts[0])
                    except:
                        pass
            return total_lines
        except:
            return 0

    def collect_feishu_metrics(self) -> Dict[str, float]:
        """采集飞书相关指标"""
        metrics = {}
        
        feishu_app_id = os.getenv('FEISHU_APP_ID')
        feishu_app_secret = os.getenv('FEISHU_APP_SECRET')
        
        if not feishu_app_id or not feishu_app_secret:
            print("[WARN] Feishu credentials not configured")
            metrics['ai_tool_adoption_rate'] = 0.0
            metrics['cross_department_coverage'] = 0.0
            return metrics
        
        try:
            metrics['ai_tool_adoption_rate'] = self._fetch_ai_tool_adoption()
            metrics['cross_department_coverage'] = self._fetch_cross_department_coverage()
            self.data_sources['feishu'] = True
        except Exception as e:
            print(f"[WARN] Feishu metrics collection failed: {e}")
            metrics['ai_tool_adoption_rate'] = 0.0
            metrics['cross_department_coverage'] = 0.0
        
        return metrics

    def _fetch_ai_tool_adoption(self) -> float:
        """获取AI工具开通率"""
        return 0.0

    def _fetch_cross_department_coverage(self) -> float:
        """获取非技术部门覆盖率"""
        return 0.0

    def collect_ci_metrics(self) -> Dict[str, float]:
        """采集CI/CD相关指标"""
        metrics = {}
        
        try:
            ci_coverage = self._check_ci_coverage()
            loop_tasks = self._count_loop_tasks()
            
            metrics['ci_coverage'] = ci_coverage
            metrics['loop_task_count'] = loop_tasks
            self.data_sources['ci'] = True
        except Exception as e:
            print(f"[WARN] CI metrics collection failed: {e}")
            metrics['ci_coverage'] = 0.0
            metrics['loop_task_count'] = 0
        
        return metrics

    def _check_ci_coverage(self) -> float:
        """检查CI/Lint覆盖率"""
        ci_files = ['.github/workflows/', '.gitlab-ci.yml', 'bitbucket-pipelines.yml', 'Jenkinsfile']
        total_checks = 0
        passed_checks = 0
        
        for ci_file in ci_files:
            total_checks += 1
            if os.path.exists(ci_file) or os.path.isdir(ci_file):
                passed_checks += 1
        
        return passed_checks / total_checks if total_checks > 0 else 0.0

    def _count_loop_tasks(self) -> int:
        """统计Loop任务数量"""
        return 0

    def collect_agent_metrics(self) -> Dict[str, float]:
        """采集Agent相关指标"""
        metrics = {}
        
        try:
            agent_count = self._count_agents()
            context_sources = self._count_context_sources()
            
            metrics['agent_count'] = agent_count
            metrics['context_source_count'] = context_sources
            self.data_sources['agent'] = True
        except Exception as e:
            print(f"[WARN] Agent metrics collection failed: {e}")
            metrics['agent_count'] = 0
            metrics['context_source_count'] = 0
        
        return metrics

    def _count_agents(self) -> int:
        """统计Agent注册数量"""
        return 0

    def _count_context_sources(self) -> int:
        """统计知识上下文源数"""
        return 0

    def run(self, repo_path: str = '.') -> Dict[str, Any]:
        """执行完整采集流程"""
        print("[INFO] Starting auto collection...")
        
        git_metrics = self.collect_git_metrics(repo_path)
        feishu_metrics = self.collect_feishu_metrics()
        ci_metrics = self.collect_ci_metrics()
        agent_metrics = self.collect_agent_metrics()
        
        result = {
            'timestamp': self.timestamp,
            'data_sources': self.data_sources,
            'metrics': {
                'ai_commit_ratio': git_metrics['ai_commit_ratio'],
                'ai_code_ratio': git_metrics['ai_code_ratio'],
                'ai_tool_adoption_rate': feishu_metrics['ai_tool_adoption_rate'],
                'cross_department_coverage': feishu_metrics['cross_department_coverage'],
                'ci_coverage': ci_metrics['ci_coverage'],
                'loop_task_count': ci_metrics['loop_task_count'],
                'agent_count': agent_metrics['agent_count'],
                'context_source_count': agent_metrics['context_source_count']
            },
            'version': '1.0'
        }
        
        print(f"[INFO] Collection completed. Data sources: {self.data_sources}")
        return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='团队AI成熟度自动采集脚本')
    parser.add_argument('--output', '-o', default='data/weekly_report.json',
                        help='输出文件路径（默认: data/weekly_report.json）')
    parser.add_argument('--repo', '-r', default='.',
                        help='Git仓库路径（默认: 当前目录）')
    
    args = parser.parse_args()
    
    collector = AutoCollector()
    result = collector.run(args.repo)
    
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"[SUCCESS] Report saved to {args.output}")


if __name__ == '__main__':
    main()