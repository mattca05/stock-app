from sqlalchemy import String, Float, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
from datetime import date


class Base(DeclarativeBase):
    pass


class Country(Base):
    __tablename__ = "countries"
    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    exchanges: Mapped[list["Exchange"]] = relationship(back_populates="country")


class Exchange(Base):
    __tablename__ = "exchanges"
    id:         Mapped[int] = mapped_column(primary_key=True)
    name:       Mapped[str] = mapped_column(String, unique=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))

    country: Mapped["Country"]       = relationship(back_populates="exchanges")
    tickers: Mapped[list["Ticker"]]  = relationship(back_populates="exchange")


class Sector(Base):
    __tablename__ = "sectors"
    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    industries: Mapped[list["Industry"]] = relationship(back_populates="sector")


class Industry(Base):
    __tablename__ = "industries"
    id:        Mapped[int] = mapped_column(primary_key=True)
    name:      Mapped[str] = mapped_column(String)
    sector_id: Mapped[int] = mapped_column(ForeignKey("sectors.id"))

    sector:  Mapped["Sector"]         = relationship(back_populates="industries")
    tickers: Mapped[list["Ticker"]]   = relationship(back_populates="industry")


class Ticker(Base):
    __tablename__ = "tickers"
    id:          Mapped[int]           = mapped_column(primary_key=True)
    symbol:      Mapped[str]           = mapped_column(String, unique=True)
    name:        Mapped[Optional[str]] = mapped_column(String, nullable=True)
    exchange_id: Mapped[int]           = mapped_column(ForeignKey("exchanges.id"))
    industry_id: Mapped[int]           = mapped_column(ForeignKey("industries.id"))
    country_id:  Mapped[Optional[int]] = mapped_column(ForeignKey("countries.id"), nullable=True)  # ← add this
    fetched_at:  Mapped[Optional[str]] = mapped_column(String, nullable=True)

    exchange:     Mapped["Exchange"]          = relationship(back_populates="tickers")
    industry:     Mapped["Industry"]          = relationship(back_populates="tickers")
    country:      Mapped[Optional["Country"]] = relationship()                          # ← and this
    prices:       Mapped[list["Price"]]       = relationship(back_populates="ticker")
    fundamentals: Mapped[list["Fundamental"]] = relationship(back_populates="ticker")


class Price(Base):
    __tablename__ = "prices"
    ticker_id: Mapped[int]   = mapped_column(ForeignKey("tickers.id"), primary_key=True)
    date:      Mapped[date]  = mapped_column(Date, primary_key=True)
    open:      Mapped[float] = mapped_column(Float)
    high:      Mapped[float] = mapped_column(Float)
    low:       Mapped[float] = mapped_column(Float)
    close:     Mapped[float] = mapped_column(Float)
    volume:    Mapped[int]   = mapped_column()

    ticker: Mapped["Ticker"] = relationship(back_populates="prices")


class Fundamental(Base):
    __tablename__ = "fundamentals"
    ticker_id:      Mapped[int]             = mapped_column(ForeignKey("tickers.id"), primary_key=True)
    pe_ratio:       Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    eps:            Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dividend_yield: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    market_cap:     Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    week_52_high:   Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    week_52_low:    Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    beta:           Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fetched_at:     Mapped[Optional[str]]   = mapped_column(String, nullable=True)

    ticker: Mapped["Ticker"] = relationship(back_populates="fundamentals")