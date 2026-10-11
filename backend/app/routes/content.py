"""Content CRUD routes for events, projects, people, equipment, documents."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_optional_current_user
from app.core.errors import NotFoundError, PermissionDeniedError
from app.db.session import get_session
from app.models.auth import User
from app.models.content import Event, Project, EventRegistration
from app.models.equipment import Equipment, EquipmentBooking
from app.models.enums import AccessLevel, BookingStatus
from app.models.knowledge import Document
from app.models.people import Faculty, Staff, Student, IdeaLabMember
from app.models.org import Department
from app.schemas.content import (
    EquipmentBookingCreate,
    EquipmentBookingRead,
    EquipmentBookingUpdate,
    EquipmentCreate,
    EquipmentRead,
    EquipmentUpdate,
    EventCreate,
    EventRead,
    EventRegistrationCreate,
    EventRegistrationRead,
    EventUpdate,
    FacultyCreate,
    FacultyRead,
    FacultyUpdate,
    IdeaLabMemberCreate,
    IdeaLabMemberRead,
    IdeaLabMemberUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    StaffCreate,
    StaffRead,
    StaffUpdate,
    StudentCreate,
    StudentRead,
    StudentUpdate,
    DocumentCreate,
    DocumentRead,
    DocumentUpdate,
)

router = APIRouter(tags=["content"])
CurrentUser = Depends(get_current_user)


def _event_read(e: Event) -> EventRead:
    return EventRead.model_validate(e)


def _project_read(p: Project) -> ProjectRead:
    return ProjectRead.model_validate(p)


# ---- Events ----------------------------------------------------------------

@router.get("/events", response_model=list[EventRead])
async def list_events(
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[EventRead]:
    stmt = select(Event)
    if user is None:
        stmt = stmt.where(Event.status == "PUBLISHED", Event.access_level == "PUBLIC")
    result = await session.execute(stmt.order_by(Event.starts_at.desc()).limit(limit))
    events = list(result.scalars())
    return [_event_read(e) for e in events]


@router.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> EventRead:
    event = Event(**payload.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return _event_read(event)


@router.get("/events/{event_id}", response_model=EventRead)
async def get_event(
    event_id: uuid.UUID,
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
) -> EventRead:
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise NotFoundError("Event not found")
    if user is None and event.access_level != AccessLevel.PUBLIC:
        raise PermissionDeniedError("Authentication required")
    return _event_read(event)


@router.patch("/events/{event_id}", response_model=EventRead)
async def update_event(
    event_id: uuid.UUID,
    payload: EventUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> EventRead:
    event = await session.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return _event_read(event)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> None:
    event = await session.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")
    await session.delete(event)
    await session.commit()


@router.post("/events/{event_id}/register", response_model=EventRegistrationRead)
async def register_for_event(
    event_id: uuid.UUID,
    payload: EventRegistrationCreate,
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
) -> EventRegistrationRead:
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise NotFoundError("Event not found")
    reg = EventRegistration(
        event_id=event_id,
        user_id=user.id if user else None,
        email=payload.email,
        full_name=payload.full_name,
    )
    session.add(reg)
    await session.commit()
    await session.refresh(reg)
    return EventRegistrationRead.model_validate(reg)


# ---- Projects ---------------------------------------------------------------

@router.get("/projects", response_model=list[ProjectRead])
async def list_projects(
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ProjectRead]:
    stmt = select(Project)
    if user is None:
        stmt = stmt.where(Project.is_published.is_(True))
    result = await session.execute(stmt.order_by(Project.created_at.desc()).limit(limit))
    projects = list(result.scalars())
    return [_project_read(p) for p in projects]


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> ProjectRead:
    project = Project(**payload.model_dump())
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return _project_read(project)


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: uuid.UUID,
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectRead:
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")
    if user is None and not project.is_published:
        raise PermissionDeniedError("Authentication required")
    return _project_read(project)


@router.patch("/projects/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> ProjectRead:
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return _project_read(project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> None:
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")
    await session.delete(project)
    await session.commit()


# ---- Faculty ---------------------------------------------------------------

@router.get("/faculty", response_model=list[FacultyRead])
async def list_faculty(
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[FacultyRead]:
    stmt = select(Faculty)
    if user is None:
        stmt = stmt.where(Faculty.is_public.is_(True))
    result = await session.execute(stmt.order_by(Faculty.full_name).limit(limit))
    return [FacultyRead.model_validate(f) for f in result.scalars()]


@router.post("/faculty", response_model=FacultyRead, status_code=status.HTTP_201_CREATED)
async def create_faculty(
    payload: FacultyCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> FacultyRead:
    faculty = Faculty(**payload.model_dump())
    session.add(faculty)
    await session.commit()
    await session.refresh(faculty)
    return FacultyRead.model_validate(faculty)


@router.get("/faculty/{faculty_id}", response_model=FacultyRead)
async def get_faculty(
    faculty_id: uuid.UUID,
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
) -> FacultyRead:
    faculty = await session.get(Faculty, faculty_id)
    if not faculty:
        raise NotFoundError("Faculty member not found")
    if user is None and not faculty.is_public:
        raise PermissionDeniedError("Authentication required")
    return FacultyRead.model_validate(faculty)


@router.patch("/faculty/{faculty_id}", response_model=FacultyRead)
async def update_faculty(
    faculty_id: uuid.UUID,
    payload: FacultyUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> FacultyRead:
    faculty = await session.get(Faculty, faculty_id)
    if not faculty:
        raise NotFoundError("Faculty member not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(faculty, field, value)
    session.add(faculty)
    await session.commit()
    await session.refresh(faculty)
    return FacultyRead.model_validate(faculty)


# ---- Staff -----------------------------------------------------------------

@router.get("/staff", response_model=list[StaffRead])
async def list_staff(
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[StaffRead]:
    result = await session.execute(select(Staff).order_by(Staff.full_name).limit(limit))
    return [StaffRead.model_validate(s) for s in result.scalars()]


@router.post("/staff", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
async def create_staff(
    payload: StaffCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> StaffRead:
    staff = Staff(**payload.model_dump())
    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    return StaffRead.model_validate(staff)


@router.get("/staff/{staff_id}", response_model=StaffRead)
async def get_staff(
    staff_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> StaffRead:
    staff = await session.get(Staff, staff_id)
    if not staff:
        raise NotFoundError("Staff member not found")
    return StaffRead.model_validate(staff)


@router.patch("/staff/{staff_id}", response_model=StaffRead)
async def update_staff(
    staff_id: uuid.UUID,
    payload: StaffUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> StaffRead:
    staff = await session.get(Staff, staff_id)
    if not staff:
        raise NotFoundError("Staff member not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(staff, field, value)
    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    return StaffRead.model_validate(staff)


# ---- IdeaLab Members -------------------------------------------------------

@router.get("/idealab-members", response_model=list[IdeaLabMemberRead])
async def list_idealab_members(
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[IdeaLabMemberRead]:
    result = await session.execute(
        select(IdeaLabMember).order_by(IdeaLabMember.full_name).limit(limit)
    )
    return [IdeaLabMemberRead.model_validate(m) for m in result.scalars()]


@router.post("/idealab-members", response_model=IdeaLabMemberRead, status_code=status.HTTP_201_CREATED)
async def create_idealab_member(
    payload: IdeaLabMemberCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> IdeaLabMemberRead:
    member = IdeaLabMember(**payload.model_dump())
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return IdeaLabMemberRead.model_validate(member)


@router.get("/idealab-members/{member_id}", response_model=IdeaLabMemberRead)
async def get_idealab_member(
    member_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> IdeaLabMemberRead:
    member = await session.get(IdeaLabMember, member_id)
    if not member:
        raise NotFoundError("IdeaLab member not found")
    return IdeaLabMemberRead.model_validate(member)


@router.patch("/idealab-members/{member_id}", response_model=IdeaLabMemberRead)
async def update_idealab_member(
    member_id: uuid.UUID,
    payload: IdeaLabMemberUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> IdeaLabMemberRead:
    member = await session.get(IdeaLabMember, member_id)
    if not member:
        raise NotFoundError("IdeaLab member not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return IdeaLabMemberRead.model_validate(member)


# ---- Students --------------------------------------------------------------

@router.get("/students", response_model=list[StudentRead])
async def list_students(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[StudentRead]:
    result = await session.execute(select(Student).order_by(Student.full_name).limit(limit))
    return [StudentRead.model_validate(s) for s in result.scalars()]


@router.post("/students", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> StudentRead:
    student = Student(**payload.model_dump())
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return StudentRead.model_validate(student)


@router.get("/students/{student_id}", response_model=StudentRead)
async def get_student(
    student_id: uuid.UUID,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> StudentRead:
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundError("Student not found")
    return StudentRead.model_validate(student)


@router.patch("/students/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: uuid.UUID,
    payload: StudentUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> StudentRead:
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundError("Student not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return StudentRead.model_validate(student)


# ---- Equipment -------------------------------------------------------------

@router.get("/equipment", response_model=list[EquipmentRead])
async def list_equipment(
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[EquipmentRead]:
    stmt = select(Equipment).where(Equipment.is_active.is_(True))
    result = await session.execute(stmt.order_by(Equipment.name).limit(limit))
    return [EquipmentRead.model_validate(e) for e in result.scalars()]


@router.post("/equipment", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    payload: EquipmentCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> EquipmentRead:
    equipment = Equipment(**payload.model_dump())
    session.add(equipment)
    await session.commit()
    await session.refresh(equipment)
    return EquipmentRead.model_validate(equipment)


@router.get("/equipment/{equipment_id}", response_model=EquipmentRead)
async def get_equipment(
    equipment_id: uuid.UUID,
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
) -> EquipmentRead:
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise NotFoundError("Equipment not found")
    return EquipmentRead.model_validate(equipment)


@router.patch("/equipment/{equipment_id}", response_model=EquipmentRead)
async def update_equipment(
    equipment_id: uuid.UUID,
    payload: EquipmentUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> EquipmentRead:
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise NotFoundError("Equipment not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(equipment, field, value)
    session.add(equipment)
    await session.commit()
    await session.refresh(equipment)
    return EquipmentRead.model_validate(equipment)


# ---- Equipment Bookings -----------------------------------------------------

@router.post("/equipment/{equipment_id}/bookings", response_model=EquipmentBookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    equipment_id: uuid.UUID,
    payload: EquipmentBookingCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> EquipmentBookingRead:
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise NotFoundError("Equipment not found")
    booking = EquipmentBooking(
        equipment_id=equipment_id,
        user_id=user.id,
        **payload.model_dump(),
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return EquipmentBookingRead.model_validate(booking)


@router.get("/bookings", response_model=list[EquipmentBookingRead])
async def list_bookings(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[EquipmentBookingRead]:
    result = await session.execute(select(EquipmentBooking))
    return [EquipmentBookingRead.model_validate(b) for b in result.scalars()]


@router.patch("/bookings/{booking_id}", response_model=EquipmentBookingRead)
async def update_booking(
    booking_id: uuid.UUID,
    payload: EquipmentBookingUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> EquipmentBookingRead:
    booking = await session.get(EquipmentBooking, booking_id)
    if not booking:
        raise NotFoundError("Booking not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(booking, field, value)
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return EquipmentBookingRead.model_validate(booking)


# ---- Documents -------------------------------------------------------------

@router.get("/documents", response_model=list[DocumentRead])
async def list_documents(
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[DocumentRead]:
    stmt = select(Document)
    if user is None:
        stmt = stmt.where(Document.access_level == AccessLevel.PUBLIC)
    result = await session.execute(stmt.order_by(Document.created_at.desc()).limit(limit))
    return [DocumentRead.model_validate(d) for d in result.scalars()]


@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> DocumentRead:
    doc = Document(**payload.model_dump())
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentRead.model_validate(doc)


@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: uuid.UUID,
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
) -> DocumentRead:
    doc = await session.get(Document, document_id)
    if not doc:
        raise NotFoundError("Document not found")
    if user is None and doc.access_level != AccessLevel.PUBLIC:
        raise PermissionDeniedError("Authentication required")
    return DocumentRead.model_validate(doc)


@router.patch("/documents/{document_id}", response_model=DocumentRead)
async def update_document(
    document_id: uuid.UUID,
    payload: DocumentUpdate,
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> DocumentRead:
    doc = await session.get(Document, document_id)
    if not doc:
        raise NotFoundError("Document not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentRead.model_validate(doc)


# ---- Departments -----------------------------------------------------------

@router.get("/departments")
async def list_departments(
    user: User = CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    result = await session.execute(select(Department).order_by(Department.name))
    deps = list(result.scalars())
    return [
        {
            "id": str(d.id),
            "name": d.name,
            "code": d.code,
            "description": d.description,
            "building": d.building,
            "email": d.email,
            "phone": d.phone,
            "website": d.website,
            "access_level": d.access_level,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in deps
    ]


# ---- Search -----------------------------------------------------------------

@router.get("/search")
async def search_all(
    q: str = Query(min_length=1, max_length=200),
    user: User | None = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=20, ge=1, le=50),
) -> list[dict]:
    """Simple keyword search across events, projects, faculty, equipment."""
    results: list[dict] = []
    pattern = f"%{q}%"

    for model, label, name_field in [
        (Event, "event", "title"),
        (Project, "project", "title"),
        (Faculty, "faculty", "full_name"),
        (Equipment, "equipment", "name"),
        (IdeaLabMember, "member", "full_name"),
    ]:
        stmt = select(model).where(
            getattr(model, name_field).ilike(pattern)
        ).limit(limit)
        result = await session.execute(stmt)
        for row in result.scalars():
            title = getattr(row, name_field, "")
            results.append({"type": label, "id": str(row.id), "title": title})

    return results
