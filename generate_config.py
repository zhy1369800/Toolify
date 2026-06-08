# SPDX-License-Identifier: GPL-3.0-or-later
#
# Toolify: Empower any LLM with function calling capabilities.
# Copyright (C) 2025 FunnyCups (https://github.com/funnycups)

import os
import yaml
import json

def main():
    # If config.yaml already exists and no configuration env vars are set, skip generation.
    has_env = any(os.getenv(k) for k in [
        "UPSTREAM_API_KEY", "ALLOWED_KEYS", "UPSTREAM_SERVICES_JSON", 
        "KEY_PASSTHROUGH", "MODEL_PASSTHROUGH", "PORT"
    ])
    
    if os.path.exists("config.yaml") and not has_env:
        print("config.yaml already exists and no Toolify environment variables are set. Skipping generation.")
        return

    print("Generating config.yaml from environment variables...")
    config = {
        "server": {
            "port": int(os.getenv("PORT", "7860")),
            "host": os.getenv("HOST", "0.0.0.0"),
            "timeout": int(os.getenv("TIMEOUT", "300")),
            "upstream_retry_attempts": int(os.getenv("UPSTREAM_RETRY_ATTEMPTS", "3")),
            "upstream_retry_base_delay": float(os.getenv("UPSTREAM_RETRY_BASE_DELAY", "0.5"))
        },
        "upstream_services": [],
        "client_authentication": {
            "allowed_keys": []
        },
        "features": {
            "enable_function_calling": os.getenv("ENABLE_FUNCTION_CALLING", "true").lower() in ("true", "1", "yes"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "convert_developer_to_system": os.getenv("CONVERT_DEVELOPER_TO_SYSTEM", "true").lower() in ("true", "1", "yes"),
            "key_passthrough": os.getenv("KEY_PASSTHROUGH", "false").lower() in ("true", "1", "yes"),
            "model_passthrough": os.getenv("MODEL_PASSTHROUGH", "true").lower() in ("true", "1", "yes"),
            "enable_fc_error_retry": os.getenv("ENABLE_FC_ERROR_RETRY", "false").lower() in ("true", "1", "yes"),
            "fc_error_retry_max_attempts": int(os.getenv("FC_ERROR_RETRY_MAX_ATTEMPTS", "3"))
        }
    }

    # Setup upstream services
    upstream_json = os.getenv("UPSTREAM_SERVICES_JSON")
    if upstream_json:
        try:
            services = json.loads(upstream_json)
            for service in services:
                if "models" not in service or not service["models"]:
                    service["models"] = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]
            config["upstream_services"] = services
        except Exception as e:
            print(f"Error parsing UPSTREAM_SERVICES_JSON: {e}")
            exit(1)
    else:
        upstream_api_key = os.getenv("UPSTREAM_API_KEY", "your-openai-api-key-here")
        upstream_base_url = os.getenv("UPSTREAM_BASE_URL", "https://api.openai.com/v1")
        upstream_name = os.getenv("UPSTREAM_NAME", "openai")
        upstream_models_str = os.getenv("UPSTREAM_MODELS", "")
        
        models = [m.strip() for m in upstream_models_str.split(",") if m.strip()]
        if not models:
            # Default to some standard models to pass Pydantic validation order constraint
            models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]
        
        config["upstream_services"].append({
            "name": upstream_name,
            "base_url": upstream_base_url,
            "api_key": upstream_api_key,
            "models": models,
            "is_default": True
        })

    # Setup client authentication
    allowed_keys_str = os.getenv("ALLOWED_KEYS", "sk-my-secret-key-1")
    config["client_authentication"]["allowed_keys"] = [
        k.strip() for k in allowed_keys_str.split(",") if k.strip()
    ]

    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    print("Successfully generated config.yaml.")

if __name__ == "__main__":
    main()
