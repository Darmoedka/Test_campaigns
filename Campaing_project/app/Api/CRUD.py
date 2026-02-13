from app.Schemas.Schemas_Campaigns import CampaignGET, CampaignScheduleGET, CampaignStatusEnum
from app.Rules import rule_management_disabled, rule_schedule_check, rule_low_stock, rule_budget_exceeded
from uuid import UUID
from typing import Callable

class RuleSet:
    which_rule: str
    def __init__(self, *rules) -> None:
        self.rules: list[Callable[[CampaignGET, list[CampaignScheduleGET]], CampaignStatusEnum | None]] = (
            list(rules)
        )

    def evaluate(self, parameters) -> str:
        k = 0
        for rule in self.rules:
            k = k + 1
            res = rule(parameters)
            if not res:
                match k:
                    case 1: self.which_rule = "management_disabled"
                    case 2: self.which_rule = "schedule"
                    case 3: self.which_rule = "low_stock"
                    case 4: self.which_rule = "budget_exceeded"
                      
                break
        if res == None:
            self.which_rule = None
        return res or CampaignStatusEnum.active
    

ruleset = RuleSet(rule_management_disabled, rule_schedule_check, rule_low_stock, rule_budget_exceeded)


