from langgraph.graph import StateGraph,END
from typing import Annotated ,List,TypedDict
import operator
from validate import input_validation_node
from valuation import valuation_node
import json
from comparision import comparison_node


class DamageReport(TypedDict):
    item:str
    issue:str
    severity:str
    estimated_cost:float

class ClaimState(TypedDict):
    property_id:str
    user_id:str
    check_in_url:str
    check_out_url:str
    is_image_clear:bool
    anamolies:Annotated[List[DamageReport],operator.add]
    total_claim_value:float
    status:str



workflow=StateGraph(ClaimState)

workflow.add_node("validate_image",input_validation_node)
workflow.add_node("compare_asset",comparison_node)
workflow.add_node("estimate_cost",valuation_node)


workflow.set_entry_point("validate_image")

workflow.add_conditional_edges("validate_image",lambda state :"continue" if state["is_image_clear"] else "stop",{
    "continue":"compare_asset",
    "stop":END
})

workflow.add_edge("compare_asset","estimate_cost")

workflow.add_edge("estimate_cost",END)



app=workflow.compile()





