"""Normalize lark-cli Base v3 NDJSON rows for this skill's offline helpers."""
from copy import deepcopy

FIELDS = ("日期", "文本内容", "收支类型", "金额", "具体花费项目", "消费类型")


def normalize_record(row):
    """Convert only data shape. Never infer missing type, amount or date."""
    if not isinstance(row, dict) or not isinstance(row.get("record_id"), str) or not row["record_id"]:
        raise ValueError("Missing record_id")
    source = row.get("fields", row)
    if not isinstance(source, dict):
        raise ValueError("Invalid record fields")
    fields = {name: deepcopy(source.get(name)) for name in FIELDS}
    kind = fields["收支类型"]
    if isinstance(kind, list):
        fields["收支类型"] = kind[0] if len(kind) == 1 and kind[0] in ("收入", "支出") else None
    elif kind not in ("收入", "支出"):
        fields["收支类型"] = None
    return {"record_id": row["record_id"], "fields": fields}
