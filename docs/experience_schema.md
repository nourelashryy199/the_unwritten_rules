
# Experience Data Model

## 1. Purpose

The Experience Data Model provides a structured and extensible representation of firsthand accounts of social interactions for **The Unwritten Rules**.

The model is designed to:

- Preserve contributors' original narratives without AI rewriting.
- Capture cultural, interpersonal, situational, verbal, and nonverbal context.
- Distinguish contributor observations, interpretations, and AI-generated inferences.
- Differentiate explicitly unknown information from missing information.
- Support new contextual dimensions without major schema changes.
- Establish boundaries between contributor data and AI-generated analysis.
- Provide validated structures for persistence, retrieval, and moderation.

Semantic similarity between experiences does not necessarily imply that they reflect the same underlying social expectation.

## 2. Experience

The `Experience` model represents a contributor's account of a social interaction.

### 2.1 Required Fields

| Field | Type | Description |
|---|---|---|
| `narrative` | `str` | Original contributor narrative |
| `country` | `str` | Country where the experience occurred |

Both fields must contain non-whitespace text.

The narrative is preserved exactly as submitted. Validation does not trim, paraphrase, or rewrite it.

### 2.2 Lifecycle Metadata

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | `UUID` | UUID4 | Unique experience identifier |
| `created_at` | `datetime` | Current UTC time | Creation timestamp |
| `updated_at` | `datetime` | Current UTC time | Initial last-updated timestamp |
| `moderation_status` | `ModerationStatus` | `pending` | Moderation state |

Supported moderation statuses:

- `pending`
- `approved`
- `rejected`

New experiences default to `pending`.

The schema defines moderation status but does not implement moderation workflows or public search restrictions.

The application or persistence layer will be responsible for updating `updated_at` when an experience changes.

### 2.3 Optional Collections

| Field | Type | Default | Description |
|---|---|---|---|
| `context` | `dict[str, ContextAttribute]` | Empty dictionary | Context indexed by dimension |
| `evidence` | `list[Evidence]` | Empty list | Contributor-supplied evidence |

Both collections use independent default factories.

## 3. ContextAttribute

A `ContextAttribute` represents one contextual dimension of an experience.

Examples of dimensions include:

- `setting`
- `cultural_background`
- `interpersonal_relationship`
- `situational_circumstances`
- `verbal_communication`
- `nonverbal_behaviour`
- `power_dynamics`
- `previous_interactions`
- `audience`
- `social_expectations`

These examples are illustrative, not exhaustive.

### 3.1 Fields

| Field | Type | Description |
|---|---|---|
| `status` | `ContextStatus` | Known or unknown |
| `value` | `str \| None` | Contextual information |
| `source` | `Literal["contributor"]` | Information origin |
| `evidence_ids` | `list[str]` | References to supporting evidence |

The default status is `known`.

The default source is `contributor`.

### 3.2 Known, Unknown, and Missing Information

**Known**

The contributor supplies a value.

Example:

- Dimension: `setting`
- Status: `known`
- Value: `Workplace meeting`

A known attribute requires a nonblank value.

**Unknown**

The contributor explicitly indicates that the value is unknown.

Example:

- Dimension: `colleague_intention`
- Status: `unknown`
- Value: `null`

An unknown attribute must not contain a value.

**Missing**

The contributor does not provide the contextual dimension.

Example:

- `previous_conflicts` is absent from the context dictionary.

Missing information must not be interpreted as irrelevant, false, or evidence that an event did not occur.

### 3.3 Extensibility

Contextual dimensions are represented as dictionary keys rather than fixed fields on the `Experience` model.

New dimensions can therefore be introduced without modifying the core experience schema.

Each dimension still follows the validated `ContextAttribute` structure.

This balances flexibility with consistency.

## 4. Evidence

The `Evidence` model represents contributor-supplied statements classified by their epistemic role.

### 4.1 Fields

| Field | Type | Description |
|---|---|---|
| `id` | `str \| None` | Optional evidence identifier |
| `type` | `EvidenceType` | Evidence classification |
| `content` | `str` | Contributor-supplied statement |

Evidence content must be nonblank.

### 4.2 Evidence Types

**Observation**

