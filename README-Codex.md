# SmartMktKV Codex 插件文档

SmartMktKV Codex Plugin 是一个用于生成营销活动 KV 主视觉图的 Codex 插件。用户可以在 Codex 中通过自然语言完成 API Key 配置、模型选择、活动信息补全和图片生成。

GitHub 仓库：[SoloMkt-KV/SoloMktKV-Codex](https://github.com/SoloMkt-KV/SoloMktKV-Codex)

## 快速开始

添加插件市场源：

```bash
codex plugin marketplace add SoloMkt-KV/SoloMktKV-Codex
```

然后在 Codex 中：

1. 运行 `/plugins`。
2. 选择 `SoloMkt-KV` 插件市场。
3. 安装 `Generator-KV`。
4. 对 Codex 说：`帮我配置 Generator-KV API Key`。
5. 配置成功后，对 Codex 说：`帮我生成一张活动 KV 主视觉图`。

## 插件信息

| 项目 | 值 |
|---|---|
| Marketplace name | `SoloMkt-KV` |
| Plugin name | `generator-kv` |
| Display name | `Generator-KV` |
| Repository | `https://github.com/SoloMkt-KV/SoloMktKV-Codex.git` |
| Main skill | `plugins/generator-kv/skills/generator-kv/SKILL.md` |
| Helper script | `plugins/generator-kv/scripts/solomkt_kv.py` |

## 功能概览

插件会引导 Codex 完成以下流程：

1. 检查 SoloMkt-KV API Key 是否已配置。
2. 每次生成前调用模型列表接口，获取最新可用模型。
3. 展示模型列表，并让用户选择一个模型。
4. 收集活动名称、主题、时间、地点等必填信息。
5. 调用 KV 生成接口，最长等待 10 分钟。
6. 返回生成后的图片 URL。

## 运行要求

- 已安装并可使用 Codex。
- Codex 环境中可运行 Python 3。
- 拥有有效的 SoloMkt-KV / SoloMkt-KV API Key。
- 当前网络可以访问 SoloMkt-KV 后端。

默认 API Base URL：

```text
https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1
```

## 安装方式

### 通过 GitHub 插件市场安装

```bash
codex plugin marketplace add SoloMkt-KV/SoloMktKV-Codex
```

添加完成后，打开 Codex 的 `/plugins`，进入 `SoloMkt-KV` 插件市场并安装 `Generator-KV`。

### 本地开发安装

如果你正在本地开发这个仓库，可以从仓库根目录启动 Codex。Codex 会读取本地插件市场文件：

```text
.agents/plugins/marketplace.json
```

该 marketplace 指向本地插件目录：

```text
./plugins/generator-kv
```

## API Key 配置

插件会把 API Key 保存在本地凭据文件中，不会把密钥保存在对话历史里。

默认凭据路径：

```text
~/.solomkt-kv/.credentials.json
```

也可以通过环境变量指定凭据目录：

```text
$SOLOMKT_KV_HOME/.credentials.json
```

为了兼容插件名称，helper 脚本也支持：

```text
$SoloMkt-KV_HOME/.credentials.json
```

凭据文件示例：

```json
{
  "schemaVersion": 1,
  "baseUrl": "https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1",
  "apiKey": "your-api-key"
}
```

### 通过 Codex 自动配置

安装插件后，直接对 Codex 说：

```text
帮我配置 Generator-KV API Key
```

或：

```text
Configure my SoloMkt-KV API key
```

Codex 会询问 API Key，写入 `.credentials.json`，并调用模型列表接口进行校验。

### 手动配置

在仓库根目录执行：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py credentials-path
python plugins/generator-kv/scripts/solomkt_kv.py configure --api-key "YOUR_API_KEY" --validate
```

macOS / Linux 可以这样设置自定义凭据目录：

```bash
export SOLOMKT_KV_HOME="$HOME/.solomkt-kv"
```

Windows PowerShell 可以这样设置用户级环境变量：

```powershell
[Environment]::SetEnvironmentVariable("SOLOMKT_KV_HOME", "$env:USERPROFILE\.solomkt-kv", "User")
```

修改用户级环境变量后，需要重启 Codex。

## 使用方式

安装并配置 API Key 后，可以直接用自然语言让 Codex 生成 KV：

```text
帮我生成一张活动 KV 主视觉图
```

也可以用英文：

```text
Generate a KV poster for our product launch event
```

Codex 会按顺序完成：

1. 校验凭据。
2. 请求 `GET /models?type=all`。
3. 展示可用模型并让用户选择。
4. 收集活动名称、活动主题、活动时间和活动地点。
5. 可选收集额外提示词、图片质量和图片尺寸。
6. 调用 `POST /generateKV`。
7. 返回生成图片 URL。

## 生成参数

必填字段：

| 字段 | 是否必填 | 限制 | 说明 |
|---|---:|---|---|
| `modelId` | 是 | 非空 | 从最新模型列表中选择的模型 ID |
| `activityName` | 是 | 1-200 字符 | 活动名称 |
| `activityTheme` | 是 | 1-200 字符 | 活动主题 |
| `activityTime` | 是 | 1-200 字符 | 活动时间 |
| `activityLocation` | 是 | 1-200 字符 | 活动地点 |

可选字段：

| 字段 | 是否必填 | 限制 / 默认值 | 说明 |
|---|---:|---|---|
| `prompt` | 否 | 最多 1000 字符 | 额外画面要求 |
| `posterQuality` | 否 | 默认 `2K` | 图片质量 |
| `posterSize` | 否 | 默认 `["16:9"]` | 图片尺寸，按字符串传入 |

示例：

```text
activityName: 春季新品发布会
activityTheme: 科技新品与智慧生活
activityTime: 2026年6月28日
activityLocation: 上海
prompt: 画面风格高级、明亮、有舞台灯光，突出新品发布氛围
posterQuality: 2K
posterSize: ["16:9"]
```

## API Reference

模型列表：

```http
GET https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/models?type=all
x-api-key: <api-key>
```

生成 KV：

```http
POST https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/generateKV
x-api-key: <api-key>
content-type: application/json
```

请求体示例：

```json
{
  "modelId": "1001",
  "activityName": "春季新品发布会",
  "activityTheme": "科技新品与智慧生活",
  "activityTime": "2026年6月28日",
  "activityLocation": "上海",
  "prompt": "画面风格高级、明亮、有舞台灯光，突出新品发布氛围",
  "posterQuality": "2K",
  "posterSize": "[\"16:9\"]"
}
```

## Helper 脚本命令

查看凭据路径：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py credentials-path
```

配置并校验凭据：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py configure --api-key "YOUR_API_KEY" --validate
```

检查凭据：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py check-credentials --validate
```

列出可用模型：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py models
```

手动生成 KV：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py generate \
  --model-id "1001" \
  --activity-name "春季新品发布会" \
  --activity-theme "科技新品与智慧生活" \
  --activity-time "2026年6月28日" \
  --activity-location "上海" \
  --prompt "画面风格高级、明亮、有舞台灯光，突出新品发布氛围" \
  --poster-quality "2K" \
  --poster-size "[\"16:9\"]" \
  --timeout 600
```

## 开发与校验

校验插件包：

```bash
python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/generator-kv
```

校验 skill：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/generator-kv/skills/generator-kv
```

测试 helper 脚本：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py credentials-path
python plugins/generator-kv/scripts/solomkt_kv.py models
```

## 安全注意事项

- 不要把真实 API Key 写入 README、issue、commit 或聊天记录。
- 不要提交 `.credentials.json`。
- 如果 API Key 泄露，应立即在服务端吊销旧 key 并重新生成。
- 文档示例中的 `YOUR_API_KEY` 和 `your-api-key` 都是占位符。

## 常见问题

### Codex 提示没有配置 API Key

先运行：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py credentials-path
```

确认凭据文件路径，然后重新配置：

```bash
python plugins/generator-kv/scripts/solomkt_kv.py configure --api-key "YOUR_API_KEY" --validate
```

### 生成前为什么总是重新获取模型列表

模型可能会更新、下线或新增。插件每次生成前重新请求模型列表，可以避免使用过期的 `modelId`。

### 生成图片为什么需要等待较久

KV 图片生成可能需要几分钟。插件默认生成请求超时时间是 600 秒，也就是 10 分钟。

### 返回 selected modelId 不存在

这说明当前选择的模型 ID 不在最新模型列表里。重新让 Codex 列出模型，并选择新的模型 ID。

## 卸载

在 Codex 中：

1. 运行 `/plugins`。
2. 打开 `Generator-KV`。
3. 卸载插件。

移除插件市场源：

```bash
codex plugin marketplace remove SoloMkt-KV
```

卸载插件不会自动删除本地凭据。如果要彻底移除配置，请删除：

```text
~/.solomkt-kv/.credentials.json
```

或删除你通过 `SOLOMKT_KV_HOME` 指定目录下的 `.credentials.json`。

## 从 OpenClaw 迁移

OpenClaw 版本使用类似下面的配置命令：

```bash
openclaw config set plugins.com.lilywlj.kvv1.apiKey YOUR_API_KEY
openclaw config set plugins.com.lilywlj.kvv1.baseUrl http://1.94.23.191:8080/api/v1
```

Codex 插件不使用 `openclaw config`。它通过 Codex skill 工作流和 `solomkt_kv.py` helper 脚本完成配置，并把凭据保存在本地 `.credentials.json` 中。

