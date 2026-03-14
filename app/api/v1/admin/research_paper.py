from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc
from app.config.database import get_db
from app.schemas.lab_entities import ResearchPaperCreate, ResearchPaperResponse, ResearchPaperUpdate
from app.models.lab_entities import ResearchPaper, PaperType
import os 
from app.config.config import settings
import shutil
from datetime import datetime
from app.utils.helper_functions import slugify
from app.services.public import UserService

router = APIRouter(prefix="/research-papers", tags=["Admin - Research Papers"])
service = UserService()

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[ResearchPaperResponse])
async def get_all_research_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    paper_type: Optional[PaperType] = None,
    is_published: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(title|published_date|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"), 
     db: Session = Depends(get_db)
     
):
    paper_type_value = paper_type.value if paper_type else None
    return await service.get_research_papers(skip, limit, search, paper_type_value, is_published, sort_by, order, db)

@router.get("/{paper_id}", response_model=ResearchPaperResponse)
async def get_research_paper(
    paper_id: int,
     db: Session = Depends(get_db)
     
):
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
    paper: ResearchPaperCreate = Depends(ResearchPaperCreate.as_form),
    pdf_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):      
    try:
        current_admin = request.state.user
        
        new_paper_data = paper.model_dump(exclude_unset=True)
        new_paper_data["slug"] = slugify(paper.title)
        
        existing_paper = db.query(ResearchPaper).filter(
            ResearchPaper.slug == new_paper_data["slug"]
        ).first()
        if existing_paper:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Research paper with the same title already exists"
            )
        
        #Handle PDF upload
        if pdf_url:
            # validate file type for PDF
            if pdf_url.content_type != "application/pdf":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Only PDF files are allowed"
                )

            # Create upload directory
            path = os.path.join(settings.upload_dir, "research_papers")
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                    
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = os.path.splitext(pdf_url.filename)[1]
            filename = f"{new_paper_data['slug']}_{timestamp}{file_ext}"
            file_location = os.path.join(path, filename)
            
            # Save file
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(pdf_url.file, buffer)
                
            # Store relative path in database
            relative_path = os.path.join('research_papers', filename)
            new_paper_data["pdf_url"] = relative_path
        
        db_paper = ResearchPaper(**new_paper_data, created_by=current_admin.id)
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
    paper: ResearchPaperUpdate = Depends(ResearchPaperUpdate.as_form),
    pdf_url: Optional[UploadFile] = File(None),
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
        update_data = paper.model_dump(exclude_unset=True, exclude_none=True)
        
        # Only update slug if title is provided and not None
        if "title" in update_data and update_data["title"]:
            new_slug = slugify(update_data["title"])
            
            # Check slug uniqueness (if changed)
            if new_slug != db_paper.slug:
                existing_paper = db.query(ResearchPaper).filter(
                    ResearchPaper.slug == new_slug,
                    ResearchPaper.id != paper_id
                ).first()
                
                if existing_paper:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Research paper with the same title already exists"
                    )
                update_data["slug"] = new_slug
        
        # Update only provided fields
        for key, value in update_data.items():
            setattr(db_paper, key, value)
        
        # Handle PDF upload
        if pdf_url:
            # Validate file type for PDF
            if pdf_url.content_type != "application/pdf":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Only PDF files are allowed"
                )
            
            try:
                # Delete old PDF if exists
                if db_paper.pdf_url:
                    old_pdf_path = os.path.join(settings.upload_dir, db_paper.pdf_url)
                    if os.path.exists(old_pdf_path):
                        try:
                            os.remove(old_pdf_path)
                        except Exception as e:
                            print(f"Warning: Could not delete old PDF: {e}")
                
                # Create upload directory
                path = os.path.join(settings.upload_dir, 'research_papers')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Create unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = os.path.splitext(pdf_url.filename)[1]
                filename = f"{db_paper.slug}_{timestamp}{file_ext}"
                file_location = os.path.join(path, filename)
                
                # Save file
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(pdf_url.file, buffer)
                
                # Store relative path
                relative_path = os.path.join('research_papers', filename)
                db_paper.pdf_url = relative_path
                
            except Exception as e:
                # Cleanup on error
                if 'file_location' in locals() and os.path.exists(file_location):
                    os.remove(file_location)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload PDF: {str(e)}"
                )
        
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
     
):
    db_paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not db_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Research paper with id {paper_id} not found"
        )
    
    try:
        # Delete associated PDF file if it exists
        if db_paper.pdf_url:
            pdf_path = os.path.join(settings.upload_dir, db_paper.pdf_url)
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception as e:
                    print(f"Warning: Could not delete PDF file: {e}")

        db.delete(db_paper)
        db.commit()
        return {"message": "Research paper deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete research paper"
        )