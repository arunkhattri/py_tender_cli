> **A CLI application that takes a tender PDF and lets you query its Make List and BOQ/SOQ.**

## Proposed end-state

``` text
                    tender.pdf
                        │
                        ▼
                 ┌─────────────┐
                 │  CLI: ingest │
                 └──────┬──────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
          Make List             BOQ/SOQ
          DataFrame             DataFrame
              │                   │
              └─────────┬─────────┘
                        ▼
                  local storage
                        │
                        ▼
                 ┌─────────────┐
                 │  CLI: query  │
                 └──────┬──────┘
                        │
                 natural language
                        │
                        ▼
                     Answer
```

## Engineering Principle

> **Use structured data first; use AI where structured querying isn't sufficient.**
