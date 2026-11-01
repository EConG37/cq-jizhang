"""Summarize complete six-field Feishu records in UTC+8; no network or writes."""
import argparse
import json
from collections import defaultdict
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

TZ = timezone(timedelta(hours=8))


def money(value, allow_zero=False):
    if value is None or value == '' or isinstance(value, bool):
        raise ValueError('金额缺失或类型错误')
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError('金额不是数字') from None
    if not result.is_finite() or result < 0 or (result == 0 and not allow_zero):
        raise ValueError('金额必须是有限正数，预算允许零')
    if result != result.quantize(Decimal('0.01')):
        raise ValueError('金额最多两位小数')
    return result


def timestamp(value, end_of_day=False):
    if isinstance(value, bool) or value is None:
        raise ValueError('日期缺失或无效')
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value / 1000, TZ)
        if not isinstance(value, str):
            raise ValueError()
        if len(value) == 10:
            result = datetime.fromisoformat(value)
            if end_of_day:
                result = datetime.combine(result.date(), time.max)
        else:
            result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return result.replace(tzinfo=TZ) if result.tzinfo is None else result.astimezone(TZ)
    except (ValueError, OverflowError, OSError):
        raise ValueError('日期须为毫秒时间戳或ISO日期时间') from None


def rows_from(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise ValueError('输入须为记录数组或完整读取结果')
    if payload.get('code', 0) != 0:
        raise ValueError('平台返回错误，不能生成消费总额')
    data = payload.get('data', payload)
    if not isinstance(data, dict) or data.get('has_more') or data.get('complete') is False:
        raise ValueError('读取未完成，请完整分页后再统计')
    rows = data.get('items', data.get('records'))
    if not isinstance(rows, list):
        raise ValueError('缺少items或records记录数组')
    return rows


def group(value):
    if value in (None, '', []):
        return '未分类'
    if isinstance(value, list):
        categories = list(dict.fromkeys(v for v in value if isinstance(v, str) and v))
        return categories[0] if len(categories) == 1 else '多分类待核对' if categories else '未分类'
    return value if isinstance(value, str) else '多分类待核对'


def summarize(payload, as_of, weekly_budget=None, excluded_ids=()):
    cutoff = timestamp(as_of, end_of_day=True)
    today = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
    week = today - timedelta(days=today.weekday())
    excluded_ids = set(excluded_ids)
    seen = {}
    totals = {'今日支出': Decimal(0), '今日收入': Decimal(0),
              '本周支出': Decimal(0), '本周收入': Decimal(0)}
    counts = {'今日支出笔数': 0, '今日收入笔数': 0, '本周支出笔数': 0, '本周收入笔数': 0}
    categories = defaultdict(lambda: Decimal(0))
    pending = []
    undated = []
    duplicate_returns = 0
    excluded_count = 0
    for row in rows_from(payload):
        if not isinstance(row, dict) or not isinstance(row.get('record_id'), str) or not row['record_id']:
            raise ValueError('记录缺少record_id，无法可靠去重')
        rid = row['record_id']
        fields = row.get('fields')
        if not isinstance(fields, dict):
            raise ValueError('记录缺少fields对象')
        fingerprint = json.dumps(fields, sort_keys=True, ensure_ascii=False)
        if rid in seen:
            if seen[rid] != fingerprint:
                raise ValueError('相同record_id内容冲突，请重新读取一致数据')
            duplicate_returns += 1
            continue
        seen[rid] = fingerprint
        if rid in excluded_ids:
            excluded_count += 1
            continue
        try:
            at = timestamp(fields.get('日期'))
        except ValueError:
            undated.append(rid)
            continue
        if not week <= at <= cutoff:
            continue
        typ = fields.get('收支类型')
        currency = fields.get('币种', 'CNY')
        if currency not in ('CNY', '人民币', '元') or typ not in ('支出', '收入'):
            pending.append(rid)
            continue
        try:
            amount = money(fields.get('金额'))
        except (ValueError, InvalidOperation):
            pending.append(rid)
            continue
        totals['本周' + typ] += amount
        counts['本周' + typ + '笔数'] += 1
        if at >= today:
            totals['今日' + typ] += amount
            counts['今日' + typ + '笔数'] += 1
        if typ == '支出':
            categories[group(fields.get('消费类型'))] += amount
    budget = money(weekly_budget, allow_zero=True) if weekly_budget is not None else None
    spent = totals['本周支出']
    complete = not pending and not undated
    remaining = max(Decimal(0), budget - spent) if budget is not None and complete else None
    days_after_today = 6 - today.weekday()
    report = {'时区': 'UTC+08:00', '截至': cutoff.isoformat(), '本周起始': week.date().isoformat(),
              '本周结束': (week + timedelta(days=6)).date().isoformat(), '币种': 'CNY',
              **{k: format(v, '.2f') for k, v in totals.items()}, **counts,
              '本周分类支出': {k: format(v, '.2f') for k, v in sorted(categories.items(), key=lambda kv: -kv[1])},
              '每周预算': format(budget, '.2f') if budget is not None else None,
              '本周剩余额度': format(remaining, '.2f') if remaining is not None else None,
              '本周超支': format(max(Decimal(0), spent - budget), '.2f') if budget is not None and complete else None,
              '预算使用率百分比': format(spent / budget * 100, '.2f') if budget and complete else None,
              '预算统计状态': '待核对' if not complete else '未设置' if budget is None else '已核对记录',
              '明天至周日天数': days_after_today,
              '后续每日参考': format(remaining / days_after_today, '.2f') if remaining is not None and days_after_today else None,
              '下周每日参考': format(budget / 7, '.2f') if budget is not None else None,
              '本周待核对记录ID': pending, '无法归属日期记录ID': undated,
              '已排除测试记录数': excluded_count, '重复返回去重数': duplicate_returns,
              '统计完整': complete,
              '说明': '按已记录账单汇总；若有待核对记录，金额仅为已知小计。不同ID的疑似重复仍计入。'}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records', type=Path)
    parser.add_argument('--as-of', required=True, help='ISO截止时间；只有日期时按当地日末')
    parser.add_argument('--budget', default=None)
    parser.add_argument('--exclude-id', action='append', default=[])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = summarize(json.loads(args.records.read_text(encoding='utf-8-sig')),
                           args.as_of, args.budget, args.exclude_id)
        body = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            if args.output.resolve() == args.records.resolve():
                raise ValueError('输出不能覆盖输入账单')
            args.output.write_text(body + '\n', encoding='utf-8')
        else:
            print(body)
    except (ValueError, InvalidOperation) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
