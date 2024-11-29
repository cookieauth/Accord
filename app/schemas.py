# app/schemas.py

from datetime import datetime, date
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

# ----------------------------
# Enum Definitions
# ----------------------------

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

# ----------------------------
# Existing Schemas Integration
# ----------------------------

# ----------------------------
# User Schemas
# ----------------------------

class UserBase(BaseModel):
    username: str = Field(..., example="john_doe")
    email: Optional[EmailStr] = Field(None, example="john@example.com")
    role: str = Field(..., example="admin")  # e.g., 'admin', 'hr', 'department'

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")

class UserRead(UserBase):
    user_id: int
    edipi: Optional[str] = Field(None, example="1234567890")
    department: Optional['DepartmentRead'] = None  # Forward reference

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, example="john_doe_new")
    email: Optional[EmailStr] = Field(None, example="john_new@example.com")
    role: Optional[str] = Field(None, example="hr")
    password: Optional[str] = Field(None, min_length=8, example="newstrongpassword123")
    edipi: Optional[str] = Field(None, example="0987654321")

# ----------------------------
# Department Schemas
# ----------------------------

class DepartmentBase(BaseModel):
    name: str = Field(..., example="Human Resources")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int
    users: List['UserRead']
    personnel: List['PersonnelRead']
    muster_reports: List['MusterReportRead']

    class Config:
        from_attributes = True

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, example="HR Department")

# ----------------------------
# Personnel Schemas
# ----------------------------

class PersonnelBase(BaseModel):
    edipi: str = Field(..., example="1234567890")
    first_name: str = Field(..., example="Alice")
    middle_name: Optional[str] = Field(None, example="B.")
    last_name: str = Field(..., example="Smith")
    date_of_birth: date = Field(..., example="1990-01-01")
    rank_id: int = Field(..., example=1)
    rate_id: Optional[int] = Field(None, example=1)
    job_id: int = Field(..., example=1)
    branch_id: int = Field(..., example=1)
    command_id: int = Field(..., example=1)
    unit_id: int = Field(..., example=1)
    phone_number: Optional[str] = Field(None, example="555-1234")
    email: Optional[EmailStr] = Field(None, example="alice.smith@example.com")
    status: PersonnelStatusEnum
    date_enlisted: date = Field(..., example="2010-05-15")
    date_released: Optional[date] = Field(None, example="2020-05-15")
    location: Optional[str] = Field(None, example="New York Office")

class PersonnelCreate(PersonnelBase):
    pass

class PersonnelRead(PersonnelBase):
    id: int
    department: Optional['DepartmentRead'] = None
    rank: Optional['RankRead'] = None
    rate: Optional['RateRead'] = None
    job_specialty: Optional['JobSpecialtyRead'] = None
    branch: Optional['BranchRead'] = None
    command: Optional['CommandRead'] = None
    unit: Optional['UnitRead'] = None
    personnel_statuses: List['PersonnelStatusRead']
    attendance_records: List['AttendanceRead']

    class Config:
        from_attributes = True

class PersonnelUpdate(BaseModel):
    edipi: Optional[str] = Field(None, example="0987654321")
    first_name: Optional[str] = Field(None, example="Alice")
    middle_name: Optional[str] = Field(None, example="C.")
    last_name: Optional[str] = Field(None, example="Johnson")
    date_of_birth: Optional[date] = Field(None, example="1990-02-02")
    rank_id: Optional[int] = Field(None, example=2)
    rate_id: Optional[int] = Field(None, example=2)
    job_id: Optional[int] = Field(None, example=2)
    branch_id: Optional[int] = Field(None, example=2)
    command_id: Optional[int] = Field(None, example=2)
    unit_id: Optional[int] = Field(None, example=2)
    phone_number: Optional[str] = Field(None, example="555-5678")
    email: Optional[EmailStr] = Field(None, example="alice.johnson@example.com")
    status: Optional[PersonnelStatusEnum] = None
    date_enlisted: Optional[date] = Field(None, example="2011-06-16")
    date_released: Optional[date] = Field(None, example="2021-06-16")
    location: Optional[str] = Field(None, example="Los Angeles Office")

# ----------------------------
# Muster Report Schemas
# ----------------------------

class PersonnelStatusBase(BaseModel):
    edipi: str = Field(..., example="1234567890")
    status: StatusEnum

class PersonnelStatusCreate(PersonnelStatusBase):
    pass

class PersonnelStatusRead(PersonnelStatusBase):
    id: int

    class Config:
        from_attributes = True

class MusterReportBase(BaseModel):
    department_id: int
    date: date

