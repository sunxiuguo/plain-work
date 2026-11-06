# 已完成

- 新增 CSV 导出：调用 `export_invoices(invoices, user, "csv")`，返回 CSV 文本。列顺序沿用 `REPORT_COLUMNS`；使用 Python 标准库处理客户名称中的逗号、引号和换行，金额继续使用整数分，空报表也包含列标题。
- 修复跨租户访问：管理员与普通成员都只能读取自己租户的发票，管理员仍可读取本租户数据；JSON 和 CSV 共用这条过滤逻辑。
- 保持原有默认 JSON 格式及序列化方式不变，未添加依赖，也未发布。

新增 7 个回归测试，覆盖管理员租户隔离及两种导出、CSV 列顺序与金额、特殊字符、超大与负数金额、空 CSV，以及 JSON 文本兼容性。

实际检查：先运行 `python -m unittest discover -s tests -p test_invoices.py -v`，再运行 README 要求的完整单元测试 `python -m unittest discover -s tests -v`，均为 12 项通过。该项目目前只有这一个测试文件，因此两次覆盖的测试相同。实际命令与输出保存在 `commands.log`。
