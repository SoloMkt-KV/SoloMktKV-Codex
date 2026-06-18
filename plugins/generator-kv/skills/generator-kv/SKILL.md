---
name: generator-kv
description: Generate SoloMkt-KV marketing KV poster images through natural-language Codex guidance. Use when the user asks to configure a SoloMkt-KV API key, list or choose KV models, create activity/event key visual images, or call the SoloMkt-KV models and generateKV APIs.
---

# Generator-KV

Use this skill as a conversational workflow. Resolve the plugin root as two directories above this `SKILL.md`; the helper script is `scripts/solomkt_kv.py`.

## Credential Setup

- Credentials live in `$SoloMkt-KV_HOME/.credentials.json`.
- The helper also accepts `SOLOMKT_KV_HOME` because it is easier to set in common shells.
- If neither variable is set, credentials default to `~/.solomkt-kv/.credentials.json`.
- Never print the user's API key after it is provided.

When the user asks to configure the plugin or when a request fails because credentials are missing:

1. Run `python <plugin-root>/scripts/solomkt_kv.py credentials-path` and tell the user where the key will be stored.
2. Ask the user to provide the SoloMkt-KV API key if they have not already provided it.
3. Save and validate it with `python <plugin-root>/scripts/solomkt_kv.py configure --api-key "<key>" --validate`.
4. If validation succeeds, tell the user clearly that setup is complete and explain that they can now ask in natural language to generate a KV.
5. If validation fails, report the sanitized error and ask the user to confirm the key or network access.

## Generation Workflow

Every generation request must fetch the current model list first.

1. Check credentials with `python <plugin-root>/scripts/solomkt_kv.py check-credentials --validate`.
2. Fetch models with `python <plugin-root>/scripts/solomkt_kv.py models`.
3. Present the available models by index, name, id, sub-style, and tags. Ask the user to choose one model unless they already selected a model from the freshly fetched list.
4. Collect required fields before generation:
   - `activityName`: 1-200 characters
   - `activityTheme`: 1-200 characters
   - `activityTime`: 1-200 characters
   - `activityLocation`: 1-200 characters
5. Optionally collect:
   - `prompt`: up to 1000 characters
   - `posterQuality`: defaults to `2K`
   - `posterSize`: defaults to `["16:9"]` and must be passed as a string
6. Before calling generation, tell the user generation can take several minutes and the timeout is 10 minutes.
   The helper re-fetches models and rejects a stale or unknown `modelId` before posting to `generateKV`.
7. Call:

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

8. Return the generated image URLs to the user. If image URLs are returned, render them with Markdown image syntax when useful.

## API Reference

- Models: `GET https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/models?type=all`
- Generate KV: `POST https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/generateKV`
- Header: `x-api-key: <api-key>`

Generation body fields:

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
