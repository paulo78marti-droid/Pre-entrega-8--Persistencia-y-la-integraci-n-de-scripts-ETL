"""
Modelos de Base de Datos con SQLAlchemy 2.0
Módulo 9: Automatización y Patrones de Datos (Coderhouse)
"""
from datetime import datetime, date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date


# Clase base para definir tablas con el ORM de SQLAlchemy 2.0
class Base(DeclarativeBase):
    pass


# 1. Tabla de mediciones horarias
class WeatherHourly(Base):
    __tablename__ = "weather_hourly"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[float] = mapped_column(Float, default=0.0)
    wind_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    wind_category: Mapped[str] = mapped_column(String(30), nullable=False)
    is_rainy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<WeatherHourly(city='{self.city}', fecha='{self.timestamp}', temp={self.temperature_c}°C)>"


# 2. Tabla de resumen diario (KPIs acumulados)
class WeatherDailySummary(Base):
    __tablename__ = "weather_daily_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    temp_min_c: Mapped[float] = mapped_column(Float, nullable=False)
    temp_max_c: Mapped[float] = mapped_column(Float, nullable=False)
    temp_avg_c: Mapped[float] = mapped_column(Float, nullable=False)
    total_precipitation_mm: Mapped[float] = mapped_column(Float, default=0.0)
    avg_wind_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    rainy_hours_count: Mapped[int] = mapped_column(Integer, default=0)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<WeatherDailySummary(city='{self.city}', fecha='{self.date}', temp_media={self.temp_avg_c}°C)>"
