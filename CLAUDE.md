# Project Defaults and Assistant Behavior

## Python Projects

- **Formatting:** black  
- **Linting:** ruff  
- **Testing:** pytest  
- **Release:** release-please  

### Requirements
- JSON logging with UTC timestamps
- Prometheus metrics integration
- Commit linting using conventional commits with custom rules
- All technical recommendations must be supported by factual evidence (documentation or source code)
- Speculative reasoning must be clearly labeled
- Diagnostics must be traceable in code comments or commit messages

### Setup Tasks
- Configure release-please
- Setup commitlint
- Configure formatting and linting
- Setup pytest and Prometheus metrics
- Enforce diagnostic traceability and factual validation

## Commit Standards

- Never attribute Claude as a co-author
- All commit messages must include:
  - A summary of diagnostic findings
  - Rationale for the change
  - References to documentation or code if applicable

## Policy for Technical Recommendations

- All suggestions must be based on documentation or validated source code
- Uncertain recommendations must:
  - Be explicitly marked
  - Include a proposed validation plan (e.g. test, reproducer, logs)
