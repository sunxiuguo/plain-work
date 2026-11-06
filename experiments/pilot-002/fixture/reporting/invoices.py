"""Small invoice report. Monetary values are integer cents, never floats."""
import json

REPORT_COLUMNS = ("invoice_id", "customer", "net_cents", "tax_cents", "total_cents")


def visible_invoices(invoices, user):
    return [row for row in invoices if user["is_admin"] or row["tenant_id"] == user["tenant_id"]]


def report_rows(invoices, user):
    rows = []
    for source in visible_invoices(invoices, user):
        rows.append({
            "invoice_id": source["invoice_id"],
            "customer": source["customer"],
            "net_cents": source["net_cents"],
            "tax_cents": source["tax_cents"],
            "total_cents": source["net_cents"] + source["tax_cents"],
        })
    return rows


def export_invoices(invoices, user, format="json"):
    rows = report_rows(invoices, user)
    if format == "json":
        return json.dumps(rows, ensure_ascii=False, sort_keys=True)
    raise ValueError("unsupported export format")
