# Monitoring usage - Anthropic

**Source:** https://docs.anthropic.com/en/docs/claude-code/monitoring-usage

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# Claude Code

* [Overview](/en/docs/claude-code/overview)
* [Getting started](/en/docs/claude-code/getting-started)
* [Common tasks](/en/docs/claude-code/common-tasks)
* [CLI usage](/en/docs/claude-code/cli-usage)
* [IDE integrations](/en/docs/claude-code/ide-integrations)
* [Memory management](/en/docs/claude-code/memory)
* [Settings](/en/docs/claude-code/settings)
* [Security](/en/docs/claude-code/security)
* [Team setup](/en/docs/claude-code/team)
* [Monitoring usage](/en/docs/claude-code/monitoring-usage)
* [Costs](/en/docs/claude-code/costs)
* [Bedrock, Vertex, and proxies](/en/docs/claude-code/bedrock-vertex-proxies)
* [GitHub Actions](/en/docs/claude-code/github-actions)
* [SDK](/en/docs/claude-code/sdk)
* [Tutorials](/en/docs/claude-code/tutorials)
* [Troubleshooting](/en/docs/claude-code/troubleshooting)

OpenTelemetry support is currently in beta and details are subject to change.

# [​](#opentelemetry-in-claude-code) OpenTelemetry in Claude Code

Claude Code supports OpenTelemetry (OTel) metrics for monitoring and observability. This document explains how to enable and configure OTel for Claude Code.

All metrics are time series data exported via OpenTelemetry’s standard metrics protocol. It is the user’s responsibility to ensure their metrics backend is properly configured and that the aggregation granularity meets their monitoring requirements.

# [​](#quick-start) Quick Start

Configure OpenTelemetry using environment variables:

```
# 1. Enable telemetry

export CLAUDE_CODE_ENABLE_TELEMETRY=1

# 2. Choose an exporter

export OTEL_METRICS_EXPORTER=otlp       # Options: otlp, prometheus, console

# 3. Configure OTLP endpoint (for OTLP exporter)

export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# 4. Set authentication (if required)

export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# 5. For debugging: reduce export interval (default: 600000ms/10min)

export OTEL_METRIC_EXPORT_INTERVAL=10000  # 10 seconds

# 6. Run Claude Code

claude

```

The default export interval is 10 minutes. During setup, you may want to use a shorter interval for debugging purposes. Remember to reset this for production use.

