"""Institutional content schemas: events, projects, people, facilities, documents."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    AccessLevel,
    BookingStatus,
    DocumentType,
    EventKind,
    EventStatus,
)


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    kind: EventKind
    description: str | None
    venue: str | None
    starts_at: datetime | None
    ends_at: datetime | None
    organizer: str | None
    registration_url: str | None
    capacity: int | None
    is_active: bool
    status: EventStatus
    access_level: AccessLevel
    created_at: datetime
    updated_at: datetime


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    kind: EventKind = EventKind.EVENT
    description: str | None = None
    venue: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    organizer: str | None = None
    registration_url: str | None = None
    capacity: int | None = None
    access_level: AccessLevel = AccessLevel.INTERNAL

    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "title": "IdeaLab Hackathon 2024",
            "kind": "hackathon",
            "description": "Annual coding competition",
            "venue": "IdeaLab Main Hall",
            "starts_at": "2024-12-15T09:00:00Z",
            "ends_at": "2024-12-15T18:00:00Z",
            "organizer": "Tech Gurus",
            "capacity": 100,
            "access_level": "public",
        }
    })


class EventUpdate(BaseModel):
    title: str | None = None
    kind: EventKind | None = None
    description: str | None = None
    venue: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    organizer: str | None = None
    registration_url: str | None = None
    capacity: int | None = None
    is_active: bool | None = None
    status: EventStatus | None = None
    access_level: AccessLevel | None = None

    model_config = ConfigDict(use_enum_values=True)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    summary: str | None
    description: str | None
    status: str | None
    domain: str | None
    technologies: str | None
    is_active: bool
    is_published: bool
    started_at: datetime | None
    access_level: AccessLevel
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    summary: str | None = None
    description: str | None = None
    status: str | None = None
    domain: str | None = None
    technologies: str | None = None
    is_active: bool = True
    access_level: AccessLevel = AccessLevel.INTERNAL

    model_config = ConfigDict(use_enum_values=True)


class ProjectUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    status: str | None = None
    domain: str | None = None
    technologies: str | None = None
    is_active: bool | None = None
    is_published: bool | None = None
    access_level: AccessLevel | None = None


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    building: str | None
    email: str | None
    phone: str | None
    website: str | None
    access_level: AccessLevel
    created_at: datetime


class FacultyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    employee_code: str | None
    department: DepartmentRead | None
    designation: str | None
    specialization: str | None
    research_interests: str | None
    bio: str | None
    office_location: str | None
    photo_url: str | None
    is_hod: bool
    is_public: bool
    access_level: AccessLevel
    created_at: datetime


class FacultyCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: str | None = None
    phone: str | None = None
    employee_code: str | None = None
    department_id: uuid.UUID | None = None
    designation: str | None = None
    specialization: str | None = None
    research_interests: str | None = None
    bio: str | None = None
    office_location: str | None = None
    photo_url: str | None = None
    is_hod: bool = False
    is_public: bool = True
    access_level: AccessLevel = AccessLevel.PUBLIC

    model_config = ConfigDict(use_enum_values=True)


class FacultyUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    employee_code: str | None = None
    department_id: uuid.UUID | None = None
    designation: str | None = None
    specialization: str | None = None
    research_interests: str | None = None
    bio: str | None = None
    office_location: str | None = None
    photo_url: str | None = None
    is_hod: bool | None = None
    is_public: bool | None = None
    access_level: AccessLevel | None = None


class StaffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    employee_code: str | None
    designation: str | None
    responsibilities: str | None
    department: DepartmentRead | None
    access_level: AccessLevel
    created_at: datetime


class StaffCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: str | None = None
    phone: str | None = None
    employee_code: str | None = None
    department_id: uuid.UUID | None = None
    designation: str | None = None
    responsibilities: str | None = None
    access_level: AccessLevel = AccessLevel.INTERNAL

    model_config = ConfigDict(use_enum_values=True)


class StaffUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    employee_code: str | None = None
    department_id: uuid.UUID | None = None
    designation: str | None = None
    responsibilities: str | None = None
    access_level: AccessLevel | None = None


class IdeaLabMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str
    email: str | None
    role_title: str | None
    team: str | None
    bio: str | None
    skills: str | None
    joined_at: datetime | None
    is_active: bool
    access_level: AccessLevel
    department: DepartmentRead | None
    created_at: datetime


class IdeaLabMemberCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: str | None = None
    department_id: uuid.UUID | None = None
    role_title: str | None = None
    team: str | None = None
    bio: str | None = None
    skills: str | None = None
    joined_at: datetime | None = None
    is_active: bool = True
    access_level: AccessLevel = AccessLevel.INTERNAL

    model_config = ConfigDict(use_enum_values=True)


class IdeaLabMemberUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    department_id: uuid.UUID | None = None
    role_title: str | None = None
    team: str | None = None
    bio: str | None = None
    skills: str | None = None
    joined_at: datetime | None = None
    is_active: bool | None = None
    access_level: AccessLevel | None = None


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str
    email: str | None
    roll_number: str | None
    phone: str | None
    program: str | None
    year: int | None
    access_level: AccessLevel
    created_at: datetime


class StudentCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: str | None = None
    roll_number: str | None = None
    phone: str | None = None
    department_id: uuid.UUID | None = None
    program: str | None = None
    year: int | None = None
    access_level: AccessLevel = AccessLevel.RESTRICTED

    model_config = ConfigDict(use_enum_values=True)


class StudentUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    roll_number: str | None = None
    phone: str | None = None
    department_id: uuid.UUID | None = None
    program: str | None = None
    year: int | None = None
    access_level: AccessLevel | None = None


class EquipmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    category: str | None
    description: str | None
    specifications: dict | None
    serial_number: str | None
    location: str | None
    status: str | None
    is_active: bool
    quantity: int | None
    access_level: AccessLevel
    created_at: datetime
    updated_at: datetime


class EquipmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str | None = None
    description: str | None = None
    specifications: dict | None = None
    serial_number: str | None = None
    location: str | None = None
    status: str | None = None
    is_active: bool = True
    quantity: int | None = None
    access_level: AccessLevel = AccessLevel.INTERNAL

    model_config = ConfigDict(use_enum_values=True)


class EquipmentUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    specifications: dict | None = None
    serial_number: str | None = None
    location: str | None = None
    status: str | None = None
    is_active: bool | None = None
    quantity: int | None = None
    access_level: AccessLevel | None = None


class EquipmentBookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    equipment_id: uuid.UUID
    user_id: uuid.UUID | None
    purpose: str | None
    start_time: str | None
    end_time: str | None
    quantity: int | None
    status: BookingStatus
    created_at: datetime
    updated_at: datetime


class EquipmentBookingCreate(BaseModel):
    purpose: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    quantity: int | None = 1

    model_config = ConfigDict(use_enum_values=True)


class EquipmentBookingUpdate(BaseModel):
    status: BookingStatus | None = None
    purpose: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    quantity: int | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    doc_type: DocumentType
    summary: str | None
    source_url: str | None
    file_path: str | None
    content_hash: str | None
    is_indexed: bool
    processing_status: str
    access_level: AccessLevel
    department_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    doc_type: DocumentType = DocumentType.OTHER
    summary: str | None = None
    source_url: str | None = None
    department_id: uuid.UUID | None = None
    access_level: AccessLevel = AccessLevel.INTERNAL

    model_config = ConfigDict(use_enum_values=True)


class DocumentUpdate(BaseModel):
    title: str | None = None
    doc_type: DocumentType | None = None
    summary: str | None = None
    source_url: str | None = None
    access_level: AccessLevel | None = None


class EventRegistrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    event_id: uuid.UUID
    user_id: uuid.UUID | None
    email: str | None
    full_name: str | None
    attended_at: datetime | None
    created_at: datetime


class EventRegistrationCreate(BaseModel):
    event_id: uuid.UUID
    email: str | None = None
    full_name: str | None = None

    model_config = ConfigDict(use_enum_values=True)


class PaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list
    total: int
    page: int
    per_page: int
    pages: int


class SearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str | None
    url: str
    snippet: str | None
