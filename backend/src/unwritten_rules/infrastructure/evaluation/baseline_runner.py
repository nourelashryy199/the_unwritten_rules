import json
from pathlib import Path

from unwritten_rules.application.embeddings.models import (
    EmbeddedExperience,
    EmbeddingConfig,
)
from unwritten_rules.application.embeddings.service import EmbeddingService
from unwritten_rules.application.evaluation.evaluator import evaluate_query
from unwritten_rules.application.evaluation.metrics import mean_reciprocal_rank
from unwritten_rules.application.preprocessing.processor import ExperienceProcessor
from unwritten_rules.application.retrieval.models import RetrievalConfig
from unwritten_rules.application.retrieval.service import SemanticSearchService
from unwritten_rules.infrastructure.embeddings.sentence_transformer import (
    SentenceTransformerAdapter,
)
from unwritten_rules.infrastructure.retrieval.in_memory import (
    InMemoryCosineRetriever,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_baseline_evaluation(
    project_root: Path,
    output_path: Path,
) -> dict:
    """Run the semantic retrieval baseline against the labelled dataset."""

    experiences = load_json(
        project_root / "data/synthetic/experiences.json"
    )
    queries = load_json(
        project_root / "data/evaluation/queries.json"
    )
    label_data = load_json(
        project_root / "data/evaluation/relevance_labels.json"
    )

    synthetic_ids = [record["record_id"] for record in experiences]
    experience_payloads = [record["experience"] for record in experiences]

    processed = ExperienceProcessor().process(experience_payloads)

    if processed.invalid_records:
        raise ValueError("Evaluation corpus contains invalid experiences.")

    if len(processed.valid_records) != len(experiences):
        raise ValueError("Preprocessing changed the evaluation corpus size.")

    config = EmbeddingConfig()
    model = SentenceTransformerAdapter(config.model_name)

    embedding_service = EmbeddingService(model=model, config=config)
    embedded = embedding_service.generate(processed.valid_records)

    # Preserve stable synthetic IDs independently of generated UUIDs.
    candidates = [
        EmbeddedExperience(
            record_id=synthetic_id,
            embedding=item.embedding,
            model_name=item.model_name,
            dimensions=item.dimensions,
        )
        for synthetic_id, item in zip(synthetic_ids, embedded, strict=True)
    ]

    search_service = SemanticSearchService(
        embedding_model=model,
        retriever=InMemoryCosineRetriever(),
        embedding_config=config,
        retrieval_config=RetrievalConfig(top_k=len(candidates)),
    )

    judgments = {
        item["query_id"]: item["labels"]
        for item in label_data["judgments"]
    }

    k_values = (1, 3, 5, 10)
    per_query = []
    scored_results = []

    for query_record in queries:
        query_id = query_record["query_id"]

        retrieved = search_service.search(
            query=query_record["query"],
            candidates=candidates,
        )

        ranked_ids = [result.record_id for result in retrieved]

        evaluation = evaluate_query(
            ranked_ids=ranked_ids,
            labels=judgments[query_id],
            k_values=k_values,
        )

        query_result = {
            "query_id": query_id,
            "query_type": query_record["query_type"],
            "query": query_record["query"],
            "evaluation": evaluation,
            "retrieved": [
                result.model_dump(mode="json")
                for result in retrieved
            ],
        }

        per_query.append(query_result)

        if evaluation["status"] == "scored":
            scored_results.append(evaluation)

    if not scored_results:
        raise ValueError("No assessable queries were available.")

    aggregate = {
        f"mean_recall_at_{k}": sum(
            result["recall"][f"recall_at_{k}"]
            for result in scored_results
        ) / len(scored_results)
        for k in k_values
    }

    aggregate["mrr"] = mean_reciprocal_rank(
        [result["reciprocal_rank"] for result in scored_results]
    )

    report = {
        "evaluation_name": "semantic_retrieval_baseline",
        "settings": {
            "model_name": config.model_name,
            "embedding_dimensions": config.dimensions,
            "batch_size": config.batch_size,
            "similarity": "cosine",
            "candidate_count": len(candidates),
            "query_count": len(queries),
            "k_values": list(k_values),
            "relevant_label": 2,
            "partial_relevance_policy": "not counted as relevant",
            "uncertain_policy": "condensed ranking; excluded from scoring",
            "unscorable_query_policy": "excluded from aggregate metrics",
        },
        "aggregate": {
            **aggregate,
            "scored_queries": len(scored_results),
            "unscorable_queries": len(queries) - len(scored_results),
        },
        "per_query": per_query,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return report