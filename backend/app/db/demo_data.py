"""Demo data loader for first-run setup.

Populates the database with sample departments, faculty, students, events,
projects, equipment, and documents so a fresh instance is immediately
usable for development and demos. Idempotent — safe to re-run.
"""
from __future__ import annotations

import asyncio
import hashlib
import textwrap
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.bootstrap import bootstrap_database
from app.db.session import get_engine, get_session_factory
from app.models.content import Event, Project
from app.models.equipment import Equipment
from app.models.enums import AccessLevel, DocumentType, EventKind, EventStatus
from app.models.knowledge import Document
from app.models.org import Department
from app.models.people import Faculty, IdeaLabMember, Staff, Student

_DEMO_SEED = """\
IdeaLab|The campus innovation lab where students build real projects.|Building A, Ground Floor|idealab@college.edu|+1-555-0100|https://idealab.local|public
Computer Science|The CS department with a focus on AI and software engineering.|Building B, 2nd Floor|cs@college.edu|+1-555-0101|https://cs.college.edu|internal
Electrical Engineering|Electrical and Electronics Engineering department|Building C|ee@college.edu|+1-555-0102|https://ee.college.edu|internal
"""

_FACULTY = [
    ("Dr. Alice Chen", "acl@college.edu", "CL-001", "Professor", "Machine Learning, NLP",
     "Dr. Alice leads the AI research group.", "Office B-204",
     "https://cs.college.edu/alice", True),
    ("Dr. Bob Kumar", "bk@college.edu", "CS-002", "Associate Professor", "Web Systems, Databases",
     "Specialises in distributed systems and PostgreSQL.", "Office B-305",
     "https://cs.college.edu/bob", False),
]

_STUDENTS = [
    ("Riya Patel", "rp@student.college.edu", "STU-001", "Computer Science", 3),
    ("Arjun Mehta", "am@student.college.edu", "STU-002", "Computer Science", 2),
    ("Priya Sharma", "ps@student.college.edu", "STU-003", "Electrical Engineering", 4),
]

_MEMBERSHIPS = [
    ("Divya R", "divya@idealab.local", "Full-Stack Lead", "Web Team", "Frontend + backend web projects.",
     "React, TypeScript, FastAPI, Docker", "2024-01-15T00:00:00Z"),
    ("Kunal K", "kunal@idealab.local", "VR Specialist", "XR Lab", "Building immersive experiences.",
     "Unity, C#, OpenCV", "2024-02-20T00:00:00Z"),
]

_PROJECTS = [
    ("Smart Attendance System", "IoT-based attendance with face recognition.",
     "active", "IoT, Computer Vision", "Python, OpenCV, Flask", True),
    ("MentorMatch", "Matching students with mentors based on interests.",
     "active", "EdTech", "React, FastAPI, PostgreSQL", True),
    ("Campus Recycling App", "Mobile app for tracking recycling bins.",
     "planning", "Mobile", "Flutter, Firebase", False),
]

_EVENTS = [
    ("IdeaLab Hackathon 2024", "Annual hackathon with 100+ participants.",
     EventKind.HACKATHON, "Main Auditorium", 100, "Dr. Alice Chen",
     datetime(2024, 12, 15, 9, 0, tzinfo=timezone.utc),
     datetime(2024, 12, 15, 18, 0, tzinfo=timezone.utc)),
    ("Intro to Machine Learning", "Workshop on ML fundamentals.",
     EventKind.WORKSHOP, "Lab B-101", 30, "Dr. Bob Kumar",
     datetime(2024, 11, 20, 14, 0, tzinfo=timezone.utc),
     datetime(2024, 11, 20, 16, 0, tzinfo=timezone.utc)),
]

_EQUIPMENT = [
    ("3D Printer Pro", "MakerBot", "High-resolution 3D printer", None, "SN-3DP-001",
     "Lab B-102", "available", 2),
    ("Oscilloscope DSO-5072", None, "Digital oscilloscope, 70MHz", None, "SN-OSC-002",
     "EEE Lab", "available", 5),
    ("VR Headset Quest 3", None, "Meta Quest 3 for XR projects", None, "SN-VR-003",
     "XR Lab", "available", 3),
]

_STAFF = [
    ("Meera Nair", "meera@college.edu", "STF-001", "Lab Technician",
     "Manages lab equipment and inventory.", "IT Support"),
    ("Rohit S", "rs@college.edu", "STF-002", "Administrative Assistant",
     None, "Front Desk"),
]


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


