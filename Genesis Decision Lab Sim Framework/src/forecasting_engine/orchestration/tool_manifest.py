from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REQUIRED_TOOL_FIELDS = {
    "name",
    "purpose",
    "when_to_use",
    "when_not_to_use",
    "required_inputs",
    "output_shape",
    "failure_modes",
    "verification_notes",
}
ALLOWED_ROUTING_ACTIONS = {"retrieve", "simulate", "retrieve_and_simulate", "refuse"}
EXPECTED_TOOL_OUTPUT_FIELDS = {
    "bayesian_update": {
        "prior",
        "posterior",
        "effective_likelihood_ratio",
        "confidence_interval",
        "explanation",
    },
    "monte_carlo_paths": {
        "threshold_hit_probability",
        "mean_final_value",
        "quantiles",
        "model",
        "seed",
    },
    "domain_simulation": {"simulator", "state", "metrics", "artifacts", "context"},
}


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)  # type: ignore[no-untyped-call]
        if key in mapping:
            raise ValueError(f"duplicate key in manifest: {key}")
        mapping[key] = loader.construct_object(value_node)  # type: ignore[no-untyped-call]
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    purpose: str
    when_to_use: list[str]
    when_not_to_use: list[str]
    required_inputs: list[str]
    output_shape: dict[str, str]
    failure_modes: list[str]
    verification_notes: list[str]


@dataclass(frozen=True)
class SelfModelManifest:
    version: str
    tools: dict[str, ToolSpec]
    routing_defaults: dict[str, Any]
    uncertainty_policies: dict[str, dict[str, Any]]


def _as_string_list(field_name: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"tool field '{field_name}' must be a list[str]")
    return value


def _parse_tool(raw_tool: dict[str, Any]) -> ToolSpec:
    missing = REQUIRED_TOOL_FIELDS - set(raw_tool)
    if missing:
        missing_display = ", ".join(sorted(missing))
        raise ValueError(f"tool entry missing required fields: {missing_display}")
    output_shape = raw_tool["output_shape"]
    if not isinstance(output_shape, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in output_shape.items()
    ):
        raise ValueError("tool field 'output_shape' must be dict[str, str]")
    name = raw_tool["name"]
    purpose = raw_tool["purpose"]
    if not isinstance(name, str) or not isinstance(purpose, str):
        raise ValueError("tool fields 'name' and 'purpose' must be str")
    return ToolSpec(
        name=name,
        purpose=purpose,
        when_to_use=_as_string_list("when_to_use", raw_tool["when_to_use"]),
        when_not_to_use=_as_string_list("when_not_to_use", raw_tool["when_not_to_use"]),
        required_inputs=_as_string_list("required_inputs", raw_tool["required_inputs"]),
        output_shape=output_shape,
        failure_modes=_as_string_list("failure_modes", raw_tool["failure_modes"]),
        verification_notes=_as_string_list("verification_notes", raw_tool["verification_notes"]),
    )


def _validate_routing_defaults(routing_defaults: dict[str, Any]) -> None:
    unsupported_action = routing_defaults.get("unsupported_task_action")
    if unsupported_action is not None and unsupported_action not in ALLOWED_ROUTING_ACTIONS:
        raise ValueError("routing_defaults.unsupported_task_action must be a known routing action")

    allowed_actions = routing_defaults.get("allowed_routing_actions")
    if allowed_actions is not None:
        if not isinstance(allowed_actions, list) or not all(
            isinstance(item, str) for item in allowed_actions
        ):
            raise ValueError("routing_defaults.allowed_routing_actions must be list[str]")
        unknown = set(allowed_actions) - ALLOWED_ROUTING_ACTIONS
        if unknown:
            raise ValueError(
                f"routing_defaults.allowed_routing_actions has unknown actions: {unknown}"
            )


def _validate_semantics(
    tools: dict[str, ToolSpec], uncertainty_policies: dict[str, dict[str, Any]]
) -> None:
    for tool_name, tool in tools.items():
        expected_fields = EXPECTED_TOOL_OUTPUT_FIELDS.get(tool_name)
        if expected_fields is None:
            continue
        manifest_fields = set(tool.output_shape.keys())
        if manifest_fields != expected_fields:
            raise ValueError(
                f"tool '{tool_name}' output_shape must match expected fields: "
                f"expected={sorted(expected_fields)} got={sorted(manifest_fields)}"
            )

    missing_policy_tools = set(tools) - set(uncertainty_policies)
    if missing_policy_tools:
        raise ValueError(f"missing uncertainty policy for tools: {sorted(missing_policy_tools)}")


def load_self_model_manifest(path: str | Path) -> SelfModelManifest:
    manifest_path = Path(path)
    data = yaml.load(manifest_path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a mapping")
    version = data.get("version")
    raw_tools = data.get("tools")
    if not isinstance(version, str):
        raise ValueError("manifest 'version' must be a string")
    if not isinstance(raw_tools, list):
        raise ValueError("manifest 'tools' must be a list")

    parsed_tools: dict[str, ToolSpec] = {}
    for raw_tool in raw_tools:
        if not isinstance(raw_tool, dict):
            raise ValueError("each tool entry must be a mapping")
        tool = _parse_tool(raw_tool)
        if tool.name in parsed_tools:
            raise ValueError(f"duplicate tool name in manifest: {tool.name}")
        parsed_tools[tool.name] = tool

    routing_defaults = data.get("routing_defaults", {})
    if not isinstance(routing_defaults, dict):
        raise ValueError("manifest 'routing_defaults' must be a mapping")
    _validate_routing_defaults(routing_defaults)

    uncertainty_policies = data.get("uncertainty_policies", {})
    if not isinstance(uncertainty_policies, dict):
        raise ValueError("manifest 'uncertainty_policies' must be a mapping")

    normalized_policies: dict[str, dict[str, Any]] = {}
    for key, value in uncertainty_policies.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            raise ValueError(
                "manifest 'uncertainty_policies' entries must be dict[str, dict[str, Any]]"
            )
        normalized_policies[key] = value

    _validate_semantics(parsed_tools, normalized_policies)

    return SelfModelManifest(
        version=version,
        tools=parsed_tools,
        routing_defaults=routing_defaults,
        uncertainty_policies=normalized_policies,
    )
