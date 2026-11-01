# 当前Agent通过飞书CLI接入

## 安装最后一步的CLI与账号检查

默认日报、周报、Agent补全使用飞书CLI；在复制模板、应用授权、快捷指令填参和手机OCR入表通过之后，作为安装最后一步说明此依赖，检查CLI安装、登录、账号一致与本人副本读写权限。手机截图入表使用快捷指令API，不依赖CLI。原生等效方案仅在用户明确选择且实测通过时作为例外，不因某个Agent厂商自动绕过清单。

检查分开记录：cli_verified（可执行）、auth_verified（登录有效）、account_match_verified（预期账号一致）、ledger_read_permission_verified（读取本人副本成功）、ledger_update_permission_verified（目标字段实际更新并读回成功）。前一项通过不自动推出后一项。

用auth status --json --verify核对实际identity、用户登录状态、token有效性和已授权范围。默认--as user，与用户复制/使用账本时选择的账号和组织核对；能访问共享账本或昵称相同都不是一致性的充分证据。能获取同一应用/同一组织下稳定身份标识时匹配；不同应用的open_id可能不同，不能直接比较而判错。无法可靠比对时，让用户在飞书/授权页面确认当前账号和组织，只问必要确认，不索要完整邮箱/手机号/身份ID，不把账号快照写进交付文件。

未登录/过期按最小权限完成授权后再检查；账号不一致先说明并授权正确账号，未经用户明确选择不静默换操作者。bot是应用身份，不能当“同一用户已登录”；用户明确采用bot时核对应用及副本授权，记录为应用模式，不把用户账号匹配标已验证。

检查CLI是否已有时先试版本并核对实际可执行路径；缺失再检查Node.js/npm及官方安装。已有版本支持当前读写命令就复用，不强制升级、重新安装或清空CLI配置。路径/宿主策略阻挡时先排查，不把不可执行错误当未安装。

本阶段应已有本人副本及手机文字入表验证；若尚未完成，先回到 [基础安装](onboarding.md) 对应步骤，不在开头新加CLI预检。schema及本人目标记录读取成功才标读取权限；API scope和文档ACL都要满足。更新权限先检查实际接口scope/编辑授权，再按 [备用验收](verification.md) 在适当记录上实际更新并读回；dry-run和登录成功不能证明可更新，金额AI字段可写性也需单独验证。

日报正式读取前要求账号匹配、登录有效和目标读取通过；自动补写前要求实际更新验收通过。当前账号不一致或读取失败时不启用正式日报，不为跑通而改写其他账号账本。

## 路由与用量

此路径供WorkBuddy、桌面Codex、ZCode以及其他可运行命令的Agent使用，也可供有执行环境的云端Agent使用。先确认具体执行模式及实际工具，不猜目录、按钮或调度能力。

优先使用正在运行且用户选定的Agent，不默认强制切到豆包工作，不为用本Skill另装或购买Agent。若宿主不明，先检查当前环境；仍不能确定再问必要的技术问题。消费设置依然只主动问每周预算。

推理路径：飞书CLI取OCR文字→当前Agent用自身会话/订阅/项目模型额度理解→飞书CLI更新原记录。CLI只读写，不调用字段AI重新提取、不代购模型、不私下调用另一个收费API。模型计费以该Agent实际账号和项目为准，不保证免费；不假定桌面Agent就是本地离线模型。通过这个外部Agent提取时不走飞书原生字段AI的推理调用，但飞书API本身仍有权限、频率和套餐限制。

飞书字段AI仍是优先主链路；缺项时用当前Agent兜底，执行 [OCR补全规则](ocr-fallback.md)。豆包工作原生路径继续可选；已选的当前Agent也用尽额度时，报告阻塞与待核对，不自动买额度或循环换平台。

