# app/models.py

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum as SqlEnum,
    DateTime,
    Boolean,
    Date,
    DECIMAL,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

# ----------------------------------
# Enumerations
# ----------------------------------

class StatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    ON_LEAVE = "on_leave"
    ACCOUNTED_FOR = "accounted_for"
    TAD_TDY = "tad_tdy"
    LIMDU = "limdu"

class ReportStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PersonnelStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class NotificationTypeEnum(str, Enum):
    ALERT = "alert"
    REMINDER = "reminder"
    UPDATE = "update"

# ----------------------------------
# Existing Models
# ----------------------------------

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    edipi = Column(String(20), ForeignKey("personnel.edipi"), nullable=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), index=True, nullable=False)
    last_login = Column(DateTime, default=datetime.utcnow, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    department = relationship("Department", back_populates="users")
    submitted_reports = relationship("MusterReport", back_populates="submitted_by")
    notifications = relationship('Notification', back_populates='user')
    role = relationship("Role", back_populates="users")
    personnel = relationship("Personnel", back_populates="user", uselist=False)

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    # Relationships
    users = relationship("User", back_populates="department", cascade="all, delete-orphan")
    personnel = relationship("Personnel", back_populates="department", cascade="all, delete-orphan")
    muster_reports = relationship("MusterReport", back_populates="department", cascade="all, delete-orphan")

    # Constraints and Indices
    __table_args__ = (
        UniqueConstraint('name', name='uq_departments_name'),
        Index('ix_departments_id', 'id'),
    )

class MusterReport(Base):
    __tablename__ = "muster_reports"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    date = Column(Date, nullable=False)
    submitted_by_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(SqlEnum(ReportStatusEnum), default=ReportStatusEnum.PENDING, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="muster_reports")
    submitted_by = relationship("User", back_populates="submitted_reports")
    personnel_statuses = relationship("PersonnelStatus", back_populates="muster_report")

class PersonnelStatus(Base):
    __tablename__ = "personnel_statuses"

    id = Column(Integer, primary_key=True, index=True)
    muster_report_id = Column(Integer, ForeignKey("muster_reports.id"), nullable=False)
    edipi = Column(String(20), ForeignKey("personnel.edipi"), nullable=False)
    status = Column(SqlEnum(StatusEnum), nullable=False)

    muster_report = relationship("MusterReport", back_populates="personnel_statuses")
    personnel = relationship("Personnel", back_populates="personnel_statuses")

class Personnel(Base):
    __tablename__ = "personnel"

    edipi = Column(String(20), primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    rank_id = Column(Integer, ForeignKey("ranks.rank_id"), nullable=False)
    rate_id = Column(Integer, ForeignKey("rates.rate_id"), nullable=True)
    job_id = Column(Integer, ForeignKey("job_specialties.job_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    command_id = Column(Integer, ForeignKey("commands.command_id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.unit_id"), nullable=False)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    status = Column(SqlEnum(PersonnelStatusEnum), nullable=False)
    date_enlisted = Column(Date, nullable=False)
    date_released = Column(Date, nullable=True)
    profile_picture = Column(Text, nullable=True)  # Changed to Text for simplicity; adjust as needed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="personnel")
    personnel_statuses = relationship("PersonnelStatus", back_populates="personnel")
    attendance_records = relationship("Attendance", back_populates="personnel")
    user = relationship("User", back_populates="personnel")
    rank = relationship("Rank", back_populates="personnel")
    rate = relationship("Rate", back_populates="personnel")
    job_specialty = relationship("JobSpecialty", back_populates="personnel")
    branch = relationship("Branch", back_populates="personnel")
    command = relationship("Command", back_populates="personnel")
    unit = relationship("Unit", back_populates="personnel")

class Notification(Base):
    __tablename__ = 'notifications'

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notification_type = Column(SqlEnum(NotificationTypeEnum), nullable=False)

    user = relationship('User', back_populates='notifications')

# ----------------------------------
# Additional Models
# ----------------------------------

class Branch(Base):
    __tablename__ = "branches"

    branch_id = Column(Integer, primary_key=True, index=True)
    branch_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    ranks = relationship("Rank", back_populates="branch", cascade="all, delete-orphan")
    rates = relationship("Rate", back_populates="branch", cascade="all, delete-orphan")
    job_specialties = relationship("JobSpecialty", back_populates="branch", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="branch", cascade="all, delete-orphan")
    personnel = relationship("Personnel", back_populates="branch")

class Rank(Base):
    __tablename__ = "ranks"
    __table_args__ = (UniqueConstraint('branch_id', 'abbreviation', name='uq_ranks_branch_abbreviation'),)

    rank_id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    rank_name = Column(String(100), nullable=False)
    rank_order = Column(Integer, nullable=False)
    abbreviation = Column(String(10), nullable=False)

    branch = relationship("Branch", back_populates="ranks")
    personnel = relationship("Personnel", back_populates="rank")

class Rate(Base):
    __tablename__ = "rates"
    __table_args__ = (UniqueConstraint('branch_id', 'abbreviation', name='uq_rates_branch_abbreviation'),)

    rate_id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    rate_name = Column(String(100), nullable=False)
    abbreviation = Column(String(10), nullable=False)

    branch = relationship("Branch", back_populates="rates")
    personnel = relationship("Personnel", back_populates="rate")

class JobSpecialty(Base):
    __tablename__ = "job_specialties"
    __table_args__ = (UniqueConstraint('branch_id', 'job_code', name='uq_job_specialties_branch_job_code'),)

    job_id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    job_code = Column(String(20), nullable=False)
    job_title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    branch = relationship("Branch", back_populates="job_specialties")
    personnel = relationship("Personnel", back_populates="job_specialty")

class Location(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(100), unique=True, nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    latitude = Column(DECIMAL(9,6), nullable=True)
    longitude = Column(DECIMAL(9,6), nullable=True)

    commands = relationship("Command", back_populates="location", cascade="all, delete-orphan")
    muster_events = relationship("MusterEvent", back_populates="location", cascade="all, delete-orphan")
    geofencings = relationship("Geofencing", back_populates="location", cascade="all, delete-orphan")

class Command(Base):
    __tablename__ = "commands"
    __table_args__ = (UniqueConstraint('branch_id', 'command_name', name='uq_commands_branch_command_name'),)

    command_id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    parent_command_id = Column(Integer, ForeignKey("commands.command_id"), nullable=True)
    command_name = Column(String(100), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=False)
    UIC = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    branch = relationship("Branch", back_populates="commands")
    parent_command = relationship("Command", remote_side=[command_id], backref="subcommands")
    location = relationship("Location", back_populates="commands")
    units = relationship("Unit", back_populates="command", cascade="all, delete-orphan")
    muster_events = relationship("MusterEvent", back_populates="command", cascade="all, delete-orphan")
    personnel = relationship("Personnel", back_populates="command")

class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (UniqueConstraint('command_id', 'unit_name', name='uq_units_command_unit_name'),)

    unit_id = Column(Integer, primary_key=True, index=True)
    command_id = Column(Integer, ForeignKey("commands.command_id"), nullable=False)
    unit_name = Column(String(100), nullable=False)
    UIC = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    command = relationship("Command", back_populates="units")
    personnel = relationship("Personnel", back_populates="unit")
    muster_events = relationship("MusterEvent", back_populates="unit", cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey("roles.role_id"), primary_key=True, nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.permission_id"), primary_key=True, nullable=False)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

class MusterEvent(Base):
    __tablename__ = "muster_events"

    muster_id = Column(Integer, primary_key=True, index=True)
    command_id = Column(Integer, ForeignKey("commands.command_id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.unit_id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=False)
    event_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    command = relationship("Command", back_populates="muster_events")
    unit = relationship("Unit", back_populates="muster_events")
    location = relationship("Location", back_populates="muster_events")
    created_by_user = relationship("User")
    attendance_records = relationship("Attendance", back_populates="muster_event", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    muster_id = Column(Integer, ForeignKey("muster_events.muster_id"), nullable=False)
    edipi = Column(String(20), ForeignKey("personnel.edipi"), nullable=False)
    status = Column(SqlEnum(StatusEnum), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    remarks = Column(Text, nullable=True)

    muster_event = relationship("MusterEvent", back_populates="attendance_records")
    personnel = relationship("Personnel", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint('muster_id', 'edipi', name='uq_attendance_muster_edipi'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)

    user = relationship("User")

class Geofencing(Base):
    __tablename__ = "geofencing"

    geofence_id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=False)
    radius = Column(DECIMAL(10,2), nullable=False)  # in meters or relevant units
    polygon = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=True)  # Using PostGIS for spatial data
    description = Column(Text, nullable=True)

    location = relationship("Location", back_populates="geofencings")

class UserSetting(Base):
    __tablename__ = "user_settings"
    __table_args__ = (UniqueConstraint('user_id', 'setting_key', name='uq_user_settings_user_key'),)

    setting_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(String(255), nullable=False)

    user = relationship("User")

class DataImportExport(Base):
    __tablename__ = "data_import_export"

    import_id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    import_type = Column(String(50), nullable=False)  # e.g., 'Bulk Upload', 'Data Migration'
    status = Column(String(50), nullable=False)  # e.g., 'Pending', 'Completed', 'Failed'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    details = Column(Text, nullable=True)

class BackupRecovery(Base):
    __tablename__ = "backup_recovery"

    backup_id = Column(Integer, primary_key=True, index=True)
    backup_type = Column(String(50), nullable=False)  # e.g., 'Full', 'Incremental'
    backup_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), nullable=False)  # e.g., 'Successful', 'Failed'
    details = Column(Text, nullable=True)
