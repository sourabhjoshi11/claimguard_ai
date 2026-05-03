from state import ClaimState


def valuation_node(state: ClaimState):
    print("CALCULATING COSTS ")

    price_map = {"Low": 100.0, "Medium": 350.0, "High": 900.0}
    total = 0.0
    updated_items = []
    for issue in state["anamolies"]:
        severity = issue.get("severity", "").strip().title()
        cost = price_map.get(severity, 50.0)
        issue['estimated_cost'] = cost
        total += cost
        updated_items.append(issue)
    return {
        "anamolies": updated_items,
        "total_claim_value": total,
        "status": "Estimate Complete",
    }