For full configuration options, see the [OpenTelemetry specification](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md#configuration-options).

# [​](#administrator-configuration) Administrator Configuration

Administrators can configure OpenTelemetry settings for all users through the managed settings file. This allows for centralized control of telemetry settings across an organization. See the [configuration hierarchy](/en/docs/claude-code/settings#configuration-hierarchy) for more information about how settings are applied.

The managed settings file is located at:

* macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
* Linux: `/etc/claude-code/managed-settings.json`

Example managed settings configuration:

```
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.company.com:4317",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer company-token"
  }
}

```

Managed settings can be distributed via MDM (Mobile Device Management) or other device management solutions. Environment variables defined in the managed settings file have high precedence and cannot be overridden by users.

# [​](#configuration-details) Configuration Details

# [​](#common-configuration-variables) Common Configuration Variables

| Environment Variable | Description | Example Values |
| --- | --- | --- |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | Enables telemetry collection (required) | `1` |
| `OTEL_METRICS_EXPORTER` | Exporter type(s) to use (comma-separated) | `console`, `otlp`, `prometheus` |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | Protocol for OTLP exporter | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://localhost:4317` |
| `OTEL_EXPORTER_OTLP_HEADERS` | Authentication headers for OTLP | `Authorization=Bearer token` |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_KEY` | Client key for mTLS authentication | Path to client key file |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_CERTIFICATE` | Client certificate for mTLS authentication | Path to client cert file |
| `OTEL_METRIC_EXPORT_INTERVAL` | Export interval in milliseconds (default: 10000) | `5000`, `60000` |

# [​](#metrics-cardinality-control) Metrics Cardinality Control

The following environment variables control which attributes are included in metrics to manage cardinality:

| Environment Variable | Description | Default Value | Example to Disable |
| --- | --- | --- | --- |
| `OTEL_METRICS_INCLUDE_SESSION_ID` | Include session.id attribute in metrics | `true` | `false` |
| `OTEL_METRICS_INCLUDE_VERSION` | Include app.version attribute in metrics | `false` | `true` |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | Include user.account\_uuid attribute in metrics | `true` | `false` |

These variables help control the cardinality of metrics, which affects storage requirements and query performance in your metrics backend. Lower cardinality generally means better performance and lower storage costs but less granular data for analysis.

# [​](#example-configurations) Example Configurations

```
# Console debugging (1-second intervals)

export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=1000

# OTLP/gRPC

export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Prometheus

export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=prometheus

# Multiple exporters

export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console,otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json

```

# [​](#available-metrics) Available Metrics

Claude Code exports the following metrics:

| Metric Name | Description | Unit |
| --- | --- | --- |
| `claude_code.session.count` | Count of CLI sessions started | count |
| `claude_code.lines_of_code.count` | Count of lines of code modified | count |
| `claude_code.pull_request.count` | Number of pull requests created | count |
| `claude_code.commit.count` | Number of git commits created | count |
| `claude_code.cost.usage` | Cost of the Claude Code session | USD |
| `claude_code.token.usage` | Number of tokens used | tokens |

# [​](#metric-details) Metric Details

All metrics share these standard attributes:

* `session.id`: Unique session identifier (controlled by `OTEL_METRICS_INCLUDE_SESSION_ID`)
* `app.version`: Current Claude Code version (controlled by `OTEL_METRICS_INCLUDE_VERSION`)
* `organization.id`: Organization UUID (when authenticated)
* `user.account_uuid`: Account UUID (when authenticated, controlled by `OTEL_METRICS_INCLUDE_ACCOUNT_UUID`)

# [​](#1-session-counter) 1. Session Counter

Emitted at the start of each session.

# [​](#2-lines-of-code-counter) 2. Lines of Code Counter

Emitted when code is added or removed.

* Additional attribute: `type` (`"added"` or `"removed"`)

# [​](#3-pull-request-counter) 3. Pull Request Counter

Emitted when creating pull requests via Claude Code.

# [​](#4-commit-counter) 4. Commit Counter

Emitted when creating git commits via Claude Code.

# [​](#5-cost-counter) 5. Cost Counter

Emitted after each API request.

* Additional attribute: `model`

# [​](#6-token-counter) 6. Token Counter

Emitted after each API request.

* Additional attributes: `type` (`"input"`, `"output"`, `"cacheRead"`, `"cacheCreation"`) and `model`

# [​](#interpreting-metrics-data) Interpreting Metrics Data

These metrics provide insights into usage patterns, productivity, and costs:

# [​](#usage-monitoring) Usage Monitoring

| Metric | Analysis Opportunity |
| --- | --- |
| `claude_code.token.usage` | Break down by `type` (input/output), user, team, or model |
| `claude_code.session.count` | Track adoption and engagement over time |
| `claude_code.lines_of_code.count` | Measure productivity by tracking code additions/removals |
| `claude_code.commit.count` & `claude_code.pull_request.count` | Understand impact on development workflows |

# [​](#cost-monitoring) Cost Monitoring

The `claude_code.cost.usage` metric helps with:

* Tracking usage trends across teams or individuals
* Identifying high-usage sessions for optimization

Cost metrics are approximations. For official billing data, refer to your API provider (Anthropic Console, AWS Bedrock, or Google Cloud Vertex).

# [​](#alerting-and-segmentation) Alerting and Segmentation

Common alerts to consider:

* Cost spikes
* Unusual token consumption
* High session volume from specific users

All metrics can be segmented by `user.account_uuid`, `organization.id`, `session.id`, `model`, and `app.version`.

# [​](#backend-considerations) Backend Considerations

| Backend Type | Best For |
| --- | --- |
| Time series databases (Prometheus) | Rate calculations, aggregated metrics |
| Columnar stores (ClickHouse) | Complex queries, unique user analysis |
| Observability platforms (Honeycomb, Datadog) | Advanced querying, visualization, alerting |

For DAU/WAU/MAU metrics, choose backends that support efficient unique value queries.

# [​](#service-information) Service Information

All metrics are exported with:

* Service Name: `claude-code`
* Service Version: Current Claude Code version
* Meter Name: `com.anthropic.claude_code`

# [​](#security-considerations) Security Considerations

* Telemetry is opt-in and requires explicit configuration
* Sensitive information like API keys or file contents are never included in metrics

Was this page helpful?

YesNo

Team setup[Costs](/en/docs/claude-code/costs)

On this page