async def load_demo_data(session: AsyncSession) -> dict[str, int]:
    """Insert demo data if the tables are empty. Returns counts of inserted rows."""
    counts: dict[str, int] = {}

    # --- Departments ---
    dept_count = await session.scalar(select(func.count(Department.id)))
    if not dept_count:
        for line in _DEMO_SEED.strip().split("\n"):
            parts = [p.strip() for p in line.split("|")]
            name, desc, building, email, phone, website, access_str = (
                parts + [None] * 7
            )[:7]
            dept = Department(
                name=name,
                code=name[:3].upper(),
                description=desc,
                building=building,
                email=email,
                phone=phone,
                website=website,
                access_level=access_str or "public",
            )
            session.add(dept)
        counts["departments"] = len(_DEMO_SEED.strip().split("\n"))
        await session.flush()

    # Fetch departments for references
    dept_result = await session.execute(select(Department))
    departments: dict[str, Department] = {d.name: d for d in dept_result.scalars()}
    cs_dept = next((d for d in departments.values() if "Computer" in (d.name or "")), None)
    ee_dept = next((d for d in departments.values() if "Electrical" in (d.name or "")), None)
    idealab_dept = next((d for d in departments.values() if "IdeaLab" in (d.name or "")), None)

    # --- Staff ---
    staff_count = await session.scalar(select(func.count(Staff.id)))
    if not staff_count:
        for name, email, code, desig, resp, dept_hint in _STAFF:
            dept = cs_dept if dept_hint and "IT" in dept_hint else idealab_dept
            staff = Staff(
                full_name=name,
                email=email,
                employee_code=code,
                designation=desig,
                responsibilities=resp,
                department_id=dept.id if dept else None,
                access_level=AccessLevel.INTERNAL,
            )
            session.add(staff)
        counts["staff"] = len(_STAFF)
        await session.flush()

    # --- Faculty ---
    f_len = await session.scalar(select(func.count(Faculty.id)))
    if not f_len:
        for name, email, code, desig, spec, bio, office, photo, is_hod in _FACULTY:
            faculty = Faculty(
                full_name=name,
                email=email,
                employee_code=code,
                department_id=cs_dept.id if cs_dept else None,
                designation=desig,
                specialization=spec,
                bio=bio,
                office_location=office,
                photo_url=photo,
                is_hod=is_hod,
                is_public=True,
                access_level=AccessLevel.PUBLIC if is_hod else AccessLevel.INTERNAL,
            )
            session.add(faculty)
        counts["faculty"] = len(_FACULTY)
        await session.flush()

    # --- Students ---
    s_len = await session.scalar(select(func.count(Student.id)))
    if not s_len:
        for name, email, code, program, year in _STUDENTS:
            student = Student(
                full_name=name,
                email=email,
                roll_number=code,
                department_id=cs_dept.id if "Computer" in program else ee_dept.id,
                program=program,
                year=year,
                access_level=AccessLevel.RESTRICTED,
            )
            session.add(student)
        counts["students"] = len(_STUDENTS)
        await session.flush()

    # --- IdeaLab Members ---
    m_len = await session.scalar(select(func.count(IdeaLabMember.id)))
    if not m_len:
        for name, email, role_title, team, bio, skills, joined in _MEMBERSHIPS:
            member = IdeaLabMember(
                full_name=name,
                email=email,
                department_id=cs_dept.id if cs_dept else None,
                role_title=role_title,
                team=team,
                bio=bio,
                skills=skills,
                joined_at=datetime.fromisoformat(joined.replace("Z", "+00:00")) if joined else None,
                is_active=True,
                access_level=AccessLevel.INTERNAL,
            )
            session.add(member)
        counts["idealab_members"] = len(_MEMBERSHIPS)
        await session.flush()

    # --- Projects ---
    p_len = await session.scalar(select(func.count(Project.id)))
    if not p_len:
        for title, summary, status, domain, tech, published in _PROJECTS:
            project = Project(
                title=title,
                summary=summary,
                domain=domain,
                technologies=tech,
                status=status,
                is_active=True,
                is_published=published,
                access_level=AccessLevel.PUBLIC if published else AccessLevel.INTERNAL,
                started_at=datetime.now(timezone.utc) - timedelta(days=30),
            )
            session.add(project)
        counts["projects"] = len(_PROJECTS)
        await session.flush()

    # --- Events ---
    e_len = await session.scalar(select(func.count(Event.id)))
    if not e_len:
        for title, desc, kind, venue, cap, org, start, end in _EVENTS:
            event = Event(
                title=title,
                description=desc,
                kind=kind,
                venue=venue,
                capacity=cap,
                organizer=org,
                starts_at=start,
                ends_at=end,
                is_active=True,
                status=EventStatus.PUBLISHED,
                access_level=AccessLevel.PUBLIC,
                is_published=True,
            )
            session.add(event)
        counts["events"] = len(_EVENTS)
        await session.flush()

    # --- Equipment ---
    eq_len = await session.scalar(select(func.count(Equipment.id)))
    if not eq_len:
        for name, cat, desc, specs, serial, loc, status, qty in _EQUIPMENT:
            eq = Equipment(
                name=name,
                category=cat,
                description=desc,
                specifications=None if specs is None else {"notes": specs},
                serial_number=serial,
                location=loc,
                status=status,
                is_active=True,
                quantity=qty,
                access_level=AccessLevel.INTERNAL,
            )
            session.add(eq)
        counts["equipment"] = len(_EQUIPMENT)
        await session.flush()

    # --- Documents ---
    d_len = await session.scalar(select(func.count(Document.id)))
    if not d_len:
        doc_content = textwrap.dedent("""\
            The IdeaLab is a collaborative space for students and faculty to build,
            learn, and innovate. It provides equipment, mentorship, and events.
            Key initiatives include hackathons, mentorship programs, and research
            collaborations across departments.
        """)
        doc = Document(
            title="IdeaLab Overview",
            doc_type=DocumentType.OTHER,
            summary="General overview of the IdeaLab facility.",
            content_hash=_hash(doc_content),
            is_indexed=True,
            processing_status="indexed",
            access_level=AccessLevel.PUBLIC,
        )
        session.add(doc)
        counts["documents"] = 1
        await session.flush()

    await session.commit()
    return counts


async def _main() -> None:
    """CLI entry point to load demo data."""
    engine = get_engine()
    factory = get_session_factory()
    async with factory() as session:
        print("Bootstrapping roles and permissions...")
        result = await bootstrap_database(session)
        print(f"  {len(result['roles'])} roles, {len(result['permissions'])} permissions")
        print("Loading demo data...")
        counts = await load_demo_data(session)
        for k, v in counts.items():
            print(f"  {k}: {v} records")
        print("Done!")


if __name__ == "__main__":
    asyncio.run(_main())
