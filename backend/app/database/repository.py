# """
# Repository layer for database operations
# Provides clean interface for CRUD operations
# """

# from sqlalchemy.orm import Session
# from typing import List, Optional, Dict, Any
# from datetime import datetime
# import logging
# import hashlib

# from .models import (ProcessedDocument, 
#                     ClientCompany, 
#                     ProspectCompany, DocumentStatus,
#                     DocumentType, ClientUploadProfile, ProspectUploadProfile)

# log = logging.getLogger(__name__)


# class DocumentRepository:
#     """Repository for ProcessedDocument operations"""
    
#     @staticmethod
#     def create(
#         db: Session,
#         filename: str,
#         original_filename: str,
#         document_type: str,
#         file_size: int = None,
#         file_content: bytes = None,
#         excluded_pages: str = ""
#     ) -> ProcessedDocument:
#         """Create a new document record"""
        
#         # Calculate file hash if content provided
#         file_hash = None
#         if file_content:
#             file_hash = hashlib.sha256(file_content).hexdigest()
        
#         doc = ProcessedDocument(
#             filename=filename,
#             original_filename=original_filename,
#             document_type=DocumentType(document_type),
#             file_size=file_size,
#             file_hash=file_hash,
#             excluded_pages=excluded_pages,
#             status=DocumentStatus.PENDING,
#             uploaded_at=datetime.utcnow()
#         )
        
#         db.add(doc)
#         db.commit()
#         db.refresh(doc)
        
#         log.info(f"✅ Created document record: ID={doc.id}, filename={filename}")
#         return doc
    
#     @staticmethod
#     def update_processing_status(
#         db: Session,
#         document_id: int,
#         status: DocumentStatus,
#         **kwargs
#     ) -> Optional[ProcessedDocument]:
#         """Update document processing status and metadata"""
        
#         doc = db.query(ProcessedDocument).filter(ProcessedDocument.id == document_id).first()
#         if not doc:
#             log.warning(f"Document {document_id} not found")
#             return None
        
#         doc.status = status
        
#         # Update timestamps
#         if status == DocumentStatus.PROCESSING and not doc.processing_started_at:
#             doc.processing_started_at = datetime.utcnow()
#         elif status in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]:
#             doc.processing_completed_at = datetime.utcnow()
        
#         # Update optional fields
#         for key, value in kwargs.items():
#             if hasattr(doc, key):
#                 setattr(doc, key, value)
        
#         db.commit()
#         db.refresh(doc)
        
#         log.info(f"Updated document {document_id}: status={status}")
#         return doc
    
#     @staticmethod
#     def get_by_id(db: Session, document_id: int) -> Optional[ProcessedDocument]:
#         """Get document by ID"""
#         return db.query(ProcessedDocument).filter(ProcessedDocument.id == document_id).first()
    
#     @staticmethod
#     def get_by_hash(db: Session, file_hash: str) -> Optional[ProcessedDocument]:
#         """Find document by file hash (for deduplication)"""
#         return db.query(ProcessedDocument).filter(ProcessedDocument.file_hash == file_hash).first()
    
#     @staticmethod
#     def get_all(
#         db: Session,
#         document_type: Optional[str] = None,
#         status: Optional[str] = None,
#         limit: int = 100,
#         offset: int = 0
#     ) -> List[ProcessedDocument]:
#         """Get all documents with optional filters"""
        
#         query = db.query(ProcessedDocument)
        
#         if document_type:
#             query = query.filter(ProcessedDocument.document_type == DocumentType(document_type))
        
#         if status:
#             query = query.filter(ProcessedDocument.status == DocumentStatus(status))
        
#         query = query.order_by(ProcessedDocument.uploaded_at.desc())
#         query = query.limit(limit).offset(offset)
        
#         return query.all()
    
#     @staticmethod
#     def delete(db: Session, document_id: int) -> bool:
#         """Delete document and all related companies"""
#         doc = db.query(ProcessedDocument).filter(ProcessedDocument.id == document_id).first()
#         if not doc:
#             return False
        
#         db.delete(doc)
#         db.commit()
#         log.info(f"🗑️  Deleted document {document_id}")
#         return True
    