| 运行端 | CLI必须在哪里 | 报告与在线条件 |
|---|---|---|
| WorkBuddy/ZCode/桌面Codex/其他桌面Agent | 该Agent实际能执行命令的电脑或其受管环境 | 检查真实后台调度；通常需电脑开机、未休眠、联网且Agent可执行 |
| 豆包工作 | 默认也检查实际执行端CLI；用户明确选择且实测通过原生等效方案才记录例外 | 按该账号真实云端任务和额度验收 |
| Coze云端＋官方本地工作目录 | 已连接并授权的本机，实测云端Agent可执行该CLI | 推理由所选Coze云端Agent完成；电脑与桌面连接服务须在线，仍需真实调度 |
| 纯云端执行/远程HTTP MCP | 实际云端沙箱/容器/服务器，不能只装用户电脑 | 检查CLI、运行阶段鉴权、飞书外网、持久状态和独立调度；云端对话任务不等于常驻日报服务 |

WorkBuddy官方支持导入本地Skill包并执行系统命令，但账户、版本及受管运行环境仍需实际检查。本包可在其添加技能入口导入；不假定读取Codex的全局路径。使用当前宿主支持的技能目录或导入界面，不硬编码任何人的本机路径。

## 引导次序

此参考在手机OCR入表成功后的安装最后阶段使用；已有账本直接接入/专项CLI排错可复用已完成基础进度。每轮只推进当前一步；复用已完成部分，不要求用户重装、重建应用或再输入业务偏好。

1. **当前环境**：确认宿主、桌面/云端位置、命令执行权限、网络和设置持久化。只确认模型可用，不索要模型密钥或承诺能查到账户余量。
2. **CLI检查**：执行lark-cli --version及相关--help。已安装则复用；缺失先检查Node.js/npm并按官方当前安装器安装。用户授权范围内执行，遇宿主系统安装权限门禁按实际要求处理；不会用静默强制选项跳过宿主审核。
3. **配置与登录**：检查应用配置、auth状态及与使用账本账号/组织的一致性；仅缺失/失效/不一致时引导对应初始化或授权。优先本人用户身份；bot仅在用户已选定应用身份时使用。手机应用凭据不一定等于CLI配置，不在聊天收Secret。已有Hermes/OpenClaw绑定环境遵循CLI提示用config bind，不能自动force-init新建平行应用。
4. **账本与schema**：解析已复制并完成手机入表验证的本人副本链接，确认真实Base/表ID及六列和分类选项。用实际账号最小范围读取本人副本，检查OCR及目标字段；分别记录读取/更新验收，不用模板可读或共享账本可读证明账号一致。权限缺失按当前命令所需授权及文档编辑权限修复；不能把旧v1记录scope硬套到CLI v3接口。
5. **备用更新测试**：用另行选取的有明确金额证据且缺项的记录先预览最小更新；基础手机测试任意OCR文本同步即可，不强制数字句子。备用验收时更新原record_id并读回；核对ignored_fields/record_not_found和延迟原生覆盖。用户已经要求调试及补原记录时继续执行该范围，不每笔问确认；遇真实高风险门禁先展示具体动作并取得相应批准，不自动加确认标志绕过。
6. **预算和任务**：按已有周预算继续，无则只问该问题。保存非敏感配置，选择实际可用调度器；分别记录手机文本入表、备用写回、样报、真实任务与本会话投递的验收；持久conversation_ref及同会话验证结果，不能把系统通知当原会话消息。若只可手动运行，标“手动补全可用，定时未启用”，不跳回强制豆包工作。

## CLI操作示例

