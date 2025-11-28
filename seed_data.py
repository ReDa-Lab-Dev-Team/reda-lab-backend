from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine
from app.models.lab_entities import *
from app.models.user import User
from datetime import datetime, timedelta
from app.utils.auth import get_password_hash
import random

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                email="admin@lab.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created: admin / admin123")
        
        # Create sample team members
        team_members = [
            TeamMember(
                name="Dr. Jane Smith",
                position="Principal Investigator",
                bio="PhD in Computer Science, specializing in AI research",
                email="jane.smith@lab.com",
                photo_url="https://via.placeholder.com/150",
                is_active=True
            ),
            TeamMember(
                name="Dr. John Doe",
                position="Senior Researcher",
                bio="Expert in machine learning and data science",
                email="john.doe@lab.com",
                photo_url="https://via.placeholder.com/150",
                is_active=True
            ),
            TeamMember(
                name="Alice Johnson",
                position="Research Assistant",
                bio="PhD candidate in artificial intelligence",
                email="alice.johnson@lab.com",
                photo_url="https://via.placeholder.com/150",
                is_active=True
            ),
            TeamMember(
                name="Bob Wilson",
                position="Postdoctoral Researcher",
                bio="Specializes in deep learning applications",
                email="bob.wilson@lab.com",
                photo_url="https://via.placeholder.com/150",
                is_active=True
            )
        ]
        
        for member in team_members:
            existing = db.query(TeamMember).filter(TeamMember.email == member.email).first()
            if not existing:
                db.add(member)
        
        db.commit()
        
        # Get team members for relationships
        all_members = db.query(TeamMember).all()
        
        # Create sample projects
        projects = [
            ResearchProject(
                title="AI-Powered Medical Diagnosis",
                description="Developing AI models for early detection of medical conditions",
                start_date=datetime.now() - timedelta(days=365),
                end_date=datetime.now() + timedelta(days=365),
                status="active",
                funding_source="National Science Foundation",
                budget=500000
            ),
            ResearchProject(
                title="Natural Language Processing for Legal Documents",
                description="Building NLP systems to analyze and summarize legal documents",
                start_date=datetime.now() - timedelta(days=180),
                end_date=datetime.now() + timedelta(days=180),
                status="active",
                funding_source="Legal Tech Foundation",
                budget=250000
            ),
            ResearchProject(
                title="Quantum Computing Applications",
                description="Exploring quantum algorithms for optimization problems",
                start_date=datetime.now() - timedelta(days=730),
                end_date=datetime.now() - timedelta(days=30),
                status="completed",
                funding_source="Department of Energy",
                budget=750000
            )
        ]
        
        for project in projects:
            existing = db.query(ResearchProject).filter(ResearchProject.title == project.title).first()
            if not existing:
                db.add(project)
        
        db.commit()
        
        # Create sample publications
        publications = [
            Publication(
                title="Deep Learning Approaches for Medical Image Analysis",
                abstract="This paper presents novel deep learning architectures for medical image segmentation...",
                journal="Journal of Medical AI",
                publication_date=datetime.now() - timedelta(days=30),
                doi="10.1016/j.medai.2023.01.001",
                is_published=True
            ),
            Publication(
                title="Transformer Models for Legal Document Summarization",
                abstract="We propose a novel transformer-based approach for legal document summarization...",
                journal="AI and Law Review",
                publication_date=datetime.now() - timedelta(days=60),
                doi="10.1016/j.lawai.2023.02.001",
                is_published=True
            ),
            Publication(
                title="Quantum Algorithm Optimization",
                abstract="This research explores optimization techniques for quantum algorithms...",
                journal="Quantum Computing Journal",
                publication_date=datetime.now() - timedelta(days=120),
                doi="10.1016/j.quantum.2023.03.001",
                is_published=True
            )
        ]
        
        for pub in publications:
            existing = db.query(Publication).filter(Publication.title == pub.title).first()
            if not existing:
                db.add(pub)
        
        db.commit()
        
        # Assign authors to publications and contributors to projects
        all_projects = db.query(ResearchProject).all()
        all_publications = db.query(Publication).all()
        
        # Randomly assign team members to projects and publications
        for i, project in enumerate(all_projects):
            contributors = random.sample(all_members, min(2, len(all_members)))
            for member in contributors:
                if member not in project.contributors:
                    project.contributors.append(member)
        
        for i, publication in enumerate(all_publications):
            authors = random.sample(all_members, min(3, len(all_members)))
            for member in authors:
                if member not in publication.authors:
                    publication.authors.append(member)
        
        db.commit()
        
        # Create sample events
        events = [
            Event(
                title="AI in Healthcare Conference",
                description="Annual conference on artificial intelligence applications in healthcare",
                start_datetime=datetime.now() + timedelta(days=30),
                end_datetime=datetime.now() + timedelta(days=32),
                location="San Francisco, CA",
                event_type="conference"
            ),
            Event(
                title="NLP Workshop Series",
                description="Monthly workshop on natural language processing techniques",
                start_datetime=datetime.now() + timedelta(days=15),
                end_datetime=datetime.now() + timedelta(days=15, hours=4),
                location="Online",
                event_type="workshop"
            ),
            Event(
                title="Quantum Computing Seminar",
                description="Seminar on recent advances in quantum computing",
                start_datetime=datetime.now() - timedelta(days=10),
                end_datetime=datetime.now() - timedelta(days=10, hours=2),
                location="MIT Campus",
                event_type="seminar",
                is_active=False
            )
        ]
        
        for event in events:
            existing = db.query(Event).filter(Event.title == event.title).first()
            if not existing:
                db.add(event)
        
        db.commit()
        
        # Create sample news
        news_items = [
            News(
                title="Lab Receives Major Grant for AI Research",
                content="The lab has been awarded a $2M grant from the National Science Foundation...",
                published_date=datetime.now() - timedelta(days=5)
            ),
            News(
                title="New Publication in Top Journal",
                content="Our research on medical AI has been published in Nature Medicine...",
                published_date=datetime.now() - timedelta(days=10)
            ),
            News(
                title="Team Member Awarded Fellowship",
                content="Dr. Jane Smith has received a prestigious research fellowship...",
                published_date=datetime.now() - timedelta(days=15)
            )
        ]
        
        for news in news_items:
            existing = db.query(News).filter(News.title == news.title).first()
            if not existing:
                news.created_by = admin_user.id
                db.add(news)
        
        db.commit()
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()