def detect_milestone(features: dict) -> dict:

    # Most advanced milestone first

    if (
        features["has_complement"]
        and features["has_membership_check"]
        and features["has_dictionary"]
        and features["has_return"]
    ):
        return {
            "milestone": "apply_hash_map_correctly",
            "confidence": 0.95,
        }

    if (
        features["has_dictionary"]
        or features["has_seen_variable"]
    ):
        return {
            "milestone": "introduce_hash_map",
            "confidence": 0.85,
        }

    if features["has_complement"]:
        return {
            "milestone": "discover_complement",
            "confidence": 0.85,
        }

    if (
        features["has_nested_loop"]
        and features["has_pair_sum"]
    ):
        return {
            "milestone": "recognize_inefficiency",
            "confidence": 0.85,
        }

    if (
        features["has_loop"]
        or features["has_function"]
    ):
        return {
            "milestone": "brute_force",
            "confidence": 0.75,
        }

    return {
        "milestone": "brute_force",
        "confidence": 0.30,
    }