#     @staticmethod
#     def check_duplicate(db: Session, file_hash: str) -> Optional[ProcessedDocument]:
#         """Check if document with same hash already exists"""
#         return db.query(ProcessedDocument).filter(
#             ProcessedDocument.file_hash == file_hash,
#             ProcessedDocument.status == DocumentStatus.COMPLETED  # Only check successful uploads
#         ).first()

# class ClientCompanyRepository:
#     """Repository for ClientCompany operations"""
    
#     @staticmethod
#     def get_by_document(db: Session, document_id: int) -> List[ClientCompany]:
#         """Get all client companies for a document (through profile)"""
#         # First get the profile for this document
#         profile = db.query(ClientUploadProfile).filter(
#             ClientUploadProfile.document_id == document_id
#         ).first()
        
#         if not profile:
#             return []
        
#         # Then get companies for this profile
#         return db.query(ClientCompany).filter(
#             ClientCompany.profile_id == profile.id
#         ).all()
    
#     @staticmethod
#     def search(
#         db: Session,
#         company_name: Optional[str] = None,
#         country: Optional[str] = None,
#         limit: int = 100
#     ) -> List[ClientCompany]:
#         """Search client companies"""
        
#         query = db.query(ClientCompany)
        
#         if company_name:
#             query = query.filter(ClientCompany.company_name.ilike(f"%{company_name}%"))
        
#         if country:
#             query = query.filter(ClientCompany.country.ilike(f"%{country}%"))
        
#         return query.limit(limit).all()



# class ClientUploadProfileRepository:
#     """Repository for ClientUploadProfile operations"""
    
#     @staticmethod
#     def create(
#         db: Session,
#         document_id: int,
#         common_data: Dict[str, Any]
#     ) -> ClientUploadProfile:
#         """Create profile with common targeting data"""
#         profile = ClientUploadProfile(
#             document_id=document_id,
#             key_interests=common_data.get('Key_Interests', ''),
#             target_job_titles=common_data.get('Target_Job_Titles', []),
#             business_areas=common_data.get('Business_Areas', ''),
#             company_main_activities=common_data.get('Company_Main_Activities', ''),
#             companies_to_exclude=common_data.get('Companies_To_Exclude', ''),
#             excluded_countries=common_data.get('Excluded_Countries', '')
#         )
#         db.add(profile)
#         db.commit()
#         db.refresh(profile)
#         return profile


# class ProspectCompanyRepository:
#     """Repository for ProspectCompany operations"""
    
#     @staticmethod
#     def bulk_create(
#         db: Session,
#         profile_id: int,  # Changed from document_id to profile_id
#         companies_data: List[Dict[str, Any]]
#     ) -> List[ProspectCompany]:
#         """Create multiple prospect companies at once"""
        
#         companies = []
#         for data in companies_data:
#             company = ProspectCompany(
#                 profile_id=profile_id,  # Use profile_id instead
#                 reg_id=data.get('Reg ID', ''),
#                 reg_status=data.get('Reg Status', ''),
#                 create_account_date=data.get('Create Account Date'),
#                 first_name=data.get('First Name', ''),
#                 last_name=data.get('Last Name', ''),
#                 second_last_name=data.get('Second Last Name', ''),
#                 attendee_email=data.get('Attendee Email Address', ''),
#                 mobile=data.get('Mobile', ''),
#                 company_name=data.get('Company', ''),
#                 job_title=data.get('Job Title', ''),
#                 country=data.get('Country', ''),
#                 region=data.get('Region', ''),
#                 continent=data.get('Continent', ''),
#                 pass_type=data.get('Current and Latest Pass Type', ''),
#                 networking_show_me=data.get('Networking / Show Me', ''),
#                 enhanced_networking=data.get('Enhanced Networking', ''),
#                 job_function=data.get('Job function', ''),
#                 responsibility=data.get('Responsibility', ''),
#                 city=data.get('City', ''),
#                 source_file=data.get('source_file', '')
#             )
#             companies.append(company)
        
#         db.add_all(companies)
#         db.commit()
        
#         log.info(f"✅ Created {len(companies)} prospect companies for profile {profile_id}")
#         return companies
    
#     @staticmethod
#     def get_by_document(db: Session, document_id: int) -> List[ProspectCompany]:
#         """Get all prospect companies for a document"""
#         return db.query(ProspectCompany).filter(ProspectCompany.document_id == document_id).all()
    
