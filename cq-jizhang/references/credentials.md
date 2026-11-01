# 凭据填写对照

手机OCR文字同步通过后，在安装最后一步配置飞书CLI：默认日报、周报和Agent补全需其读写；已有可执行则复用，未装才安装。CLI登录账号须与复制/使用账本时的本人账号和组织一致；手机应用Secret与CLI用户登录不是同一件事。安装、登录有效、同账号确认、目标读取、实际更新逐项验证，依照 [CLI接入](agent-cli.md)。

| 项目 | 获取位置 | 填到哪里 |
|---|---|---|
| App ID | 自建应用→凭证与基础信息 | app_id对应“☑️在此处粘贴替换” |
| App Secret | 同页显示/复制 | app_secret对应“☑️在此处粘贴替换”，用户自己填，聊天不收集 |
| 副本链接 | 自己复制后的表格地址 | Agent数据源和非敏感配置 |
| app_token | 普通链接/base/后的标识 | 记录API地址/apps/后，属于文档标识，不是访问令牌 |
| table_id | “具体开支”表链接的table=参数 | 记录API地址/tables/后 |
| 记录接口URL | 用两项ID组装 | 新增记录POST地址对应“☑️在此处粘贴替换” |
| tenant_access_token | 快捷指令运行鉴权动作返回 | Authorization: Bearer，由动作运行时读取，不长期硬编码 |

没有快捷指令时按 [创建步骤](shortcut-build.md) 建立，不索要作者私人资源。本人标记版直接点击快捷指令进入编辑，三处参数各找对应标记并完整替换，不保留标记文字。填好后点击右上角播放标测试任意可OCR文本，只确认文本入本人表即可通过基础写入。找不到标记先核对版本与脱敏动作。

副本文档应用通过右上角「・・・」更多菜单→添加文档应用添加；不引导从分享/协作者安装。

副本链接示意：
`https://你的域名.feishu.cn/base/副本app_token?table=副本table_id&view=视图id`

第三处需要填的记录接口：
`https://open.feishu.cn/open-apis/bitable/v1/apps/副本app_token/tables/副本table_id/records`

用URL解析，不能用作者ID。wiki链接或缺少table参数时，使用授权文档工具解析到Base/数据表，或指导打开“具体开支”再复制链接。检查两项对应同一副本，无空格。

Secret仅保存在本人密码管理器、个人快捷指令或宿主密钥管理；不进聊天、状态JSON、报告、分享快捷指令和交付包。测试截图时避开显示凭据的编辑页或开发者页面，防止凭据进入OCR账单；不要索要含Secret的截图。宿主确实需要应用身份时，用户在宿主安全凭据设置填写，Agent只确认存在，不输出值。豆包工作使用原生用户授权读表时，不强制索要截图应用Secret。

WorkBuddy/ZCode/Codex/Coze等外部宿主按 [CLI接入](agent-cli.md) 登录和绑定本人账本；CLI授权不同于手机截图应用配置，不能直接共享或打包作者凭据。CLI v3权限按当前命令核验，不把下文旧v1接口scope硬套给CLI。Coze桥接认证留在本人私有服务安全设置，Agent只拿授权工具。

Agent OCR备用链路额外需要更新原记录。应用身份按 [更新记录接口](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update) 当前要求核查更新权限（如base:record:update）、发布及副本编辑授权；原生用户授权需检查宿主实际支持更新。新增权限不能代替更新权限。可复用与手机分开的Agent身份，不为此把Secret粘贴聊天。字段能否更新必须实测。

[官方鉴权接口](https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal)、[新增记录](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create)。
