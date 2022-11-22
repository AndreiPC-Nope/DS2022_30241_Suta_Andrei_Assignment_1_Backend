from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    role = Column(String(50), unique=True)
    users = relationship('User', back_populates='role')

    def __init__(self, role):
        self.role = role


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=False)
    username = Column(String(50), unique=True)
    password = Column(String(50), unique=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship('Role', back_populates='users')
    devices = relationship('Device', back_populates='user')

    def __init__(self, username, password, name, role_id):
        self.username = username
        self.password = password
        self.name = name
        self.role_id = role_id


class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True)
    description = Column(String(255), unique=False)
    address = Column(String(50), unique=False)
    max_energy = Column(Float, unique=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='devices')
    measurements = relationship("Measurement", back_populates='device')

    def __init__(self, description, address, max_energy):
        self.max_energy = max_energy
        self.address = address
        self.description = description


class Measurement(Base):
    __tablename__ = 'measurements'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=False), unique=False)
    energy = Column(Float, unique=False)
    device_id = Column(Integer, ForeignKey('devices.id'))
    device = relationship('Device', back_populates="measurements")

    def __int__(self, timestamp, energy, device_id):
        self.timestamp = timestamp
        self.energy = energy
        self.device_id = device_id
