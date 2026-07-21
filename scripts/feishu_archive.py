#!/usr/bin/env python3
"""
团队AI成熟度飞书归档脚本 v1.0

功能：将成熟度报告归档到飞书多维表格

使用方式：
    python scripts/feishu_archive.py --report data/full_report.json

依赖：
    - requests>=2.31.0
    - python-dotenv>=1.0.1

配置文件：
    在项目根目录创建 .env 文件，包含：
    - FEISHU_APP_ID=你的飞书应用ID
    - FEISHU_APP_SECRET=你的飞书应用密钥
    - FEISHU_TABLE_ID=飞书多维表格ID
"""

import argparse
import json
import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class FeishuArchiver:
    """飞书归档器主类"""

    def __init__(self):
        self.app_id = os.getenv('FEISHU_APP_ID')
        self.app_secret = os.getenv('FEISHU_APP_SECRET')
        self.table_id = os.getenv('FEISHU_TABLE_ID')
        self.access_token = None
        self.base_url = 'https://open.feishu.cn/open-apis'

    def get_access_token(self) -> bool:
        """获取飞书API访问令牌"""
        if not self.app_id or not self.app_secret:
            print("[ERROR] Feishu credentials not configured")
            return False

        try:
            url = f'{self.base_url}/auth/v3/tenant_access_token/internal'
            payload = {
                'app_id': self.app_id,
                'app_secret': self.app_secret
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            if data.get('code') == 0:
                self.access_token = data.get('tenant_access_token')
                print("[INFO] Obtained Feishu access token")
                return True
            else:
                print(f"[ERROR] Failed to get access token: {data.get('msg')}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to get access token: {e}")
            return False

    def load_report(self, filepath: str) -> Optional[Dict[str, Any]]:
        """加载成熟度报告"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load report: {e}")
            return None

    def prepare_record(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """准备归档记录数据"""
        dimensions = report.get('dimensions', {})
        stage = report.get('stage', {})

        record = {
            'fields': {
                '日期': datetime.now().strftime('%Y-%m-%d'),
                '时间': datetime.now().strftime('%H:%M:%S'),
                '总分': report.get('total_score', 0),
                '乘积得分': report.get('product_score', 0),
                '阶段': stage.get('name', ''),
                '宇位得分': dimensions.get('yu', 0),
                '时位得分': dimensions.get('shi', 0),
                '识位得分': dimensions.get('shi_awareness', 0),
                '缘位得分': dimensions.get('yuan', 0),
                '数据来源': '自动采集' if report.get('sources', {}).get('auto') else '人工评分',
                '版本': report.get('version', '1.0')
            }
        }

        question_scores = report.get('question_scores', {})
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15']:
            if q in question_scores:
                record['fields'][q] = question_scores[q]

        return record

    def create_record(self, record: Dict[str, Any]) -> bool:
        """创建飞书多维表格记录"""
        if not self.access_token:
            print("[ERROR] No access token available")
            return False

        if not self.table_id:
            print("[ERROR] Feishu table ID not configured")
            return False

        try:
            url = f'{self.base_url}/bitable/v1/apps/{self.table_id}/tables/tblXXXXXXXX/records'
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, json=record)
            response.raise_for_status()

            data = response.json()
            if data.get('code') == 0:
                print(f"[SUCCESS] Record created in Feishu table")
                return True
            else:
                print(f"[ERROR] Failed to create record: {data.get('msg')}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to create record: {e}")
            return False

    def run(self, report_path: str) -> bool:
        """执行归档流程"""
        print("[INFO] Starting Feishu archive...")

        if not self.get_access_token():
            return False

        report = self.load_report(report_path)
        if not report:
            return False

        record = self.prepare_record(report)
        print(f"[INFO] Prepared record: {json.dumps(record, ensure_ascii=False, indent=2)}")

        return self.create_record(record)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='团队AI成熟度飞书归档脚本')
    parser.add_argument('--report', '-r', required=True, help='成熟度报告文件路径')

    args = parser.parse_args()

    archiver = FeishuArchiver()
    success = archiver.run(args.report)

    if success:
        print("[SUCCESS] Archive completed successfully")
    else:
        print("[ERROR] Archive failed")
        exit(1)


if __name__ == '__main__':
    main()