class MusterReportCreate(MusterReportBase):
    personnel_statuses: List[PersonnelStatusCreate]
    submitted_by_id: int

class MusterReportRead(MusterReportBase):
    id: int
    submitted_by_id: int
    status: ReportStatusEnum
    archived: bool
    archived_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    personnel_statuses: List[PersonnelStatusRead]
    department: Optional[DepartmentRead] = None
    submitted_by: Optional[UserRead] = None

    class Config:
        from_attributes = True

class MusterReportUpdate(BaseModel):
    status: Optional[ReportStatusEnum] = None
    archived: Optional[bool] = None
    archived_at: Optional[datetime] = None

class ReviewMusterReport(BaseModel):
    status: ReportStatusEnum

# ----------------------------
# Notification Schemas
# ----------------------------

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    notification_type: NotificationTypeEnum

class NotificationRead(BaseModel):
    notification_id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime
    notification_type: NotificationTypeEnum
    user: Optional['UserRead'] = None

    class Config:
        from_attributes = True

# ----------------------------
# Additional Schemas
# ----------------------------

# Branch Schemas
class BranchBase(BaseModel):
    branch_name: str = Field(..., example="Army")
    description: Optional[str] = Field(None, example="United States Army")

class BranchCreate(BranchBase):
    pass

class BranchRead(BranchBase):
    branch_id: int
    ranks: List['RankRead']
    rates: List['RateRead']
    job_specialties: List['JobSpecialtyRead']
    commands: List['CommandRead']
    personnel: List['PersonnelRead']

    class Config:
        from_attributes = True

class BranchUpdate(BaseModel):
    branch_name: Optional[str] = Field(None, example="Army")
    description: Optional[str] = Field(None, example="Updated description")

# Rank Schemas
class RankBase(BaseModel):
    branch_id: int
    rank_name: str = Field(..., example="Private")
    rank_order: int = Field(..., example=1)
    abbreviation: str = Field(..., example="PVT")

class RankCreate(RankBase):
    pass

class RankRead(RankBase):
    rank_id: int
    branch: Optional['BranchRead'] = None
    personnel: List['PersonnelRead']

    class Config:
        from_attributes = True

class RankUpdate(BaseModel):
    rank_name: Optional[str] = Field(None, example="Private First Class")
    rank_order: Optional[int] = Field(None, example=2)
    abbreviation: Optional[str] = Field(None, example="PFC")

# Rate Schemas
class RateBase(BaseModel):
    branch_id: int
    rate_name: str = Field(..., example="Infantry")
    abbreviation: str = Field(..., example="INF")

class RateCreate(RateBase):
    pass

class RateRead(RateBase):
    rate_id: int
    branch: Optional['BranchRead'] = None
    personnel: List['PersonnelRead']

    class Config:
        from_attributes = True

class RateUpdate(BaseModel):
    rate_name: Optional[str] = Field(None, example="Mechanized Infantry")
    abbreviation: Optional[str] = Field(None, example="MI")

# JobSpecialty Schemas
class JobSpecialtyBase(BaseModel):
    branch_id: int
    job_code: str = Field(..., example="11B")
    job_title: str = Field(..., example="Infantryman")
    description: Optional[str] = Field(None, example="Handles infantry operations")

class JobSpecialtyCreate(JobSpecialtyBase):
    pass

class JobSpecialtyRead(JobSpecialtyBase):
    job_id: int
    branch: Optional['BranchRead'] = None
    personnel: List['PersonnelRead']

    class Config:
        from_attributes = True

class JobSpecialtyUpdate(BaseModel):
    job_code: Optional[str] = Field(None, example="11C")
    job_title: Optional[str] = Field(None, example="Indirect Fire Infantryman")
    description: Optional[str] = Field(None, example="Handles indirect fire infantry operations")

# Location Schemas
class LocationBase(BaseModel):
    location_name: str = Field(..., example="Fort Bragg")
    address: Optional[str] = Field(None, example="123 Military Rd")
    city: Optional[str] = Field(None, example="Fayetteville")
    state: Optional[str] = Field(None, example="NC")
    country: Optional[str] = Field(None, example="USA")
    latitude: Optional[float] = Field(None, example=35.0621)
    longitude: Optional[float] = Field(None, example=-78.8784)

class LocationCreate(LocationBase):
    pass

class LocationRead(LocationBase):
    location_id: int
    commands: List['CommandRead']
    muster_events: List['MusterEventRead']
    geofencings: List['GeofencingRead']

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    location_name: Optional[str] = Field(None, example="Fort Liberty")
    address: Optional[str] = Field(None, example="456 New Address Rd")
    city: Optional[str] = Field(None, example="Fayetteville")
    state: Optional[str] = Field(None, example="NC")
    country: Optional[str] = Field(None, example="USA")
    latitude: Optional[float] = Field(None, example=35.1)
    longitude: Optional[float] = Field(None, example=-78.9)

