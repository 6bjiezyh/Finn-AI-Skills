---
name: daily-ai-topic-planner
description: Generate daily content topics for AI-focused creators across long-form and short-form video platforms. Use when users ask for daily topic ideas, title options, publishing priorities, or monetization-oriented content planning for AI, n8n automation, AI tools, Coze, vibe coding, AI赚钱, and AIGC.
---

# Daily AI Topic Planner

## Overview

Generate a daily topic package for an AI creator business that publishes long videos on Bilibili and short videos on Chinese short-form platforms. Keep output conversion-oriented for paid community growth and custom workflow services.

## Workflow

1. Parse input constraints.
2. Collect hot signals by using `references/hot-signal-sources.md`.
3. Add evergreen candidates by using `references/content-pillars.md`.
4. Split ideas by platform by using `references/platform-playbook.md`.
5. Attach monetization hooks by using `references/monetization-hooks.md`.
6. Score, filter, and rank by using `references/scoring-model.md`.
7. Build an expanded 20-topic pool by using category quotas in `references/content-pillars.md`.
8. Render final output with `references/daily-output-template.md`.
9. Persist the generated topics to CSV and then upload to Feishu Bitable with `/Users/heyang/Workspace/.agents/skills/daily-ai-topic-planner/upload_feishu_bitable.py`.

## Input Contract

Use these optional fields when provided:

- `date`: planning date, default to today.
- `recent_published_topics`: list of topics published in last 7 days.
- `priority_track`: optional focus track such as `n8n` or `AI赚钱`.
- `campaign_goal`: optional goal such as `社群拉新` or `定制咨询`.
- `avoid_topics`: forbidden topics.
- `feishu_auto_upload`: upload generated topics after output, default `true`.

## Topic Generation Rules

Apply all rules below:

- Keep coverage inside these seven pillars: AI, n8n自动化, AI工具, 扣子, Vibe Coding, AI赚钱, AIGC.
- Use hot-signal mix: platform trend 50%, official releases 30%, trend-demand 20%.
- Use time windows: main window 24h, backup window 7d.
- Enforce conversion feasibility: each topic must map to paid community or workflow customization.
- Enforce de-duplication: if overlap with recent topics, downgrade or replace.
- Generate `ExpandedTopicPool20` as AI-original topics. Do not copy, lightly rewrite, or mirror source headlines.
- For every expanded-pool item, synthesize a new angle by combining signal + audience pain + monetization path.

## Output Contract

Always return these sections:

- `LongVideoIdeas`: exactly 3 items.
- `ShortVideoIdeas`: exactly 7 items.
- `PublishPriority`: exactly 1 long + 2 short priorities.
- `ExpandedTopicPool20`: exactly 20 items.

`ExpandedTopicPool20` is mandatory in every response, even when the user does not ask for it explicitly.

Each idea item must include all fields:

- `topic_angle`
- `category`
- `audience_pain`
- `titles` (exactly 3)
- `content_outline`
- `monetization_hook`
- `cta`
- `timeliness` (`hot` or `evergreen`)
- `difficulty` (`low` / `medium` / `high`)
- `score`

`ExpandedTopicPool20` must satisfy these category counts:

- `AI自动化`: 6 items.
- `Vibe Coding`: 4 items.
- `AIGC`: 4 items.
- `AI提效`: 3 items.
- `AI变现案例`: 3 items.

## Quality Guardrails

- Reject any idea that does not match at least one of the seven pillars.
- Reject long-video ideas with score `< 7.0`.
- Reject short-video ideas with score `< 6.5`.
- Reject expanded-pool ideas with score `< 6.5`.
- Backfill rejected slots from evergreen pool.
- Enforce `ExpandedTopicPool20` category counts exactly as defined.
- Reject any expanded-pool item that is a near-duplicate of a source headline.
- Keep language in Chinese unless user asks otherwise.

## References

- Pillars and angles: `references/content-pillars.md`
- Platform structures: `references/platform-playbook.md`
- Conversion hooks and CTA: `references/monetization-hooks.md`
- Hot-signal source map: `references/hot-signal-sources.md`
- Scoring formula and thresholds: `references/scoring-model.md`
- Final output schema and template: `references/daily-output-template.md`
- Feishu uploader script: `/Users/heyang/Workspace/.agents/skills/daily-ai-topic-planner/upload_feishu_bitable.py`
