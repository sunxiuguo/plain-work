import json
import unittest
from reporting.invoices import export_invoices, report_rows, visible_invoices

ROWS = [
    {"invoice_id": "INV-A", "tenant_id": "a", "customer": "Sample One", "net_cents": 1000, "tax_cents": 125},
    {"invoice_id": "INV-B", "tenant_id": "b", "customer": "Sample Two", "net_cents": 2000, "tax_cents": 250},
]
MEMBER = {"tenant_id": "a", "is_admin": False}


class InvoiceTests(unittest.TestCase):
    def test_member_sees_own_tenant(self):
        self.assertEqual([r["invoice_id"] for r in visible_invoices(ROWS, MEMBER)], ["INV-A"])

    def test_total_uses_integer_cents(self):
        self.assertEqual(report_rows(ROWS, MEMBER)[0]["total_cents"], 1125)

    def test_default_json(self):
        result = json.loads(export_invoices(ROWS, MEMBER))
        self.assertEqual(result, report_rows(ROWS, MEMBER))

    def test_unknown_format(self):
        with self.assertRaises(ValueError):
            export_invoices(ROWS, MEMBER, "pdf")

    def test_empty_report(self):
        self.assertEqual(export_invoices([], MEMBER), "[]")


if __name__ == "__main__":
    unittest.main()