下面按lark-cli命令形态示例说明；执行前必须核对当前安装版本的--help。示例中的副本ID必须换成本人真实值。安装器以 [官方仓库](https://github.com/larksuite/cli) 为准：

```text
npx @larksuite/cli@latest install
lark-cli --version
lark-cli auth status --json --verify
```

初始化只在缺少应用配置时执行lark-cli config init；新建应用路径用config init --new，在后台运行并把实际返回链接交给用户，不重新创建已有应用。需要Secret时本人在安全输入入口输入；支持stdin的命令不要把Secret置于参数、共享文件或日志。

授权选择当前Base读/更新命令实际所需scope；不默认--domain all，不要求通讯录或消息权限来修账。Agent发起用户授权应分两轮：

```text
lark-cli auth login --scope 实际所需scope --no-wait --json
lark-cli auth qrcode 原样verification_url --output ./feishu-auth.png
lark-cli auth login --device-code 本次device_code
```

先展示原样URL及PNG二维码，再等用户回复已授权，由Agent执行device-code完成登录。过期重新生成；状态JSON只记录身份/是否验证/错误，不能保存授权token或device_code到交付进度。auth status有效仍不代表有目标账本权限。

确认schema及读取本人记录：

```text
lark-cli base +field-list --base-token 本人Base标识 --table-id 本人table_id --as user
lark-cli base +record-list --base-token 本人Base标识 --table-id 本人table_id --field-id 日期 --field-id 文本内容 --field-id 收支类型 --field-id 金额 --field-id 具体花费项目 --field-id 消费类型 --format ndjson --output ./accounting-records.ndjson --as user
lark-cli base +record-get --base-token 本人Base标识 --table-id 本人table_id --record-id 目标record_id --format ndjson --output ./accounting-readback.ndjson --as user
```

路径参数用当前工作区相对路径。保留manifest并核对has_more=false才算范围读全；有截断时按当前版本支持的分页或日期分段继续读，不把默认最多2000条当全量。不要以调用飞书云端AI分析替代当前Agent的OCR推理。仅候选的必要OCR进入模型上下文，不将整个账本贴聊天；运行数据文件按用户宿主私有存储管理，不纳入技能ZIP、版本控制或公开教程。

CLI Base v3 NDJSON每行是平铺字段，收支单选也为数组，例如：
```json
{"record_id":"recExample","日期":"2026-10-13T12:00:00.000+08:00","文本内容":"午餐实付28.50元","收支类型":["支出"],"金额":null,"具体花费项目":null,"消费类型":[]}
```
调用本包统计/提案保护脚本前，用 [lark_adapter.py](../scripts/lark_adapter.py) 将行转为record_id+fields，收支单选唯一元素转字符串；保留消费类型数组和金额。多项或不识别的收支类型留待核对，不挑第一个。日期保留时区并按已配置账本/报告口径计算。别把CLI的字段值或外层协议照抄成旧v1请求。

只补缺失三列的CLI更新外层（没有缺项不提交）：
```json
{"update_records":{"真实record_id":{"金额":28.5,"具体花费项目":"午餐","消费类型":["饮食"]}}}
```
由安全JSON序列化写入本人私有工作区的相对文件repair-patch.json，不拼shell字符串；金额是number，多选是已有选项数组。用相同文件预览后执行：
```text
lark-cli base +record-batch-update --base-token 本人Base标识 --table-id 本人table_id --json @repair-patch.json --as user --dry-run
lark-cli base +record-batch-update --base-token 本人Base标识 --table-id 本人table_id --json @repair-patch.json --as user
```
dry-run后实际写前仍须重读并根据缺项重新生成提案，不把预览当锁。CLI成功信封看ok=true及退出码0，不能沿用原生HTTP的顶层code=0；部分字段忽略、记录不存在、只读或读回不符均不标完成。CLI批量更新不事先证明record_id存在，必须按原ID读回。不同记录串行更新，继续遵守OCR规则的有限重试和幂等。

## 定时、跨Agent与云端

持久记录宿主、runtime_location、model_source=current_agent、CLI版本/身份/配置引用、已验证读写、任务ID、本人当前conversation_ref、同会话投递状态和本次补全结果；不保存密钥或OCR全文。

默认只让一个Agent/调度器负责同一账本的补全与日报。用户更换Agent时迁移预算、排除测试IDs、修复状态和发送周期键，暂停旧任务后启用新任务；若不能验证旧任务已停则不并行启用。同record_id写入与日报周期去重，避免多个Agent分别补写或重复通知。两个平台并行用且不能共享持久状态/锁时只指定一个负责人。

桌面任务只在其真实调度能调用Agent并加载Skill、CLI身份和配置时启用。不能只让系统定时器运行CLI，因为CLI不替用户推理；也不能把待办提醒称为执行日报。不默认安装后台服务或设置开机常驻。电脑关闭时按需模式暂停；下次恢复检查未处理记录和本次查询范围，不补发过期日报轰炸用户。

云端接入不是“本机装过CLI便可用”。逐项测试实际执行阶段CLI可用、open.feishu.cn与实际认证域可访问、短期token可安全获取/续期、配置能跨任务读取、单次任务退出后有真正调度器及本人通知。共享云端项目避免混用买家账户与凭据；不把本机keychain或长期token打包上传。部分Codex旧云端环境的Secrets仅在setup阶段可用，不能假定Agent阶段可读，必须按当前产品的安全凭据方案验证；不通过导出明文文件绕过限制。只有浏览器聊天且不能执行CLI的版本不适用本CLI链路，可继续已验证原生连接器或人工补齐。

## Coze云端本机接入、桥接与ZCode导入

ZCode官方支持设置→技能→导入，扫描其他Agent技能目录；其原生目录是~/.zcode/skills；也可由界面导入已维护的技能目录。不替用户自动改其ZCode目录或启用后台服务。

**Coze优先复用官方本地连接**：桌面端创建项目→选择“本地目录”及本人私有记账工作区→在项目中@选定的云端Agent→完成本地操作授权→让该云端Agent实测执行lark-cli --version和登录检查。官方本地工作目录支持云端Agent执行部分Shell命令，桌面端自动连接coze-bridge；本机有CLI且实际命令/网络/凭据访问通过，便可用Coze模型理解OCR、通过本机CLI补表，不需另架公网服务。

同样支持从本机扫描/添加Skill；或按当前界面上传完整Skill包。只添加Skill并不授予CLI权限。核验目标确为Coze云端Agent，不是@了另一个本地Codex/Hermes；后者的推理用量属那个本地Agent。云端＋本机执行仍需电脑、Coze桌面端/连接组件在线；退出、睡眠、断网时不能承诺任务继续。授权卡片按当前产品实际展示，不直接改系统安全设置。

**没有可用本机连接时才用HTTP桥接**：Coze官方自定义MCP当前支持Streamable HTTP/SSE，不支持STDIO。若其云端模式没有可直接运行且持久授权的CLI环境，使用本人已部署的HTTP MCP（或API插件）连接一个运行飞书CLI的服务。先验证具体入口、后端授权、工具已绑定当前Agent，再按同一读写验收推进。云端本身可直接执行CLI时也必须验证运行阶段凭据、网络和持久状态。

桥接设计仅暴露受限账本操作：状态/身份检查、六列schema、限定日期范围读取、按record_id读回、补空的三列。每个用户绑定自己的Base与表；拒绝任意shell命令、任意账本和作者模板，不把CLI全部操作透传。服务端以参数数组调用CLI，校验模型提案的OCR哈希、缺项和分类，核对读回；保留限流、单记录串行处理和幂等结果。CLI凭据留在该用户隔离服务端安全配置，Coze只使用桥接鉴权。具体工具名称、地址和接口属于部署方案，不是当前已经存在的工具，不编造MCP地址。

关键推理分工：Coze读取必要OCR后用Coze当前Agent模型提取，服务只执行确定性读写与保护检查，不让桥接再次调用本地完整Agent推理，以免实际消耗另一套模型额度。coze-bridge“接入本地Agent”是另一种可选运行模式，可能由本地Agent完成推理，不等同于Coze云端额度方案，不能混称。不要把“云端Agent通过本地目录调用CLI”和“扣子仅做入口、由本地Agent推理”混为一谈；两者可能共用连接组件，但模型用量归属不同。

本包尚未部署桥接服务；没有现成服务时将Coze云端CLI接入标待配置，给出具体所需服务设计，允许使用已验证的桌面Agent先跑通，不称云端兼容性已验收。公开部署、收费云资源或变更用户连接器需按用户实际授权继续，不自动替用户购买/发布。

## 来源与验收范围

[飞书CLI官方仓库](https://github.com/larksuite/cli)、[WorkBuddy官方技能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[ZCode技能说明](https://zcode.z.ai/cn/docs/skill)、[Coze MCP说明](https://docs.coze.cn/mcp)、[Coze本地工作目录](https://docs.coze.cn/local-project)、[Coze技能导入](https://docs.coze.cn/cozespace_using_skills)、[Coze本地Agent说明](https://docs.coze.cn/cozespace_local_agent)、[Codex旧云端环境说明](https://learn.chatgpt.com/docs/environments/cloud-environment)。以上文档与本机帮助核查于2026-10-13；各宿主具体版本、云端运行工具及账号需实际验收。宿主用量以自己实际套餐或项目为准，不提供未验证的免费额度数字。
