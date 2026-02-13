from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.Schemas.Schemas_Campaigns import CampaignPOST, CampaignGET, CampaignScheduleGET, CampaignSchedulePOST, RuleEvaluationLogPOST, RuleParameters
from sqlalchemy.orm import Session
from app.Core.DB import SessionLocal
from sqlalchemy import select, delete
from app.Models.models import Campaign, CampaignSchedule, CampaignStatus
from .CRUD import ruleset
from typing import List
from datetime import datetime, time

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/campaigns")
def create_campaign(campaign: CampaignPOST, db: Session = Depends(get_db)):
    db.add(campaign)
    db.commit()
    Campaign.created_at = datetime.now()
    Campaign.updated_at = datetime.now()
    return campaign

@router.get("/campaigns")
def get_list_campaigns(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    campaing_query = select(Campaign).offset(offset).limit(limit)
    result_campaign = db.execute(campaing_query).scalars().unique().all()
    if result_campaign:
        campaign_schema = CampaignGET.model_validate(result_campaign, from_attributes=True)
        return campaign_schema
    return HTTPException(status_code=404, detail="Список кампаний отсутствует")

@router.get("/campaigns/{id}")
def get_campaign(id: UUID, db: Session = Depends(get_db)):
    campaing_query = select(Campaign).filter(Campaign.id == id)
    result_campaign = db.execute(campaing_query).scalar_one_or_none()
    if result_campaign:
        campaign_schema = CampaignGET.model_validate(result_campaign, from_attributes=True)
        return campaign_schema
    return HTTPException(status_code=404, detail="Кампания не найдена")



@router.patch("/campaigns/{id}")
def campaign_update(id: UUID, campaign_update: CampaignPOST, db: Session = Depends(get_db)):
    campaing_query = select(Campaign).filter(Campaign.id == id)
    result_campaign = db.execute(campaing_query).scalar_one_or_none()
    if result_campaign:
        campaign_schema = CampaignGET.model_validate(result_campaign, from_attributes=True)
        for key, value in campaign_update.items():
            setattr(campaign_schema, key, value)
        Campaign.updated_at = datetime.now()
        db.commit()
        db.refresh(campaign_update)
        return campaign_schema
    return HTTPException(status_code=404, detail="Кампания для обновления не найдена")

@router.put("/campaigns/{id}/schedule")
def set_schedule(id: UUID, campaign_schedule_update: List[CampaignSchedulePOST], db: Session = Depends(get_db)):
    campaing_schedule_query = select(CampaignSchedule).filter(CampaignSchedule.id == id)
    result_campaing_schedule = db.execute(campaing_schedule_query).scalars().unique().all()
    if result_campaing_schedule:
        delete_query_campaign_schedule = delete(CampaignSchedule).where(CampaignSchedule.campaign_id == id)
        db.execute(delete_query_campaign_schedule)
        new_campaing_schedule = [CampaignSchedule(**slot.model_validate(), campaign_id=id) for slot in campaign_schedule_update]
        db.add_all(new_campaing_schedule)
        db.commit()
        return new_campaing_schedule
    return HTTPException(status_code=404, detail="Активные слоты для установления не найдены")

@router.get("/campaigns/{id}/schedule")
def get_schedule(id: UUID, db: Session = Depends(get_db)):
    campaing_schedule_query = select(CampaignSchedule).filter(CampaignSchedule.id == id)
    result_campaing_schedule = db.execute(campaing_schedule_query).scalars().unique().all()
    if result_campaing_schedule:
        campaign_schedule_schema = CampaignScheduleGET.model_validate(result_campaing_schedule, from_attributes=True)
        return campaign_schedule_schema
    return HTTPException(status_code=404, detail="Активные слоты кампании не найдены")

@router.delete("/campaigns/{id}/schedule")
def delete_schedule(id: UUID, db: Session = Depends(get_db)):
    campaing_schedule_query = delete(CampaignSchedule).where(CampaignSchedule.campaign_id == id)
    db.execute(campaing_schedule_query)
    db.commit()
    return

@router.post("/campaigns/{id}/evaluate")
def evaluate(id: UUID, db: Session = Depends(get_db)):
    campaing_query = select(Campaign).filter(Campaign.id == id)
    result_campaign = db.execute(campaing_query).scalar_one_or_none()
    if result_campaign:
        campaing_schedule_query = select(CampaignSchedule).filter(CampaignSchedule.campaign_id == result_campaign.id)
        result_campaign_schedule = db.execute(campaing_schedule_query).scalars().unique().all()
        if result_campaign_schedule:
            campaign_schema = CampaignGET.model_validate(result_campaign, from_attributes=True)
            campaign_schedule_schema = CampaignScheduleGET.model_validate(result_campaign_schedule, from_attributes=True)
            result_status = ruleset.evaluate(RuleParameters(campaign=campaign_schema, campaign_Schedule=campaign_schedule_schema))
            evaluation_context = {
                "campaign": CampaignGET.model_validate(result_campaign).model_dump(mode='json'),
                "schedule": [CampaignScheduleGET.model_validate(s).model_dump(mode='json') for s in campaing_schedule_query],
                "server_time": datetime.now().isoformat()
                }
            rule_log = RuleEvaluationLogPOST(campaign_id=result_campaign.id, triggered_rule=ruleset.which_rule, 
                                                 previous_target=Campaign.target_status, 
                                             new_target=result_status, context=evaluation_context , created_at=datetime.now())
           
            result_campaign.target_status = result_status
            db.add(rule_log)
            db.add(result_campaign)
            db.commit()
            
    return HTTPException(status_code=404, detail="Активные слоты кампании не найдены")


@router.post("/campaigns/evaluate-all")
def evaluate(db: Session = Depends(get_db)):
    campaing_query = select(Campaign)
    result_campaign = db.execute(campaing_query).scalars().unique().all()
    if result_campaign:
        for campaign in result_campaign:
            campaing_schedule_query = select(CampaignSchedule).filter(CampaignSchedule.campaign_id == campaign.id)
            result_campaign_schedule = db.execute(campaing_schedule_query).scalars().unique().all()
            if result_campaign_schedule:
                campaign_schema = CampaignGET.model_validate(campaign, from_attributes=True)
                campaign_schedule_schema = CampaignScheduleGET.model_validate(result_campaign_schedule, from_attributes=True)
                result_status = ruleset.evaluate(RuleParameters(campaign=campaign_schema, campaign_Schedule=campaign_schedule_schema))
                evaluation_context = {
                "campaign": CampaignGET.model_validate(result_campaign).model_dump(mode='json'),
                "schedule": [CampaignScheduleGET.model_validate(s).model_dump(mode='json') for s in campaing_schedule_query],
                "server_time": datetime.now().isoformat()
                }
                rule_log = RuleEvaluationLogPOST(campaign_id=campaign.id, triggered_rule=ruleset.which_rule, 
                                                 previous_target=Campaign.target_status, 
                                             new_target=result_status, context=evaluation_context , created_at=datetime.now())
                result_campaign.target_status = result_status
                db.add(rule_log)
                db.add(result_campaign)
                db.commit()
                
    return HTTPException(status_code=404, detail="Список кампаний пуст")
    

@router.get("/campaigns/{id}/evaluation-history")
def get_evaluation_history(id: UUID, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    campaing_query = select(Campaign).filter(Campaign.id == id)
    result_campaign = db.execute(campaing_query).scalar_one_or_none()
    if result_campaign:
        history_query = (select(RuleEvaluationLogPOST).filter(RuleEvaluationLogPOST.campaign_id == id).order_by(RuleEvaluationLogPOST.created_at.desc()).offset(offset).limit(limit))
        result_history = db.execute(history_query).scalars().unique().all()
        return result_history
    return HTTPException(status_code=404, detail="Кампания не найдена")