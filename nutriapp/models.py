from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Enum
from datetime import datetime
import enum

class UserRole(enum.Enum):
    normal = "normal"
    ahli_gizi = "ahli_gizi"
    admin = "admin"

class MealType(enum.Enum):
    sarapan = "sarapan"
    camilan_pagi = "camilan_pagi"
    makan_siang = "makan_siang"
    camilan_sore = "camilan_sore"
    makan_malam = "makan_malam"
    supper = "supper"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nama = Column(String,  nullable=False)

    role = Column(
    Enum(UserRole, name="userrole", create_type=False),  # ← tambah ini
    default=UserRole.normal)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    alamat = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    reseps = relationship("Resep", back_populates="user")
    nutrisi = relationship("Nutrisi", back_populates="user")


class Resep(Base):
    __tablename__ = 'reseps'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    nama = Column(String, nullable=False)
    deskripsi = Column(String, nullable=True)
    foto = Column(String, nullable=True)
    tipe = Column(String, nullable=True)
    bahan_utama = Column(String, nullable=True)
    keterangan = Column(String, nullable=True)
    bahan = Column(String, nullable=True)
    cara_memasak = Column(String, nullable=True)
    kalori = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    karbohidrat = Column(Float, nullable=True)
    lemak = Column(Float, nullable=True)

    user = relationship("User", back_populates="reseps")
    resep_bahans = relationship("ResepBahan", back_populates="resep", cascade="all, delete-orphan")

class Nutrisi(Base):
    __tablename__ = 'nutrients'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    nama = Column(String, nullable=False)
    kalori = Column(Float, nullable=True)
    karbohidrat = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    lemak = Column(Float, nullable=True)
    serat = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)
    kalium = Column(Float, nullable=True)

    amount = Column(Float, default=100 ,nullable=False)

    user = relationship("User", back_populates="nutrisi")
    resep_bahans = relationship("ResepBahan", back_populates="nutrisi")

class ResepBahan(Base):
    __tablename__ = 'resep_bahans'
    __table_args__ = (UniqueConstraint('resep_id', 'nutrisi_id', name='unique_resep_bahan'),)

    id = Column(Integer, primary_key=True)
    resep_id = Column(Integer, ForeignKey("reseps.id", ondelete="CASCADE"), nullable=False)
    nutrisi_id = Column(Integer, ForeignKey("nutrients.id"), nullable=False)
    amount = Column(Float, nullable=True)

    resep = relationship("Resep", back_populates="resep_bahans")
    nutrisi = relationship("Nutrisi", back_populates="resep_bahans")

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resep_id = Column(Integer, ForeignKey("reseps.id"), nullable=False)

    tanggal = Column(Date, nullable=False, index=True)
    meal_type = Column(Enum(MealType, name="mealtype", create_type=False), nullable=False)

    user = relationship("User")
    resep = relationship("Resep")