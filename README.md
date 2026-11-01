# CQ-jizhang｜让 Agent 带你配置飞书截图记账

把这个仓库链接发给你的 Agent，它会帮你安装 Skill，再一步一步完成飞书账本、iPhone 快捷指令、OCR 补全和预算日报的配置。

## 直接发给 Agent

```text
请阅读 https://github.com/EConG37/cq-jizhang 的 README.md 和 INSTALL.md，
将 cq-jizhang Skill 安装到当前用户的全局技能目录，再读取其中的 SKILL.md，
从零带我配置飞书截图记账。已有配置请复用，每次只带我完成当前一步。
App Secret 和访问令牌由我在安全入口填写，不要让我发到聊天里。
写入、读取及任务投递分别实测后，再报告哪些功能已启用。
```

安装说明：[INSTALL.md](INSTALL.md) · [完整配置教程](cq-jizhang/assets/公开教程.md) · [隐私检查](PRIVACY.md)

## 能做什么

- iPhone 截图后 OCR，把文字保存到你自己的飞书多维表格。
- 飞书字段捷径先提取金额、项目和分类；仍有缺项时，由你当前的 Agent 补原记录。
- 文字补记收入或支出，按周预算生成日报，周日附周报与下周建议。
- 分别检查手机写入、Agent 读写、真实调度和消息投递，保存进度后继续配置。

## 准备条件

需要飞书账号、可创建和授权自建应用的权限、iPhone 的「快捷指令」，以及能读取本地 Skill 并执行命令或调用授权工具的 Agent。辅助统计脚本使用 Python 3.10+ 标准库；没有 Python 时可由宿主计算工具完成相同统计。

桌面端默认通过官方 [飞书 CLI](https://github.com/larksuite/cli) 读写账本，已有安装会复用。日报需要宿主真实支持后台任务；桌面方案通常需要电脑保持在线。其他 Agent 的导入入口和云端执行能力须按实际版本检查。

## 第一次使用

安装完成后说：

```text
使用 $cq-jizhang，从零带我配置飞书截图记账，验证成功后开启日报周报。
```

先整份复制[配套账本模板](https://zk5ckzju3h.feishu.cn/base/PhL3bQFKBa6jaks44mpcaMPMnbc?table=tblQkH2HRaCsoqbV&view=vewxPd2biE)到自己的飞书云文档，保留六列、三个视图和仪表盘；已有自己的账本可直接复用。Agent 应使用你的副本，不向模板原件写账。模板无法复制时，可按[空白账本说明](cq-jizhang/references/blank-ledger.md)建立备用账本，再按[快捷指令创建步骤](cq-jizhang/references/shortcut-build.md)引导手机配置。

安装 Skill 本身不会登录飞书、写账、收集数据或创建定时任务。账本与配置由使用者自己保存。截图默认记录支出，收入单独告诉 Agent，不抵扣周消费预算。飞书和 Agent 的额度、费用以各自账号为准。

## 下载与验证

[下载 Skill ZIP](https://github.com/EConG37/cq-jizhang/releases/latest)；解压后只有 `cq-jizhang/` 技能目录。仓库源码另外包含离线测试、打包工具及发布说明。

```text
python -m unittest discover -s tests -p "test_*.py"
python scripts/audit_release.py
python scripts/package_release.py --version 3.7.1
```

离线检查不能代替每位使用者的手机、飞书权限和定时投递实测。公开版的空白账本和手工快捷指令流程尚未完成独立 iPhone 全链路验收。

仓库原创内容采用 [MIT License](LICENSE)。飞书、Apple 及其他平台的产品和官方资料遵循各自条款。
