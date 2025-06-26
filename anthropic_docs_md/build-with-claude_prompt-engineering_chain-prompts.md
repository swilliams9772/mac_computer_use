# Chain complex prompts for stronger performance - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-prompts

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# First steps

* [Intro to Claude](/en/docs/welcome)
* [Get started](/en/docs/get-started)

# Models & pricing

* [Models overview](/en/docs/about-claude/models/overview)
* [Choosing a model](/en/docs/about-claude/models/choosing-a-model)
* [Migrating to Claude 4](/en/docs/about-claude/models/migrating-to-claude-4)
* [Model deprecations](/en/docs/about-claude/model-deprecations)
* [Pricing](/en/docs/about-claude/pricing)

# Learn about Claude

* [Building with Claude](/en/docs/overview)
* Use cases
* [Context windows](/en/docs/build-with-claude/context-windows)
* [Glossary](/en/docs/about-claude/glossary)
* Prompt engineering

  + [Overview](/en/docs/build-with-claude/prompt-engineering/overview)
  + [Claude 4 best practices](/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
  + [Prompt generator](/en/docs/build-with-claude/prompt-engineering/prompt-generator)
  + [Use prompt templates](/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables)
  + [Prompt improver](/en/docs/build-with-claude/prompt-engineering/prompt-improver)
  + [Be clear and direct](/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)
  + [Use examples (multishot prompting)](/en/docs/build-with-claude/prompt-engineering/multishot-prompting)
  + [Let Claude think (CoT)](/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
  + [Use XML tags](/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
  + [Give Claude a role (system prompts)](/en/docs/build-with-claude/prompt-engineering/system-prompts)
  + [Prefill Claude's response](/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response)
  + [Chain complex prompts](/en/docs/build-with-claude/prompt-engineering/chain-prompts)
  + [Long context tips](/en/docs/build-with-claude/prompt-engineering/long-context-tips)
  + [Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips)

# Explore features

* [Features overview](/en/docs/build-with-claude/overview)
* [Prompt caching](/en/docs/build-with-claude/prompt-caching)
* [Extended thinking](/en/docs/build-with-claude/extended-thinking)
* [Streaming Messages](/en/docs/build-with-claude/streaming)
* [Batch processing](/en/docs/build-with-claude/batch-processing)
* [Citations](/en/docs/build-with-claude/citations)
* [Multilingual support](/en/docs/build-with-claude/multilingual-support)
* [Token counting](/en/docs/build-with-claude/token-counting)
* [Embeddings](/en/docs/build-with-claude/embeddings)
* [Vision](/en/docs/build-with-claude/vision)
* [PDF support](/en/docs/build-with-claude/pdf-support)

# Agent components

* Tools
* Model Context Protocol (MCP)
* [Computer use (beta)](/en/docs/agents-and-tools/computer-use)
* [Google Sheets add-on](/en/docs/agents-and-tools/claude-for-sheets)

# Test & evaluate

* [Define success criteria](/en/docs/test-and-evaluate/define-success)
* [Develop test cases](/en/docs/test-and-evaluate/develop-tests)
* Strengthen guardrails
* [Using the Evaluation Tool](/en/docs/test-and-evaluate/eval-tool)

# Legal center

* [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy)
* [Security and compliance](https://trust.anthropic.com/)

While these tips apply broadly to all Claude models, you can find prompting tips specific to extended thinking models [here](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips).

When working with complex tasks, Claude can sometimes drop the ball if you try to handle everything in a single prompt. Chain of thought (CoT) prompting is great, but what if your task has multiple distinct steps that each require in-depth thought?

Enter prompt chaining: breaking down complex tasks into smaller, manageable subtasks.

# [​](#why-chain-prompts%3F) Why chain prompts?

1. **Accuracy**: Each subtask gets Claude’s full attention, reducing errors.
2. **Clarity**: Simpler subtasks mean clearer instructions and outputs.
3. **Traceability**: Easily pinpoint and fix issues in your prompt chain.

# [​](#when-to-chain-prompts) When to chain prompts

Use prompt chaining for multi-step tasks like research synthesis, document analysis, or iterative content creation. When a task involves multiple transformations, citations, or instructions, chaining prevents Claude from dropping or mishandling steps.

**Remember:** Each link in the chain gets Claude’s full attention!

**Debugging tip**: If Claude misses a step or performs poorly, isolate that step in its own prompt. This lets you fine-tune problematic steps without redoing the entire task.

# [​](#how-to-chain-prompts) How to chain prompts

1. **Identify subtasks**: Break your task into distinct, sequential steps.
2. **Structure with XML for clear handoffs**: Use XML tags to pass outputs between prompts.
3. **Have a single-task goal**: Each subtask should have a single, clear objective.
4. **Iterate**: Refine subtasks based on Claude’s performance.

# [​](#example-chained-workflows%3A) Example chained workflows:

* **Multi-step analysis**: See the legal and business examples below.
* **Content creation pipelines**: Research → Outline → Draft → Edit → Format.
* **Data processing**: Extract → Transform → Analyze → Visualize.
* **Decision-making**: Gather info → List options → Analyze each → Recommend.
* **Verification loops**: Generate content → Review → Refine → Re-review.

**Optimization tip**: For tasks with independent subtasks (like analyzing multiple docs), create separate prompts and run them in parallel for speed.

# [​](#advanced%3A-self-correction-chains) Advanced: Self-correction chains

You can chain prompts to have Claude review its own work! This catches errors and refines outputs, especially for high-stakes tasks.

# [​](#prompt-1) Prompt 1

| Role | Content |
| --- | --- |
| User | Summarize this medical research paper.<paper>{{RESEARCH\_PAPER}}</paper>Focus on methodology, findings, and clinical implications. |
| Assistant{{SUMMARY}} | Methodology: Double-blind RCT with 500 Type 2 diabetes patients. Group A (n=250) received novel GLP-1/GIP dual agonist; Group B (n=250) received standard GLP-1 agonist. 24-week trial, primary endpoint: HbA1c reduction.Findings:- Group A: 1.8% mean HbA1c reduction- Group B: 1.1% mean HbA1c reduction- 68% of Group A vs. 52% of Group B achieved HbA1c <7%- Group A: 5.2kg mean weight loss- Group B: 3.1kg mean weight lossSafety: Similar adverse event profiles, no serious events attributed to treatment.Clinical Implications: Dual agonist shows superior glycemic control and weight loss compared to standard therapy. Could be a game-changer, especially for obese diabetics. |

# [​](#prompt-2) Prompt 2

| Role | Content |
| --- | --- |
| User | Your task is to provide feedback on a research paper summary. Here is a summary of a medical research paper:<summary>{{SUMMARY}}</summary>Here is the research paper:<paper>{{RESEARCH\_PAPER}}</paper>Review this summary for accuracy, clarity, and completeness on a graded A-F scale. |
| Assistant{{FEEDBACK}} | 1. Accuracy: A - Correctly reported key stats: HbA1c reductions, weight loss. - Accurately noted safety profile and lack of serious adverse events. - Assertion of “game-changer” is justified by significantly better outcomes.2. Clarity: A- - Concise and well-structured with clear sections. - Good use of comparative language (e.g., “up 3% from Q1”) for context. - Minor issue: Acronyms like “RCT,” “GLP-1,” and “GIP” not defined. Consider spelling out first use.3. Completeness: B+ - Covers all requested areas: methodology, findings, clinical implications. - Missing: Baseline characteristics of groups (were they well-matched?). - Missing: Any secondary endpoints (e.g., blood pressure, lipids). - Consider: Long-term implications or need for further research.Overall, the summary is accurate and clear, providing key insights for a quick grasp of the study. To elevate to A+, define acronyms, mention group baseline stats, note any secondary outcomes, and briefly touch on the need for long-term studies. |

# [​](#prompt-3) Prompt 3

| Role | Content |
| --- | --- |
| User | Your task is to improve a paper summary given feedback. Here is the first draft of a medical research paper:<summary>{{SUMMARY}}</summary>Here is the research paper:<paper>{{RESEARCH\_PAPER}}</paper>Here is the feedback:<feedback>{{FEEDBACK}}</feedback>Update the summary based on the feedback. |
| Assistant | Methodology: Double-blind randomized controlled trial (RCT) with 500 Type 2 diabetes patients. Group A (n=250) received a novel glucagon-like peptide-1/glucose-dependent insulinotropic polypeptide (GLP-1/GIP) dual agonist; Group B (n=250) received a standard GLP-1 agonist. The 24-week trial’s primary endpoint was HbA1c reduction. Groups were well-matched for age, BMI, and baseline HbA1c.Findings:- Group A: 1.8% mean HbA1c reduction- Group B: 1.1% mean HbA1c reduction- 68% of Group A vs. 52% of Group B achieved HbA1c <7%- Group A: 5.2kg mean weight loss- Group B: 3.1kg mean weight lossSecondary endpoints showed improvements in blood pressure and lipid profiles for both groups, with Group A showing slightly better results.Safety: Similar adverse event profiles, with no serious events attributed to either treatment.Clinical Implications: The dual GLP-1/GIP agonist demonstrates superior glycemic control and weight loss compared to standard GLP-1 therapy. These results suggest it could be a significant advancement, particularly for obese diabetics. However, longer-term studies are needed to confirm sustained efficacy and safety, as well as to investigate potential benefits on cardiovascular outcomes. |

# [​](#examples) Examples

Example: Analyzing a legal contract (without chaining)

Note that Claude misses the instruction to provide proposed changes in its email draft.

| Role | Content |
| --- | --- |
| User | You’re our Chief Legal Officer. Review this SaaS contract for risks, focusing on data privacy, SLAs, and liability caps.<contract>{{CONTRACT}}</contract>Then draft an email to the vendor with your concerns and proposed changes. |
| Assistant | After reviewing the SaaS contract, I’ve identified several concerns:1. Data Privacy (Section 7): - Issue: Vendor has broad rights to use client data for “service improvement.” - Risk: Could lead to unauthorized data sharing or monetization.2. SLAs (Section 5): - Issue: 99.5% uptime guarantee is below industry standard. - Risk: Excessive downtime could impact our operations.3. Liability (Section 9): - Issue: Cap set at 3 months of fees. - Risk: Inadequate for potential data breaches or service failures.Draft email:Dear {{VENDOR}},After reviewing the SaaS agreement, we have concerns:1. Data Privacy: We require that our data only be used for direct service provision, not broad “service improvement.” Please amend Section 7.2. SLAs: 99.5% uptime is insufficient. We need 99.99% with clearly defined penalties. Please revise Section 5.3. Liability: The current cap of 3 months’ fees is inadequate. We propose a cap of 12 months’ fees, with no cap for data breaches or willful misconduct.We value our potential partnership and believe these changes will set us up for success. Please send a revised agreement.Best regards,{{CLO\_NAME}} |

Example: Analyzing a legal contract (with chaining)

# [​](#prompt-1-2) Prompt 1

| Role | Content |
| --- | --- |
| User | You’re our Chief Legal Officer. Review this SaaS contract for risks, focusing on data privacy, SLAs, and liability caps.<contract>{{CONTRACT}}</contract>Output your findings in <risks> tags. |
| Assistant{{CONCERNS}} | 1. Data Privacy (Section 7): - Issue: Vendor has broad rights to use client data for “service improvement.” - Risk: Could lead to unauthorized data sharing or monetization of client data. - Impact: Potential breach of client trust, regulatory fines (GDPR, CCPA).2. SLAs (Section 5): - Issue: 99.5% uptime guarantee is below industry standard (typically 99.99%). - Risk: Up to 43.8 hours of downtime per year vs. 52.6 minutes at 99.99%. - Impact: Operational disruptions, revenue loss, client dissatisfaction.3. Liability (Section 9): - Issue: Liability cap set at 3 months of fees. - Risk: Inadequate for potential data breaches, IP theft, or prolonged service failures. - Impact: Insufficient compensation for damages that could far exceed the cap, like class-action lawsuits or regulatory fines. |

# [​](#prompt-2-2) Prompt 2

| Role | Content |
| --- | --- |
| User | Draft an email to a SaaS product vendor outlining the following concerns and proposing changes. Here are the concerns:<concerns>{{CONCERNS}}</concerns> |
| Assistant{{EMAIL}} | Dear {{VENDOR}},After a thorough review of the proposed SaaS agreement, our legal team has identified several high-priority concerns that must be addressed before we can proceed:1. Data Privacy (Section 7): - Current: Broad rights to use client data for “service improvement.” - Concern: Potential unauthorized data sharing or monetization. - Proposed Change: Limit data use to direct service provision. Any use for improvement, analytics, or marketing must be opt-in, revocable, and anonymized.2. SLAs (Section 5): - Current: 99.5% uptime guarantee. - Concern: Up to 43.8 hours of downtime per year, risking operational disruptions. - Proposed Change: 99.99% uptime with tiered service credits. E.g., 10% credit for <99.99%, 25% for <99.9%, 50% for <99.5%.3. Liability (Section 9): - Current: Cap at 3 months of fees. - Concern: Grossly inadequate for data breaches, IP theft, or prolonged outages. - Proposed Change: 12 months’ fees for general liability. Uncapped for data breaches, willful misconduct, IP infringement.These changes are non-negotiable for us. They align with industry standards and our commitment to data security, operational excellence, and fiduciary responsibility. We value the potential of our partnership, and addressing these will set a strong foundation.Please have your legal team review and incorporate these changes. We’re happy to discuss further to ensure mutual understanding and agreement.Best regards,{{CLO\_NAME}} |

# [​](#prompt-3-2) Prompt 3

| Role | Content |
| --- | --- |
| User | Your task is to review an email and provide feedback. Here is the email:<email>{{EMAIL}}</email>Give feedback on tone, clarity, and professionalism. |
| Assistant | 1. Tone: - Professional and assertive without being confrontational. - Use of “non-negotiable” is strong but justified given the criticality of the issues. - Collaborative language (“we value,” “happy to discuss”) balances the firmness, maintaining a constructive tone.2. Clarity: - Excellent structuring: Current state, concern, and proposed change for each issue. - Technical terms (e.g., “EBITDA,” “tiered service credits”) are appropriate for a B2B SaaS context. - Action items are clear: vendor’s legal team to review and incorporate changes.3. Professionalism: - Focuses on mutual benefit and industry standards, not just our demands. - Mentions broader responsibilities (data security, operational excellence, fiduciary duty), elevating the discussion. - Offers further discussion, showing commitment to understanding and resolving issues.Overall, the email strikes the right balance of assertiveness and collaboration. It clearly articulates our concerns, proposes specific solutions, and maintains a professional, partnership-oriented tone. No revisions needed; proceed with sending. |

Example: Multitenancy strategy review

# [​](#prompt-1-3) Prompt 1

| Role | Content |
| --- | --- |
| User | As a senior solutions architect, review and analyze this multitenancy strategy for our new enterprise SaaS product.<strategy>{{STRATEGY}}</strategy>Focus on scalability, security, and cost-effectiveness. |
| Assistant{{ANALYSIS}} | 1. Scalability: + Database sharding by tenant reduces contention, supports high growth. + Microservices allow independent scaling of components. - Shared app servers could bottleneck under extreme load. - No mention of auto-scaling or load balancing for app tier.2. Security: + Tenant data isolation via sharding mitigates data leaks. + JWT with short expiry and refresh tokens is industry best practice. - No mention of encryption (at rest, in transit) or key management. - IAM strategy lacks detail on roles, permissions, or RBAC.3. Cost-effectiveness: + Shared app servers reduce idle resource costs. + Serverless functions for infrequent tasks optimize costs. - Per-tenant DB could increase costs at scale vs. optimized multi-tenant DB. - No discussion of reserved instances or spot instances for cost saving. |

# [​](#prompt-2-3) Prompt 2

| Role | Content |
| --- | --- |
| User | Draft a strategy review document for engineering leadership based on this analysis of a multitenancy strategy.<strategy>{{STRATEGY}}</strategy><analysis>{{ANALYSIS}}</analysis>Include an executive summary, detailed analysis, and recommendations. |
| Assistant{{STRATEGY\_DOC}} | # Multitenancy Strategy Review: SaaS Enterprise Product## Executive SummaryThe proposed strategy demonstrates a solid foundation in scalability and security principles but has gaps in implementation details. It excels in data isolation and component-level scaling but lacks robust app-tier scaling and advanced security measures. Cost optimizations are present but may falter at high scale. With targeted enhancements, this strategy can effectively support our enterprise SaaS ambitions.## Detailed Analysis### 1. Scalability: B+Strengths:- Database sharding by tenant is excellent. It minimizes query latency, supports high data growth, and facilitates seamless per-tenant scaling.- Microservices architecture allows scaling individual components based on demand, crucial for handling diverse enterprise workloads.Weaknesses:- Shared application servers risk becoming a bottleneck. As tenant count and traffic grow, these could degrade performance across all tenants.- Absence of auto-scaling and load balancing for the app tier is a critical oversight. These are essential for handling traffic spikes without over-provisioning.### 2. Security: B-Strengths:- Sharded databases provide strong tenant data isolation, mitigating risks of data leaks or unauthorized access between tenants.- JWT with short expiry and refresh tokens align with OWASP best practices, reducing token vulnerability windows.Weaknesses:- No mention of data encryption at rest or in transit (TLS 1.3). This is non-negotiable for enterprise data.- Key management strategy is missing. How are encryption keys, JWT secrets, and DB credentials managed and rotated?- IAM lacks depth. We need RBAC with well-defined roles, attribute-based access control (ABAC) for fine-grained permissions, and integration with enterprise identity providers (SAML, OIDC).### 3. Cost-effectiveness: BStrengths:- Shared app servers reduce idle capacity costs, good for steady-state traffic.- Serverless for infrequent tasks (e.g., reporting) is smart; pay only when these resources are used.Weaknesses:- Per-tenant databases may not be cost-effective at scale compared to a well-designed multi-tenant database with robust data partitioning.- No mention of cost-saving measures like reserved instances for predictable workloads or spot instances for fault-tolerant tasks.- Lack of app-tier auto-scaling could lead to over-provisioning, increasing costs.## Recommendations1. **App Tier Resilience**: Implement auto-scaling with Kubernetes or cloud-native services (EKS, GKE). Deploy across availability zones with a CDN for static assets.2. **Security Hardening**: a. Encrypt data at rest (AES-256) and in transit (TLS 1.3). b. Use a managed KMS (AWS KMS, GCP KMS) for key management. c. Enhance IAM with RBAC, ABAC, and SAML/OIDC for enterprise SSO.3. **Cost Optimization**: a. Evaluate columnar multi-tenant DB (e.g., Snowflake) vs. sharding at scale. b. Use reserved instances for app servers, spot instances for non-critical workloads. c. Implement proactive monitoring and right-sizing to avoid overprovisioning.4. **Proof of Concept (PoC)**: Before full implementation, conduct a PoC with a high-scale simulation: a. Test sharded DB vs. optimized multi-tenant DB for cost and performance. b. Stress-test app tier with simulated enterprise-level traffic spikes. c. Conduct third-party security audit, focusing on data isolation and access controls.With these enhancements, our multi-tenancy strategy will be enterprise-grade: scalable, secure, and cost-effective. The PoC will validate our design choices and instill confidence in our enterprise clients. |

# [​](#prompt-3-3) Prompt 3

| Role | Content |
| --- | --- |
| User | Grade this strategy review document for clarity, actionability, and alignment with enterprise priorities. <priorities>{{PRIORITIES}}</priorities><strategy\_doc>{{STRATEGY\_DOC}}</strategy\_doc> |
| Assistant | 1. Clarity: A + Clear structure with Executive Summary, Detailed Analysis, and Recommendations. + Analysis uses a grading system (B+, B-) for quick grasp of strengths/weaknesses. + Technical terms (RBAC, ABAC, TLS) are explained or contextualized, aiding non-technical leadership. + Visual aids (bullet points, indentation) enhance readability.2. Actionability: A- + Recommendations are specific and technical (e.g., “Implement auto-scaling with Kubernetes”). + PoC plan with clear objectives provides a roadmap. + Missing: Timelines, resource requirements, or team assignments for each recommendation. + Consider: Add a “Next Steps” section with immediate actions, roles, and a high-level timeline.3. Enterprise Alignment: A+ + Directly addresses enterprise priorities: - Scalability: Discusses handling enterprise-level traffic spikes. - Security: Focuses on data isolation, encryption, and enterprise IAM. - Cost: Strategies align with enterprise FinOps (reserved instances, right-sizing). + PoC with “high-scale simulation” and security audit shows commitment to enterprise-grade quality. + Language resonates with enterprise concerns: “unacceptable risk,” “enterprise-grade,” “instill confidence.”Overall, the document excels in clarity and enterprise alignment. The actionability is strong but could be elevated to A+ with a “Next Steps” section. The technical depth, coupled with clear explanations, makes this highly effective for both technical and non-technical leadership. Great work! |

## Prompt library

Get inspired by a curated selection of prompts for various tasks and use cases.[## GitHub prompting tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)[## Google Sheets prompting tutorial

A lighter weight version of our prompt engineering tutorial via an interactive spreadsheet.](https://docs.google.com/spreadsheets/d/19jzLgRruG9kjUQNKtCg1ZjdD6l6weA6qRXG5zLIAhC8)

Was this page helpful?

YesNo

Prefill Claude's response[Long context tips](/en/docs/build-with-claude/prompt-engineering/long-context-tips)

On this page
