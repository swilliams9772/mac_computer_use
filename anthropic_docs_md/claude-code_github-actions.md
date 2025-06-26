# GitHub Actions - Anthropic

**Source:** https://docs.anthropic.com/en/docs/claude-code/github-actions

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

Claude Code GitHub Actions brings AI-powered automation to your GitHub workflow. With a simple `@claude` mention in any PR or issue, Claude can analyze your code, create pull requests, implement features, and fix bugs - all while following your project’s standards.

Claude Code GitHub Actions is currently in beta. Features and functionality may evolve as we refine the experience.

Claude Code GitHub Actions is built on top of the [Claude Code SDK](/en/docs/claude-code/sdk), which enables programmatic integration of Claude Code into your applications. You can use the SDK to build custom automation workflows beyond GitHub Actions.

# [​](#why-use-claude-code-github-actions%3F) Why use Claude Code GitHub Actions?

* **Instant PR creation**: Describe what you need, and Claude creates a complete PR with all necessary changes
* **Automated code implementation**: Turn issues into working code with a single command
* **Follows your standards**: Claude respects your `CLAUDE.md` guidelines and existing code patterns
* **Simple setup**: Get started in minutes with our installer and API key
* **Secure by default**: Your code stays on Github’s runners

# [​](#what-can-claude-do%3F) What can Claude do?

Claude Code provides powerful GitHub Actions that transform how you work with code:

# [​](#claude-code-action) Claude Code Action

This GitHub Action allows you to run Claude Code within your GitHub Actions workflows. You can use this to build any custom workflow on top of Claude Code.

