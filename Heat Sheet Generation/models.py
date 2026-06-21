from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    short_id = Column(String, index=True)

    swimmers = relationship("Swimmer", back_populates="team")

class Swimmer(Base):
    __tablename__ = "swimmers"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    gender = Column(String) # 'M' or 'F' (or 'm'/'f')
    team_id = Column(String, ForeignKey("teams.id"))

    team = relationship("Team", back_populates="swimmers")
    entries = relationship("Entry", back_populates="swimmer")

class Meet(Base):
    __tablename__ = "meets"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Date, nullable=True)
    num_lanes = Column(Integer, default=6)
    empty_lanes = Column(Boolean, default=False)

    entries = relationship("Entry", back_populates="meet")
    relay_entries = relationship("RelayEntry", back_populates="meet")

class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meet_id = Column(String, ForeignKey("meets.id"))
    swimmer_id = Column(String, ForeignKey("swimmers.id"))
    event_type = Column(String) # e.g. "free", "breast", "back", "fly", "im"

    meet = relationship("Meet", back_populates="entries")
    swimmer = relationship("Swimmer", back_populates="entries")

class RelayEntry(Base):
    __tablename__ = "relay_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meet_id = Column(String, ForeignKey("meets.id"))
    team_id = Column(String, ForeignKey("teams.id"))
    age_group = Column(String)
    gender = Column(String)
    stroke = Column(String)
    identifier = Column(String) # e.g. "A", "B", "C"
    
    # Optional foreign keys to specific swimmers (can be string ID or relationship)
    swimmer1_id = Column(String, ForeignKey("swimmers.id"), nullable=True)
    swimmer2_id = Column(String, ForeignKey("swimmers.id"), nullable=True)
    swimmer3_id = Column(String, ForeignKey("swimmers.id"), nullable=True)
    swimmer4_id = Column(String, ForeignKey("swimmers.id"), nullable=True)

    meet = relationship("Meet", back_populates="relay_entries")
    team = relationship("Team")
    swimmer1 = relationship("Swimmer", foreign_keys=[swimmer1_id])
    swimmer2 = relationship("Swimmer", foreign_keys=[swimmer2_id])
    swimmer3 = relationship("Swimmer", foreign_keys=[swimmer3_id])
    swimmer4 = relationship("Swimmer", foreign_keys=[swimmer4_id])
