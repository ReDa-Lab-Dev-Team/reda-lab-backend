from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc

from app.config.database import get_db
from app.schemas.lab_entities import ResearchPaperCreate, ResearchPaperResponse, ResearchPaperUpdate
from app.models.lab_entities import ResearchPaper, PaperType

router = APIRouter(prefix="/research-papers", tags=["Admin - Research Papers"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[ResearchPaperResponse])
async def get_all_research_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    paper_type: Optional[PaperType] = None,
    is_published: Optional[bool] = None,
    sort_by: str = Query("published_date", pattern="^(title|published_date|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    """Get all research papers with pagination and filters (Admin only)"""
    try:
        query = db.query(ResearchPaper)

        if search:
            query = query.filter(
                or_(
                    ResearchPaper.title.ilike(f"%{search}%"),
                    ResearchPaper.abstract.ilike(f"%{search}%"),
                    ResearchPaper.authors.ilike(f"%{search}%")
                )
            )

        if paper_type:
            query = query.filter(ResearchPaper.paper_type == paper_type)

        if is_published is not None:
            query = query.filter(ResearchPaper.is_published == is_published)

        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(ResearchPaper, sort_by)))
        
        # Apply pagination
        papers = query.offset(skip).limit(limit).all()
        return papers
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve research papers"
        )

@router.get("/{paper_id}", response_model=ResearchPaperResponse)
async def get_research_paper(
    paper_id: int,
     db: Session = Depends(get_db)
     
):
    """Get a single research paper by ID (Admin only)"""
    db_paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not db_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with id {paper_id} not found"
        )
    return db_paper

# ========== CREATE OPERATION ==========

@router.post("", response_model=ResearchPaperResponse, status_code=status.HTTP_201_CREATED)
async def create_research_paper(
    request: Request,
    paper: ResearchPaperCreate,
     db: Session = Depends(get_db)
     
):
    """Create a new research paper (Admin only)"""
    try:
        current_admin = request.state.user
        db_paper = ResearchPaper(**paper.model_dump(exclude_unset=True), created_by=current_admin.id)
        db.add(db_paper)
        db.commit()
        db.refresh(db_paper)
        return db_paper
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Research paper already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{paper_id}", response_model=ResearchPaperResponse)
async def update_research_paper(
    paper_id: int,
    paper: ResearchPaperUpdate,
     db: Session = Depends(get_db)
     
):
    """Update an existing research paper (Admin only)"""
    db_paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not db_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Research paper with id {paper_id} not found"
        )
    
    try:
        for key, value in paper.model_dump(exclude_unset=True).items():
            setattr(db_paper, key, value)
        
        db.commit()
        db.refresh(db_paper)
        return db_paper
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Update violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== DELETE OPERATION ==========

@router.delete("/{paper_id}", status_code=status.HTTP_200_OK)
async def delete_research_paper(
    paper_id: int,
     db: Session = Depends(get_db)
     
) -> Dict[str, str]:
    """Delete a research paper (Admin only)"""
    db_paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not db_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Research paper with id {paper_id} not found"
        )
    
    try:
        db.delete(db_paper)
        db.commit()
        return {"message": "Research paper deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete research paper"
        )