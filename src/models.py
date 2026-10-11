from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Clase base declarativa unificada para SQLAlchemy 2.0."""
    pass


class WeatherHourly(Base):
    """Entidad ORM que mapea la tabla analítica 'weather_hourly'."""
    __tablename__ = "weather_hourly"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    wind_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    wind_category: Mapped[str] = mapped_column(String(30), nullable=False)
    is_rainy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("city", "timestamp", name="uq_city_timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"WeatherHourly(city={self.city!r}, timestamp={self.timestamp.isoformat()!r}, "
            f"temp={self.temperature_c}°C, rain={self.is_rainy})"
        )


class WeatherDailySummary(Base):
    """Entidad ORM que mapea la tabla de agregación diaria 'weather_daily_summary'."""
    __tablename__ = "weather_daily_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    temp_min_c: Mapped[float] = mapped_column(Float, nullable=False)
    temp_max_c: Mapped[float] = mapped_column(Float, nullable=False)
    temp_avg_c: Mapped[float] = mapped_column(Float, nullable=False)
    total_precipitation_mm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_wind_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    rainy_hours_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("city", "date", name="uq_city_date"),
    )

    def __repr__(self) -> str:
        return (
            f"WeatherDailySummary(city={self.city!r}, date={self.date.isoformat()!r}, "
            f"min={self.temp_min_c}°C, max={self.temp_max_c}°C, avg={self.temp_avg_c}°C)"
        )
