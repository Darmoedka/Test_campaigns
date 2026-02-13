from pydantic import BaseModel, Json
from typing import Optional, List
from enum import Enum
from datetime import datetime, time
from uuid import UUID, uuid4

class CampaignStatusEnum(str, Enum):
    active = "active"
    paused = "paused"

class CampaignPOST(BaseModel):
    name: str
    current_status: CampaignStatusEnum
    target_status: CampaignStatusEnum
    is_managed: bool
    budget_limit: Optional[float] = None
    spend_today: float 
    stock_days_left: Optional[int] = None
    stock_days_min: Optional[int] = None
    schedule_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 


class CampaignGET(CampaignPOST):
    id: UUID  

class CampaignSchedulePOST(BaseModel):
    campaign_id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    
    class Config:
        orm_mode = True

class CampaignScheduleGET(CampaignSchedulePOST):
    id: UUID  

class RuleEvaluationLogPOST(BaseModel):
    campaign_id: UUID
    triggered_rule: Optional[str] = None
    previous_target: CampaignStatusEnum
    new_target: CampaignStatusEnum
    context: Json
    created_at: datetime

class RuleEvaluationLogGET(RuleEvaluationLogPOST):
    id: UUID


class RuleParameters():
    campaign: CampaignGET
    campaign_Schedule: List[CampaignScheduleGET]