#     @staticmethod
#     def search(
#         db: Session,
#         company_name: Optional[str] = None,
#         country: Optional[str] = None,
#         limit: int = 100
#     ) -> List[ProspectCompany]:
#         """Search prospect companies"""
        
#         query = db.query(ProspectCompany)
        
#         if company_name:
#             query = query.filter(ProspectCompany.company_name.ilike(f"%{company_name}%"))
        
#         if country:
#             query = query.filter(ProspectCompany.country.ilike(f"%{country}%"))
        
#         return query.limit(limit).all()
    


# class ProspectUploadProfileRepository:
#     """Repository for ProspectUploadProfile operations"""
    
#     @staticmethod
#     def create(
#         db: Session,
#         document_id: int,
#         common_data: Dict[str, Any]
#     ) -> ProspectUploadProfile:
#         """Create profile with common targeting data"""
#         profile = ProspectUploadProfile(
#             document_id=document_id,
#             key_interests=common_data.get('Key_Interests', ''),
#             target_job_titles=common_data.get('Target_Job_Titles', []),
#             business_areas=common_data.get('Business_Areas', ''),
#             company_main_activities=common_data.get('Company_Main_Activities', ''),
#             companies_to_exclude=common_data.get('Companies_To_Exclude', ''),
#             excluded_countries=common_data.get('Excluded_Countries', '')
#         )
#         db.add(profile)
#         db.commit()
#         db.refresh(profile)
#         return profile


# # Convenience function to get appropriate repository
# def get_company_repository(document_type: str):
#     """Get the correct repository based on document type"""
#     if document_type == "clients":
#         return ClientCompanyRepository
#     elif document_type == "prospects":
#         return ProspectCompanyRepository
#     else:
#         raise ValueError(f"Invalid document type: {document_type}")
    








from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import hashlib

from database.models import ClientEmbedding, ProspectEmbedding

from .models import (
    ProcessedDocument, 
    ClientCompany, 
    Prospects, 
    DocumentStatus,
    DocumentType, 
    ClientUploadProfile,
    ClientProspectMatch,
)

log = logging.getLogger(__name__)

