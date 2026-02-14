# Scoring Model

## Formula

Use this formula for every candidate idea:

`Score = 0.35*Trend + 0.25*AudienceFit + 0.25*Monetization + 0.15*ProductionEase`

Use 0-10 for each component.

## Dimensions

- `Trend`: recency and market attention.
- `AudienceFit`: relevance to AI beginners, AI efficiency seekers, AI income seekers.
- `Monetization`: clarity of conversion path to paid community or workflow service.
- `ProductionEase`: fit to current production bandwidth and complexity.

## Acceptance Threshold

- Long video idea: keep only if `Score >= 7.0`.
- Short video idea: keep only if `Score >= 6.5`.
- If candidates are insufficient, pull from evergreen pool and rescore.

## Ranking Rule

- Rank long and short pools separately by score.
- Break ties by monetization score, then trend score.
- Publish priority should choose:
  - highest-scoring long video with strong conversion fit
  - top 2 short videos with high trend and fast production ease
