"""Meaningful offline guards; no Feishu integration claims."""
import copy
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "cq-jizhang/scripts/ocr_repair.py"
SPEC = importlib.util.spec_from_file_location("ocr_repair", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.record = {"record_id": "rec1", "fields": {
            "日期": 1700000000000, "文本内容": "餐厅午餐 原价38.50元 优惠10元 实付28.50元",
            "收支类型": "支出", "金额": None, "具体花费项目": "", "消费类型": []}}
        self.proposal = {"record_id": "rec1", "ocr_sha256": MODULE.ocr_hash(self.record["fields"]["文本内容"]),
            "decision": "ready", "amount": "28.50", "project": "餐厅午餐", "category": "饮食",
            "evidence": {"amount": "实付28.50元", "project": "餐厅午餐", "category": "餐厅午餐"},
            "reason": "single clear final payment"}
        self.before = copy.deepcopy(self.record)

    def plan(self, **kwargs):
        return MODULE.plan_repair(self.record, self.proposal, age_seconds=kwargs.pop("age_seconds", 121), **kwargs)

    def test_full_patch_is_only_three_fields_and_no_mutation(self):
        result = self.plan()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["fields"], {"金额": 28.5, "具体花费项目": "餐厅午餐", "消费类型": ["饮食"]})
        self.assertEqual(self.record, self.before)

    def test_partial_completion_preserves_existing_values(self):
        self.record["fields"].update({"金额": 9.99, "具体花费项目": "人工确认的午餐"})
        self.assertEqual(self.plan()["fields"], {"消费类型": ["饮食"]})

    def test_native_finished_means_no_write(self):
        self.record["fields"].update({"金额": 28.5, "具体花费项目": "午餐", "消费类型": ["饮食"]})
        self.assertEqual(self.plan()["status"], "complete")
        self.assertEqual(self.plan()["fields"], {})

    def test_zero_is_valid_not_missing(self):
        self.record["fields"]["金额"] = 0
        self.assertNotIn("金额", self.plan()["fields"])

    def test_invalid_nonblank_amount_is_not_overwritten(self):
        for bad in ("未知", -3, True, "NaN", "1e1000", "3.001"):
            self.record["fields"]["金额"] = bad
            self.assertEqual(self.plan()["status"], "pending")

    def test_grace_period_delays_write(self):
        for age in (0, 119, None):
            self.assertEqual(self.plan(age_seconds=age)["status"], "waiting")

    def test_invalid_age_is_not_ready(self):
        for age in (-1, float("nan"), float("inf"), True):
            self.assertEqual(self.plan(age_seconds=age)["status"], "pending")

    def test_changed_ocr_discards_old_proposal(self):
        self.record["fields"]["文本内容"] += " 追加另一笔实付50元"
        self.assertEqual(self.plan()["status"], "stale")

    def test_other_record_cannot_be_patched(self):
        self.proposal["record_id"] = "another-record"
        self.assertEqual(self.plan()["status"], "stale")

    def test_unsupported_evidence_blocks_write(self):
        self.proposal["evidence"]["amount"] = "实付18元"
        self.assertEqual(self.plan()["status"], "pending")

    def test_hallucinated_amount_blocks_write(self):
        self.proposal["amount"] = "38.50"
        self.assertEqual(self.plan()["status"], "pending")

    def test_unknown_category_blocks_write(self):
        self.proposal["category"] = "餐饮"
        self.assertEqual(self.plan()["status"], "pending")

    def test_schema_choices_are_runtime_configurable(self):
        self.proposal["category"] = "餐饮"
        result = self.plan(categories={"餐饮"})
        self.assertEqual(result["fields"]["消费类型"], ["餐饮"])

    def test_ambiguous_model_decision_never_writes(self):
        self.proposal.update(decision="pending", reason="two payments")
        self.assertEqual(self.plan()["fields"], {})

    def test_income_type_is_preserved(self):
        self.record["fields"]["收支类型"] = "收入"
        self.assertEqual(self.plan()["status"], "ready")
        self.assertNotIn("收支类型", self.plan()["fields"])

    def test_missing_income_expense_type_blocks_write(self):
        self.record["fields"]["收支类型"] = None
        self.assertEqual(self.plan()["status"], "pending")

    def test_rich_text_ocr_is_supported(self):
        ocr = self.record["fields"]["文本内容"]
        self.record["fields"]["文本内容"] = [{"text": ocr[:4]}, {"text": ocr[4:]}]
        self.assertEqual(self.plan()["status"], "ready")

    def test_missing_ocr_blocks_write(self):
        self.record["fields"]["文本内容"] = ""
        self.assertEqual(self.plan()["status"], "pending")

    def test_unsafe_float_precision_blocks_write(self):
        self.record["fields"]["文本内容"] = "餐厅午餐 实付10000000000000000.01元"
        self.proposal.update(ocr_sha256=MODULE.ocr_hash(self.record["fields"]["文本内容"]), amount="10000000000000000.01")
        self.proposal["evidence"]["amount"] = "实付10000000000000000.01元"
        self.assertEqual(self.plan()["status"], "pending")

    def test_comma_money_is_supported(self):
        self.record["fields"]["文本内容"] = "餐厅午餐 实付1,028.50元"
        self.proposal.update(ocr_sha256=MODULE.ocr_hash(self.record["fields"]["文本内容"]), amount="1028.50")
        self.proposal["evidence"]["amount"] = "实付1,028.50元"
        self.assertEqual(self.plan()["fields"]["金额"], 1028.5)


if __name__ == "__main__":
    unittest.main()
