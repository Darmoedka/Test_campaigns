import pytest
from datetime import datetime, time
from app.Api.CRUD import ruleset
from app.Schemas.Schemas_Campaigns import CampaignStatusEnum, CampaignPOST, CampaignGET, CampaignScheduleGET, CampaignSchedulePOST, RuleEvaluationLogPOST, RuleParameters
from uuid import UUID, uuid4



def create_test_campaign(**kwargs):
    defaults = {
        "id": uuid4(),
        "name": "Тестовая компания",
        "is_managed": False,
        "stock_days_min": 0,
        "stock_days_left": 100,
        "budget_limit": 10000.0,
        "spend_today": 0.0,
        "current_status": CampaignStatusEnum.active,      # или другое дефолтное значение из CampaignStatusEnum
        "target_status": CampaignStatusEnum.active,
        "schedule_enabled": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    defaults.update(kwargs)
    return CampaignGET(**defaults)

def make_slot(id: UUID, day: int, start: str, end: str):
    return CampaignScheduleGET(id=uuid4(), campaign_id=id, day_of_week=day, start_time=time.fromisoformat(start), end_time=time.fromisoformat(end))

def test_example_1_schedule_outside_hours():
    #Вне расписания (Среда, 22:30)
    campaign = create_test_campaign()

    schedule = [make_slot(campaign.id, d, "09:00", "21:00") for d in range(1, 6)] 
    rule_parameters = RuleParameters(campaign, schedule)
    result = ruleset.evaluate(rule_parameters)
    
    assert result
    assert ruleset.which_rule

def test_example_2_low_stock():
    #Низкий остаток
    campaign = create_test_campaign(stock_days_min=5, stock_days_left=3)
    schedule = [make_slot(None, d, None, None) for d in range(1, 6)]
    rule_parameters = RuleParameters(campaign, schedule)
    result = ruleset.evaluate(rule_parameters)
    
    assert result
    assert ruleset.which_rule

def test_example_3_budget_exceeded():
    #Превышение бюджета
    campaign = create_test_campaign(budget_limit=1000, spend_today=1000)
    schedule = [make_slot(None, d, None, None) for d in range(1, 6)]
    rule_parameters = RuleParameters(campaign, schedule)
    result = ruleset.evaluate(rule_parameters)
    assert result
    assert ruleset.which_rule

def test_example_4_priority_schedule_vs_budget():
    #Превышен бюджет (1500 > 1000), но время вне расписания
    campaign = create_test_campaign(budget_limit=1000, spend_today=1500)
    schedule = [make_slot(campaign.id, 1, "09:00", "18:00")]
    rule_parameters = RuleParameters(campaign, schedule)
    ruleset.evaluate(rule_parameters)
    assert ruleset.which_rule

def test_example_5_all_ok():
    """Пример 5: Все условия в норме"""
    campaign = create_test_campaign(
        stock_days_min=5, stock_days_left=10, 
        budget_limit=1000, spend_today=500
    )
    # Понедельник, 12:00 (в расписании)
    schedule = [make_slot(campaign.id,1, "09:00", "18:00")]
    rule_parameters = RuleParameters(campaign=campaign, campaing_Schedule = schedule)
    result = ruleset.evaluate(rule_parameters)
    
    assert result
    assert ruleset.which_rule

# --- ТЕСТЫ НА ГРАНИЧНЫЕ СЛУЧАИ ---

@pytest.mark.parametrize("current_time_str, expected_status", [
    ("09:00:00", CampaignStatusEnum.active),  # Точно в момент начала
    ("21:00:00", CampaignStatusEnum.active),  # Точно в момент окончания
    ("08:59:59", CampaignStatusEnum.paused),  # За секунду до начала
    ("21:00:01", CampaignStatusEnum.paused),  # Через секунду после окончания
])
def test_time_boundary_cases(current_time_str, expected_status):
    """Граничные случаи времени на границе слота"""
    campaign = create_test_campaign()
    schedule = [make_slot(campaign.id,1, "09:00", "21:00")]
    current_time = datetime.combine(
        datetime(2026, 2, 9), # Понедельник
        time.fromisoformat(current_time_str)
    )
    rule_parameters = RuleParameters(campaign, schedule)
    ruleset.evaluate(rule_parameters)
    assert ruleset.which_rule

