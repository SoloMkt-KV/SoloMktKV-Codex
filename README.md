# Generator-KV / SoloMktKV-Codex

Generator-KV is a Codex plugin from SoloMkt-KV for creating marketing KV poster images through natural-language conversation. It always fetches the current SoloMkt-KV model list before generation, asks the user to choose a model, collects required event information, and calls the KV generation API with a 10-minute timeout.

Generator-KV 是 SoloMkt-KV 提供的 Codex 插件，用于通过自然语言对话生成营销活动 KV 主视觉图片。插件每次生成前都会先请求模型列表接口，让用户选择模型，然后收集活动必填信息，并以 10 分钟超时时间调用 KV 生成接口。

Repository: https://github.com/SoloMkt-KV/SoloMktKV-Codex.git  
Marketplace name: `SoloMkt-KV`  
Plugin name: `generator-kv`  
Display name: `Generator-KV`

## Features / 功能

- Fetches models before every generation request.
- Lets the user choose the model ID from the latest model list.
- Guides API key setup and validates the key through the model API.
- Saves credentials to `$SoloMkt-KV_HOME/.credentials.json`; also supports `SOLOMKT_KV_HOME`.
- Calls `POST /generateKV` with a 600-second timeout and friendly waiting messages.
- Supports natural-language usage in Codex.

- 每次生成前都会先查询可用模型。
- 基于最新模型列表引导用户选择模型 ID。
- 支持 API Key 配置引导，并通过模型接口自动校验。
- 凭据保存到 `$SoloMkt-KV_HOME/.credentials.json`，同时兼容 `SOLOMKT_KV_HOME`。
- 调用 `POST /generateKV` 时使用 600 秒超时，并向用户提示生成可能耗时较久。
- 默认通过 Codex 自然语言对话使用。

## Install / 安装

From the GitHub marketplace source:

```bash
codex plugin marketplace add SoloMkt-KV/SoloMktKV-Codex
```

Then open Codex, run `/plugins`, select the `SoloMkt-KV` marketplace, and install `Generator-KV`.

通过 GitHub 插件市场源安装：

```bash
codex plugin marketplace add SoloMkt-KV/SoloMktKV-Codex
```

然后在 Codex 中运行 `/plugins`，进入 `SoloMkt-KV` 插件市场并安装 `Generator-KV`。

For local development, clone this repository and open Codex from the repository root. Codex can discover the repo-local marketplace at `.agents/plugins/marketplace.json`.

本地开发时，克隆本仓库并从仓库根目录启动 Codex。Codex 可以发现仓库内置插件市场文件 `.agents/plugins/marketplace.json`。

## API Key Setup / API Key 配置

Generator-KV follows the same credential-home pattern used by Codex plugins such as mem9: credentials are stored in the plugin home instead of being kept in chat history. Configure the API key before generation, or provide it when Codex asks and Codex will save and validate it for you. Reference: https://github.com/mem9-ai/mem9/blob/main/codex-plugin/README.md

Generator-KV 参考 mem9 Codex 插件的凭据目录模式：API Key 会保存在插件 Home 目录中，而不是保存在对话历史里。你可以先手动配置，也可以在使用时把 API Key 提供给 Codex，让 Codex 自动写入并校验。参考文档：https://github.com/mem9-ai/mem9/blob/main/codex-plugin/README.md

Credential file:

```text
$SoloMkt-KV_HOME/.credentials.json
```

Because environment variables with hyphens are awkward in some shells, the helper also supports:

```text
$SOLOMKT_KV_HOME/.credentials.json
```

If neither variable is set, the default path is:

```text
~/.solomkt-kv/.credentials.json
```

Example credential file:

```json
{
  "schemaVersion": 1,
  "baseUrl": "https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1",
  "apiKey": "your-api-key"
}
```

### Configure with Codex / 使用 Codex 自动配置

After installing the plugin, ask Codex:

```text
帮我配置 Generator-KV API Key
```

or:

```text
Configure my SoloMkt-KV API key
```

Codex will ask for the key, write `.credentials.json`, call the model-list API to validate it, and then explain how to generate a KV.

安装插件后，可以直接对 Codex 说：

```text
帮我配置 Generator-KV API Key
```

Codex 会询问 API Key，写入 `.credentials.json`，调用模型列表接口完成校验，并提示后续如何生成 KV。

### Manual Paths by Environment / 不同环境与设备中的凭据地址

