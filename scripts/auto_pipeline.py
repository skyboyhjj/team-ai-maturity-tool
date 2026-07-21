#!/usr/bin/env python3
"""
团队AI成熟度自动合并流水线脚本 v1.0

功能：合并自动采集指标和人工评分，生成完整的成熟度报告

使用方式：
    python scripts/auto_pipeline.py --auto data/weekly_report.json --manual data/manual_scores.json --output data/full_report.json

依赖：
    - python-dotenv>=1.0.1
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


class AutoPipeline:
    """自动合并流水线主类"""

    def __init__(self):
        self.auto_metrics = {}
        self.manual_scores = {}
        self.full_report = {}
        self.timestamp = datetime.now().isoformat()

    def load_auto_metrics(self, filepath: str) -> bool:
        """加载自动采集指标"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.auto_metrics = json.load(f)
            print(f"[INFO] Loaded auto metrics from {filepath}")
            return True
        except Exception as e:
            print(f"[WARN] Failed to load auto metrics: {e}")
            return False

    def load_manual_scores(self, filepath: str) -> bool:
        """加载人工评分数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.manual_scores = json.load(f)
            print(f"[INFO] Loaded manual scores from {filepath}")
            return True
        except Exception as e:
            print(f"[WARN] Failed to load manual scores: {e}")
            return False

    def convert_to_question_scores(self) -> Dict[str, float]:
        """将自动指标转换为对应题目的分数（1-5分制）"""
        question_scores = {}
        metrics = self.auto_metrics.get('metrics', {})

        question_scores['Q1'] = min(5.0, max(1.0, metrics.get('ai_tool_adoption_rate', 0) * 5))
        question_scores['Q4'] = min(5.0, max(1.0, metrics.get('ai_commit_ratio', 0) * 5))
        question_scores['Q5'] = min(5.0, max(1.0, metrics.get('ai_code_ratio', 0) * 5))
        question_scores['Q7'] = min(5.0, max(1.0, metrics.get('ci_coverage', 0) * 5))
        question_scores['Q8'] = min(5.0, max(1.0, min(metrics.get('loop_task_count', 0) / 10, 1) * 5))
        question_scores['Q9'] = min(5.0, max(1.0, min(metrics.get('agent_count', 0) / 20, 1) * 5))
        question_scores['Q12'] = min(5.0, max(1.0, min(metrics.get('context_source_count', 0) / 10, 1) * 5))
        question_scores['Q13'] = min(5.0, max(1.0, metrics.get('cross_department_coverage', 0) * 5))

        return question_scores

    def merge_scores(self) -> Dict[str, float]:
        """合并自动指标和人工评分"""
        auto_scores = self.convert_to_question_scores()
        manual_scores = self.manual_scores.get('scores', {})

        merged_scores = {}

        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15']:
            if q in manual_scores and manual_scores[q] > 0:
                merged_scores[q] = manual_scores[q]
            elif q in auto_scores:
                merged_scores[q] = auto_scores[q]
            else:
                merged_scores[q] = 0

        return merged_scores

    def calculate_dimensions(self, merged_scores: Dict[str, float]) -> Dict[str, float]:
        """计算四个维度得分"""
        dimensions = {}

        yu_scores = [merged_scores.get(q, 0) for q in ['Q1', 'Q2', 'Q3', 'Q9', 'Q13']]
        shi_scores = [merged_scores.get(q, 0) for q in ['Q4', 'Q5', 'Q8']]
        shi_awareness_scores = [merged_scores.get(q, 0) for q in ['Q6', 'Q11', 'Q15']]
        yuan_scores = [merged_scores.get(q, 0) for q in ['Q7', 'Q10', 'Q12', 'Q14']]

        dimensions['yu'] = sum(yu_scores) / len(yu_scores) if yu_scores else 0
        dimensions['shi'] = sum(shi_scores) / len(shi_scores) if shi_scores else 0
        dimensions['shi_awareness'] = sum(shi_awareness_scores) / len(shi_awareness_scores) if shi_awareness_scores else 0
        dimensions['yuan'] = sum(yuan_scores) / len(yuan_scores) if yuan_scores else 0

        return dimensions

    def calculate_total(self, merged_scores: Dict[str, float]) -> float:
        """计算折算后总分（满分64分）"""
        valid_scores = [s for s in merged_scores.values() if s > 0]
        if not valid_scores:
            return 0.0

        raw_total = sum(valid_scores)
        max_possible = len(valid_scores) * 5
        normalized = (raw_total / max_possible) * 64

        return round(normalized, 2)

    def determine_stage(self, total_score: float) -> Dict[str, Any]:
        """判定成熟度阶段"""
        if total_score < 25:
            return {'stage': 1, 'name': '辅助模式', 'description': '零星使用 AI 工具，无系统化流程，AI 作为"外挂"存在'}
        elif total_score < 35:
            return {'stage': 2, 'name': '并行模式', 'description': 'AI 与人工工作流并行，部分环节已常规化使用 AI'}
        elif total_score < 45:
            return {'stage': 3, 'name': '自主运行', 'description': 'AI 承担部分独立任务，团队开始建立 AI 使用规范'}
        elif total_score < 55:
            return {'stage': 4, 'name': '常驻智能体', 'description': 'AI 智能体嵌入日常工作，具备持续上下文与主动建议能力'}
        else:
            return {'stage': 5, 'name': 'AI 原生', 'description': '团队流程以 AI 为核心重新设计，AI 深度参与决策与执行'}

    def generate_report(self) -> Dict[str, Any]:
        """生成完整报告"""
        print("[INFO] Generating full report...")

        merged_scores = self.merge_scores()
        dimensions = self.calculate_dimensions(merged_scores)
        total_score = self.calculate_total(merged_scores)
        stage_info = self.determine_stage(total_score)

        product_score = round(dimensions['yu'] * dimensions['shi'] * dimensions['shi_awareness'] * dimensions['yuan'], 2)

        self.full_report = {
            'timestamp': self.timestamp,
            'version': '1.0',
            'sources': {
                'auto': bool(self.auto_metrics),
                'manual': bool(self.manual_scores)
            },
            'question_scores': merged_scores,
            'dimensions': {
                'yu': round(dimensions['yu'], 2),
                'shi': round(dimensions['shi'], 2),
                'shi_awareness': round(dimensions['shi_awareness'], 2),
                'yuan': round(dimensions['yuan'], 2)
            },
            'total_score': total_score,
            'product_score': product_score,
            'stage': stage_info,
            'auto_metrics_raw': self.auto_metrics.get('metrics', {})
        }

        print(f"[INFO] Report generated. Total score: {total_score}, Stage: {stage_info['name']}")
        return self.full_report

    def save_report(self, filepath: str) -> bool:
        """保存报告"""
        try:
            output_dir = os.path.dirname(filepath)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.full_report, f, ensure_ascii=False, indent=2)

            print(f"[SUCCESS] Report saved to {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save report: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='团队AI成熟度自动合并流水线')
    parser.add_argument('--auto', '-a', required=True, help='自动采集指标文件路径')
    parser.add_argument('--manual', '-m', default=None, help='人工评分文件路径（可选）')
    parser.add_argument('--output', '-o', default='data/full_report.json', help='输出文件路径')

    args = parser.parse_args()

    pipeline = AutoPipeline()

    pipeline.load_auto_metrics(args.auto)

    if args.manual and os.path.exists(args.manual):
        pipeline.load_manual_scores(args.manual)

    pipeline.generate_report()
    pipeline.save_report(args.output)


if __name__ == '__main__':
    main()