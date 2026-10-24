"""
Modelos de Base de Datos con SQLAlchemy 2.0
Curso: Data Science II - Coderhouse

Define las tablas para almacenar las mediciones de calidad del aire y el resumen analitico.
"""
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Boolean, DateTime


# Clase Base para los modelos declarativos de SQLAlchemy 2.0
class Base(DeclarativeBase):
    pass


class AirQualityMeasurement(Base):
    """
    Tabla de mediciones individuales de calidad del aire.
    Almacena los registros limpios y normalizados.
    """
    __tablename__ = "air_quality_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    pm25: Mapped[float] = mapped_column(Float, nullable=False)
    pm10: Mapped[float] = mapped_column(Float, nullable=False)
    nox: Mapped[float] = mapped_column(Float, nullable=False)
    no2: Mapped[float] = mapped_column(Float, nullable=False)
    so2: Mapped[float] = mapped_column(Float, nullable=False)
    vocs: Mapped[float] = mapped_column(Float, nullable=False)
    co: Mapped[float] = mapped_column(Float, nullable=False)
    co2: Mapped[float] = mapped_column(Float, nullable=False)
    ch4: Mapped[float] = mapped_column(Float, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    quality_level: Mapped[str] = mapped_column(String(30), nullable=False)
    is_high_pollution: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AirQualityMeasurement(id={self.measurement_id}, PM2.5={self.pm25}, Nivel='{self.quality_level}')>"


class AirQualitySummary(Base):
    """
    Tabla de resumen analitico (Data Mart) agrupado por categoria de calidad del aire.
    """
    __tablename__ = "air_quality_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quality_level: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_pm25: Mapped[float] = mapped_column(Float, nullable=False)
    avg_pm10: Mapped[float] = mapped_column(Float, nullable=False)
    avg_co2: Mapped[float] = mapped_column(Float, nullable=False)
    avg_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    max_pm25: Mapped[float] = mapped_column(Float, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AirQualitySummary(Nivel='{self.quality_level}', Registros={self.record_count}, PM2.5_Prom={self.avg_pm25})>"