| Environment | Default credential path | Optional home variable |
|---|---|---|
| macOS / Linux | `~/.solomkt-kv/.credentials.json` | `SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` |
| Windows PowerShell | `$env:USERPROFILE\.solomkt-kv\.credentials.json` | `$env:SOLOMKT_KV_HOME="$env:USERPROFILE\.solomkt-kv"` |
| WSL | `/home/<user>/.solomkt-kv/.credentials.json` | `SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` |
| Dev Container / Codespaces | `/home/codespace/.solomkt-kv/.credentials.json` | `SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` |
| Custom shared home | `$SoloMkt-KV_HOME/.credentials.json` | Set `SoloMkt-KV_HOME` or `SOLOMKT_KV_HOME` before starting Codex |

| 环境 | 默认凭据地址 | 可选 Home 变量 |
|---|---|---|
| macOS / Linux | `~/.solomkt-kv/.credentials.json` | `SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` |
| Windows PowerShell | `$env:USERPROFILE\.solomkt-kv\.credentials.json` | `$env:SOLOMKT_KV_HOME="$env:USERPROFILE\.solomkt-kv"` |
| WSL | `/home/<user>/.solomkt-kv/.credentials.json` | `SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` |
| Dev Container / Codespaces | `/home/codespace/.solomkt-kv/.credentials.json` | `SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` |
| 自定义共享目录 | `$SoloMkt-KV_HOME/.credentials.json` | 启动 Codex 前设置 `SoloMkt-KV_HOME` 或 `SOLOMKT_KV_HOME` |

Windows user-level setting:

```powershell
[Environment]::SetEnvironmentVariable("SOLOMKT_KV_HOME", "$env:USERPROFILE\.solomkt-kv", "User")
```

macOS / Linux shell setting:

```bash
export SOLOMKT_KV_HOME="$HOME/.solomkt-kv"
```

To use the exact documented hyphenated variable for one Codex launch on macOS/Linux:

```bash
env 'SoloMkt-KV_HOME'="$HOME/.solomkt-kv" codex
```

## Usage / 使用

Natural-language examples:

```text
帮我生成一张活动 KV 主视觉
```

```text
Generate a KV poster for our product launch event
```

The plugin workflow is:

1. Codex checks whether the API key is configured.
2. Codex calls `GET /models?type=all`.
3. Codex shows the latest models and asks you to choose one.
4. Codex asks for required fields: activity name, theme, time, and location.
5. Codex optionally accepts prompt, poster quality, and poster size.
6. Codex re-fetches models, confirms the selected `modelId` is still available, calls `POST /generateKV`, and waits up to 10 minutes.
7. Codex returns the generated image URLs.

插件使用流程：

1. Codex 检查 API Key 是否已配置。
2. Codex 调用 `GET /models?type=all`。
3. Codex 展示最新模型并要求你选择一个模型。
4. Codex 询问必填字段：活动名称、活动主题、活动时间、活动地点。
5. Codex 可选收集补充 prompt、图片质量和图片尺寸。
6. Codex 再次查询模型，确认所选 `modelId` 仍可用，然后调用 `POST /generateKV`，最长等待 10 分钟。
7. Codex 返回生成图片 URL。

Required generation fields / 生成必填字段：

| Field | Required | Limit | Description |
|---|---:|---|---|
| `modelId` | Yes | Non-empty | Model ID from `data.system[].id` or selected model |
| `activityName` | Yes | 1-200 chars | Activity name |
| `activityTheme` | Yes | 1-200 chars | Activity theme |
| `activityTime` | Yes | 1-200 chars | Activity time |
| `activityLocation` | Yes | 1-200 chars | Activity location |
| `prompt` | No | 1000 chars | Extra generation requirements |
| `posterQuality` | No | Default `2K` | Image quality |
| `posterSize` | No | Default `["16:9"]` | Image size, passed as a string |

## APIs / 接口

Model list:

```http
GET https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/models?type=all
x-api-key: <api-key>
```

Generate KV:

```http
POST https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/generateKV
x-api-key: <api-key>
content-type: application/json
```

## Uninstall / 卸载

In Codex, run `/plugins`, open `Generator-KV`, and uninstall it.

To remove the marketplace:

```bash
codex plugin marketplace remove SoloMkt-KV
```

The uninstall flow does not remove credentials automatically. To fully remove local credentials, delete:

```text
$SoloMkt-KV_HOME/.credentials.json
```

在 Codex 中运行 `/plugins`，打开 `Generator-KV` 并卸载。

如需移除插件市场：

```bash
codex plugin marketplace remove SoloMkt-KV
```

卸载插件不会自动删除凭据。如需彻底移除本地凭据，请删除：

```text
$SoloMkt-KV_HOME/.credentials.json
```

## Development / 开发

Validate the plugin:

```bash
python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/generator-kv
```

Validate the skill:

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/generator-kv/skills/generator-kv
```

Test the helper:

```bash
python plugins/generator-kv/scripts/solomkt_kv.py credentials-path
python plugins/generator-kv/scripts/solomkt_kv.py models
```

## License / 许可证

MIT
