from sqlalchemy import create_engine, Column, String, Enum, Boolean, Integer, DateTime, ForeignKey, DECIMAL, JSON, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
import enum

Base = declarative_base()

class CampaignStatus(str, enum.Enum):
    active = "active"
    paused = "paused"

class Campaign(Base):
    __tablename__ = "Campaign"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)
    current_status = Column(Enum(CampaignStatus), default=CampaignStatus.active)
    target_status = Column(Enum(CampaignStatus))
    is_managed = Column(Boolean, default=True)
    budget_limit = Column(DECIMAL, nullable=True)
    spend_today = Column(DECIMAL, default=0)
    stock_days_left = Column(Integer, nullable=True)
    stock_days_min = Column(Integer, nullable=True)
    schedule_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class CampaignSchedule(Base):
    __tablename__ = 'Campaign_schedule'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey('campaigns.id'))
    day_of_week = Column(Integer)
    start_time = Column(Time)
    end_time = Column(Time)
    campaign = relationship("Campaign", back_populates="schedules")

Campaign.schedules = relationship("CampaignSchedule", back_populates="campaign")

class RuleEvaluationLog(Base):
    __tablename__ = 'rule_evaluation_log'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey('campaigns.id'))
    triggered_rule = Column(String, unique=True, nullable=True)
    previous_target = Column(Enum(CampaignStatus))
    new_target = Column(Enum(CampaignStatus))
    context = Column(JSON)
    created_at = Column(DateTime)
    campaign = relationship("Campaign", back_populates="schedules")

Campaign.schedules = relationship("CampaignSchedule", back_populates="campaign")
    