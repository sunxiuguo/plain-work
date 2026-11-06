"""Independent fixed artifact checks. Run with a completed fixture directory."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "reporting" / "invoices.py"
spec = importlib.util.spec_from_file_location("submission", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
columns = ["invoice_id", "customer", "net_cents", "tax_cents", "total_cents"]
rows = [
    {"invoice_id": "A-1", "tenant_id": "a", "customer": 'Synthetic, "quoted"\nname', "net_cents": 1901, "tax_cents": 199},
    {"invoice_id": "B-1", "tenant_id": "b", "customer": "Other synthetic tenant", "net_cents": 999, "tax_cents": 0},
]
checks = []

def check(name, condition):
    checks.append({"name": name, "passed": bool(condition)})

for admin in (False, True):
    user = {"tenant_id": "a", "is_admin": admin}
    expected = [{"invoice_id": "A-1", "customer": rows[0]["customer"], "net_cents": 1901, "tax_cents": 199, "total_cents": 2100}]
    text = mod.export_invoices(rows, user)
    check(f"json-content-admin-{admin}", json.loads(text) == expected)
    if not admin:
        check("json-byte-compatibility", text == json.dumps(expected, ensure_ascii=False, sort_keys=True))
    reader = csv.DictReader(io.StringIO(mod.export_invoices(rows, user, "csv")))
    parsed = list(reader)
    check(f"csv-columns-admin-{admin}", reader.fieldnames == columns)
    check(f"csv-round-trip-and-scope-admin-{admin}", parsed == [{key: str(value) for key, value in expected[0].items()}])
empty_user = {"tenant_id": "empty", "is_admin": True}
reader = csv.DictReader(io.StringIO(mod.export_invoices(rows, empty_user, "csv")))
check("empty-admin-csv", list(reader) == [] and reader.fieldnames == columns)
check("empty-admin-json", json.loads(mod.export_invoices(rows, empty_user)) == [])
check("empty-input-csv", next(csv.reader(io.StringIO(mod.export_invoices([], empty_user, "csv")))) == columns)
try:
    mod.export_invoices(rows, empty_user, "pdf")
except ValueError:
    check("unsupported-format", True)
else:
    check("unsupported-format", False)
print(json.dumps(checks, indent=2))
if not all(row["passed"] for row in checks):
    raise SystemExit(1)