Something the contributor reports directly observing or experiencing.

Example:

"My colleague looked away without responding."

An observation is contributor-reported, not independently verified.

**Interpretation**

The contributor's understanding of what an interaction meant.

Example:

"I thought my colleague was upset with me."

An interpretation does not establish another participant's actual intentions.

**Unknown**

Information the contributor explicitly identifies as unknown.

Example:

"Why my colleague did not respond."

Unknown evidence records an information gap rather than an explanation.

### 4.3 Evidence References

Contextual attributes may reference evidence through `evidence_ids`.

The `Experience` model validates that:

- Provided evidence identifiers are unique within the experience.
- Contextual evidence references correspond to existing evidence identifiers.

Evidence identifiers are optional unless another attribute needs to reference them.

## 5. AI-Generated Inferences

AI-generated hypotheses are represented separately from contributor-supplied evidence.

This prevents AI-generated interpretations from being mistaken for firsthand accounts.

### 5.1 AIInference

| Field | Type | Description |
|---|---|---|
| `content` | `str` | AI-generated hypothesis |
| `model_name` | `str` | Model responsible for generation |
| `supporting_evidence_ids` | `list[str]` | Referenced contributor evidence |

Both `content` and `model_name` must be nonblank.

A numerical confidence score is not included because no calibrated uncertainty measure has been established.

### 5.2 ExperienceAnalysis

The `ExperienceAnalysis` model associates AI-generated analysis with an experience.

| Field | Type | Description |
|---|---|---|
| `experience_id` | `UUID` | Associated experience identifier |
| `inferences` | `list[AIInference]` | AI-generated hypotheses |

AI-generated analysis is stored separately from the original `Experience`.

This allows analyses to be regenerated or replaced without modifying the contributor's original account.

### 5.3 Provenance Boundaries

The system distinguishes:

1. Contributor observation
2. Contributor interpretation
3. AI-generated inference
4. Explicitly unknown information
5. Missing information

These categories must remain distinguishable throughout retrieval and RAG generation.

An AI hypothesis must not be presented as an established fact or attributed to the original contributor.

## 6. Representative Experience

Consider the following narrative:

> I greeted my colleague during a meeting, but she looked away without responding. I thought she was upset with me.

### 6.1 Experience Metadata

| Field | Example |
|---|---|
| `id` | Generated UUID |
| `country` | United Kingdom |
| `created_at` | Generated UTC timestamp |
| `updated_at` | Generated UTC timestamp |
| `moderation_status` | `pending` |

The original narrative is preserved.

### 6.2 Contextual Attributes

| Dimension | Status | Value |
|---|---|---|
| `setting` | known | Workplace meeting |
| `interpersonal_relationship` | known | Colleagues |
| `colleague_intention` | unknown | null |
| `previous_conflicts` | missing | Not provided |

The model does not infer that previous conflicts occurred or did not occur.

The colleague's intention remains unknown despite the contributor's interpretation.

### 6.3 Contributor Evidence

**Evidence e1**

- Type: `observation`
- Content: "My colleague looked away without responding."

**Evidence e2**

- Type: `interpretation`
- Content: "I thought she was upset with me."

These are different kinds of statements, even though they describe the same interaction.

### 6.4 AI-Generated Analysis

A separate `ExperienceAnalysis` references the experience's UUID.

Illustrative inference:

- Content: "The colleague may have been distracted."
- Model: `example-model`
- Supporting evidence IDs: `["e1"]`

This is a possible explanation, not a verified conclusion.

The AI-generated hypothesis does not modify the original narrative or replace the contributor's interpretation.

### 6.5 Interpretation Boundaries

The system can establish that:

- The contributor reported greeting a colleague.
- The contributor reported that the colleague looked away.
- The contributor interpreted the interaction as possible anger.
- The colleague's actual intention remains unknown.
- An AI model proposed distraction as an alternative hypothesis.

The system cannot establish that the colleague was angry, distracted, or deliberately dismissive without additional evidence.

## 7. Structured and Flexible Fields

The schema combines predefined structures with extensible contextual information.

### 7.1 Structured Fields

Structured fields have predefined types and validation rules.

Examples:

