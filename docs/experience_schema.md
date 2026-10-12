
# Experience Data Model

## Purpose

The Experience model represents a contributor's firsthand account
of a social interaction, together with contextual information and
contributor-supplied evidence.

The model preserves the original narrative and distinguishes
observations, interpretations, and unknown information.

## Experience

Required fields:
- narrative: Original contributor narrative.
- country: Country where the experience occurred.

Optional collections:
- context: Contextual attributes indexed by dimension.
- evidence: Contributor-supplied observations, interpretations,
  and explicitly unknown details.

Both collections default to empty.

## ContextAttribute

Each contextual attribute contains:

- status: known or unknown.
- value: Textual information when status is known.
- source: Currently restricted to contributor.
- evidence_ids: Optional references to supporting evidence.

A known attribute requires a nonblank value.

An unknown attribute must not contain a value.

An absent attribute means the information was not provided,
which is different from explicitly unknown information.

Context dimensions are extensible and are not restricted to
a predefined list.

## Evidence

Each evidence entry contains:

- id: Optional identifier.
- type: observation, interpretation, or unknown.
- content: Nonblank contributor-supplied text.

Observations are contributor-reported, not independently
verified facts.

Interpretations represent the contributor's understanding,
not necessarily another participant's actual intention.

Unknown evidence records an explicitly identified gap
in knowledge.

## Validation Rules

- Narrative and country are required and cannot be blank.
- Original narrative text is preserved without rewriting.
- Unknown model fields are rejected.
- Context status and value must be consistent.
- Evidence identifiers must be unique when provided.
- Context attributes cannot reference nonexistent evidence.

## Architectural Decisions

1. Domain models use Pydantic for structural validation.
2. Context dimensions are extensible rather than hardcoded.
3. Evidence is represented separately from contextual attributes.
4. Context attributes may reference evidence through identifiers.
5. Missing information is not interpreted as irrelevant.
6. The model does not infer unwritten rules automatically.
7. Database persistence, retrieval, and AI generation are
   separate responsibilities.

## Known Limitations

- Evidence identifiers are optional until persistence design.
- Evidence classifications are contributor-supplied and not verified.
- Context dimensions do not yet have a controlled vocabulary.
- The model validates evidence references at creation time,
  but later mutation of nested collections can bypass that check.
- The model does not yet enforce how evidence is used by
  retrieval or generation components.

These limitations will be addressed where relevant in later
milestones.
