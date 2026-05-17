from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.crud.base import CRUDBase

class CRUDTeacher(CRUDBase[Teacher, TeacherCreate, TeacherUpdate]):
    def get_by_aadhar(self, db: Session, *, aadhar_number: str) -> Optional[Teacher]:
        return db.query(Teacher).filter(Teacher.aadhar_number == aadhar_number).first()
        
    def get_by_rci(self, db: Session, *, rci_number: str) -> Optional[Teacher]:
        return db.query(Teacher).filter(Teacher.rci_number == rci_number).first()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Teacher]:
        return db.query(Teacher).filter(Teacher.email == email).first()
teacher = CRUDTeacher(Teacher) 