- Experience identifier
- Narrative
- Country
- Timestamps
- Moderation status
- Evidence classifications
- Context status
- Provenance fields
- Evidence references

### 7.2 Flexible Fields

Flexible fields accommodate differences between experiences.

Examples:

- Context dimension names
- Context descriptions
- Contributor observations
- Contributor interpretations
- Explicitly unknown details

This approach avoids imposing a rigid universal taxonomy while maintaining predictable data structures.

## 8. Validation Rules

The domain models enforce the following:

1. Narrative and country are required.
2. Required text cannot be empty or whitespace-only.
3. Original narrative text is preserved.
4. Unrecognised model fields are rejected.
5. Known contextual attributes require nonblank values.
6. Unknown contextual attributes must not contain values.
7. Context values cannot be whitespace-only.
8. Evidence content cannot be blank.
9. Evidence types must belong to the defined enumeration.
10. Provided evidence identifiers must be unique within an experience.
11. Context evidence references must point to existing evidence identifiers.
12. Moderation status must be a supported enumeration value.
13. Experience identifiers use UUIDs.
14. Default timestamps are timezone-aware and generated in UTC.
15. AI inference content and model name must be nonblank.
16. AI-generated analysis is represented separately from contributor data.

These rules are covered by automated pytest tests.

## 9. Architectural Decisions

The schema follows these decisions:

1. **Narrative preservation:** Contributor narratives are not automatically rewritten.
2. **Extensible context:** New contextual dimensions do not require changes to the Experience class.
3. **Epistemic distinctions:** Observations, interpretations, unknown information, and AI inferences remain distinguishable.
4. **Separation of AI analysis:** Generated hypotheses are not stored as contributor evidence.
5. **Evidence traceability:** Context attributes may reference supporting evidence.
6. **Missing information:** Absence is not assigned an assumed meaning.
7. **Domain validation:** Pydantic enforces structural and cross-field consistency.
8. **Separation of responsibilities:** Domain models do not implement persistence, retrieval, or generation.
9. **Moderation by default:** New experiences begin in the pending state.
10. **Avoidance of premature abstraction:** The design addresses current requirements without implementing unrelated infrastructure.

These decisions support maintainability, testability, and extensibility.

## 10. Known Limitations

### 10.1 Evidence Identifiers

Evidence identifiers are currently optional.

Identifier generation and persistence strategies will be revisited during database implementation.

### 10.2 Contributor-Reported Information

Observations and interpretations are contributor-supplied.

The schema does not independently verify their truth.

### 10.3 Context Vocabulary

Context dimensions do not yet use a controlled vocabulary.

Different contributors might use `relationship` and `interpersonal_relationship` for similar information.

Dataset preprocessing and retrieval design must account for this.

### 10.4 Mutable Collections

Cross-reference validation occurs when an Experience is validated.

Subsequent direct mutation of nested collections may bypass these checks.

Application services must revalidate modified experiences before persistence.

### 10.5 AI Inference References

AI inference evidence references are not currently cross-validated against the associated experience.

This will require application-level validation.

### 10.6 Timestamp Updates

The schema initialises `created_at` and `updated_at`.

Automatic updates to `updated_at` are not yet implemented.

### 10.7 Moderation Enforcement

The schema defines moderation states but does not enforce public search eligibility.

Future persistence and retrieval components must ensure that only approved experiences are publicly searchable.

### 10.8 Retrieval and Generation

The schema does not determine:

- Which contextual dimensions matter for a query.
- Whether two experiences express the same underlying social expectation.
- How observations and interpretations should be weighted.
- How context-aware reranking should work.
- Whether AI explanations are faithful to their sources.

These are responsibilities of later retrieval, evaluation, and RAG milestones.

## 11. Scope and Responsibility Boundaries

The Experience Data Model defines the structure and validity of experience-related information.

It does not implement:

- Experience submission endpoints
- Database persistence
- Moderation workflows
- Public search eligibility
- Dataset preprocessing
- Embedding generation
- Semantic retrieval
- Context-aware reranking
- RAG generation
- AI inference verification
- Frontend interfaces

These components will be implemented under their respective GitHub user stories.

The purpose of US-003 is to establish a validated, documented, and extensible data model that future components can build upon.