[View repository →](https://github.com/anthropics/claude-code-action)

# [​](#claude-code-action-base) Claude Code Action (Base)

The foundation for building custom GitHub workflows with Claude. This extensible framework gives you full access to Claude’s capabilities for creating tailored automation.

[View repository →](https://github.com/anthropics/claude-code-base-action)

# [​](#quick-start) Quick start

The easiest way to set up this action is through Claude Code in the terminal. Just open claude and run `/install-github-app`.

This command will guide you through setting up the GitHub app and required secrets.

* You must be a repository admin to install the GitHub app and add secrets
* This quickstart method is only available for direct Anthropic API users. If you’re using AWS Bedrock or Google Vertex AI, please see the [Using with AWS Bedrock & Google Vertex AI](/_sites/docs.anthropic.com/en/docs/claude-code/github-actions#using-with-aws-bedrock-%26-google-vertex-ai) section.

# [​](#if-the-setup-script-fails) If the setup script fails

If the `/install-github-app` command fails or you prefer manual setup, please follow these manual setup instructions:

1. **Install the Claude GitHub app** to your repository: <https://github.com/apps/claude>
2. **Add ANTHROPIC\_API\_KEY** to your repository secrets ([Learn how to use secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions))
3. **Copy the workflow file** from [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) into your repository’s `.github/workflows/`

1

Test the action

After completing either the quickstart or manual setup, test the action by tagging `@claude` in an issue or PR comment!

# [​](#example-use-cases) Example use cases

Claude Code GitHub Actions can help you with a variety of tasks, including:

# [​](#turn-issues-into-prs) Turn issues into PRs

```
# In an issue comment:

@claude implement this feature based on the issue description

```

Claude will analyze the issue, write the code, and create a PR for review.

# [​](#get-implementation-help) Get implementation help

```
# In a PR comment:

@claude how should I implement user authentication for this endpoint?

```

Claude will analyze your code and provide specific implementation guidance.

# [​](#fix-bugs-quickly) Fix bugs quickly

```
# In an issue:

@claude fix the TypeError in the user dashboard component

```

Claude will locate the bug, implement a fix, and create a PR.

# [​](#best-practices) Best practices

# [​](#claude-md-configuration) CLAUDE.md configuration

Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns. This file guides Claude’s understanding of your project standards.

# [​](#security-considerations) Security considerations

**⚠️ IMPORTANT: Never commit API keys directly to your repository!**

Always use GitHub Secrets for API keys:

* Add your API key as a repository secret named `ANTHROPIC_API_KEY`
* Reference it in workflows: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
* Limit action permissions to only what’s necessary
* Review Claude’s suggestions before merging

```
# ✅ CORRECT - Uses GitHub secrets

anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

# ❌ WRONG - Exposes your API key

anthropic_api_key: "sk-ant-..."

```

**Use explicit tools for better security:**

When configuring `allowed_tools`, avoid wildcard patterns and instead explicitly list the specific commands Claude can use:

```
# ✅ RECOMMENDED - Explicit commands for better security

allowed_tools: "Bash(git status),Bash(git log),Bash(git diff),View,GlobTool"

# ❌ LESS SECURE - Allows any git command

allowed_tools: "Bash(git:*),View,GlobTool"

```

This approach ensures Claude can only execute the specific commands you’ve authorized, reducing potential security risks.

# [​](#optimizing-performance) Optimizing performance

Use issue templates to provide context, keep your `CLAUDE.md` concise and focused, and configure appropriate timeouts for your workflows.

# [​](#ci-costs) CI costs

When using Claude Code GitHub Actions, be aware of the associated costs:

**GitHub Actions costs:**

* Claude Code runs on GitHub-hosted runners, which consume your GitHub Actions minutes
* See [GitHub’s billing documentation](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions) for detailed pricing and minute limits

**API costs:**

* Each Claude interaction consumes API tokens based on the length of prompts and responses
* Token usage varies by task complexity and codebase size
* See [Claude’s pricing page](https://www.anthropic.com/api) for current token rates

**Cost optimization tips:**

* Use specific `@claude` commands to reduce unnecessary API calls
* Configure appropriate `max_turns` limits to prevent excessive iterations
* Set reasonable `timeout_minutes` to avoid runaway workflows
* Consider using GitHub’s concurrency controls to limit parallel runs

# [​](#configuration-examples) Configuration examples

This section provides ready-to-use workflow configurations for different use cases:

* [Basic workflow setup](/_sites/docs.anthropic.com/en/docs/claude-code/github-actions#basic-workflow-setup) - The default configuration for issue and PR comments
* [Code review on pull requests](/_sites/docs.anthropic.com/en/docs/claude-code/github-actions#code-review-on-pull-requests) - Automated code reviews on new PRs

# [​](#basic-workflow-setup) Basic workflow setup

This is the default workflow created by the installer. It enables Claude to respond to `@claude` mentions in issues and PR comments:

```
name: Claude PR Creation
on:
  issue_comment:
    types: [created]  # Triggers when someone comments on an issue or PR

jobs:
  create-pr:
    # Only run if the comment mentions @claude
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
  - uses: anthropics/claude-code-action@beta
        with:
          # Pass the comment text as the prompt
          prompt: "${{ github.event.comment.body }}"

          # Define which tools Claude can use
          allowed_tools: "Bash(git status),Bash(git log),Bash(git show),Bash(git blame),Bash(git reflog),Bash(git stash list),Bash(git ls-files),Bash(git branch),Bash(git tag),Bash(git diff),View,GlobTool,GrepTool,BatchTool"

          # Your Anthropic API key (stored as a GitHub secret)
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

```

This workflow responds to issue comments, allowing Claude to understand context from the issue description and previous comments.

# [​](#code-review-on-pull-requests) Code review on pull requests

This workflow automatically reviews code changes when a PR is opened or updated:

```
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]  # Runs on new PRs and updates

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      # Check out the code to allow git diff operations
  - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Fetch full history for accurate diffs
  - name: Run Code Review with Claude
        id: code-review
        uses: anthropics/claude-code-action@beta
        with:
          # Define the review focus areas
          prompt: "Review the PR changes. Focus on code quality, potential bugs, and performance issues. Suggest improvements where appropriate."

          # Limited tools for safer review operations
          allowed_tools: "Bash(git diff --name-only HEAD~1),Bash(git diff HEAD~1),View,GlobTool,GrepTool"

          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

```

For more focused reviews, customize the prompt to check specific aspects like security, performance, or compliance with your coding standards.

# [​](#using-with-aws-bedrock-%26-google-vertex-ai) Using with AWS Bedrock & Google Vertex AI

For enterprise environments, you can use Claude Code GitHub Actions with your own cloud infrastructure. This approach gives you control over data residency and billing while maintaining the same functionality.

# [​](#prerequisites) Prerequisites

Before setting up Claude Code GitHub Actions with cloud providers, you need:

# [​](#for-google-cloud-vertex-ai%3A) For Google Cloud Vertex AI:

1. A Google Cloud Project with Vertex AI enabled
2. Workload Identity Federation configured for GitHub Actions
3. A service account with the required permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

# [​](#for-aws-bedrock%3A) For AWS Bedrock:

1. An AWS account with Amazon Bedrock enabled
2. GitHub OIDC Identity Provider configured in AWS
3. An IAM role with Bedrock permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

1

Create a custom GitHub App (Recommended for 3P Providers)

For best control and security when using 3P providers like Vertex AI or Bedrock, we recommend creating your own GitHub App:

1. Go to <https://github.com/settings/apps/new>
2. Fill in the basic information:
   * **GitHub App name**: Choose a unique name (e.g., “YourOrg Claude Assistant”)
   * **Homepage URL**: Your organization’s website or the repository URL
3. Configure the app settings:
   * **Webhooks**: Uncheck “Active” (not needed for this integration)
4. Set the required permissions:
   * **Repository permissions**:
  + Contents: Read & Write
  + Issues: Read & Write
  + Pull requests: Read & Write
5. Click “Create GitHub App”
6. After creation, click “Generate a private key” and save the downloaded `.pem` file
7. Note your App ID from the app settings page
8. Install the app to your repository:
   * From your app’s settings page, click “Install App” in the left sidebar
   * Select your account or organization
   * Choose “Only select repositories” and select the specific repository
   * Click “Install”
9. Add the private key as a secret to your repository:
   * Go to your repository’s Settings → Secrets and variables → Actions
   * Create a new secret named `APP_PRIVATE_KEY` with the contents of the `.pem` file
10. Add the App ID as a secret:

* Create a new secret named `APP_ID` with your GitHub App’s ID

This app will be used with the [actions/create-github-app-token](https://github.com/actions/create-github-app-token) action to generate authentication tokens in your workflows.

**Alternative for Anthropic API or if you don’t want to setup your own Github app**: Use the official Anthropic app:

1. Install from: <https://github.com/apps/claude>
2. No additional configuration needed for authentication

2

Configure cloud provider authentication

Choose your cloud provider and set up secure authentication:

AWS Bedrock

**Configure AWS to allow GitHub Actions to authenticate securely without storing credentials.**

> **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

**Required Setup**:

1. **Enable Amazon Bedrock**:
  * Request access to Claude models in Amazon Bedrock
   * For cross-region models, request access in all required regions
2. **Set up GitHub OIDC Identity Provider**:
  * Provider URL: `https://token.actions.githubusercontent.com`
   * Audience: `sts.amazonaws.com`
3. **Create IAM Role for GitHub Actions**:
  * Trusted entity type: Web identity
   * Identity provider: `token.actions.githubusercontent.com`
   * Permissions: `AmazonBedrockFullAccess` policy
   * Configure trust policy for your specific repository

**Required Values**:

After setup, you’ll need:

* **AWS\_ROLE\_TO\_ASSUME**: The ARN of the IAM role you created

OIDC is more secure than using static AWS access keys because credentials are temporary and automatically rotated.

See [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) for detailed OIDC setup instructions.

Google Vertex AI

**Configure Google Cloud to allow GitHub Actions to authenticate securely without storing credentials.**

> **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

**Required Setup**:

1. **Enable APIs** in your Google Cloud project:
2. **Create Workload Identity Federation resources**:
  * Create a Workload Identity Pool
   * Add a GitHub OIDC provider with:
  + Issuer: `https://token.actions.githubusercontent.com`
  + Attribute mappings for repository and owner
  + **Security recommendation**: Use repository-specific attribute conditions
3. **Create a Service Account**:
  * Grant only `Vertex AI User` role
   * **Security recommendation**: Create a dedicated service account per repository
4. **Configure IAM bindings**:
  * Allow the Workload Identity Pool to impersonate the service account
   * **Security recommendation**: Use repository-specific principal sets

**Required Values**:

After setup, you’ll need:

* **GCP\_WORKLOAD\_IDENTITY\_PROVIDER**: The full provider resource name
* **GCP\_SERVICE\_ACCOUNT**: The service account email address

Workload Identity Federation eliminates the need for downloadable service account keys, improving security.

For detailed setup instructions, consult the [Google Cloud Workload Identity Federation documentation](https://cloud.google.com/iam/docs/workload-identity-federation).

3

Add Required Secrets

Add the following secrets to your repository (Settings → Secrets and variables → Actions):

# [​](#for-anthropic-api-direct-%3A) For Anthropic API (Direct):

1. **For API Authentication**:
2. **For GitHub App (if using your own app)**:
  * `APP_ID`: Your GitHub App’s ID
   * `APP_PRIVATE_KEY`: The private key (.pem) content

# [​](#for-google-cloud-vertex-ai%3A) For Google Cloud Vertex AI:

1. **For GCP Authentication**:
  * `GCP_WORKLOAD_IDENTITY_PROVIDER`
   * `GCP_SERVICE_ACCOUNT`
2. **For GitHub App (if using your own app)**:
  * `APP_ID`: Your GitHub App’s ID
   * `APP_PRIVATE_KEY`: The private key (.pem) content

# [​](#for-aws-bedrock%3A) For AWS Bedrock:

1. **For AWS Authentication**:
  * `AWS_ROLE_TO_ASSUME`
2. **For GitHub App (if using your own app)**:
  * `APP_ID`: Your GitHub App’s ID
   * `APP_PRIVATE_KEY`: The private key (.pem) content

4

Create workflow files

Create GitHub Actions workflow files that integrate with your cloud provider. The examples below show complete configurations for both AWS Bedrock and Google Vertex AI:

AWS Bedrock workflow

**Prerequisites:**

* AWS Bedrock access enabled with Claude model permissions
* GitHub configured as an OIDC identity provider in AWS
* IAM role with Bedrock permissions that trusts GitHub Actions

**Required GitHub secrets:**

| Secret Name | Description |
| --- | --- |
| `AWS_ROLE_TO_ASSUME` | ARN of the IAM role for Bedrock access |
| `APP_ID` | Your GitHub App ID (from app settings) |
| `APP_PRIVATE_KEY` | The private key you generated for your GitHub App |

```
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    env:
      AWS_REGION: us-west-2
    steps:
  - name: Checkout repository
        uses: actions/checkout@v4
  - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
  - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
          aws-region: us-west-2
  - uses: ./.github/actions/claude-pr-action
        with:
          trigger_phrase: "@claude"
          timeout_minutes: "60"
          github_token: ${{ steps.app-token.outputs.token }}
          use_bedrock: "true"
          model: "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

```

The model ID format for Bedrock includes the region prefix (e.g., `us.anthropic.claude...`) and version suffix.

Google Vertex AI workflow

**Prerequisites:**

* Vertex AI API enabled in your GCP project
* Workload Identity Federation configured for GitHub
* Service account with Vertex AI permissions

**Required GitHub secrets:**

| Secret Name | Description |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload identity provider resource name |
| `GCP_SERVICE_ACCOUNT` | Service account email with Vertex AI access |
| `APP_ID` | Your GitHub App ID (from app settings) |
| `APP_PRIVATE_KEY` | The private key you generated for your GitHub App |

```
name: Claude PR Action

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    steps:
  - name: Checkout repository
        uses: actions/checkout@v4
  - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
  - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
  - uses: ./.github/actions/claude-pr-action
        with:
          trigger_phrase: "@claude"
          timeout_minutes: "60"
          github_token: ${{ steps.app-token.outputs.token }}
          use_vertex: "true"
          model: "claude-3-7-sonnet@20250219"
        env:
          ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
          CLOUD_ML_REGION: us-east5
          VERTEX_REGION_CLAUDE_3_7_SONNET: us-east5

```

The project ID is automatically retrieved from the Google Cloud authentication step, so you don’t need to hardcode it.

# [​](#troubleshooting) Troubleshooting

# [​](#claude-not-responding-to-%40claude-commands) Claude not responding to @claude commands

Verify the GitHub App is installed correctly, check that workflows are enabled, ensure API key is set in repository secrets, and confirm the comment contains `@claude` (not `/claude`).

# [​](#ci-not-running-on-claude%E2%80%99s-commits) CI not running on Claude’s commits

Ensure you’re using the GitHub App or custom app (not Actions user), check workflow triggers include the necessary events, and verify app permissions include CI triggers.

# [​](#authentication-errors) Authentication errors

Confirm API key is valid and has sufficient permissions. For Bedrock/Vertex, check credentials configuration and ensure secrets are named correctly in workflows.

# [​](#advanced-configuration) Advanced configuration

# [​](#action-parameters) Action parameters

The Claude Code Action supports these key parameters:

| Parameter | Description | Required |
| --- | --- | --- |
| `prompt` | The prompt to send to Claude | Yes\* |
| `prompt_file` | Path to file containing prompt | Yes\* |
| `allowed_tools` | Comma-separated string of allowed tools | No |
| `anthropic_api_key` | Anthropic API key | Yes\*\* |
| `max_turns` | Maximum conversation turns | No |
| `timeout_minutes` | Execution timeout | No |

\*Either `prompt` or `prompt_file` required
\*\*Required for direct Anthropic API, not for Bedrock/Vertex

# [​](#alternative-integration-methods) Alternative integration methods

While the `/install-github-app` command is the recommended approach, you can also:

* **Custom GitHub App**: For organizations needing branded usernames or custom authentication flows. Create your own GitHub App with required permissions (contents, issues, pull requests) and use the actions/create-github-app-token action to generate tokens in your workflows.
* **Manual GitHub Actions**: Direct workflow configuration for maximum flexibility
* **MCP Configuration**: Dynamic loading of Model Context Protocol servers

See the [Claude Code Action repository](https://github.com/anthropics/claude-code-action) for detailed documentation.

# [​](#customizing-claude%E2%80%99s-behavior) Customizing Claude’s behavior

You can configure Claude’s behavior in two ways:

1. **CLAUDE.md**: Define coding standards, review criteria, and project-specific rules in a `CLAUDE.md` file at the root of your repository. Claude will follow these guidelines when creating PRs and responding to requests. Check out our [Memory documentation](/en/docs/claude-code/memory) for more details.
2. **Custom prompts**: Use the `prompt` parameter in the workflow file to provide workflow-specific instructions. This allows you to customize Claude’s behavior for different workflows or tasks.

Claude will follow these guidelines when creating PRs and responding to requests.

Was this page helpful?

YesNo

Bedrock, Vertex, and proxies[SDK](/en/docs/claude-code/sdk)

On this page
