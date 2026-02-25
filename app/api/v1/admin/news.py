from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc

from app.config.database import get_db
from app.schemas.lab_entities import NewsCreate, NewsResponse, NewsUpdate
from app.models.lab_entities import News

router = APIRouter(prefix="/news", tags=["Admin - News"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[NewsResponse])
async def get_all_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_published: Optional[bool] = None,
    sort_by: str = Query("published_date", pattern="^(title|published_date|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    """Get all news articles with pagination and filters (Admin only)"""
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
    """Get a single news article by ID (Admin only)"""
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
    news: NewsCreate,
     db: Session = Depends(get_db)
     
):
    """Create a new news article (Admin only)"""
    try:
        current_admin = request.state.user
        db_news = News(**news.model_dump(exclude_unset=True), created_by=current_admin.id)
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
    news: NewsUpdate,
     db: Session = Depends(get_db)
     
):
    """Update an existing news article (Admin only)"""
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"News with id {news_id} not found"
        )
    
    try:
        for key, value in news.model_dump(exclude_unset=True).items():
            setattr(db_news, key, value)
        
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
     
) -> Dict[str, str]:
    """Delete a news article (Admin only)"""
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"News with id {news_id} not found"
        )
    
    try:
        db.delete(db_news)
        db.commit()
        return {"message": "News deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete news"
        )