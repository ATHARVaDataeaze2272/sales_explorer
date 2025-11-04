"""
Embedding Generation Service
Generates and stores vector embeddings for clients and prospects
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from tqdm import tqdm
import logging

from database.models import (
    ClientUploadProfile, 
    ClientEmbedding,
    Prospects,
    ProspectEmbedding
)
from matching.text_templates import (
    format_client_job_title_text,
    format_client_business_area_text,
    format_client_activity_text,
    format_prospect_job_title_text,
    format_prospect_business_area_text,
    format_prospect_expertise_text,
    validate_text_for_embedding
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and managing vector embeddings.
    Uses sentence-transformers for embedding generation.
    """
    
    def __init__(
        self, 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        batch_size: int = 32
    ):
        """
        Initialize the embedding service.
        
        Args:
            model_name: HuggingFace model identifier
            batch_size: Batch size for processing
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        logger.info(f"Embedding service initialized with model: {model_name}")
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model to save memory."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        return self._model
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats (384 dimensions) or None if invalid
        """
        if not validate_text_for_embedding(text):
            logger.warning(f"Text too short or invalid: {text[:50]}...")
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings (or None for invalid texts)
        """
        if not texts:
            return []
        
        # Filter valid texts and keep track of indices
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if validate_text_for_embedding(text):
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            logger.warning("No valid texts in batch")
            return [None] * len(texts)
        
        try:
            # Generate embeddings for valid texts
            embeddings = self.model.encode(
                valid_texts, 
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            # Map embeddings back to original positions
            result = [None] * len(texts)
            for i, embedding in zip(valid_indices, embeddings):
                result[i] = embedding.tolist()
            
            return result
        except Exception as e:
            logger.error(f"Error in batch embedding generation: {e}")
            return [None] * len(texts)
    
    # ============================================
    # CLIENT EMBEDDING GENERATION
    # ============================================
    
    def generate_client_embeddings(
        self, 
        db: Session, 
        profile_id: int,
        regenerate: bool = False
    ) -> bool:
        """
        Generate embeddings for a single client profile.
        
        Args:
            db: Database session
            profile_id: Client profile ID
            regenerate: Force regeneration even if exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if embeddings already exist
            if not regenerate:
                existing = db.query(ClientEmbedding).filter(
                    ClientEmbedding.profile_id == profile_id
                ).first()
                if existing:
                    logger.info(f"Embeddings already exist for client {profile_id}")
                    return True
            
            # Get client profile
            profile = db.query(ClientUploadProfile).filter(
                ClientUploadProfile.id == profile_id
            ).first()
            
            if not profile:
                logger.error(f"Client profile {profile_id} not found")
                return False
            
            # Generate text for each embedding type
            job_title_text = format_client_job_title_text(profile)
            business_area_text = format_client_business_area_text(profile)
            activity_text = format_client_activity_text(profile)
            
            # Generate embeddings
            job_title_emb = self.generate_embedding(job_title_text)
            business_area_emb = self.generate_embedding(business_area_text)
            activity_emb = self.generate_embedding(activity_text)
            
            # Check if at least one embedding was generated
            if not any([job_title_emb, business_area_emb, activity_emb]):
                logger.error(f"No valid embeddings generated for client {profile_id}")
                return False
            
            # Store or update embeddings
            if regenerate:
                # Delete existing
                db.query(ClientEmbedding).filter(
                    ClientEmbedding.profile_id == profile_id
                ).delete()
            
            embedding_record = ClientEmbedding(
                profile_id=profile_id,
                document_id=profile.document_id,
                job_title_embedding=job_title_emb,
                business_area_embedding=business_area_emb,
                activity_embedding=activity_emb
            )
            
            db.add(embedding_record)
            db.commit()
            
            logger.info(f"Successfully generated embeddings for client {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating embeddings for client {profile_id}: {e}")
            db.rollback()
            return False
    
    def generate_all_client_embeddings(
        self, 
        db: Session,
        regenerate: bool = False,
        show_progress: bool = True
    ) -> Dict:
        """
        Generate embeddings for all client profiles.
        
        Args:
            db: Database session
            regenerate: Force regeneration for all
            show_progress: Show progress bar
            
        Returns:
            Dictionary with statistics
        """
        logger.info("Starting bulk client embedding generation")
        
        # Get all client profiles
        profiles = db.query(ClientUploadProfile).all()
        total = len(profiles)
        
        if total == 0:
            logger.warning("No client profiles found")
            return {"success_count": 0, "error_count": 0, "total": 0}
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        # Process with progress bar
        iterator = tqdm(profiles, desc="Generating client embeddings") if show_progress else profiles
        
        for profile in iterator:
            try:
                # Check if already exists
                if not regenerate:
                    existing = db.query(ClientEmbedding).filter(
                        ClientEmbedding.profile_id == profile.id
                    ).first()
                    if existing:
                        skipped_count += 1
                        continue
                
                success = self.generate_client_embeddings(db, profile.id, regenerate)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing client {profile.id}: {e}")
                error_count += 1
        
        result = {
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "total": total
        }
        
        logger.info(f"Client embedding generation complete: {result}")
        return result
    
    # ============================================
    # PROSPECT EMBEDDING GENERATION
    # ============================================
    
    def generate_prospect_embeddings(
        self, 
        db: Session, 
        prospect_id: int,
        regenerate: bool = False
    ) -> bool:
        """
        Generate embeddings for a single prospect.
        
        Args:
            db: Database session
            prospect_id: Prospect ID
            regenerate: Force regeneration even if exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if embeddings already exist
            if not regenerate:
                existing = db.query(ProspectEmbedding).filter(
                    ProspectEmbedding.prospect_id == prospect_id
                ).first()
                if existing:
                    logger.info(f"Embeddings already exist for prospect {prospect_id}")
                    return True
            
            # Get prospect
            prospect = db.query(Prospects).filter(
                Prospects.id == prospect_id
            ).first()
            
            if not prospect:
                logger.error(f"Prospect {prospect_id} not found")
                return False
            
            # Generate text for each embedding type
            job_title_text = format_prospect_job_title_text(prospect)
            business_area_text = format_prospect_business_area_text(prospect)
            expertise_text = format_prospect_expertise_text(prospect)
            
            # Generate embeddings
            job_title_emb = self.generate_embedding(job_title_text)
            business_area_emb = self.generate_embedding(business_area_text)
            expertise_emb = self.generate_embedding(expertise_text)
            
            # Check if at least one embedding was generated
            if not any([job_title_emb, business_area_emb, expertise_emb]):
                logger.error(f"No valid embeddings generated for prospect {prospect_id}")
                return False
            
            # Store or update embeddings
            if regenerate:
                # Delete existing
                db.query(ProspectEmbedding).filter(
                    ProspectEmbedding.prospect_id == prospect_id
                ).delete()
            
            embedding_record = ProspectEmbedding(
                prospect_id=prospect_id,
                document_id=prospect.document_id,
                job_title_embedding=job_title_emb,
                business_area_embedding=business_area_emb,
                expertise_embedding=expertise_emb
            )
            
            db.add(embedding_record)
            db.commit()
            
            logger.info(f"Successfully generated embeddings for prospect {prospect_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating embeddings for prospect {prospect_id}: {e}")
            db.rollback()
            return False
    
    def generate_all_prospect_embeddings(
        self, 
        db: Session,
        regenerate: bool = False,
        show_progress: bool = True,
        batch_size: Optional[int] = None
    ) -> Dict:
        """
        Generate embeddings for all prospects.
        Uses batch processing for efficiency.
        
        Args:
            db: Database session
            regenerate: Force regeneration for all
            show_progress: Show progress bar
            batch_size: Override default batch size
            
        Returns:
            Dictionary with statistics
        """
        logger.info("Starting bulk prospect embedding generation")
        
        batch_size = batch_size or self.batch_size
        
        # Get all prospects
        prospects = db.query(Prospects).all()
        total = len(prospects)
        
        if total == 0:
            logger.warning("No prospects found")
            return {"success_count": 0, "error_count": 0, "total": 0}
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        # Process in batches
        iterator = tqdm(
            range(0, total, batch_size), 
            desc="Generating prospect embeddings"
        ) if show_progress else range(0, total, batch_size)
        
        for i in iterator:
            batch = prospects[i:i + batch_size]
            
            for prospect in batch:
                try:
                    # Check if already exists
                    if not regenerate:
                        existing = db.query(ProspectEmbedding).filter(
                            ProspectEmbedding.prospect_id == prospect.id
                        ).first()
                        if existing:
                            skipped_count += 1
                            continue
                    
                    success = self.generate_prospect_embeddings(db, prospect.id, regenerate)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing prospect {prospect.id}: {e}")
                    error_count += 1
        
        result = {
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "total": total
        }
        
        logger.info(f"Prospect embedding generation complete: {result}")
        return result
    
    # ============================================
    # UTILITY METHODS
    # ============================================
    
    def check_missing_embeddings(self, db: Session) -> Dict:
        """
        Check for profiles/prospects missing embeddings.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with missing counts
        """
        # Count clients
        total_clients = db.query(ClientUploadProfile).count()
        clients_with_embeddings = db.query(ClientEmbedding).count()
        
        # Count prospects
        total_prospects = db.query(Prospects).count()
        prospects_with_embeddings = db.query(ProspectEmbedding).count()
        
        return {
            "clients": {
                "total": total_clients,
                "with_embeddings": clients_with_embeddings,
                "missing": total_clients - clients_with_embeddings
            },
            "prospects": {
                "total": total_prospects,
                "with_embeddings": prospects_with_embeddings,
                "missing": total_prospects - prospects_with_embeddings
            }
        }
    
    def get_embedding_stats(self, db: Session) -> Dict:
        """
        Get statistics about embeddings.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        stats = self.check_missing_embeddings(db)
        
        # Add dimension info
        stats["embedding_dimensions"] = 384
        stats["model_name"] = self.model_name
        
        return stats
    
    def delete_all_embeddings(self, db: Session, confirm: bool = False) -> Dict:
        """
        Delete all embeddings (use with caution).
        
        Args:
            db: Database session
            confirm: Must be True to execute
            
        Returns:
            Dictionary with deletion counts
        """
        if not confirm:
            raise ValueError("Must set confirm=True to delete embeddings")
        
        client_count = db.query(ClientEmbedding).count()
        prospect_count = db.query(ProspectEmbedding).count()
        
        db.query(ClientEmbedding).delete()
        db.query(ProspectEmbedding).delete()
        db.commit()
        
        logger.warning(f"Deleted {client_count} client and {prospect_count} prospect embeddings")
        
        return {
            "client_embeddings_deleted": client_count,
            "prospect_embeddings_deleted": prospect_count
        }