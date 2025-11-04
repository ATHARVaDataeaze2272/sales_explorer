from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base 

class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentType(str, enum.Enum):
    """Document category"""
    CLIENT = "clients"
    PROSPECT = "prospects"

class ProcessedDocument(Base):
    """
    Tracks all processed documents with metadata
    """
    __tablename__ = 'processed_documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_size = Column(Integer)
    file_hash = Column(String(64), index=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    excluded_pages = Column(String(100))
    total_pages = Column(Integer)
    processed_pages = Column(Integer)
    ocr_cached = Column(Boolean, default=False)
    ocr_cache_path = Column(String(500))
    markdown_length = Column(Integer)
    entities_extracted = Column(Integer, default=0)
    extraction_success = Column(Boolean, default=False)
    excel_filename = Column(String(255))
    excel_path = Column(String(500))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    error_message = Column(String)
    
    client_profile = relationship("ClientUploadProfile", back_populates="document", uselist=False, cascade="all, delete-orphan")
    prospects = relationship("Prospects", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProcessedDocument(id={self.id}, filename='{self.filename}', type='{self.document_type}', status='{self.status}')>"

class ClientUploadProfile(Base):
    """Stores common targeting data for a client document upload"""
    __tablename__ = 'client_upload_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('processed_documents.id', ondelete='CASCADE'), unique=True, nullable=False)
    key_interests = Column(String)
    target_job_titles = Column(JSON)
    business_areas = Column(String)
    company_main_activities = Column(String)
    companies_to_exclude = Column(String)
    excluded_countries = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    document = relationship("ProcessedDocument", back_populates="client_profile")
    companies = relationship("ClientCompany", back_populates="profile", cascade="all, delete-orphan")

    embeddings = relationship("ClientEmbedding", back_populates="profile", uselist=False)
    matches = relationship("ClientProspectMatch", back_populates="client_profile")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'key_interests': self.key_interests,
            'target_job_titles': self.target_job_titles,
            'business_areas': self.business_areas,
            'company_main_activities': self.company_main_activities,
            'companies_to_exclude': self.companies_to_exclude,
            'excluded_countries': self.excluded_countries,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ClientCompany(Base):
    """Individual client companies - only unique data per company"""
    __tablename__ = 'client_companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('client_upload_profiles.id', ondelete='CASCADE'), nullable=False)
    company_name = Column(String(255), nullable=False)
    country = Column(String(100))
    city = Column(String(100))
    source_file = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile = relationship("ClientUploadProfile", back_populates="companies")
    
    def __repr__(self):
        return f"<ClientCompany(id={self.id}, name='{self.company_name}', country='{self.country}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'company_name': self.company_name,
            'country': self.country,
            'city': self.city,
            'source_file': self.source_file,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Prospects(Base):
    """Individual prospect records from Excel uploads"""
    __tablename__ = 'prospects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('processed_documents.id', ondelete='CASCADE'), nullable=False)
    reg_id = Column(String(100))
    reg_status = Column(String(50))
    create_account_date = Column(DateTime)
    first_name = Column(String(100))
    last_name = Column(String(100))
    second_last_name = Column(String(100))
    attendee_email = Column(String(255))
    mobile = Column(String(50))
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255))
    country = Column(String(100))
    region = Column(String(100))
    continent = Column(String(100))
    pass_type = Column(String(100))
    networking_show_me = Column(String(100))
    enhanced_networking = Column(String(100))
    job_function = Column(String(255))
    responsibility = Column(String(255))
    company_main_activity = Column(String)
    area_of_interests = Column(String)
    source_file = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    document = relationship("ProcessedDocument", back_populates="prospects")

    embeddings = relationship("ProspectEmbedding", back_populates="prospect", uselist=False)
    matches = relationship("ClientProspectMatch", back_populates="prospect")
    
    def __repr__(self):
        return f"<Prospects(id={self.id}, company_name='{self.company_name}', country='{self.country}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'reg_id': self.reg_id,
            'reg_status': self.reg_status,
            'create_account_date': self.create_account_date.isoformat() if self.create_account_date else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'second_last_name': self.second_last_name,
            'attendee_email': self.attendee_email,
            'mobile': self.mobile,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'country': self.country,
            'region': self.region,
            'continent': self.continent,
            'pass_type': self.pass_type,
            'networking_show_me': self.networking_show_me,
            'enhanced_networking': self.enhanced_networking,
            'job_function': self.job_function,
            'responsibility': self.responsibility,
            'company_main_activity': self.company_main_activity,
            'area_of_interests': self.area_of_interests,
            'source_file': self.source_file,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }






"""
SQLAlchemy Models for Vector Embeddings
Add these classes to your existing database/models.py file
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database.config import Base  # Your existing Base


class ClientEmbedding(Base):
    """
    Stores vector embeddings for client profiles.
    Each client has 3 embeddings (job title, business area, activity)
    """
    __tablename__ = "client_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("client_upload_profiles.id", ondelete="CASCADE"), 
                       nullable=False, unique=True)
    document_id = Column(Integer, nullable=True)
    
    # Vector embeddings (384 dimensions for all-MiniLM-L6-v2)
    job_title_embedding = Column(Vector(384))
    business_area_embedding = Column(Vector(384))
    activity_embedding = Column(Vector(384))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    profile = relationship("ClientUploadProfile", back_populates="embeddings")
    
    def __repr__(self):
        return f"<ClientEmbedding(profile_id={self.profile_id})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "document_id": self.document_id,
            "has_job_title_embedding": self.job_title_embedding is not None,
            "has_business_area_embedding": self.business_area_embedding is not None,
            "has_activity_embedding": self.activity_embedding is not None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProspectEmbedding(Base):
    """
    Stores vector embeddings for prospects.
    Each prospect has 3 embeddings (job title, business area, expertise)
    """
    __tablename__ = "prospect_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id", ondelete="CASCADE"), 
                        nullable=False, unique=True)
    document_id = Column(Integer, nullable=True)
    
    # Vector embeddings (384 dimensions)
    job_title_embedding = Column(Vector(384))
    business_area_embedding = Column(Vector(384))
    expertise_embedding = Column(Vector(384))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    prospect = relationship("Prospects", back_populates="embeddings")
    
    def __repr__(self):
        return f"<ProspectEmbedding(prospect_id={self.prospect_id})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "prospect_id": self.prospect_id,
            "document_id": self.document_id,
            "has_job_title_embedding": self.job_title_embedding is not None,
            "has_business_area_embedding": self.business_area_embedding is not None,
            "has_expertise_embedding": self.expertise_embedding is not None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ClientProspectMatch(Base):
    """
    Stores matching results between clients and prospects
    """
    __tablename__ = "client_prospect_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    client_profile_id = Column(Integer, ForeignKey("client_upload_profiles.id", ondelete="CASCADE"), 
                               nullable=False)
    prospect_id = Column(Integer, ForeignKey("prospects.id", ondelete="CASCADE"), 
                        nullable=False)
    
    # Similarity scores (0.0 to 1.0)
    job_title_score = Column(DECIMAL(5, 4))
    business_area_score = Column(DECIMAL(5, 4))
    activity_score = Column(DECIMAL(5, 4))
    overall_score = Column(DECIMAL(5, 4), nullable=False)
    
    # Match metadata
    match_rank = Column(Integer)  # 1-15 ranking for this client
    status = Column(String(50), default="pending")  # pending, contacted, meeting_scheduled, rejected
    notes = Column(Text)
    rejection_reason = Column(Text)
    
    match_type = Column(String(20), default="discovery")
    # Timestamps
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    contacted_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client_profile = relationship("ClientUploadProfile", back_populates="matches")
    prospect = relationship("Prospects", back_populates="matches")
    
    def __repr__(self):
        return f"<ClientProspectMatch(client={self.client_profile_id}, prospect={self.prospect_id}, score={self.overall_score})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "client_profile_id": self.client_profile_id,
            "prospect_id": self.prospect_id,
            "job_title_score": float(self.job_title_score) if self.job_title_score else None,
            "business_area_score": float(self.business_area_score) if self.business_area_score else None,
            "activity_score": float(self.activity_score) if self.activity_score else None,
            "overall_score": float(self.overall_score),
            "match_rank": self.match_rank,
            "status": self.status,
            "notes": self.notes,
            "rejection_reason": self.rejection_reason,
            "matched_at": self.matched_at.isoformat() if self.matched_at else None,
            "contacted_at": self.contacted_at.isoformat() if self.contacted_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class MatchingRun(Base):
    """
    Tracks when matching was executed and statistics
    """
    __tablename__ = "matching_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_type = Column(String(50))  # 'single_client', 'all_clients', 'manual'
    client_profile_id = Column(Integer, ForeignKey("client_upload_profiles.id", ondelete="SET NULL"))
    
    # Statistics
    total_clients_processed = Column(Integer)
    total_matches_created = Column(Integer)
    average_score = Column(DECIMAL(5, 4))
    
    # Status
    status = Column(String(50), default="running")  # running, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Configuration
    config = Column(JSON)
    
    # Relationships
    client_profile = relationship("ClientUploadProfile")
    
    def __repr__(self):
        return f"<MatchingRun(id={self.id}, type={self.run_type}, status={self.status})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "run_type": self.run_type,
            "client_profile_id": self.client_profile_id,
            "total_clients_processed": self.total_clients_processed,
            "total_matches_created": self.total_matches_created,
            "average_score": float(self.average_score) if self.average_score else None,
            "status": self.status,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "config": self.config
        }


