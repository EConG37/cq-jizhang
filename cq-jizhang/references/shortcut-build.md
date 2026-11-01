# 不依赖私人链接创建 iPhone 截图记账快捷指令

已有本人可信、无预填作者凭据的快捷指令时先核对并复用。没有安装资源时，Agent 按本页一次带用户添加一组动作，不要求去寻找作者私人分享链接。本仓库不包含已签名的 `.shortcut` 文件；以下是手工创建方法，须在本人的 iPhone 上验收。

## 1. 三个参数

打开「快捷指令」→ 新建，命名「截屏记账」。添加三个「文本」动作，分别作为 App ID、App Secret、记录接口 URL，用「设定变量」保存为 `AppID`、`AppSecret`、`RecordURL`。每个文本初始填「☑️在此处粘贴替换」，用户随后替换为本人的值。

RecordURL 为：

```text
https://open.feishu.cn/open-apis/bitable/v1/apps/副本app_token/tables/副本table_id/records
```

Secret 由用户自己在手机填写，不发送聊天，不分享填写后的快捷指令。Agent 只需要核对动作结构和脱敏错误。

## 2. 截图与 OCR

添加「截屏」→「从图像中提取文本」，输入选择刚才的截屏，保存识别文字变量 `OCRText`。若结果为文本列表，用「合并文本」以换行符连接。添加「如果」：OCRText 为空时提示未识别到文字并停止，不提交空账单。

搜索动作名称因系统版本或语言略有差异时按当前界面核对；不要改为上传整张截图给陌生服务。

## 3. 应用鉴权

为兼容现有个人快捷指令，本流程使用仍有官方文档的 v3 自建应用鉴权接口；已有快捷指令采用新版 OAuth 时保留其协议，不混用响应字段。

添加「获取 URL 内容」，设置：

- URL：`https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`
- 方法：POST；请求体：JSON；请求头 `Content-Type` 为 `application/json`。
- JSON 字段 `app_id`：选择 AppID 变量；`app_secret`：选择 AppSecret 变量。

从返回字典分别读取 `code` 和 `tenant_access_token`。只有 code 为数字 0 且令牌非空才继续；否则只显示错误码/脱敏错误并停止，不输出完整鉴权响应或令牌。

这是旧版接口的 `tenant_access_token` 字段。新版 `https://accounts.feishu.cn/oauth/v3/token` 使用 `client_id/client_secret/grant_type`，响应字段为 `access_token`，不能只换 URL 而沿用旧动作。

## 4. 结构化提交一条支出

添加「字典」动作，命名 `Fields`：

| 键 | 类型 | 值 |
|---|---|---|
| 文本内容 | 文本 | OCRText 变量 |
| 收支类型 | 文本 | 支出 |

再添加一个字典 `Body`，键 `fields` 的类型为字典，值选择 Fields。用字典动作构造 JSON，不把识别文字拼进 JSON 文本；引号、换行和反斜杠必须由系统序列化。

添加「获取 URL 内容」：

- URL：选择 RecordURL 变量；方法：POST。
- 请求头：`Content-Type: application/json`；`Authorization` 为文本 `Bearer ` 后插入本次令牌变量（Bearer 后有一个空格）。
- 请求体：JSON，顶层键 `fields` 设为字典并填入 Fields 的两项。若该系统版本允许选择整个字典作为请求体，可直接选择 Body；以实际界面为准。

日期采用本人账本已配置的新增默认时间；金额、项目和分类留给字段捷径或 Agent 提取，不发送空字符串覆盖它们。这里使用 bitable v1 记录协议，单选「收支类型」是字符串；CLI Base v3 的数组协议不能照搬进这个 POST。

检查新增响应 `code=0` 且 `data.record.record_id` 非空，显示「文字已记入账本」，不宣称金额已提取。失败只显示脱敏错误。网络断开、超时或返回未知时先去本人账本核对是否已有本次记录，不自动再提交。

## 5. 播放与权限验收

填完三个参数，用不含敏感信息的画面测试一次。不要截取显示 App Secret、令牌或个人凭据的配置页；可离开编辑页后用 Siri 或已绑定入口运行。若在编辑页点击播放，先确保可见画面没有凭据。在本人账本看到本次 OCR 文字才算手机链路通过。金额尚为空不重复点击播放。首次运行按手机提示授权截屏、文字识别和飞书网络请求。非真实消费的演练记录按实际 ID 排除统计，真实消费正常计入。

通过后再配置轻点背面或操作按钮，并继续飞书 CLI 和 Agent 读写验收；还没有手机实测时保持 `shortcut_write_verified=false`。

官方依据：[Apple 请求 API](https://support.apple.com/en-euro/guide/shortcuts/apd58d46713f/ios)、[飞书旧版鉴权](https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal)、[新版鉴权](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/authentication-management/access-token/tenant_access_token)、[新增记录](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create)。
