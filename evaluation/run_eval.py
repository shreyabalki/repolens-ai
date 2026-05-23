import argparse
import json
import statistics
import time
import urllib.request


def post_json(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def recall_at_k(predicted, expected):
    expected_set = set(expected)
    if not expected_set:
        return 0.0
    hits = len(expected_set.intersection(predicted))
    return hits / len(expected_set)


def precision_at_k(predicted, expected):
    if not predicted:
        return 0.0
    expected_set = set(expected)
    hits = len(expected_set.intersection(predicted))
    return hits / len(predicted)


def mrr(predicted, expected):
    expected_set = set(expected)
    for idx, item in enumerate(predicted, start=1):
        if item in expected_set:
            return 1.0 / idx
    return 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--repository-id", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--queries-file", default="evaluation/golden_queries.json")
    args = parser.parse_args()

    with open(args.queries_file, "r", encoding="utf-8") as f:
        queries = json.load(f)

    recalls, precisions, mrrs, latencies = [], [], [], []

    for item in queries:
        start = time.perf_counter()
        response = post_json(
            f"{args.base_url}/ask",
            {"repository_id": args.repository_id, "question": item["question"]},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        latencies.append(elapsed_ms)

        sources = response.get("sources", [])[: args.top_k]
        predicted = [s.get("file_path") for s in sources if s.get("file_path")]
        expected = item.get("expected_files", [])

        recalls.append(recall_at_k(predicted, expected))
        precisions.append(precision_at_k(predicted, expected))
        mrrs.append(mrr(predicted, expected))

        print(f"[{item['id']}] recall={recalls[-1]:.3f} precision={precisions[-1]:.3f} mrr={mrrs[-1]:.3f} latency_ms={elapsed_ms:.1f}")

    print("\n=== Aggregate ===")
    print(f"Recall@{args.top_k}: {statistics.mean(recalls):.3f}")
    print(f"Precision@{args.top_k}: {statistics.mean(precisions):.3f}")
    print(f"MRR: {statistics.mean(mrrs):.3f}")
    print(f"Avg latency (ms): {statistics.mean(latencies):.1f}")


if __name__ == "__main__":
    main()
