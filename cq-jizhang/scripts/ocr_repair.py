"""Offline guard for model-proposed OCR repairs; never calls Feishu or a model."""
import hashlib
import math
import re
from decimal import Decimal, InvalidOperation

TARGETS = ("金额", "具体花费项目", "消费类型")
CATEGORIES = frozenset(("饮食", "交通", "生活花费", "零食", "会员费", "无匹配类别"))


def text_value(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(x, dict) and isinstance(x.get("text"), str) for x in value):
        return "".join(x["text"] for x in value)
    return ""


def ocr_hash(ocr):
    return hashlib.sha256(ocr.encode("utf-8")).hexdigest()


def blank(value):
    return value is None or value == [] or (isinstance(value, str) and not value.strip())


def money(value):
    if isinstance(value, bool):
        raise ValueError("invalid amount")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid amount") from None
    if not result.is_finite() or result < 0:
        raise ValueError("invalid amount")
    try:
        if result != result.quantize(Decimal("0.01")):
            raise ValueError("invalid amount")
    except InvalidOperation:
        raise ValueError("invalid amount") from None
    return result


def plan_repair(record, proposal, *, age_seconds, grace_seconds=120, categories=CATEGORIES):
    """Use a freshly re-read record. Returns ready fields or a non-writing reason.
    This is a guard, not proof of semantic extraction or atomic compare-and-swap.
    """
    def result(status, reason, fields=None):
        return {"status": status, "record_id": record.get("record_id"),
                "reason": reason, "fields": fields or {}}

    fields = record.get("fields")
    if not record.get("record_id") or not isinstance(fields, dict):
        return result("pending", "record identity or fields missing")
    ocr = text_value(fields.get("文本内容"))
    if not ocr.strip():
        return result("pending", "OCR missing")
    if fields.get("收支类型") not in ("支出", "收入"):
        return result("pending", "income/expense type needs review")
    amount = fields.get("金额")
    if not blank(amount):
        try:
            money(amount)
        except ValueError:
            return result("pending", "existing nonblank amount invalid; do not overwrite")
    missing = [key for key in TARGETS if blank(fields.get(key))]
    if not missing:
        return result("complete", "native or manual values already present")
    if age_seconds is None:
        return result("waiting", "save first_seen_at and retry on a later run")
    if isinstance(age_seconds, bool) or not isinstance(age_seconds, (int, float)) or not math.isfinite(age_seconds) or age_seconds < 0:
        return result("pending", "invalid observation age")
    if grace_seconds < 0 or age_seconds < grace_seconds:
        return result("waiting", "native processing grace window")
    if not isinstance(proposal, dict) or proposal.get("decision") != "ready":
        return result("pending", "extraction ambiguous or unavailable")
    if proposal.get("record_id") != record["record_id"]:
        return result("stale", "record identity changed")
    if proposal.get("ocr_sha256") != ocr_hash(ocr):
        return result("stale", "OCR changed; discard proposal")
    if not isinstance(proposal.get("reason"), str) or not proposal["reason"].strip():
        return result("pending", "extraction rationale missing")
    evidence = proposal.get("evidence")
    if not isinstance(evidence, dict):
        return result("pending", "OCR evidence missing")

    patch = {}
    for key in missing:
        name = {"金额": "amount", "具体花费项目": "project", "消费类型": "category"}[key]
        quote = evidence.get(name)
        if not isinstance(quote, str) or not quote.strip() or quote not in ocr:
            return result("pending", "evidence must be an exact OCR substring")
        value = proposal.get(name)
        if key == "金额":
            try:
                parsed = money(value)
            except ValueError:
                return result("pending", "invalid proposed amount")
            tokens = re.findall(r"(?<![0-9.])(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:[.][0-9]{1,2})?(?![0-9.])", quote)
            if not any(Decimal(token.replace(",", "")) == parsed for token in tokens):
                return result("pending", "amount does not match quoted OCR digits")
            numeric = float(parsed)
            if not math.isfinite(numeric) or Decimal(str(numeric)) != parsed:
                return result("pending", "amount cannot be represented safely by this API adapter")
            patch[key] = numeric
        elif key == "具体花费项目":
            if not isinstance(value, str) or not value.strip() or len(value) > 120:
                return result("pending", "project missing or too long")
            patch[key] = value.strip()
        else:
            if not isinstance(value, str) or value not in categories:
                return result("pending", "category not in actual schema choices")
            patch[key] = [value]
    return result("ready", "patch missing fields on this existing record only", patch)
