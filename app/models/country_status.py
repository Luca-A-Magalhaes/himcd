from app import db
from app.models import Base
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey
from math import nan
class CountryStatus(Base):
    __tablename__ = 'country_status'
    country_id = Column(Integer, ForeignKey('country.id'))
    date = Column(Date, nullable=False)
    total = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    total_deaths = Column(Integer, nullable=False)
    daily_deaths = Column(Integer, nullable=False)
    daily_cases = Column(Integer, nullable=False)
    total_per_100k = Column(Float(precision=17), nullable=True)
    total_deaths_per_100k = Column(Float(precision=17), nullable=True)
    daily_deaths_per_100k = Column(Integer, nullable=True)
    daily_cases_per_100k = Column(Integer, nullable=True)
    day_norm = Column(Integer, nullable=True)
    growth_rate = Column(Float(precision=15), nullable=True)
    growth_rate_deaths = Column(Float(precision=15), nullable=True)
    days_to_double = Column(Float(precision=16), nullable=True)
    days_to_double_death = Column(Float(precision=16), nullable=True)
    weekly_growth = Column(Float(precision=14), nullable=True)
    weekly_growth_deaths = Column(Float(precision=14), nullable=True)

    def all_status(self):
        return [self.date, 
                self.total or nan, 
                self.day or nan, 
                self.total_deaths or nan, 
                self.daily_deaths or nan, 
                self.daily_cases or nan, 
                self.total_per_100k or nan, 
                self.total_deaths_per_100k or nan, 
                self.daily_deaths_per_100k or nan, 
                self.daily_cases_per_100k or nan, 
                self.day_norm or nan,
                self.growth_rate or nan,
                self.growth_rate_deaths or nan,
                self.days_to_double or nan,
                self.days_to_double_death or nan,
                self.weekly_growth or nan,
                self.weekly_growth_deaths or nan]
    