# Command Schemas
class CommandBase(BaseModel):
    branch_id: int
    parent_command_id: Optional[int] = Field(None, example=1)
    command_name: str = Field(..., example="1st Infantry Division")
    location_id: int
    UIC: str = Field(..., example="1ID")
    description: Optional[str] = Field(None, example="Handles infantry operations")

class CommandCreate(CommandBase):
    pass

class CommandRead(CommandBase):
    command_id: int
    branch: Optional['BranchRead'] = None
    parent_command: Optional['CommandRead'] = None
    subcommands: List['CommandRead']
    units: List['UnitRead']
    muster_events: List['MusterEventRead']
    personnel: List['PersonnelRead']

    class Config:
        from_attributes = True

class CommandUpdate(BaseModel):
    branch_id: Optional[int] = Field(None, example=2)
    parent_command_id: Optional[int] = Field(None, example=2)
    command_name: Optional[str] = Field(None, example="2nd Infantry Division")
    location_id: Optional[int] = Field(None, example=2)
    UIC: Optional[str] = Field(None, example="2ID")
    description: Optional[str] = Field(None, example="Handles mechanized infantry operations")

# Unit Schemas
class UnitBase(BaseModel):
    command_id: int
    unit_name: str = Field(..., example="3rd Battalion")
    UIC: str = Field(..., example="3BN")
    description: Optional[str] = Field(None, example="Handles 3rd Battalion operations")

class UnitCreate(UnitBase):
    pass

class UnitRead(UnitBase):
    unit_id: int
    command: Optional['CommandRead'] = None
    personnel: List['PersonnelRead']
    muster_events: List['MusterEventRead']

    class Config:
        from_attributes = True

class UnitUpdate(BaseModel):
    command_id: Optional[int] = Field(None, example=3)
    unit_name: Optional[str] = Field(None, example="4th Battalion")
    UIC: Optional[str] = Field(None, example="4BN")
    description: Optional[str] = Field(None, example="Handles 4th Battalion operations")

# Role Schemas
class RoleBase(BaseModel):
    role_name: str = Field(..., example="admin")
    description: Optional[str] = Field(None, example="Administrator role with full access")

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    role_id: int
    permissions: List['PermissionRead']
    users: List['UserRead']

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, example="superadmin")
    description: Optional[str] = Field(None, example="Super Administrator role with elevated access")

# Permission Schemas
class PermissionBase(BaseModel):
    permission_name: str = Field(..., example="read_reports")
    description: Optional[str] = Field(None, example="Allows reading of reports")

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    permission_id: int
    roles: List['RoleRead']

    class Config:
        from_attributes = True

class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = Field(None, example="write_reports")
    description: Optional[str] = Field(None, example="Allows writing of reports")

# RolePermission Schemas
class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionRead(RolePermissionBase):
    class Config:
        from_attributes = True

# MusterEvent Schemas
class MusterEventBase(BaseModel):
    command_id: int
    unit_id: Optional[int] = Field(None, example=1)
    location_id: int
    event_date: date
    description: Optional[str] = Field(None, example="Monthly muster at Fort Bragg")
    created_by: int

class MusterEventCreate(MusterEventBase):
    pass

class MusterEventRead(MusterEventBase):
    muster_id: int
    created_at: datetime
    command: Optional['CommandRead'] = None
    unit: Optional['UnitRead'] = None
    location: Optional['LocationRead'] = None
    attendance_records: List['AttendanceRead']

    class Config:
        from_attributes = True

class MusterEventUpdate(BaseModel):
    command_id: Optional[int] = Field(None, example=2)
    unit_id: Optional[int] = Field(None, example=2)
    location_id: Optional[int] = Field(None, example=2)
    event_date: Optional[date] = Field(None, example="2024-12-01")
    description: Optional[str] = Field(None, example="Updated muster description")

# Attendance Schemas
class AttendanceBase(BaseModel):
    muster_id: int
    edipi: str = Field(..., example="1234567890")
    status: StatusEnum
    remarks: Optional[str] = Field(None, example="Arrived late due to traffic")

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceRead(AttendanceBase):
    attendance_id: int
    timestamp: datetime
    muster_event: Optional['MusterEventRead'] = None
    personnel: Optional['PersonnelRead'] = None

    class Config:
        from_attributes = True

class AttendanceUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    remarks: Optional[str] = Field(None, example="Left early due to emergency")

