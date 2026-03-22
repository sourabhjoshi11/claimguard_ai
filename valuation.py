
from state import  ClaimState
def valuation_node(state: ClaimState):
    print("CALCULATING COSTS ")
    
    price_map = {"Low": 100.0, "Medium": 350.0, "High": 900.0}
    total = 0.0
    updated_items=[]
    for issue in state['anamolies']:
        cost = price_map.get(issue.get('severity'), 50.0)
        issue['estimated_cost'] = cost
        total += cost
        updated_items.append(issue)
    return {"total_claim_value": total, "status": "Finished"}