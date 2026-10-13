
# Initial Synthetic Experience Dataset

## Purpose

The initial synthetic dataset supports the development and preliminary evaluation of context-aware retrieval for *The Unwritten Rules*.

It contains 16 fictional social experiences organised into 8 comparison pairs.

The dataset is intended to investigate whether retrieval systems can distinguish between surface-level behavioural similarity and similarity in underlying social expectations.

## Dataset Structure

Each synthetic record contains:

- A unique synthetic record identifier (`record_id`).
- An explicit synthetic label (`record_type`).
- A comparison pair identifier (`pair_id`).
- A comparison type (`comparison_type`).
- A curator-assigned expectation label (`expectation_label`).
- An experience containing a narrative, country, contextual attributes, and evidence.

The experience schema is validated using the existing Pydantic domain models.

Dataset location: `data/synthetic/experiences.json`

## Comparison Categories

### 1. Same Behaviour, Different Expectations

Four pairs describe similar observable behaviours associated with different candidate social expectations.

| Pair | Behaviour | Candidate Expectations |
|------|-----------|------------------------|
| PAIR-001 | Declining an invitation | Refusal requires explanation vs refusal needs no justification |
| PAIR-002 | Remaining silent during disagreement | Preserving harmony vs perceived disengagement |
| PAIR-003 | Offering to pay | Hospitality vs reciprocity |
| PAIR-004 | Avoiding sustained eye contact | Deference to seniority vs interpersonal discomfort |

### 2. Different Behaviours, Similar Expectations

Four pairs describe different observable behaviours associated with a shared candidate expectation.

| Pair | Behaviours | Shared Candidate Expectation |
|------|------------|-----------------------------|
| PAIR-005 | Declining food vs declining a gift | Refusing an offering may be interpreted as rejecting care |
| PAIR-006 | Replying late vs leaving a gathering early | Availability may be interpreted as relational commitment |
| PAIR-007 | Using formal titles vs standing when someone enters | Respect for hierarchy may be communicated through formal acknowledgment |
| PAIR-008 | Asking personal questions vs offering unsolicited advice | Personal involvement may be understood as an expression of care |

## Interpretation of Labels

Expectation labels are curator-generated hypotheses about the social expectations potentially illustrated by each synthetic narrative.

They are not:

- Verified psychological explanations.
- Objective statements about participants' intentions.
- Universal cultural rules.
- Claims about national populations.

Country is recorded as contextual information and must not be treated as a sufficient explanation for an individual's behaviour.

Multiple interpretations may be plausible for the same experience.

## Observations and Interpretations

Each experience distinguishes between two types of evidence:

**Observation:** A description of behaviour, speech, or events presented as directly witnessed by the narrator.

**Interpretation:** The narrator's explanation or understanding of what the observed behaviour might mean.

This distinction is important because an interpretation is not equivalent to an established fact about another person's intentions.

## Dataset Limitations

### 1. Synthetic Origin

All experiences are fictional.

They may not accurately represent the complexity, ambiguity, emotional nuance, or linguistic characteristics of authentic user submissions.

### 2. Small Sample Size

The dataset contains only 16 records.

This is sufficient for initial development and basic testing but insufficient for reliable statistical generalisation.

### 3. Curator Bias

Narratives, comparison pairs, and expectation labels were constructed by the dataset creator.

They may reflect assumptions about interpersonal behaviour and social expectations.

### 4. Constructed Relationships

The similarities and differences between paired experiences were deliberately designed.

Consequently, successful retrieval of these relationships does not necessarily demonstrate an ability to discover equivalent relationships in authentic data.

### 5. Cultural Representation

Although the dataset includes multiple countries, it is not culturally representative.

Country labels must not be interpreted as evidence that a behaviour or expectation is characteristic of an entire national population.

### 6. Interpretive Uncertainty

A single observable behaviour may have several plausible explanations.

For example, silence during disagreement could reflect discomfort, reflection, politeness, emotional regulation, or disengagement.

The assigned expectation labels should therefore be treated as hypotheses rather than ground truth.

### 7. Limited Linguistic Diversity

All narratives are written in English.

The dataset does not adequately represent multilingual communication, translation effects, dialects, or culturally specific expressions.

### 8. Evaluation Leakage

If the same examples are used to design, tune, and evaluate retrieval methods, evaluation results may be overly optimistic.

A separate labelled retrieval evaluation dataset should eventually be developed.

## Intended Use

The dataset may be used for:

- Testing data ingestion and schema validation.
- Developing semantic retrieval.
- Developing context-aware retrieval.
- Investigating retrieval failure cases.
- Comparing behaviour-level and expectation-level similarity.
- Constructing preliminary evaluation examples.

The dataset must not be used to make population-level cultural or psychological claims.

## Validation

Automated tests are located in:

`backend/tests/test_synthetic_dataset.py`

They verify:

- Minimum dataset size.
- Schema validity.
- Unique record identifiers.
- Multiple countries and social settings.
- Explicit synthetic labelling.
- Pair membership and comparison-type consistency.
- Expected label relationships within pairs.
- Distinguishable observations and interpretations.
- Presence of contextual information.

Run the tests from the repository root:

```bash
python -m pytest backend/tests/test_synthetic_dataset.py -v
```

Automated tests verify structural consistency. They do not independently establish the semantic validity of the assigned social expectations.

## Future Work

Subsequent development tasks will address:

1. Dataset validation and preprocessing.
2. A separate labelled retrieval evaluation dataset.
3. Semantic retrieval baselines.
4. Context-aware retrieval and reranking.
5. Retrieval evaluation using explicit relevance criteria.
6. Expansion with more diverse or authentic experiences, subject to appropriate privacy and moderation safeguards.
