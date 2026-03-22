
from typing import Annotated ,List,TypedDict
import operator

class DamageReport(TypedDict):
    item:str
    issue:str
    severity:str
    estimated_cost:int


class ClaimState(TypedDict):
    property_id:str
    user_id:str

    check_in_url:str
    check_out_url:str

    is_image_clear:bool
    anamolies:Annotated[List[DamageReport],operator.add]

    totoal_claim_value:int
    pdf_report_s3_key:str
    status:str