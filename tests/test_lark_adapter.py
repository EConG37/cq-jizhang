"""CLI v3 shape adapter, with real offline repair/report integration."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "cq-jizhang/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = load("lark_adapter")
repair = load("ocr_repair")
summary = load("weekly_summary")


class AdapterTests(unittest.TestCase):
    def row(self, kind=None, amount=28.5):
        return {"record_id": "rec1", "日期": "2026-10-13T12:00:00.000+08:00",
                "文本内容": "午餐实付28.50元", "收支类型": ["支出"] if kind is None else kind,
                "金额": amount, "具体花费项目": "午餐", "消费类型": ["饮食"]}

    def test_flat_expense_and_canonical_form_match(self):
        normalized = adapter.normalize_record(self.row())
        self.assertEqual(normalized["fields"]["收支类型"], "支出")
        self.assertEqual(normalized, adapter.normalize_record(normalized))

    def test_income_is_preserved(self):
        self.assertEqual(adapter.normalize_record(self.row(["收入"]))["fields"]["收支类型"], "收入")

    def test_ambiguous_or_unknown_type_remains_pending(self):
        for kind in ([], ["收入", "支出"], ["未知"], "unknown"):
            normalized = adapter.normalize_record(self.row(kind))
            self.assertIsNone(normalized["fields"]["收支类型"])
            self.assertFalse(summary.summarize([normalized], "2026-10-13", 800)["统计完整"])

    def test_missing_type_is_not_defaulted_to_expense(self):
        row = self.row()
        del row["收支类型"]
        self.assertIsNone(adapter.normalize_record(row)["fields"]["收支类型"])

    def test_zero_date_and_categories_are_not_reinterpreted(self):
        row = self.row(amount=0)
        normalized = adapter.normalize_record(row)
        self.assertEqual(normalized["fields"]["金额"], 0)
        self.assertEqual(normalized["fields"]["日期"], row["日期"])
        self.assertEqual(normalized["fields"]["消费类型"], ["饮食"])

    def test_normalization_does_not_mutate_or_share_lists(self):
        row = self.row()
        before = deepcopy(row)
        normalized = adapter.normalize_record(row)
        normalized["fields"]["消费类型"].append("零食")
        self.assertEqual(row, before)

    def test_missing_record_identity_is_rejected(self):
        row = self.row()
        del row["record_id"]
        with self.assertRaises(ValueError):
            adapter.normalize_record(row)

    def test_cli_repair_then_report_does_not_count_income_as_budget(self):
        row = self.row(amount=None)
        record = adapter.normalize_record(row)
        proposal = {"record_id": "rec1", "ocr_sha256": repair.ocr_hash(row["文本内容"]),
                    "decision": "ready", "amount": "28.50", "reason": "single final payment",
                    "evidence": {"amount": "实付28.50元"}}
        plan = repair.plan_repair(record, proposal, age_seconds=121)
        self.assertEqual(plan["status"], "ready")
        record["fields"].update(plan["fields"])  # simulated readback, not a live CLI write
        income = self.row(["收入"], amount=1000)
        income["record_id"] = "rec2"
        result = summary.summarize([record, adapter.normalize_record(income)], "2026-10-13", 800)
        self.assertEqual(result["本周支出"], "28.50")
        self.assertEqual(result["本周收入"], "1000.00")
        self.assertEqual(result["本周剩余额度"], "771.50")


if __name__ == "__main__":
    unittest.main()
