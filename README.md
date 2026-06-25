# Trello-lite

A Kanban-style project board that ships via a fully automated AI-assisted delivery pipeline.

## Delivery Pipeline

Features are built by AI and shipped through deterministic CI: the pipeline decides pass or fail based on BDD specs that were written before any implementation exists.

See the full slide deck: [docs/pipeline-deck.html](docs/pipeline-deck.html)

### How it works

```mermaid
flowchart LR
    Spec["Spec (BDD feature)"] --> tests["tests run in CI"]
    tests --> review["AI code review"]
    review --> deploy["deploy to GitHub Pages"]
```

1. **Spec** — a `.feature` file captures the desired behaviour before any code is written.
2. **tests** — pytest-bdd runs the scenarios deterministically; the pipeline decides pass or fail.
3. **review** — an AI implementer writes the code; a reviewer checks it.
4. **deploy** — once tests pass the site is deployed to GitHub Pages automatically.
