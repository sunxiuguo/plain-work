import csv
import io
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

    def test_admin_sees_only_own_tenant(self):
        for tenant, expected in (("a", [ROWS[0]]), ("b", [ROWS[1]]), ("missing", [])):
            with self.subTest(tenant=tenant):
                admin = {"tenant_id": tenant, "is_admin": True}
                self.assertEqual(visible_invoices(ROWS, admin), expected)

    def test_admin_exports_only_own_tenant(self):
        for tenant, expected_id in (("a", "INV-A"), ("b", "INV-B")):
            admin = {"tenant_id": tenant, "is_admin": True}
            for format in ("json", "csv"):
                with self.subTest(tenant=tenant, format=format):
                    output = export_invoices(ROWS, admin, format)
                    if format == "json":
                        rows = json.loads(output)
                    else:
                        rows = list(csv.DictReader(io.StringIO(output, newline="")))
                    self.assertEqual([row["invoice_id"] for row in rows], [expected_id])
                    self.assertNotIn("tenant_id", rows[0])

    def test_csv_columns_and_integer_cents(self):
        rows = list(csv.reader(io.StringIO(export_invoices(ROWS, MEMBER, "csv"), newline="")))
        self.assertEqual(rows, [
            ["invoice_id", "customer", "net_cents", "tax_cents", "total_cents"],
            ["INV-A", "Sample One", "1000", "125", "1125"],
        ])

    def test_csv_preserves_special_customer_names(self):
        names = ["Comma, Name", 'A "quoted" name', "Line one\nLine two", "甲,\"乙\"\r\n丙"]
        invoices = [dict(ROWS[0], customer=name) for name in names]
        output = export_invoices(invoices, MEMBER, "csv")
        rows = list(csv.DictReader(io.StringIO(output, newline="")))
        self.assertEqual([row["customer"] for row in rows], names)

    def test_csv_keeps_large_and_negative_integer_cents(self):
        for net, tax in ((9007199254740993, 2), (-1000, -125), (0, 0)):
            with self.subTest(net=net, tax=tax):
                invoices = [dict(ROWS[0], net_cents=net, tax_cents=tax)]
                output = export_invoices(invoices, MEMBER, "csv")
                row = next(csv.DictReader(io.StringIO(output, newline="")))
                self.assertEqual([row[key] for key in ("net_cents", "tax_cents", "total_cents")],
                                 [str(net), str(tax), str(net + tax)])

    def test_empty_csv_has_header(self):
        for invoices, user in (([], MEMBER), (ROWS, {"tenant_id": "missing", "is_admin": True})):
            with self.subTest(invoices=invoices):
                self.assertEqual(export_invoices(invoices, user, "csv"),
                                 "invoice_id,customer,net_cents,tax_cents,total_cents\r\n")

    def test_json_serialization_compatibility(self):
        invoices = [dict(ROWS[0], customer="客户,\"甲\"\n乙")]
        expected = ('[{"customer": "客户,\\"甲\\"\\n乙", "invoice_id": "INV-A", '
                    '"net_cents": 1000, "tax_cents": 125, "total_cents": 1125}]')
        self.assertEqual(export_invoices(invoices, MEMBER), expected)
        self.assertEqual(export_invoices(invoices, MEMBER, "json"), expected)


if __name__ == "__main__":
    unittest.main()
