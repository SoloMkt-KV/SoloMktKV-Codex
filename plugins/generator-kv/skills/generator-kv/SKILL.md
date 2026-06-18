---
name: generator-kv
description: Guide Codex users through installing and using the Generator-KV plugin, configuring a SoloMkt-KV API key, validating credentials automatically, fetching available KV models, and generating marketing KV images through natural-language conversation.
---

# Generator-KV Skill

Use this skill as the default natural-language workflow for Generator-KV. The goal is to help the user install the plugin when needed, configure an API key, validate the configuration, explain successful setup clearly, and then generate KV images through conversation.

Resolve paths from this file:

- Skill file: `<plugin-root>/skills/generator-kv/SKILL.md`
- Plugin root: two directories above this file
- Helper script: `<plugin-root>/scripts/solomkt_kv.py`
- Credentials: `$SoloMkt-KV_HOME/.credentials.json`

The helper also supports `SOLOMKT_KV_HOME` for shell compatibility. If neither variable is set, it uses `~/.solomkt-kv/.credentials.json`.

Never reveal, echo, summarize, or store the user's API key in chat after receiving it.

## Natural-Language Entry

Prefer conversational guidance. Users should be able to say things like:

- "帮我配置 Generator-KV API Key"
- "帮我生成一张活动 KV 主视觉"
- "Generate a KV poster for my product launch"
- "List SoloMkt-KV models and help me choose one"

Do not require users to know command-line flags. Use the helper script yourself and explain results in plain language.

## Installation Guidance

If the user asks how to install the plugin, explain:

1. Install the marketplace from the GitHub repository:

```bash
codex plugin marketplace add SoloMkt-KV/SmartMktKV-Codex
```

2. Open Codex plugin management with `/plugins`.
3. Choose the `SoloMkt-KV` marketplace.
4. Install `Generator-KV`.
5. Start a new Codex thread after installation so the skill is loaded.

If the plugin is already running in the current thread, do not repeat installation steps unless the user asks.

## API Key Configuration

Before any model or generation request, check whether credentials exist.

Run:

```bash
python <plugin-root>/scripts/solomkt_kv.py credentials-path
```

Tell the user the resolved credentials path. Then run:

```bash
python <plugin-root>/scripts/solomkt_kv.py check-credentials --validate
```

If credentials are missing or invalid:

1. Tell the user that Generator-KV needs a SoloMkt-KV API key before it can fetch models or generate KV images.
2. Ask the user to provide the API key.
3. After the user provides it, save and validate it:

```bash
python <plugin-root>/scripts/solomkt_kv.py configure --api-key "<api-key>" --validate
```

4. If validation passes, tell the user:
   - The API key has been saved.
   - The credentials file path.
   - The model API validation passed.
   - They can now use natural language to generate KV images.

Use this concise success message shape:

```text
Generator-KV is configured successfully. Your API key was saved to <credentials-path>, and the model-list API validation passed. You can now say: "帮我生成一张活动 KV 主视觉", and I will fetch models, ask you to choose one, collect the activity details, and generate the KV images.
```

If validation fails:

- Report the sanitized error only.
- Do not print the key.
- Ask the user to confirm the key is correct and has access to SoloMkt-KV.

## Generation Workflow

Every generation request must fetch the latest model list before choosing or using a model.

1. Validate credentials:

```bash
python <plugin-root>/scripts/solomkt_kv.py check-credentials --validate
```

2. Fetch models:

```bash
python <plugin-root>/scripts/solomkt_kv.py models
```

3. Present models in a clear numbered list with:
   - index
   - model name
   - model id
   - sub-style when available
   - tags when available

4. Ask the user to choose a model from this latest list.

5. Collect required generation fields:
   - `activityName`: activity name, 1-200 characters
   - `activityTheme`: activity theme, 1-200 characters
   - `activityTime`: activity time, 1-200 characters
   - `activityLocation`: activity location, 1-200 characters

6. Collect optional fields only if useful:
   - `prompt`: extra visual requirements, up to 1000 characters
   - `posterQuality`: defaults to `2K`
   - `posterSize`: defaults to `["16:9"]`, passed as a string

7. Before generation, tell the user:

```text
KV generation may take several minutes. I will wait up to 10 minutes for the result.
```

8. Generate:

```bash
python <plugin-root>/scripts/solomkt_kv.py generate \
  --model-id "<modelId>" \
  --activity-name "<activityName>" \
  --activity-theme "<activityTheme>" \
  --activity-time "<activityTime>" \
  --activity-location "<activityLocation>" \
  --prompt "<prompt>" \
  --poster-quality "2K" \
  --poster-size "[\"16:9\"]" \
  --timeout 600
```

The helper re-fetches models and rejects stale or unknown `modelId` values before calling `generateKV`.

9. Return generated image URLs. If the response contains image URLs, render them with Markdown image syntax when helpful.

## User-Facing Usage Explanation After Setup

After successful API key validation, give the user clear next steps:

- They can ask in natural language.
- You will fetch the latest models first.
- They will choose a model.
- You will ask for missing required activity fields.
- The generation request may take several minutes.
- The final result will be one or more image URLs.

Example:

```text
Setup is complete. To generate a KV, say something like:
"帮我生成一张活动 KV 主视觉，活动名称是第四届中国国际供应链促进博览会，主题是链接世界，共创未来，时间是2026年6月22日到26日，地点是中国国际展览中心顺义馆。"

I will fetch the latest model list, let you choose a style, ask for any missing details, and then generate the KV images.
```

## API Reference

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

Generation body:

```json
{
  "modelId": "1001",
  "activityName": "International Supply Chain Expo",
  "activityTheme": "Connect the world, create the future",
  "activityTime": "June 22-26, 2026",
  "activityLocation": "China International Exhibition Center",
  "prompt": "Create a dark, technology-inspired supply chain expo key visual.",
  "posterQuality": "2K",
  "posterSize": "[\"16:9\"]"
}
```
