"""Descriptive manuscript statistics; no fitting, tuning, or data modification.

When copied into repo/scripts, run: python scripts/paper_statistics.py
From elsewhere, pass --repo PATH. Output goes to stdout unless --output is given.
"""
import argparse
import collections
import importlib.util
import json
import re
import statistics
import sys
from pathlib import Path


def quantile(values, proportion):
    values = sorted(values)
    position = (len(values) - 1) * proportion
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def summarize(values):
    return {"minimum": min(values), "q25": quantile(values, .25),
            "median": statistics.median(values), "q75": quantile(values, .75),
            "maximum": max(values), "mean": statistics.mean(values)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo.resolve()
    sys.path.insert(0, str(root))
    from contractchecker.rules import TASKS, features, boundary
    from contractchecker.model import tokens

    spec = importlib.util.spec_from_file_location("archived_rules", root / "research/initial_rules.py")
    initial_rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(initial_rules)
    records = [json.loads(line) for line in (root / "data/maud_mae.jsonl").read_text(encoding="utf-8").splitlines()]
    predictions = [json.loads(line) for line in (root / "results/predictions.jsonl").read_text(encoding="utf-8").splitlines()]
    test = [record for record in records if record["split"] == "test"]
    train = [record for record in records if record["split"] == "train"]
    result = {"length_unit": "ASCII alphabetic unigram tokens from re.findall('[a-z]+', text.lower()); no stopword removal",
              "quartiles": "linear interpolation at (n-1)*p", "sample": {}}
    for partition in ("all", "train", "dev", "test"):
        group = records if partition == "all" else [r for r in records if r["split"] == partition]
        result["sample"][partition] = {
            "agreements": len(group),
            "characters": summarize([len(r["text"]) for r in group]),
            "alphabetic_tokens": summarize([len(re.findall(r"[a-z]+", r["text"].lower())) for r in group]),
            "positive_labels": {task: sum(r["labels"][task] for r in group) for task in TASKS},
            "omission_ids": [r["contract_id"] for r in group if r["contains_source_omission"]]}

    result["v1_to_v11_test_transitions"] = {}
    for task in TASKS:
        changes = collections.Counter()
        ids = collections.defaultdict(list)
        for record in test:
            gold = record["labels"][task]
            before = int(initial_rules.features(record["text"])[task]["value"])
            after = int(features(record["text"])[task]["value"])
            transition = ("correct" if before == gold else "error") + "_to_" + ("correct" if after == gold else "error")
            changes[transition] += 1
            ids[transition].append(record["contract_id"])
        result["v1_to_v11_test_transitions"][task] = {"counts": dict(changes), "ids": dict(ids)}

    result["test_agreement_correct_task_distribution"] = {}
    for method in ("majority", "rules", "naive_bayes"):
        distribution = collections.Counter()
        for record in test:
            selected = [p for p in predictions if p["contract_id"] == record["contract_id"]]
            assert len(selected) == 4
            distribution[sum(p[method] == p["gold"] for p in selected)] += 1
        result["test_agreement_correct_task_distribution"][method] = dict(distribution)

    vocabulary = set().union(*(tokens(record["text"]) for record in train))
    result["training_vocabulary"] = {"total": len(vocabulary),
        "unigrams": sum("_" not in token for token in vocabulary),
        "bigrams": sum("_" in token for token in vocabulary)}

    # Exact source slices for manuscript examples. The strings are deliberately
    # short; the supplied source text and full context remain in maud_mae.jsonl.
    requests = [
        ("contract_8", "consummation", "the ability of such Person and its Subsidiaries to consummate the Transactions before the End Date"),
        ("contract_14", "consummation", "or (ii) the ability of such party to timely consummate the transactions contemplated hereby"),
        ("contract_18", "consummation", "or (ii) the ability of such party to timely consummate the transactions contemplated hereby"),
        ("contract_29", "buyer_actions", "any action taken or omitted to be taken by the Company or any of its Subsidiaries at the written request of Parent"),
        ("contract_32", "buyer_actions", "any action expressly required or permitted to be taken by Parent, Purchaser or the Company"),
        ("contract_32", "buyer_actions", "any breach by Parent or Purchaser of this Agreement"),
        ("contract_43", "buyer_actions", "the identity of, or any facts or circumstances relating to, Parent, Purchaser or any of their respective Affiliates"),
        ("contract_146", "buyer_actions", "any action taken by Parent or any Affiliate thereof"),
        ("contract_146", "shareholder_litigation", "any stockholder litigation related to this Agreement or the transactions contemplated by this Agreement"),
        ("contract_96", "shareholder_litigation", "any Action initiated or threatened on or after the date hereof by any stockholders of the Company"),
        ("contract_72", "shareholder_litigation", "the initiation of litigation by any Person with respect to this Agreement or the Transactions"),
        ("contract_30", "forward_looking", "would materially impair the ability of either United or CBTC to perform its respective obligations under this Agreement"),
        ("contract_141", "forward_looking", "has occurred or would reasonably be expected to occur"),
    ]
    by_id = {r["contract_id"]: r for r in records}
    result["source_examples"] = []
    for contract_id, task, quote in requests:
        record = by_id[contract_id]
        start = record["text"].find(quote)
        assert start >= 0, (contract_id, quote)
        end = start + len(quote)
        assert record["text"][start:end] == quote
        result["source_examples"].append({"contract_id": contract_id, "task": task,
            "gold": record["labels"][task],
            "source_row": record["source_rows"][task],
            "source_excerpt_sha256": record["text_sha256"],
            "initial_prediction": int(initial_rules.features(record["text"])[task]["value"]),
            "revised_prediction": int(features(record["text"])[task]["value"]),
            "first_exclusion_cutoff": boundary(record["text"]),
            "start": start, "end": end, "quote": quote})
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
