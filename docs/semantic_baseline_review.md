# US-009 Review: Semantic Retrieval Baseline

## 1. Purpose

This document specifies the reproducibility controls, evaluation protocol, and architectural boundaries for the semantic-only retrieval baseline implemented in US-009.

The objective is to preserve a fixed reference system against which future context-aware retrieval approaches can be compared fairly.

This review does not implement context-aware ranking, guidance generation, or quantitative evaluation.

## 2. Baseline Definition

### Inputs

The semantic baseline accepts:

- A natural-language query.
- A collection of previously embedded experiences.
- An embedding model configuration.
- A retrieval configuration specifying top-K.

Candidate embeddings must have been generated using the configured embedding model.

### Embedding Model

| Parameter | Baseline configuration |
|---|---|
| Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Embedding dimensions | 384 |
| Batch size | 32 |
| Embedding adapter | `SentenceTransformerAdapter` |
| Query embedding | Same model as candidate embeddings |

The model revision and dependency versions must be recorded when producing a formal evaluation run.

### Ranking

The baseline uses cosine similarity.

For query embedding `q` and candidate embedding `e`:

\[
\operatorname{sim}(q,e)
=
\frac{q \cdot e}{\|q\|\|e\|}
\]

Candidates are sorted by descending similarity.

Equal similarity scores are resolved by ascending experience identifier.

### Outputs

Each retrieved result contains:

- `record_id`
- `similarity_score`
- `rank`

The number of returned results is at most K.

## 3. Baseline Isolation

The baseline ranking function uses:

1. Query embedding.
2. Candidate experience embeddings.
3. Candidate identifiers.
4. The requested top-K value.

It does not directly consume:

- Relevance judgments.
- Expectation labels.
- Context compatibility scores.
- Contextual reranking signals.
- M9 guidance-generation components.
- LLM-generated recommendations.

The retrieval text used to generate candidate embeddings may contain contextual descriptions produced during preprocessing.

Consequently, **semantic-only does not mean context-free**.

It means that contextual information is not separately interpreted, weighted, filtered, or reranked by the baseline retrieval algorithm.

This distinction must be preserved when reporting experimental results.

## 4. Evaluation Dataset

The current curated evaluation dataset contains:

| Component | Count |
|---|---:|
| Synthetic experiences | 16 |
| Evaluation queries | 12 |
| Query-experience relevance judgments | 192 |

The dataset includes cases designed to distinguish:

- Similar behaviour with different underlying expectations.
- Different behaviour involving similar expectations.
- Ambiguous situations.
- Context-dependent interpretations.

The evaluation labels must not influence embedding generation or retrieval ranking.

They are used only after retrieval to calculate evaluation metrics.

## 5. Evaluation Protocol

All compared retrieval systems must use the same:

- Candidate experience corpus.
- Evaluation query set.
- Relevance judgments.
- Top-K values.
- Relevance threshold.
- Metric definitions.

The baseline configuration and results must be preserved before introducing context-aware ranking.

### 5.1 Binary Relevance

Recall@K and MRR require a definition of relevant versus non-relevant experiences.

The evaluation must define a binary relevance threshold based on the dataset's existing relevance-label scale.

The threshold must be selected and documented before comparing retrieval approaches.

It must not be chosen retrospectively to favour a particular system.

Uncertain relevance judgments require an explicit treatment policy, applied consistently across systems.

### 5.2 Recall@K

Recall@K measures the fraction of relevant experiences retrieved among the first K results.

\[
\operatorname{Recall@K}(q)
=
\frac{
|\operatorname{Relevant}(q) \cap \operatorname{TopK}(q)|
}{
|\operatorname{Relevant}(q)|
}
\]

Macro-averaged Recall@K is calculated across evaluation queries.

Queries without any relevant experiences require a predefined handling policy.

### 5.3 Mean Reciprocal Rank (MRR)

Reciprocal Rank measures how early the first relevant experience appears.

\[
RR(q)=
\begin{cases}
1/r_q, & \text{if a relevant result is found}\\
0, & \text{otherwise}
\end{cases}
\]

where \(r_q\) is the rank of the first relevant result.

MRR is the mean reciprocal rank across evaluation queries.

The evaluation must specify whether MRR is computed over the full candidate ranking or truncated at K.

### 5.4 Additional Metrics

Potential supplementary metrics include:

- Precision@K
- nDCG@K
- Performance on hard-negative examples
- Performance by query type

These metrics belong to the evaluation implementation rather than the retrieval service.

## 6. Reproducibility Controls

A formal baseline evaluation must record:

| Control | Requirement |
|---|---|
| Source revision | Git commit hash |
| Embedding model | Exact model identifier |
| Model revision | Exact model revision or artifact hash where available |
| Model dimensions | 384 |
| Preprocessing | Code revision and retrieval-text construction |
| Candidate corpus | Dataset version or content hash |
| Evaluation queries | Dataset version or content hash |
| Relevance judgments | Dataset version or content hash |
| Ranking | Cosine similarity, descending |
| Tie-breaking | Ascending record ID |
| Top-K | Explicitly recorded values |
| Relevance threshold | Defined before comparison |
| Uncertain labels | Explicit, consistent treatment |
| Dependencies | Python and relevant package versions |
| Randomness | Record seeds where applicable |
| Outputs | Per-query rankings and aggregate metrics |

A successful smoke test is not a substitute for these controls.

## 7. Future Comparison Requirements

A future context-aware retriever may use additional information, including:

- Country and cultural context.
- Interpersonal relationships.
- Situational context.
- Verbal and nonverbal observations.
- Explicitly known or unknown contextual attributes.
- Candidate social expectations.

These signals must not be introduced into the baseline after its results have been established.

Future comparisons must distinguish between:

1. Improvements attributable to retrieval architecture.
2. Improvements attributable to additional input information.
3. Improvements attributable to different embedding models.
4. Improvements attributable to changes in the evaluation dataset.

Where possible, comparisons should vary one major experimental factor at a time.

## 8. Interface Compatibility

The current `SemanticRetriever` interface accepts a query embedding, candidate embeddings, and top-K.

This is sufficient for semantic-only retrieval.

A future context-aware retrieval approach may require additional query context, candidate metadata, or ranking configuration.

The existing interface should not be expanded prematurely.

Instead, future implementation work should determine whether a separate context-aware retrieval contract or a more general application-level search interface is appropriate.

Similarly, the current `RetrievalResult.similarity_score` represents cosine similarity.

A context-aware system may produce a score with a different interpretation.

Future comparisons should preserve ranked experience identifiers as a common evaluation output without assuming that scores from different ranking methods are directly comparable.

## 9. Baseline Limitations

The current baseline:

- Uses an in-memory linear scan.
- Requires precomputed candidate embeddings.
- Does not provide persistent vector storage.
- Does not perform context-aware reranking.
- Does not identify or resolve conflicting social expectations.
- Does not generate guidance.
- Does not independently enforce publication or moderation eligibility.