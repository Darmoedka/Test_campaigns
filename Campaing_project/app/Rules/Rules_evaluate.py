from app.Schemas.Schemas_Campaigns import CampaignGET, CampaignScheduleGET, CampaignStatusEnum, RuleParameters
from datetime import datetime

def rule_management_disabled(campaign: RuleParameters):
    if not campaign.campaign.is_managed:
        return campaign.campaign.current_status
    return None

def rule_schedule_check(campaign: RuleParameters):
    if campaign.campaign.schedule_enabled:
        current_day_of_week = datetime.now().weekday()
        current_time = datetime.now().time()
        
        is_not_in_any_slot = all(not ((slot.start_time <= current_time < slot.end_time) and (current_day_of_week == slot.day_of_week)) for slot in campaign.campaign_Schedule)
        if not is_not_in_any_slot:
            return CampaignStatusEnum.paused
    return None

def rule_low_stock(campaign: RuleParameters):
    if campaign.campaign.stock_days_min is not None and campaign.campaign.stock_days_left is not None:
        if campaign.campaign.stock_days_left <campaign.campaign.stock_days_min:
            return CampaignStatusEnum.paused 
    return None

def rule_budget_exceeded(campaign: RuleParameters):
    if campaign.campaign.budget_limit is not None and campaign.campaign.spend_today >= campaign.campaign.budget_limit:
        return CampaignStatusEnum.paused
    return None
