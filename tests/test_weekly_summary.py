"""Offline synthetic cases; not real customer bills."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('weekly', ROOT / 'cq-jizhang/scripts/weekly_summary.py')
weekly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weekly)


def bill(rid, amount, typ='支出', at='2026-10-13T12:00:00+08:00', categories=None):
    return {'record_id': rid, 'fields': {'日期': at, '收支类型': typ, '金额': amount,
            '消费类型': categories or ['饮食'], '文本内容': '离线测试', '具体花费项目': '测试项目'}}


class SummaryTests(unittest.TestCase):
    def test_income_does_not_expand_budget(self):
        r = weekly.summarize([bill('a', '100'), bill('b', '5000', '收入')], '2026-10-13T22:00:00+08:00', '800')
        self.assertEqual(r['本周支出'], '100.00')
        self.assertEqual(r['本周收入'], '5000.00')
        self.assertEqual(r['本周剩余额度'], '700.00')

    def test_only_known_test_ids_excluded(self):
        r = weekly.summarize([bill('test', '.01'), bill('real', '20')], '2026-10-13', '800', ['test'])
        self.assertEqual(r['本周支出'], '20.00')
        self.assertEqual(r['已排除测试记录数'], 1)

    def test_page_duplicates_but_not_same_amount_different_ids(self):
        a = bill('a', '20')
        r = weekly.summarize([a, a, bill('b', '20')], '2026-10-13')
        self.assertEqual(r['本周支出'], '40.00')
        self.assertEqual(r['重复返回去重数'], 1)

    def test_conflicting_same_id_stops_report(self):
        with self.assertRaises(ValueError):
            weekly.summarize([bill('a', '20'), bill('a', '30')], '2026-10-13')

    def test_multiselect_not_double_counted(self):
        r = weekly.summarize([bill('a', '30', categories=['饮食', '生活花费'])], '2026-10-13')
        self.assertEqual(r['本周分类支出'], {'多分类待核对': '30.00'})

    def test_missing_money_remains_pending(self):
        r = weekly.summarize([bill('a', ''), bill('b', '15')], '2026-10-13', '800')
        self.assertFalse(r['统计完整'])
        self.assertEqual(r['本周支出'], '15.00')
        self.assertEqual(r['本周待核对记录ID'], ['a'])
        self.assertIsNone(r['本周剩余额度'])
        self.assertIsNone(r['预算使用率百分比'])

    def test_zero_budget_not_missing_and_overrun_clamped(self):
        rows = [bill('a', '10')]
        no_budget = weekly.summarize(rows, '2026-10-13')
        zero = weekly.summarize(rows, '2026-10-13', '0')
        self.assertIsNone(no_budget['每周预算'])
        self.assertEqual(zero['本周剩余额度'], '0.00')
        self.assertEqual(zero['本周超支'], '10.00')
        self.assertIsNone(zero['预算使用率百分比'])

    def test_cutoff_and_local_day_conversion(self):
        rows = [bill('before', '12', at='2026-10-12T16:30:00Z'),
                bill('after', '25', at='2026-10-13T23:00:00+08:00'),
                bill('lastweek', '10', at='2026-10-11T20:00:00+08:00')]
        r = weekly.summarize(rows, '2026-10-13T22:00:00+08:00')
        self.assertEqual(r['今日支出'], '12.00')
        self.assertEqual(r['本周支出'], '12.00')

    def test_incomplete_paging_rejected(self):
        with self.assertRaises(ValueError):
            weekly.summarize({'data': {'items': [bill('a', '10')], 'has_more': True}}, '2026-10-13')

    def test_sunday_has_no_remaining_daily_division(self):
        r = weekly.summarize([bill('a', '100', at='2026-10-18T12:00:00+08:00')], '2026-10-18', '700')
        self.assertEqual(r['明天至周日天数'], 0)
        self.assertIsNone(r['后续每日参考'])
        self.assertEqual(r['下周每日参考'], '100.00')

    def test_week_across_month_uses_week_budget(self):
        rows = [bill('a', '10', at='2026-09-30'), bill('b', '20', at='2026-10-01')]
        r = weekly.summarize(rows, '2026-10-01', '700')
        self.assertEqual(r['本周起始'], '2026-09-28')
        self.assertEqual(r['本周剩余额度'], '670.00')

    def test_invalid_budget_cannot_become_zero(self):
        for b in ('-10', 'NaN', '', True):
            with self.subTest(budget=b), self.assertRaises(ValueError):
                weekly.summarize([], '2026-10-13', b)


if __name__ == '__main__':
    unittest.main()
