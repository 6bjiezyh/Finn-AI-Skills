#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime
from typing import Dict, List, Tuple

BASE = "https://open.feishu.cn/open-apis"


def http_json(method: str, url: str, headers=None, body=None, timeout=30):
    headers = headers or {}
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = {**headers, "Content-Type": "application/json; charset=utf-8"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"raw": raw}
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {payload}") from e


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    url = f"{BASE}/auth/v3/tenant_access_token/internal"
    data = http_json("POST", url, body={"app_id": app_id, "app_secret": app_secret})
    if data.get("code") != 0:
        raise RuntimeError(f"Get tenant_access_token failed: {data}")
    return data["tenant_access_token"]


def list_records(app_token: str, table_id: str, token: str) -> List[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    all_items: List[dict] = []
    page_token = None

    while True:
        q = {"page_size": 500}
        if page_token:
            q["page_token"] = page_token
        url = f"{BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records?{urllib.parse.urlencode(q)}"
        data = http_json("GET", url, headers=headers)
        if data.get("code") != 0:
            raise RuntimeError(f"List records failed: {data}")
        payload = data.get("data", {})
        items = payload.get("items", [])
        all_items.extend(items)
        if not payload.get("has_more"):
            break
        page_token = payload.get("page_token")
    return all_items


def update_record(app_token: str, table_id: str, record_id: str, token: str, fields: dict) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    data = http_json("PUT", url, headers=headers, body={"fields": fields})
    if data.get("code") != 0:
        raise RuntimeError(f"Update record failed(record_id={record_id}): {data}")


def batch_create(app_token: str, table_id: str, token: str, rows: List[dict]) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
    data = http_json("POST", url, headers=headers, body={"records": [{"fields": r} for r in rows]})
    if data.get("code") != 0:
        raise RuntimeError(f"Batch create failed: {data}")


def normalize_fields(row: Dict[str, str]) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for key, value in row.items():
        if value is None:
            continue
        v = str(value).strip()
        if not v:
            continue
        if key == "评分":
            try:
                out[key] = float(v)
                continue
            except ValueError:
                pass
        if key == "关键词":
            parts = [p.strip() for p in v.replace("，", ",").split(",") if p.strip()]
            out[key] = parts if parts else [v]
            continue
        if key == "日期":
            try:
                ts_ms = int(datetime.strptime(v, "%Y-%m-%d").timestamp() * 1000)
                out[key] = ts_ms
                continue
            except ValueError:
                pass
        out[key] = v
    return out


def read_csv_rows(csv_path: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not (row.get("选题ID", "").strip() or row.get("选题标题", "").strip()):
                continue
            rows.append(normalize_fields(row))
    return rows


def index_existing(records: List[dict], key_field: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for rec in records:
        fields = rec.get("fields", {})
        key = fields.get(key_field)
        rid = rec.get("record_id")
        if isinstance(key, str) and key.strip() and isinstance(rid, str):
            out[key.strip()] = rid
    return out


def chunks(items: List[dict], size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def main():
    p = argparse.ArgumentParser(description="Upload topic CSV into Feishu Bitable (upsert by key field)")
    p.add_argument("--csv", required=True, help="Local CSV path")
    p.add_argument("--app-id", default=os.getenv("FEISHU_APP_ID"))
    p.add_argument("--app-secret", default=os.getenv("FEISHU_APP_SECRET"))
    p.add_argument("--app-token", default=os.getenv("FEISHU_APP_TOKEN"))
    p.add_argument("--table-id", default=os.getenv("FEISHU_TABLE_ID"))
    p.add_argument("--upsert-key", default="选题ID", help="Default uses 选题ID")
    p.add_argument("--batch-size", type=int, default=200)
    p.add_argument("--sleep-ms", type=int, default=100)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    required = {
        "app_id": args.app_id,
        "app_secret": args.app_secret,
        "app_token": args.app_token,
        "table_id": args.table_id,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"Missing config: {', '.join(missing)}")
        sys.exit(2)

    csv_rows = read_csv_rows(args.csv)
    if not csv_rows:
        print("CSV has no valid rows")
        return

    token = get_tenant_access_token(args.app_id, args.app_secret)
    existing = list_records(args.app_token, args.table_id, token)
    existing_idx = index_existing(existing, args.upsert_key)

    to_create: List[dict] = []
    to_update: List[Tuple[str, dict]] = []

    for row in csv_rows:
        key = str(row.get(args.upsert_key, "")).strip()
        rid = existing_idx.get(key) if key else None
        if rid:
            to_update.append((rid, row))
        else:
            to_create.append(row)

    print(f"CSV rows: {len(csv_rows)}")
    print(f"Existing records: {len(existing)}")
    print(f"Will update: {len(to_update)}")
    print(f"Will create: {len(to_create)}")

    if args.dry_run:
        return

    for record_id, fields in to_update:
        update_record(args.app_token, args.table_id, record_id, token, fields)
        time.sleep(args.sleep_ms / 1000)

    for batch in chunks(to_create, args.batch_size):
        batch_create(args.app_token, args.table_id, token, batch)
        time.sleep(args.sleep_ms / 1000)

    print("Upload completed")


if __name__ == "__main__":
    main()
