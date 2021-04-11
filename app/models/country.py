from app import db
from app.models import Base
from datetime import datetime
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from pandas import DataFrame

class Country(Base):
    __tablename__ = 'country'
    name = Column(String(80), nullable=False)
    statuses = relationship('CountryStatus')

    @staticmethod
    def all_countries_as_df():
        countries = Country.query.all()
        df = []
        for country in countries:
            for status in country.statuses:
                row = [[country.name] + status.all_status()]
                df += row
        
        return DataFrame(df, columns=["Name","Date","Total","Day","TotalDeaths","DailyDeaths","DailyCases","TotalPer100k","TotalDeathsPer100k","DailyDeathsPer100k","DailyCasesPer100k","DayNorm","GrowthRate","GrowthRateDeaths","DaysToDouble","DaysToDoubleDeaths","WeeklyGrowth","WeeklyGrowthDeaths"])

    @staticmethod
    def all_countries_names_as_df():
        countries = Country.query.all()
        df = []
        for country in countries:
            df += [country.name]

        return DataFrame(df, columns=["Name"])