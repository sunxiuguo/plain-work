import csv
import io
import json
import unittest
from reporting.invoices import REPORT_COLUMNS, export_invoices, report_rows, visible_invoices

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


    def test_admin_sees_only_own_tenant(self):
        for tenant, expected_id in (("a", "INV-A"), ("b", "INV-B")):
            with self.subTest(tenant=tenant):
                admin = {"tenant_id": tenant, "is_admin": True}
                self.assertEqual(
                    [row["invoice_id"] for row in visible_invoices(ROWS, admin)],
                    [expected_id],
                )

    def test_all_reports_respect_tenant_boundary(self):
        for is_admin in (False, True):
            user = {"tenant_id": "a", "is_admin": is_admin}
            with self.subTest(is_admin=is_admin):
                self.assertEqual(
                    [row["invoice_id"] for row in report_rows(ROWS, user)],
                    ["INV-A"],
                )
                for format in ("json", "csv"):
                    with self.subTest(format=format):
                        output = export_invoices(ROWS, user, format)
                        rows = (
                            json.loads(output) if format == "json"
                            else list(csv.DictReader(io.StringIO(output, newline="")))
                        )
                        self.assertEqual(
                            [row["invoice_id"] for row in rows], ["INV-A"]
                        )

    def test_csv_columns_and_integer_money(self):
        rows = list(csv.reader(io.StringIO(
            export_invoices(ROWS, MEMBER, "csv"), newline=""
        )))
        self.assertEqual(rows, [
            list(REPORT_COLUMNS),
            ["INV-A", "Sample One", "1000", "125", "1125"],
        ])

    def test_csv_preserves_special_customer_characters(self):
        customer = '合成客户, "Quoted"\nSecond line\r\nThird line'
        invoices = [dict(ROWS[0], customer=customer)]
        rows = list(csv.DictReader(io.StringIO(
            export_invoices(invoices, MEMBER, "csv"), newline=""
        )))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["customer"], customer)

    def test_csv_keeps_large_and_negative_cents_exact(self):
        invoices = [dict(ROWS[0], net_cents=10 ** 30 + 1, tax_cents=-2)]
        row = next(csv.DictReader(io.StringIO(
            export_invoices(invoices, MEMBER, "csv"), newline=""
        )))
        self.assertEqual(row["net_cents"], str(10 ** 30 + 1))
        self.assertEqual(row["tax_cents"], "-2")
        self.assertEqual(row["total_cents"], str(10 ** 30 - 1))

    def test_empty_csv_retains_header(self):
        for invoices in ([], [ROWS[1]]):
            with self.subTest(invoices=invoices):
                rows = list(csv.reader(io.StringIO(
                    export_invoices(invoices, MEMBER, "csv"), newline=""
                )))
                self.assertEqual(rows, [list(REPORT_COLUMNS)])

    def test_json_serialization_stays_compatible(self):
        invoices = [dict(ROWS[0], customer='合成客户, "Quoted"\nSecond line')]
        expected = json.dumps(
            report_rows(invoices, MEMBER), ensure_ascii=False, sort_keys=True
        )
        self.assertEqual(export_invoices(invoices, MEMBER), expected)
        self.assertEqual(export_invoices(invoices, MEMBER, "json"), expected)


if __name__ == "__main__":
    unittest.main()
