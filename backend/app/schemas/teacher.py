from datetime import date
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal

# Base Teacher Schema
class ClassAssignment(BaseModel):
    class_name: Optional[str] = Field(None, alias='class')
    year: Optional[str] = None
    division: Optional[Literal['A', 'B', 'C', 'D']] = None

    # validation for requiring division if class is assigned is handled
    # in the TeacherCreate and TeacherUpdate models to avoid raising
    # during response serialization for existing records.

    class Config:
        allow_population_by_field_name = True


class TeacherBase(BaseModel):
    name: str
    address: str
    date_of_birth: date
    gender: str
    blood_group: str
    mobile_number: str
    aadhar_number: str
    religion: str
    caste: str
    rci_number: str
    rci_renewal_date: date
    qualifications_details: str
    category: str
    email: Optional[str] = None
    class_assignments: Optional[List[ClassAssignment]] = None

# Create Teacher Schema (used for input when creating)
class TeacherCreate(TeacherBase):
    from pydantic import root_validator

    @root_validator(pre=True)
    def validate_assignments(cls, values):
        assignments = values.get('class_assignments') or []
        for a in assignments:
            # allow both alias 'class' and field name 'class_name'
            class_present = bool(a.get('class') or a.get('class_name'))
            division_present = bool(a.get('division'))
            if class_present and not division_present:
                raise ValueError('Each class assignment must include a division when a class is specified')
        return values

# Update Teacher Schema (allows partial updates)
class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    mobile_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    religion: Optional[str] = None
    caste: Optional[str] = None
    rci_number: Optional[str] = None
    rci_renewal_date: Optional[date] = None
    qualifications_details: Optional[str] = None
    category: Optional[str] = None
    email: Optional[str] = None
    class_assignments: Optional[List[ClassAssignment]] = None

    from pydantic import root_validator

    @root_validator(pre=True)
    def validate_assignments(cls, values):
        assignments = values.get('class_assignments') or []
        for a in assignments:
            class_present = bool(a.get('class') or a.get('class_name'))
            division_present = bool(a.get('division'))
            if class_present and not division_present:
                raise ValueError('Each class assignment must include a division when a class is specified')
        return values

# Teacher Schema (used for responses)
class Teacher(TeacherBase):
    id: int

    class Config:
        from_attributes = True  # Allows model to read data from ORM objects 