# AuditLog Schemas
class AuditLogBase(BaseModel):
    action: str = Field(..., example="User Created")
    table_name: str = Field(..., example="users")
    record_id: int = Field(..., example=1)
    details: Optional[str] = Field(None, example="Created user john_doe")

class AuditLogCreate(AuditLogBase):
    user_id: int

class AuditLogRead(AuditLogBase):
    audit_id: int
    user_id: int
    timestamp: datetime
    user: Optional['UserRead'] = None

    class Config:
        from_attributes = True

# Geofencing Schemas
class GeofencingBase(BaseModel):
    location_id: int
    radius: float = Field(..., example=100.00)  # in meters or relevant units
    polygon: Optional[Dict] = Field(None, example={
        "type": "Polygon",
        "coordinates": [
            [
                [-78.8784, 35.0621],
                [-78.8784, 35.0721],
                [-78.8684, 35.0721],
                [-78.8684, 35.0621],
                [-78.8784, 35.0621]
            ]
        ]
    })  # Represented as GeoJSON
    description: Optional[str] = Field(None, example="Geofence around Fort Bragg perimeter")

class GeofencingCreate(GeofencingBase):
    pass

class GeofencingRead(GeofencingBase):
    geofence_id: int
    location: Optional['LocationRead'] = None

    class Config:
        from_attributes = True

class GeofencingUpdate(BaseModel):
    location_id: Optional[int] = Field(None, example=2)
    radius: Optional[float] = Field(None, example=150.00)
    polygon: Optional[Dict] = Field(None, example={
        "type": "Polygon",
        "coordinates": [
            [
                [-78.8784, 35.0621],
                [-78.8784, 35.0821],
                [-78.8484, 35.0821],
                [-78.8484, 35.0621],
                [-78.8784, 35.0621]
            ]
        ]
    })
    description: Optional[str] = Field(None, example="Updated geofence description")

# UserSetting Schemas
class UserSettingBase(BaseModel):
    user_id: int
    setting_key: str = Field(..., example="theme")
    setting_value: str = Field(..., example="dark")

class UserSettingCreate(UserSettingBase):
    pass

class UserSettingRead(UserSettingBase):
    setting_id: int
    user: Optional['UserRead'] = None

    class Config:
        from_attributes = True

class UserSettingUpdate(BaseModel):
    setting_value: Optional[str] = Field(None, example="light")

# DataImportExport Schemas
class DataImportExportBase(BaseModel):
    file_name: str = Field(..., example="personnel_data.csv")
    import_type: str = Field(..., example="Bulk Upload")  # e.g., 'Bulk Upload', 'Data Migration'
    status: str = Field(..., example="Pending")  # e.g., 'Pending', 'Completed', 'Failed'
    details: Optional[str] = Field(None, example="Uploaded 1000 records successfully")

class DataImportExportCreate(DataImportExportBase):
    pass

class DataImportExportRead(DataImportExportBase):
    import_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DataImportExportUpdate(BaseModel):
    status: Optional[str] = Field(None, example="Completed")
    completed_at: Optional[datetime] = None
    details: Optional[str] = Field(None, example="Processed 1000 records successfully")

# BackupRecovery Schemas
class BackupRecoveryBase(BaseModel):
    backup_type: str = Field(..., example="Full")  # e.g., 'Full', 'Incremental'
    status: str = Field(..., example="Successful")  # e.g., 'Successful', 'Failed'
    details: Optional[str] = Field(None, example="Backup completed without errors")

class BackupRecoveryCreate(BackupRecoveryBase):
    pass

class BackupRecoveryRead(BackupRecoveryBase):
    backup_id: int
    backup_date: datetime

    class Config:
        from_attributes = True

class BackupRecoveryUpdate(BaseModel):
    status: Optional[str] = Field(None, example="Failed")
    details: Optional[str] = Field(None, example="Backup failed due to network issues")

# ----------------------------
# Nested Models Forward References
# ----------------------------

# Update forward references
UserRead.update_forward_refs()
DepartmentRead.update_forward_refs()
PersonnelRead.update_forward_refs()
MusterReportRead.update_forward_refs()
AttendanceRead.update_forward_refs()
CommandRead.update_forward_refs()
UnitRead.update_forward_refs()
BranchRead.update_forward_refs()
RankRead.update_forward_refs()
RateRead.update_forward_refs()
JobSpecialtyRead.update_forward_refs()
LocationRead.update_forward_refs()
MusterEventRead.update_forward_refs()
GeofencingRead.update_forward_refs()
AuditLogRead.update_forward_refs()
RoleRead.update_forward_refs()
PermissionRead.update_forward_refs()
