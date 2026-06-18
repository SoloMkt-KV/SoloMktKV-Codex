#!/usr/bin/env python3
"""SoloMkt-KV helper for Codex plugin workflows."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1"
DEFAULT_HOME = Path.home() / ".solomkt-kv"
DEFAULT_TIMEOUT_SECONDS = 600


class KVError(Exception):
    pass


def _env_home() -> str | None:
    return os.environ.get("SoloMkt-KV_HOME") or os.environ.get("SOLOMKT_KV_HOME")


def credential_path() -> Path:
    home = _env_home()
    root = Path(home).expanduser() if home else DEFAULT_HOME
    return root / ".credentials.json"


def read_credentials() -> dict[str, Any]:
    path = credential_path()
    if not path.exists():
        raise KVError(
            "SoloMkt-KV API key is not configured. Configure it first at "
            f"{path} with `configure --api-key <key>`."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KVError(f"Credentials file is not valid JSON: {path}") from exc
    api_key = data.get("apiKey") or data.get("api_key") or data.get("x-api-key")
    if not isinstance(api_key, str) or not api_key.strip():
        raise KVError(f"Credentials file does not contain apiKey: {path}")
    data["apiKey"] = api_key.strip()
    data.setdefault("baseUrl", DEFAULT_BASE_URL)
    return data


def write_credentials(api_key: str, base_url: str) -> Path:
    api_key = api_key.strip()
    if not api_key:
        raise KVError("API key cannot be empty.")
    path = credential_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "baseUrl": base_url.rstrip("/"),
        "apiKey": api_key,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def http_json(method: str, url: str, api_key: str, body: dict[str, Any] | None, timeout: int) -> Any:
    data = None
    headers = {"x-api-key": api_key, "Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise KVError(f"HTTP {exc.code} from SoloMkt-KV API: {detail}") from exc
    except urllib.error.URLError as exc:
        raise KVError(f"Unable to reach SoloMkt-KV API: {exc}") from exc
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise KVError(f"API returned non-JSON response: {raw[:500]}") from exc


def fetch_models(timeout: int) -> dict[str, Any]:
    credentials = read_credentials()
    url = f"{credentials['baseUrl'].rstrip('/')}/models?type=all"
    payload = http_json("GET", url, credentials["apiKey"], None, timeout)
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise KVError(f"Model API did not return success=true: {json.dumps(payload, ensure_ascii=False)}")
    return payload


def flatten_models(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload, dict) else {}
    models: list[dict[str, Any]] = []
    for group in ("system", "custom"):
        for item in (data or {}).get(group, []) or []:
            if isinstance(item, dict):
                copy = dict(item)
                copy["group"] = group
                models.append(copy)
    return models


def print_models(payload: dict[str, Any], as_json: bool) -> None:
    models = flatten_models(payload)
    if as_json:
        print(json.dumps(models, ensure_ascii=False, indent=2))
        return
    if not models:
        print("No public SoloMkt-KV models are currently available.")
        return
    print("Available SoloMkt-KV models:")
    for index, model in enumerate(models, start=1):
        tags = ", ".join(model.get("tags") or [])
        sub = model.get("sub") or ""
        suffix = f" | {sub}" if sub else ""
        tag_text = f" | tags: {tags}" if tags else ""
        print(f"{index}. id={model.get('id')} | {model.get('name')}{suffix}{tag_text}")


def validate_length(name: str, value: str, maximum: int) -> None:
    if not value or not value.strip():
        raise KVError(f"{name} is required.")
    if len(value) > maximum:
        raise KVError(f"{name} must be at most {maximum} characters.")


def generate(args: argparse.Namespace) -> list[str]:
    credentials = read_credentials()
    validate_length("modelId", args.model_id, 200)
    validate_length("activityName", args.activity_name, 200)
    validate_length("activityTheme", args.activity_theme, 200)
    validate_length("activityTime", args.activity_time, 200)
    validate_length("activityLocation", args.activity_location, 200)
    if args.prompt and len(args.prompt) > 1000:
        raise KVError("prompt must be at most 1000 characters.")

    print("Fetching the latest SoloMkt-KV model list before generation...", file=sys.stderr)
    models_payload = fetch_models(min(args.timeout, 60))
    model_ids = {str(model.get("id")) for model in flatten_models(models_payload)}
    if args.model_id.strip() not in model_ids:
        raise KVError(
            "Selected modelId was not found in the latest model list. "
            "Fetch models again and ask the user to choose one of the returned IDs."
        )

    body = {
        "modelId": args.model_id.strip(),
        "activityName": args.activity_name.strip(),
        "activityTheme": args.activity_theme.strip(),
        "activityTime": args.activity_time.strip(),
        "activityLocation": args.activity_location.strip(),
        "posterQuality": args.poster_quality,
        "posterSize": args.poster_size,
    }
    if args.prompt:
        body["prompt"] = args.prompt.strip()

    print(
        "SoloMkt-KV is generating the KV images. This can take several minutes; "
        "the request timeout is 10 minutes.",
        file=sys.stderr,
    )
    url = f"{credentials['baseUrl'].rstrip('/')}/generateKV"
    result = http_json("POST", url, credentials["apiKey"], body, args.timeout)
    if not isinstance(result, list) or not all(isinstance(item, str) for item in result):
        raise KVError(f"Unexpected generateKV response: {json.dumps(result, ensure_ascii=False)}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SoloMkt-KV Codex plugin helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("credentials-path", help="Print the resolved credentials path")

    configure = subparsers.add_parser("configure", help="Save a SoloMkt-KV API key")
    configure.add_argument("--api-key", required=True)
    configure.add_argument("--base-url", default=DEFAULT_BASE_URL)
    configure.add_argument("--validate", action="store_true", help="Validate by calling the models API after saving")
    configure.add_argument("--timeout", type=int, default=30)

    check = subparsers.add_parser("check-credentials", help="Check that credentials exist and can be parsed")
    check.add_argument("--validate", action="store_true", help="Validate by calling the models API")
    check.add_argument("--timeout", type=int, default=30)

    models = subparsers.add_parser("models", help="Fetch and print available models")
    models.add_argument("--json", action="store_true")
    models.add_argument("--timeout", type=int, default=30)

    generate_cmd = subparsers.add_parser("generate", help="Generate KV images")
    generate_cmd.add_argument("--model-id", required=True)
    generate_cmd.add_argument("--activity-name", required=True)
    generate_cmd.add_argument("--activity-theme", required=True)
    generate_cmd.add_argument("--activity-time", required=True)
    generate_cmd.add_argument("--activity-location", required=True)
    generate_cmd.add_argument("--prompt", default="")
    generate_cmd.add_argument("--poster-quality", default="2K")
    generate_cmd.add_argument("--poster-size", default='["16:9"]')
    generate_cmd.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "credentials-path":
            print(credential_path())
        elif args.command == "configure":
            path = write_credentials(args.api_key, args.base_url)
            print(f"Saved SoloMkt-KV credentials to {path}")
            if args.validate:
                payload = fetch_models(args.timeout)
                count = len(flatten_models(payload))
                print(f"Validation passed. {count} model(s) available.")
        elif args.command == "check-credentials":
            path = credential_path()
            read_credentials()
            print(f"Credentials found at {path}")
            if args.validate:
                payload = fetch_models(args.timeout)
                count = len(flatten_models(payload))
                print(f"Validation passed. {count} model(s) available.")
        elif args.command == "models":
            print_models(fetch_models(args.timeout), args.json)
        elif args.command == "generate":
            urls = generate(args)
            print(json.dumps(urls, ensure_ascii=False, indent=2))
        else:
            parser.error("unknown command")
    except KVError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