class DocumentRepository:
    """Repository for ProcessedDocument operations"""
    
    @staticmethod
    def create(
        db: Session,
        filename: str,
        original_filename: str,
        document_type: str,
        file_size: int = None,
        file_content: bytes = None,
        excluded_pages: str = ""
    ) -> ProcessedDocument:
        """Create a new document record"""
        
        file_hash = None
        if file_content:
            file_hash = hashlib.sha256(file_content).hexdigest()
        
        doc = ProcessedDocument(
            filename=filename,
            original_filename=original_filename,
            document_type=DocumentType(document_type),
            file_size=file_size,
            file_hash=file_hash,
            excluded_pages=excluded_pages,
            status=DocumentStatus.PENDING,
            uploaded_at=datetime.utcnow()
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        log.info(f"✅ Created document record: ID={doc.id}, filename={filename}")
        return doc
    
    @staticmethod
    def update_processing_status(
        db: Session,
        document_id: int,
        status: DocumentStatus,
        **kwargs
    ) -> Optional[ProcessedDocument]:
        """Update document processing status and metadata"""
        
        doc = db.query(ProcessedDocument).filter(ProcessedDocument.id == document_id).first()
        if not doc:
            log.warning(f"Document {document_id} not found")
            return None
        
        doc.status = status
        
        if status == DocumentStatus.PROCESSING and not doc.processing_started_at:
            doc.processing_started_at = datetime.utcnow()
        elif status in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]:
            doc.processing_completed_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        db.commit()
        db.refresh(doc)
        
        log.info(f"Updated document {document_id}: status={status}")
        return doc
    
    @staticmethod
    def get_by_id(db: Session, document_id: int) -> Optional[ProcessedDocument]:
        """Get document by ID"""
        return db.query(ProcessedDocument).filter(ProcessedDocument.id == document_id).first()
    
    @staticmethod
    def get_by_hash(db: Session, file_hash: str) -> Optional[ProcessedDocument]:
        """Find document by file hash (for deduplication)"""
        return db.query(ProcessedDocument).filter(ProcessedDocument.file_hash == file_hash).first()
    
    @staticmethod
    def get_all(
        db: Session,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ProcessedDocument]:
        """Get all documents with optional filters"""
        
        query = db.query(ProcessedDocument)
        
        if document_type:
            query = query.filter(ProcessedDocument.document_type == DocumentType(document_type))
        
        if status:
            query = query.filter(ProcessedDocument.status == DocumentStatus(status))
        
        query = query.order_by(ProcessedDocument.uploaded_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @staticmethod
    @staticmethod
    def delete(db: Session, document_id: int) -> bool:
        """Delete a document and all associated records"""
        try:
            # FIX: Use ProcessedDocument instead of Document
            doc = db.query(ProcessedDocument).filter(ProcessedDocument.id == document_id).first()
            
            if not doc:
                return False
            
            # Get document type before deletion
            doc_type = doc.document_type
            
            # CRITICAL FIX: Delete embeddings BEFORE deleting profiles/prospects
            if doc_type == DocumentType.CLIENT:
                # Get profile first
                profile = db.query(ClientUploadProfile).filter(
                    ClientUploadProfile.document_id == document_id
                ).first()
                
                if profile:
                    # Delete embeddings first
                    db.query(ClientEmbedding).filter(
                        ClientEmbedding.profile_id == profile.id
                    ).delete(synchronize_session=False)
                    
                    # Delete matches
                    db.query(ClientProspectMatch).filter(
                        ClientProspectMatch.client_profile_id == profile.id
                    ).delete(synchronize_session=False)
                    
                    # Now delete profile (companies will cascade)
                    db.delete(profile)
            
            elif doc_type == DocumentType.PROSPECT:
                # Get all prospects for this document
                prospects = db.query(Prospects).filter(
                    Prospects.document_id == document_id
                ).all()
                
                prospect_ids = [p.id for p in prospects]
                
                if prospect_ids:
                    # Delete embeddings first
                    db.query(ProspectEmbedding).filter(
                        ProspectEmbedding.prospect_id.in_(prospect_ids)
                    ).delete(synchronize_session=False)
                    
                    # Delete matches
                    db.query(ClientProspectMatch).filter(
                        ClientProspectMatch.prospect_id.in_(prospect_ids)
                    ).delete(synchronize_session=False)
                    
                    # Now delete prospects
                    db.query(Prospects).filter(
                        Prospects.id.in_(prospect_ids)
                    ).delete(synchronize_session=False)
            
            # Finally delete the document
            db.delete(doc)
            db.commit()
            
            log.info(f"🗑️ Deleted document {document_id} and all associated records")
            return True
            
        except Exception as e:
            db.rollback()
            log.error(f"Failed to delete document {document_id}: {e}")
            raise
    
    @staticmethod
    def check_duplicate(db: Session, file_hash: str) -> Optional[ProcessedDocument]:
        """Check if document with same hash already exists"""
        return db.query(ProcessedDocument).filter(
            ProcessedDocument.file_hash == file_hash,
            ProcessedDocument.status == DocumentStatus.COMPLETED
        ).first()

class ClientCompanyRepository:
    """Repository for ClientCompany operations"""
    
    @staticmethod
    def get_by_document(db: Session, document_id: int) -> List[ClientCompany]:
        """Get all client companies for a document (through profile)"""
        profile = db.query(ClientUploadProfile).filter(
            ClientUploadProfile.document_id == document_id
        ).first()
        
        if not profile:
            return []
        
        return db.query(ClientCompany).filter(
            ClientCompany.profile_id == profile.id
        ).all()
    
    @staticmethod
    def search(
        db: Session,
        company_name: Optional[str] = None,
        country: Optional[str] = None,
        limit: int = 100
    ) -> List[ClientCompany]:
        """Search client companies"""
        
        query = db.query(ClientCompany)
        
        if company_name:
            query = query.filter(ClientCompany.company_name.ilike(f"%{company_name}%"))
        
        if country:
            query = query.filter(ClientCompany.country.ilike(f"%{country}%"))
        
        return query.limit(limit).all()
    
    @staticmethod
    def bulk_create(
        db: Session,
        profile_id: int,
        companies_data: List[Dict[str, Any]]
    ) -> List[ClientCompany]:
        """Create multiple client company records at once"""
        
        companies = []
        for data in companies_data:
            company = ClientCompany(
                profile_id=profile_id,
                company_name=data.get('Company_Name', ''),
                country=data.get('Country', ''),
                city=data.get('City', ''),
                source_file=data.get('source_file', '')
            )
            companies.append(company)
        
        db.add_all(companies)
        db.commit()
        
        log.info(f"✅ Created {len(companies)} client companies for profile {profile_id}")
        return companies

class ClientUploadProfileRepository:
    """Repository for ClientUploadProfile operations"""
    
    @staticmethod
    def create(
        db: Session,
        document_id: int,
        common_data: Dict[str, Any]
    ) -> ClientUploadProfile:
        """Create profile with common targeting data"""
        profile = ClientUploadProfile(
            document_id=document_id,
            key_interests=common_data.get('Key_Interests', ''),
            target_job_titles=common_data.get('Target_Job_Titles', []),
            business_areas=common_data.get('Business_Areas', ''),
            company_main_activities=common_data.get('Company_Main_Activities', ''),
            companies_to_exclude=common_data.get('Companies_To_Exclude', ''),
            excluded_countries=common_data.get('Excluded_Countries', '')
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

class ProspectRepository:
    """Repository for Prospects operations"""
    
    @staticmethod
    def bulk_create(
        db: Session,
        document_id: int,
        prospects_data: List[Dict[str, Any]]
    ) -> List[Prospects]:
        """Create multiple prospect records at once"""
        
        prospects = []
        for data in prospects_data:
            prospect = Prospects(
                document_id=document_id,
                reg_id=data.get('Reg ID', ''),
                reg_status=data.get('Reg Status', ''),
                create_account_date=data.get('Create Account Date'),
                first_name=data.get('First Name', ''),
                last_name=data.get('Last Name', ''),
                second_last_name=data.get('Second Last Name', ''),
                attendee_email=data.get('Attendee Email Address', ''),
                mobile=data.get('Mobile', ''),
                company_name=data.get('Company', ''),
                job_title=data.get('Job Title', ''),
                country=data.get('Country', ''),
                region=data.get('Region', ''),
                continent=data.get('Continent', ''),
                pass_type=data.get('Current and Latest Pass Type', ''),
                networking_show_me=data.get('Networking / Show Me', ''),
                enhanced_networking=data.get('Enhanced Networking', ''),
                job_function=data.get('Job function', ''),
                responsibility=data.get('Responsibility', ''),
                company_main_activity=data.get('Company Main Activity', ''),
                area_of_interests=data.get('Area of Interests', ''),
                source_file=data.get('source_file', '')
            )
            prospects.append(prospect)
        
        db.add_all(prospects)
        db.commit()
        
        log.info(f"✅ Created {len(prospects)} prospects for document {document_id}")
        return prospects
    
    @staticmethod
    def get_by_document(db: Session, document_id: int) -> List[Prospects]:
        """Get all prospects for a document"""
        return db.query(Prospects).filter(Prospects.document_id == document_id).all()
    
    @staticmethod
    def search(
        db: Session,
        company_name: Optional[str] = None,
        country: Optional[str] = None,
        limit: int = 100
    ) -> List[Prospects]:
        """Search prospects"""
        
        query = db.query(Prospects)
        
        if company_name:
            query = query.filter(Prospects.company_name.ilike(f"%{company_name}%"))
        
        if country:
            query = query.filter(Prospects.country.ilike(f"%{country}%"))
        
        return query.limit(limit).all()
    
    @staticmethod
    def update(
        db: Session,
        prospect_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Prospects]:
        """Update a prospect record"""
        prospect = db.query(Prospects).filter(Prospects.id == prospect_id).first()
        if not prospect:
            return None
        
        for key, value in update_data.items():
            if hasattr(prospect, key):
                setattr(prospect, key, value)
        
        prospect.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(prospect)
        log.info(f"Updated prospect {prospect_id}")
        return prospect
    
    @staticmethod
    def delete(db: Session, prospect_id: int) -> bool:
        """Delete a prospect record"""
        prospect = db.query(Prospects).filter(Prospects.id == prospect_id).first()
        if not prospect:
            return False
        
        db.delete(prospect)
        db.commit()
        log.info(f"🗑️ Deleted prospect {prospect_id}")
        return True

def get_company_repository(document_type: str):
    """Get the correct repository based on document type"""
    if document_type == "clients":
        return ClientCompanyRepository
    elif document_type == "prospects":
        return ProspectRepository
    else:
        raise ValueError(f"Invalid document type: {document_type}")