# Using the Admin API - Anthropic

**Source:** https://docs.anthropic.com/en/docs/administration/administration-api

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

**The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.

The [Admin API](/en/api/admin-api) allows you to programmatically manage your organization’s resources, including organization members, workspaces, and API keys. This provides programmatic control over administrative tasks that would otherwise require manual configuration in the [Anthropic Console](https://console.anthropic.com).

**The Admin API requires special access**

The Admin API requires a special Admin API key (starting with `sk-ant-admin...`) that differs from standard API keys. Only organization members with the admin role can provision Admin API keys through the Anthropic Console.

# [​](#how-the-admin-api-works) How the Admin API works

When you use the Admin API:

1. You make requests using your Admin API key in the `x-api-key` header
2. The API allows you to manage:

This is useful for:

* Automating user onboarding/offboarding
* Programmatically managing workspace access
* Monitoring and managing API key usage

# [​](#organization-roles-and-permissions) Organization roles and permissions

There are five organization-level roles.

| Role | Permissions |
| --- | --- |
| user | Can use Workbench |
| claude\_code\_user | Can use Workbench and [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) |
| developer | Can use Workbench and manage API keys |
| billing | Can use Workbench and manage billing details |
| admin | Can do all of the above, plus manage users |

# [​](#key-concepts) Key concepts

# [​](#organization-members) Organization Members

You can list organization members, update member roles, and remove members.

Shell

```
# List organization members

curl "https://api.anthropic.com/v1/organizations/users?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Update member role

curl "https://api.anthropic.com/v1/organizations/users/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{"role": "developer"}'

# Remove member

curl --request DELETE "https://api.anthropic.com/v1/organizations/users/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

```

# [​](#organization-invites) Organization Invites

You can invite users to organizations and manage those invites.

Shell

```
# Create invite

curl --request POST "https://api.anthropic.com/v1/organizations/invites" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "email": "newuser@domain.com",
    "role": "developer"
  }'

# List invites

curl "https://api.anthropic.com/v1/organizations/invites?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Delete invite

curl --request DELETE "https://api.anthropic.com/v1/organizations/invites/{invite_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

```

# [​](#workspaces) Workspaces

Create and manage [workspaces](https://console.anthropic.com/settings/workspaces) to organize your resources:

Shell

```
# Create workspace

curl --request POST "https://api.anthropic.com/v1/organizations/workspaces" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{"name": "Production"}'

# List workspaces

curl "https://api.anthropic.com/v1/organizations/workspaces?limit=10&include_archived=false" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Archive workspace

curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/archive" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

```

# [​](#workspace-members) Workspace Members

Manage user access to specific workspaces:

Shell

```
# Add member to workspace

curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "user_id": "user_xxx",
    "workspace_role": "workspace_developer"
  }'

# List workspace members

curl "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Update member role

curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "workspace_role": "workspace_admin"
  }'

# Remove member from workspace

curl --request DELETE "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

```

# [​](#api-keys) API Keys

Monitor and manage API keys:

Shell

```
# List API keys

curl "https://api.anthropic.com/v1/organizations/api_keys?limit=10&status=active&workspace_id=wrkspc_xxx" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Update API key

curl --request POST "https://api.anthropic.com/v1/organizations/api_keys/{api_key_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "status": "inactive",
    "name": "New Key Name"
  }'

```

# [​](#best-practices) Best practices

To effectively use the Admin API:

* Use meaningful names and descriptions for workspaces and API keys
* Implement proper error handling for failed operations
* Regularly audit member roles and permissions
* Clean up unused workspaces and expired invites
* Monitor API key usage and rotate keys periodically

# [​](#faq) FAQ

Only organization members with the admin role can use the Admin API. They must also have a special Admin API key (starting with `sk-ant-admin`).

No, new API keys can only be created through the Anthropic Console for security reasons. The Admin API can only manage existing API keys.

API keys persist in their current state as they are scoped to the Organization, not to individual users.

How long do organization invites last?

Organization invites expire after 21 days. There is currently no way to modify this expiration period.

Are there limits on workspaces?

Yes, you can have a maximum of 100 workspaces per Organization. Archived workspaces do not count towards this limit.

What's the Default Workspace?

Every Organization has a “Default Workspace” that cannot be edited or removed, and has no ID. This Workspace does not appear in workspace list endpoints.

How do organization roles affect Workspace access?

Organization admins automatically get the `workspace_admin` role to all workspaces. Organization billing members automatically get the `workspace_billing` role. Organization users and developers must be manually added to each workspace.

Which roles can be assigned in workspaces?

Organization users and developers can be assigned `workspace_admin`, `workspace_developer`, or `workspace_user` roles. The `workspace_billing` role can’t be manually assigned - it’s inherited from having the organization `billing` role.

Can organization admin or billing members' workspace roles be changed?

Only organization billing members can have their workspace role upgraded to an admin role. Otherwise, organization admins and billing members can’t have their workspace roles changed or be removed from workspaces while they hold those organization roles. Their workspace access must be modified by changing their organization role first.

What happens to workspace access when organization roles change?

If an organization admin or billing member is demoted to user or developer, they lose access to all workspaces except ones where they were manually assigned roles. When users are promoted to admin or billing roles, they gain automatic access to all workspaces.

Was this page helpful?

YesNo

Supported regions[Getting help](/en/api/getting-help)

On this page
