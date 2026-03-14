from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc
import os
import shutil
from datetime import datetime

from app.config.database import get_db
from app.schemas.lab_entities import NewsCreate, NewsResponse, NewsUpdate
from app.models.lab_entities import News, ResearchClub
from app.utils.helper_functions import slugify
from app.config.config import settings

router = APIRouter(prefix="/news", tags=["Admin - News"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[NewsResponse])
async def get_all_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_published: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(title|published_date|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    try:
        query = db.query(News)

        if search:
            query = query.filter(
                or_(
                    News.title.ilike(f"%{search}%"),
                    News.summary.ilike(f"%{search}%"),
                    News.content.ilike(f"%{search}%")
                )
            )

        if is_published is not None:
            query = query.filter(News.is_published == is_published)

        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(News, sort_by)))
        
        # Apply pagination
        news = query.offset(skip).limit(limit).all()
        return news
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve news"
        )

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,
     db: Session = Depends(get_db)
     
):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"News with id {news_id} not found"
        )
    return db_news

# ========== CREATE OPERATION ==========

@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    request: Request,
    news: NewsCreate = Depends(NewsCreate.as_form),
    image_url: UploadFile = File(...),
     db: Session = Depends(get_db)
     
):
    try:
        current_admin = request.state.user
        
        # Convert Pydantic model to dictionary
        news_data = news.model_dump(exclude_unset=True)
        news_data['slug'] = slugify(news.title)
            
        existing_news = db.query(News).filter(
            News.slug == news_data['slug']
        ).first()
        if existing_news:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="News already exists"
            )
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if image_url.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
            )

        # Create upload directory
        path = os.path.join(settings.upload_dir, "news")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(image_url.filename)[1]
        filename = f"{news_data['slug']}_{timestamp}{file_ext}"
        file_location = os.path.join(path, filename)
        
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image_url.file, buffer)
            
        # Store relative path in database
        relative_path = os.path.join('news', filename)
        news_data["image_url"] = relative_path
        
        db_news = News(**news_data, created_by=current_admin.id)
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        return db_news
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="News already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news: NewsUpdate = Depends(NewsUpdate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"News with id {news_id} not found"
        )
    
    try:
        update_data = news.model_dump(exclude_unset=True, exclude_none=True)
        
        # Only update slug if title is provided and not None
        if "title" in update_data and update_data["title"]:
            new_slug = slugify(update_data["title"])
            
            # Check slug uniqueness (if changed)
            if new_slug != db_news.slug:
                existing_news = db.query(News).filter(
                    News.slug == new_slug,
                    News.id != news_id
                ).first()
                
                if existing_news:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"News with the same title already exists"
                    )
                update_data["slug"] = new_slug
        
        # Update only provided fields
        for key, value in update_data.items():
            setattr(db_news, key, value)
        
        # Handle image upload
        if image_url:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if image_url.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
                )
            
            try:
                # Delete old image if exists
                if db_news.image_url:
                    old_image_path = os.path.join(settings.upload_dir, db_news.image_url)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except Exception as e:
                            print(f"Warning: Could not delete old image: {e}")
                
                # Create upload directory
                path = os.path.join(settings.upload_dir, 'news')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Create unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = os.path.splitext(image_url.filename)[1]
                filename = f"{db_news.slug}_{timestamp}{file_ext}"
                file_location = os.path.join(path, filename)
                
                # Save file
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(image_url.file, buffer)
                
                # Store relative path
                relative_path = os.path.join('news', filename)
                db_news.image_url = relative_path
                
            except Exception as e:
                # Cleanup on error
                if 'file_location' in locals() and os.path.exists(file_location):
                    os.remove(file_location)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {str(e)}"
                )
        
        db.commit()
        db.refresh(db_news)
        return db_news
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

@router.delete("/{news_id}", status_code=status.HTTP_200_OK)
async def delete_news(
    news_id: int,
     db: Session = Depends(get_db)
     
):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"News with id {news_id} not found"
        )
    
    try:
        # Delete associated image if it exists
        if db_news.image_url:
            image_path = os.path.join(settings.upload_dir, db_news.image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Warning: Could not delete image file: {e}")

        db.delete(db_news)
        db.commit()
        return {"message": "News deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete news"
        )