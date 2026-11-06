# 选择接入方式

官方资料核对日期：2026-11-06。支持情况可能随客户端与版本变化。
本项目实际验证的是本地文件修改/撤回工具与一次云端指令对照，**没有完成各客户端的原生加载验收**。

## AGENTS.md：先从一个项目试起

适合希望整个项目都采用这段工作约定的用户。先备份或提交原有文件，再用 README 中的预览/应用命令。

[官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
说明了全局到项目目录逐层加载；同目录的 `AGENTS.override.md` 优先于
`AGENTS.md`，默认项目指导总量上限为 32 KiB。因此文件写成功不等于实际
加载成功：检查当前位置、覆盖文件和总量，不要为了加载本片段擅自删除原规则。

用一个新的项目任务验收：让代理确认实际读到的约定，并完成一个有明确结果的小任务；
对照最终产物和实际工具调用，而不只听它说“我会遵守”。若表现变差就移除本片段。
本工具不会调整用户全局配置，也不会把安装成功描述成行为改进。

## Skills：适合按需使用，不应强制每轮触发

[技能概念](https://developers.openai.com/plugins/concepts/skills)和
[构建说明](https://developers.openai.com/plugins/build/skills)规定了元信息发现、
按需加载完整指令的方式。若只想在“帮我做判断”或“把这段话说清楚”时使用，
可由所用产品的技能创建流程把约定做成窄范围技能。

本版未安装或发布个人技能，不提供“必定自动触发”的承诺。不要同时把同一段内容
复制到全局指令、多个技能和每次提示中。官方也明确警告过宽触发、过细步骤和
每次必读全部材料会增加负担，见
[重新思考技能与提示词](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)。

已有相关方案值得先比较：

- [Compound Engineering ce-pov](https://github.com/EveryInc/compound-engineering-plugin/blob/main/docs/guides/ce-pov.md)：有依据地给建议，能查到的事实先查，不把判断流程变成每次必走步骤。
- [Humanizer-zh](https://github.com/op7418/Humanizer-zh/blob/main/SKILL.md)：中文表达与生造词、保留事实和确定程度。

本项目不是首个相关提示词方案。它尝试把表达、判断和执行范围放在一起，并公开
反例与不改善的对照结果。不以禁词计数代替用户是否理解、任务是否完成。

## Plugins：打包方式，不是新的权限或能力

[官方插件构建文档](https://developers.openai.com/plugins/build/plugins)支持打包
skills/MCP。含 lifecycle hooks 的插件目前不符合公共目录提交条件，需要手工
Codex desktop 安装。插件安装和启用不等于信任 hook；网页安装也不会替用户把
本地脚本部署到执行环境。

本版没有插件清单或 MCP 服务。若先证实这段约定在真实项目有收益，再决定是否
值得增加打包、安装、升级和兼容维护成本。无需为一段指令先运行一个服务。

## Hooks：只在明确支持的本地环境考虑

[官方 hooks 文档](https://learn.chatgpt.com/docs/hooks)列出以下重要区别：

- 本地 Codex CLI/App 的 `UserPromptSubmit` 可追加上下文；它不能降低指令层级或授予权限。
- `Stop` 的 block 会追加续跑提示，不是直接改写答案。反复阻止结束可能正好制造本项目要减少的循环；使用时需识别 `stop_hook_active` 并限制次数。
- `PreModelRequest` / `PostModelRequest` 只作诊断，不能据此宣称能修改上下文或阻断请求。
- `PostToolUse` 不能撤销已经发生的外部副作用。
- 多个配置来源的 hooks 会共同运行，不会自动互相替代。

云端 Work/dots 编排不运行本地配置、插件或目录中的命令 hooks。企业管理员的
远端 MCP managed hooks 是另一个受限场景，不能推导成个人账户可用。不要把本地
hook 安装教程称为能改变当前云端对话的方案。

本版刻意不提供 Stop 拦截器。若未来确有需要，先固定真实客户端版本，在合成环境
测试触发、停止、重复、崩溃和卸载，不直接拿生产任务试。

## 评估应与实际使用环境相同

参考[技能评估实践](https://developers.openai.com/blog/eval-skills)和
[harness-aware plugin evals](https://developers.openai.com/cookbook/examples/partners/harness_aware_plugin_evals/harness_aware_plugin_evals)。
API 单轮回答的改善不等于 Codex 多轮开发任务的改善。要保留实际产物、命令、失败
和安全反例，覆盖用户真正遇到的任务，不靠模型自评“更自然/更高效”。
