from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.activity_logger import record_admin_activity
from app.database import SessionLocal
from app.model import Branch
from app.schema import BranchCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/branches")
def get_branches(db: Session = Depends(get_db)):
    return db.query(Branch).all()


@router.post("/branches")
def create_branch(data: BranchCreate, db: Session = Depends(get_db)):
    new_branch = Branch(name=data.name)

    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)

    record_admin_activity(
        db=db,
        action="Added Branch",
        target_type="Branch",
        target_name=new_branch.name
    )

    return {"message": "Branch added"}


@router.put("/branches/{branch_name}")
def update_branch(
    branch_name: str,
    data: BranchCreate,
    db: Session = Depends(get_db)
):
    branch = db.query(Branch).filter(
        Branch.name == branch_name
    ).first()

    if not branch:
        return {"error": "Branch not found"}

    old_branch_name = branch.name
    branch.name = data.name

    db.commit()

    record_admin_activity(
        db=db,
        action="Updated Branch",
        target_type="Branch",
        target_name=f"{old_branch_name} -> {data.name}"
    )

    return {"message": "Branch updated"}


@router.delete("/branches/{branch_name}")
def delete_branch(branch_name: str, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(
        Branch.name == branch_name
    ).first()

    if not branch:
        return {"error": "Branch not found"}

    deleted_branch_name = branch.name

    db.delete(branch)
    db.commit()

    record_admin_activity(
        db=db,
        action="Deleted Branch",
        target_type="Branch",
        target_name=deleted_branch_name
    )

    return {"message": "Branch deleted"}