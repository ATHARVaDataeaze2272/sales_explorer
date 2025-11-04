"""
Matching Engine with Semantic Similarity and Business Rules
Efficiently matches clients to prospects using vector search and constraints
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, func, text
import numpy as np
from datetime import datetime
import logging

from database.models import (
    ClientUploadProfile,
    ClientEmbedding,
    Prospects,
    ProspectEmbedding,
    ClientProspectMatch
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Core matching engine using pgvector for semantic similarity search.
    """
    
    def __init__(
        self,
        db: Session,
        max_matches: int = 15,
        max_per_company: int = 3,
        min_score: float = 0.5,
        weight_job_title: float = 0.40,
        weight_business_area: float = 0.30,
        weight_activity: float = 0.30
    ):
        self.db = db
        self.max_matches = max_matches
        self.max_per_company = max_per_company
        self.min_score = min_score
        self.weights = {
            'job_title': weight_job_title,
            'business_area': weight_business_area,
            'activity': weight_activity
        }
    

    def match_client_to_prospects(
    self, 
    client_id: int,
    store_results: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Match a single client to top prospects in two separate pools.
        
        Args:
            client_id: Client profile ID
            store_results: Store matches in database
            
        Returns:
            Dictionary with 'priority_matches' and 'discovery_matches'
        """
        try:
            # Get client profile and embeddings (same as before)
            client = self.db.query(ClientUploadProfile).filter(
                ClientUploadProfile.id == client_id
            ).first()
            
            if not client:
                logger.error(f"Client profile {client_id} not found")
                raise ValueError(f"Client profile {client_id} not found")
            
            client_emb = self.db.query(ClientEmbedding).filter(
                ClientEmbedding.profile_id == client_id
            ).first()
            
            if not client_emb:
                logger.error(f"No embeddings found for client {client_id}")
                raise ValueError(f"No embeddings found for client {client_id}")
            
            # Validate embeddings
            if (client_emb.job_title_embedding is None or 
                client_emb.business_area_embedding is None or 
                client_emb.activity_embedding is None):
                logger.error(f"Incomplete embeddings for client {client_id}")
                raise ValueError(f"Incomplete embeddings for client {client_id}")
            
            # Build separate candidate pools
            pools = self._build_candidate_pool(client)
            
            if not pools['priority'] and not pools['discovery']:
                logger.warning(f"No candidates found for client {client_id}")
                return {'priority_matches': [], 'discovery_matches': []}
            
            logger.info(f"Processing priority pool: {len(pools['priority'])}, discovery pool: {len(pools['discovery'])}")
            
            # Match priority pool - ONLY job title, NO threshold, ALL prospects
            # Match priority pool
            priority_matches = []
            if pools['priority']:
                priority_matches = self._vector_similarity_search(
                    client_emb=client_emb,
                    candidate_ids=pools['priority'],
                    apply_threshold=False,
                    use_job_title_only=True
                )
                priority_matches = self._apply_business_rules(
                    matches=priority_matches,
                    client=client,
                    max_matches=len(pools['priority']),  # Return ALL priority matches
                    match_type='priority'
                )

            # Match discovery pool
            discovery_matches = []
            if pools['discovery']:
                discovery_matches = self._vector_similarity_search(
                    client_emb=client_emb,
                    candidate_ids=pools['discovery'],
                    apply_threshold=True,
                    use_job_title_only=False
                )
                discovery_matches = self._apply_business_rules(
                    matches=discovery_matches,
                    client=client,
                    max_matches=self.max_matches,
                    match_type='discovery'
                )
            
            logger.info(f"Priority matches: {len(priority_matches)}, Discovery matches: {len(discovery_matches)}")
            
            # Store results with match_type
            if store_results:
                try:
                    self._store_matches(client_id, priority_matches, match_type='priority')
                    self._store_matches(client_id, discovery_matches, match_type='discovery')
                    logger.info(f"Stored matches for client {client_id}")
                except Exception as e:
                    logger.error(f"Error storing matches: {e}")
            
            return {
                'priority_matches': priority_matches,
                'discovery_matches': discovery_matches
            }
            
        except ValueError as ve:
            logger.error(f"Validation error for client {client_id}: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error matching client {client_id}: {e}", exc_info=True)
            raise RuntimeError(f"Error matching client {client_id}: {str(e)}") from e


  

    # def _build_candidate_pool(self, client: ClientUploadProfile) -> Dict[str, List[int]]:
    #     """
    #     Filter prospects into two separate pools with enhanced fuzzy matching.
    #     Now matches individual words from company names.
    #     """
    #     target_companies = self._extract_target_companies(client)
        
    #     # Base query with exclusions
    #     base_query = self.db.query(Prospects.id, Prospects.company_name)
        
    #     # Exclude companies
    #     if client.companies_to_exclude:
    #         excluded_companies = [
    #             c.strip().lower() 
    #             for c in client.companies_to_exclude.split(',')
    #             if c.strip()
    #         ]
    #         if excluded_companies:
    #             base_query = base_query.filter(
    #                 not_(func.lower(Prospects.company_name).in_(excluded_companies))
    #             )
        
    #     # Exclude countries/regions/continents
    #     if client.excluded_countries:
    #         excluded_locations = [
    #             c.strip().lower() 
    #             for c in client.excluded_countries.split(',')
    #             if c.strip()
    #         ]
    #         if excluded_locations:
    #             base_query = base_query.filter(
    #                 and_(
    #                     not_(func.lower(Prospects.country).in_(excluded_locations)),
    #                     not_(func.lower(Prospects.region).in_(excluded_locations)),
    #                     not_(func.lower(Prospects.continent).in_(excluded_locations))
    #                 )
    #             )
        
    #     # Must have embeddings
    #     base_query = base_query.join(
    #         ProspectEmbedding,
    #         ProspectEmbedding.prospect_id == Prospects.id
    #     )
        
    #     all_candidates = base_query.all()
        
    #     # Enhanced fuzzy matching with word-level matching
    #     priority_pool = []
    #     priority_companies = []
        
    #     if target_companies:
    #         like_conditions = []
            
    #         for company in target_companies:
    #             # Original full name LIKE match
    #             like_conditions.append(func.lower(Prospects.company_name).like(f"%{company}%"))
                
    #             # NEW: Split company name into words and match individually
    #             words = [w.strip() for w in company.split() if len(w.strip()) > 2]  # Skip short words
    #             for word in words:
    #                 like_conditions.append(func.lower(Prospects.company_name).like(f"%{word}%"))
            
    #         if like_conditions:
    #             priority_candidates = base_query.filter(or_(*like_conditions)).all()
    #             priority_pool = [p[0] for p in priority_candidates]
    #             priority_companies = [p[1].strip().lower() if p[1] else "" for p in priority_candidates]
            
    #         # Discovery pool - exclude priority matches
    #         priority_ids = set(priority_pool)
    #         discovery_pool = [c[0] for c in all_candidates if c[0] not in priority_ids]
    #     else:
    #         priority_pool = []
    #         priority_companies = []
    #         discovery_pool = [c[0] for c in all_candidates]
        
    #     logger.info(f"Priority pool: {len(priority_pool)} candidates (word-level matching enabled)")
    #     logger.info(f"Discovery pool: {len(discovery_pool)} candidates")
        
    #     with open('debug_pools.txt', 'a') as f:
    #         f.write(f"Client {client.id} - Priority: {priority_companies}\n  Discovery: {len(discovery_pool)} prospects\n")
        
    #     return {
    #         'priority': priority_pool,
    #         'discovery': discovery_pool
    #     }



    def _build_candidate_pool(self, client: ClientUploadProfile) -> Dict[str, List[int]]:
        """
        Filter prospects into two separate pools:
        - priority_pool: Companies client explicitly wants to meet (with fuzzy matching)
        - discovery_pool: Other companies matching business logic
        
        Args:
            client: Client profile
            
        Returns:
            Dictionary with 'priority' and 'discovery' prospect ID lists
        """
        # Get target companies
        target_companies = self._extract_target_companies(client)
        
        # Base query with exclusions
        base_query = self.db.query(Prospects.id, Prospects.company_name)
        
        # Exclude companies
        if client.companies_to_exclude:
            excluded_companies = [
                c.strip().lower() 
                for c in client.companies_to_exclude.split(',')
                if c.strip()
            ]
            if excluded_companies:
                base_query = base_query.filter(
                    not_(func.lower(Prospects.company_name).in_(excluded_companies))
                )
        
        # UPDATED: Exclude countries - check against country, region, AND continent
        if client.excluded_countries:
            excluded_locations = [
                c.strip().lower() 
                for c in client.excluded_countries.split(',')
                if c.strip()
            ]
            if excluded_locations:
                base_query = base_query.filter(
                    and_(
                        not_(func.lower(Prospects.country).in_(excluded_locations)),
                        not_(func.lower(Prospects.region).in_(excluded_locations)),
                        not_(func.lower(Prospects.continent).in_(excluded_locations))
                    )
                )
        
        # Must have embeddings
        base_query = base_query.join(
            ProspectEmbedding,
            ProspectEmbedding.prospect_id == Prospects.id
        )
        
        # Get all eligible candidates
        all_candidates = base_query.all()
        
        # Separate into two pools with fuzzy matching
        priority_pool = []
        discovery_pool = []
        priority_companies = []
        
        if target_companies:
            # Build OR conditions for LIKE matching (SQL-based fuzzy matching)
            priority_query = base_query
            like_conditions = []
            for company in target_companies:
                like_conditions.append(func.lower(Prospects.company_name).like(f"%{company}%"))
            
            priority_candidates = priority_query.filter(or_(*like_conditions)).all()
            priority_pool = [p[0] for p in priority_candidates]
            priority_companies = [p[1].strip().lower() if p[1] else "" for p in priority_candidates]
            
            # Discovery pool - exclude priority matches
            priority_ids = set(priority_pool)
            discovery_pool = [c[0] for c in all_candidates if c[0] not in priority_ids]
        else:
            # No target companies, all go to discovery pool
            priority_pool = []
            priority_companies = []
            discovery_pool = [c[0] for c in all_candidates]
        
        logger.info(f"Priority pool: {len(priority_pool)} candidates, Discovery pool: {len(discovery_pool)} candidates")
        with open('debug_pools.txt', 'a') as f:
            f.write(f"Client {client.id} - Priority: {priority_companies}\n  Discovery: {len(discovery_pool)} prospects\n")
        
        return {
            'priority': priority_pool,
            'discovery': discovery_pool
        }
    





    def _remove_duplicate_prospects(self, matches: List[Dict]) -> List[Dict]:
        """
        Remove duplicate prospects from matches list.
        UPDATED: Now checks both prospect_id AND reg_id for duplicates
        Keeps the match with the highest overall score for each unique prospect.
        
        Args:
            matches: List of match dictionaries
            
        Returns:
            Deduplicated list of matches
        """
        from database.models import Prospects
        
        # Get all prospect IDs from matches
        prospect_ids = [m['prospect_id'] for m in matches]
        
        # Fetch prospects with their reg_id
        prospects = self.db.query(Prospects).filter(
            Prospects.id.in_(prospect_ids)
        ).all()
        
        # Create mapping of prospect_id to reg_id
        prospect_to_reg_id = {p.id: p.reg_id for p in prospects}
        
        # Group matches by both prospect_id and reg_id
        unique_matches = {}
        
        for match in matches:
            prospect_id = match['prospect_id']
            reg_id = prospect_to_reg_id.get(prospect_id, None)
            
            # Create a unique key based on both prospect_id and reg_id
            # If reg_id exists and is not empty, use it as primary identifier
            if reg_id and reg_id.strip():
                unique_key = f"reg_id:{reg_id}"
            else:
                # Fallback to prospect_id if reg_id is missing
                unique_key = f"prospect_id:{prospect_id}"
            
            if unique_key not in unique_matches:
                unique_matches[unique_key] = match
            else:
                # Keep the match with higher overall score
                if match['overall_score'] > unique_matches[unique_key]['overall_score']:
                    unique_matches[unique_key] = match
        
        # Convert back to list and sort by overall score
        deduplicated = list(unique_matches.values())
        deduplicated.sort(key=lambda x: x['overall_score'], reverse=True)
        
        removed_count = len(matches) - len(deduplicated)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate prospects (checked both prospect_id and reg_id)")
        
        return deduplicated

    
   


    def _vector_similarity_search(
    self,
    client_emb: ClientEmbedding,
    candidate_ids: List[int],
    apply_threshold: bool = True,
    use_job_title_only: bool = False  # New parameter
) -> List[Dict]:
        """
        Perform semantic similarity search using pgvector.
        
        Args:
            client_emb: Client embeddings
            candidate_ids: Filtered prospect IDs
            apply_threshold: Whether to apply minimum score threshold
            use_job_title_only: If True, only use job title for scoring (for priority pool)
            
        Returns:
            List of scored matches
        """
        if not candidate_ids:
            return []
        
        # Convert embeddings to lists and then to string format for PostgreSQL
        try:
            job_emb = client_emb.job_title_embedding
            business_emb = client_emb.business_area_embedding
            activity_emb = client_emb.activity_embedding
            
            # Convert numpy arrays to lists if they aren't already
            if hasattr(job_emb, 'tolist'):
                job_emb = job_emb.tolist()
            if hasattr(business_emb, 'tolist'):
                business_emb = business_emb.tolist()
            if hasattr(activity_emb, 'tolist'):
                activity_emb = activity_emb.tolist()
            
            # Convert lists to PostgreSQL vector string format: '[val1,val2,val3,...]'
            job_emb_str = '[' + ','.join(map(str, job_emb)) + ']'
            business_emb_str = '[' + ','.join(map(str, business_emb)) + ']'
            activity_emb_str = '[' + ','.join(map(str, activity_emb)) + ']'
            
        except Exception as e:
            logger.error(f"Error converting embeddings: {e}")
            return []
        
        # Choose query based on scoring method
        if use_job_title_only:
            # Priority pool: Only job title scoring
            query = text("""
                WITH similarity_scores AS (
                    SELECT 
                        pe.prospect_id,
                        1 - (pe.job_title_embedding <=> CAST(:job_emb AS vector)) AS job_score,
                        1 - (pe.business_area_embedding <=> CAST(:business_emb AS vector)) AS business_score,
                        1 - (pe.expertise_embedding <=> CAST(:activity_emb AS vector)) AS activity_score
                    FROM prospect_embeddings pe
                    WHERE pe.prospect_id = ANY(:candidate_ids)
                        AND pe.job_title_embedding IS NOT NULL
                        AND pe.business_area_embedding IS NOT NULL
                        AND pe.expertise_embedding IS NOT NULL
                )
                SELECT 
                    prospect_id,
                    job_score,
                    business_score,
                    activity_score,
                    job_score AS overall_score
                FROM similarity_scores
                ORDER BY job_score DESC
            """)
        else:
            # Discovery pool: Weighted scoring with threshold
            query = text("""
                WITH similarity_scores AS (
                    SELECT 
                        pe.prospect_id,
                        1 - (pe.job_title_embedding <=> CAST(:job_emb AS vector)) AS job_score,
                        1 - (pe.business_area_embedding <=> CAST(:business_emb AS vector)) AS business_score,
                        1 - (pe.expertise_embedding <=> CAST(:activity_emb AS vector)) AS activity_score
                    FROM prospect_embeddings pe
                    WHERE pe.prospect_id = ANY(:candidate_ids)
                        AND pe.job_title_embedding IS NOT NULL
                        AND pe.business_area_embedding IS NOT NULL
                        AND pe.expertise_embedding IS NOT NULL
                )
                SELECT 
                    prospect_id,
                    job_score,
                    business_score,
                    activity_score,
                    (:w_job * job_score + :w_business * business_score + :w_activity * activity_score) AS overall_score
                FROM similarity_scores
                WHERE (:apply_threshold = false OR (:w_job * job_score + :w_business * business_score + :w_activity * activity_score) >= :min_score)
                ORDER BY overall_score DESC
            """)
        
        try:
            results = self.db.execute(
                query,
                {
                    'job_emb': job_emb_str,
                    'business_emb': business_emb_str,
                    'activity_emb': activity_emb_str,
                    'candidate_ids': candidate_ids,
                    'w_job': self.weights['job_title'],
                    'w_business': self.weights['business_area'],
                    'w_activity': self.weights['activity'],
                    'min_score': self.min_score,
                    'apply_threshold': apply_threshold 
                }
            ).fetchall()
            
            matches = []
            for row in results:
                matches.append({
                    'prospect_id': row[0],
                    'job_title_score': float(row[1]),
                    'business_area_score': float(row[2]),
                    'activity_score': float(row[3]),
                    'overall_score': float(row[4])
                })
            
            logger.info(f"Found {len(matches)} matches (job_title_only: {use_job_title_only})")
            return matches
            
        except Exception as e:
            logger.error(f"Error executing vector similarity search: {e}")
            return []
   





    def _apply_business_rules(
    self,
    matches: List[Dict],
    client: ClientUploadProfile,
    max_matches: int = None,
    match_type: str = 'discovery'
) -> List[Dict]:
        """
        Apply business constraints and rank final matches.
        UPDATED: Now limits how many times a prospect can be matched (max 3 clients per prospect)
        
        Args:
            matches: Raw similarity matches
            client: Client profile
            max_matches: Override default max_matches
            match_type: 'priority' or 'discovery'
            
        Returns:
            Final ranked matches
        """
        if not matches:
            return []
        
        if max_matches is None:
            max_matches = self.max_matches
        
        # STEP 1: Remove duplicate prospects (keep highest score)
        matches = self._remove_duplicate_prospects(matches)
        
        # Load full prospect details
        prospect_ids = [m['prospect_id'] for m in matches]
        prospects = self.db.query(Prospects).filter(
            Prospects.id.in_(prospect_ids)
        ).all()
        
        prospects_dict = {p.id: p for p in prospects}
        
        # Enrich matches
        enriched_matches = []
        for match in matches:
            prospect = prospects_dict.get(match['prospect_id'])
            if prospect:
                match['prospect'] = prospect
                match['company_name'] = prospect.company_name
                match['match_type'] = match_type
                enriched_matches.append(match)
        
        # STEP 2: Check how many times each prospect has been matched already
        prospect_match_counts = {}
        for prospect_id in prospect_ids:
            count = self.db.query(ClientProspectMatch).filter(
                ClientProspectMatch.prospect_id == prospect_id
            ).count()
            prospect_match_counts[prospect_id] = count
        
        # STEP 3: Filter prospects that have reached max matches (3 clients)
        MAX_CLIENTS_PER_PROSPECT = 3
        
        filtered_matches = []
        for match in sorted(enriched_matches, key=lambda x: x['overall_score'], reverse=True):
            prospect_id = match['prospect_id']
            
            # Skip if prospect already matched to 3 or more clients
            if prospect_match_counts.get(prospect_id, 0) >= MAX_CLIENTS_PER_PROSPECT:
                logger.debug(f"Skipping prospect {prospect_id} - already matched to {prospect_match_counts[prospect_id]} clients")
                continue
            
            filtered_matches.append(match)
            
            # Stop when we reach max_matches for this client
            if len(filtered_matches) >= max_matches:
                break
        
        # Add rankings
        for rank, match in enumerate(filtered_matches, start=1):
            match['match_rank'] = rank
        
        logger.info(f"Final {match_type} matches: {len(filtered_matches)} (removed {len(enriched_matches) - len(filtered_matches)} over-matched prospects)")
        return filtered_matches[:max_matches]
    
   

    def _store_matches(self, client_id: int, matches: List[Dict], match_type: str = 'discovery'):
        """
        Store match results in database with match type.
        Handles overlapping prospects between priority and discovery pools.
        
        Args:
            client_id: Client profile ID
            matches: List of match dictionaries
            match_type: 'priority' or 'discovery'
        """
        if not matches:
            return
        
        prospect_ids_to_insert = [match['prospect_id'] for match in matches]
        
        # Delete existing matches of this type for this client
        self.db.query(ClientProspectMatch).filter(
            and_(
                ClientProspectMatch.client_profile_id == client_id,
                ClientProspectMatch.match_type == match_type
            )
        ).delete()
        
        # CRITICAL FIX: If storing priority matches, also delete these prospects 
        # from discovery pool to avoid duplicates (priority takes precedence)
        if match_type == 'priority':
            self.db.query(ClientProspectMatch).filter(
                and_(
                    ClientProspectMatch.client_profile_id == client_id,
                    ClientProspectMatch.prospect_id.in_(prospect_ids_to_insert),
                    ClientProspectMatch.match_type == 'discovery'
                )
            ).delete()
            logger.info(f"Removed {len(prospect_ids_to_insert)} prospects from discovery pool to avoid duplicates")
        
        # If storing discovery matches, exclude any prospects that exist in priority pool
        if match_type == 'discovery':
            existing_priority_prospects = self.db.query(ClientProspectMatch.prospect_id).filter(
                and_(
                    ClientProspectMatch.client_profile_id == client_id,
                    ClientProspectMatch.match_type == 'priority'
                )
            ).all()
            
            existing_priority_ids = {p[0] for p in existing_priority_prospects}
            
            # Filter out matches that are already in priority pool
            matches = [m for m in matches if m['prospect_id'] not in existing_priority_ids]
            
            if len(existing_priority_ids) > 0:
                logger.info(f"Filtered out {len(prospect_ids_to_insert) - len(matches)} discovery matches that exist in priority pool")
        
        # Commit deletions before insertions
        self.db.commit()
        
        # Insert new matches
        for match in matches:
            match_record = ClientProspectMatch(
                client_profile_id=client_id,
                prospect_id=match['prospect_id'],
                job_title_score=match['job_title_score'],
                business_area_score=match['business_area_score'],
                activity_score=match['activity_score'],
                overall_score=match['overall_score'],
                match_rank=match['match_rank'],
                match_type=match_type,
                status='pending'
            )
            self.db.add(match_record)
        
        try:
            self.db.commit()
            logger.info(f"Successfully stored {len(matches)} {match_type} matches for client {client_id}")
        except Exception as e:
            logger.error(f"Error committing matches: {e}")
            self.db.rollback()
            raise



    def match_all_clients(self) -> Dict:
        """
        Run matching for all clients with embeddings.
        
        Returns:
            Summary statistics
        """
        clients = self.db.query(ClientUploadProfile).join(
            ClientEmbedding,
            ClientEmbedding.profile_id == ClientUploadProfile.id
        ).all()
        
        total_clients = len(clients)
        total_priority_matches = 0
        total_discovery_matches = 0
        errors = 0
        
        logger.info(f"Starting matching for {total_clients} clients")
        
        for client in clients:
            try:
                result = self.match_client_to_prospects(client.id, store_results=True)
                # FIXED: Handle dictionary structure
                total_priority_matches += len(result.get('priority_matches', []))
                total_discovery_matches += len(result.get('discovery_matches', []))
            except Exception as e:
                logger.error(f"Error matching client {client.id}: {e}")
                errors += 1
        
        total_matches = total_priority_matches + total_discovery_matches
        
        result = {
            'total_clients': total_clients,
            'total_matches': total_matches,
            'priority_matches': total_priority_matches,
            'discovery_matches': total_discovery_matches,
            'average_matches_per_client': total_matches / total_clients if total_clients > 0 else 0,
            'errors': errors
        }
        
        logger.info(f"Matching complete: {result}")
        return result
    
    def get_client_matches(
        self,
        client_id: int,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve stored matches for a client.
        
        Args:
            client_id: Client profile ID
            limit: Maximum number of results
            
        Returns:
            List of match dictionaries with prospect details
        """
        query = self.db.query(ClientProspectMatch).filter(
            ClientProspectMatch.client_profile_id == client_id
        ).order_by(ClientProspectMatch.match_rank)
        
        if limit:
            query = query.limit(limit)
        
        matches = query.all()
        
        # Enrich with prospect details
        result = []
        for match in matches:
            prospect = self.db.query(Prospects).filter(
                Prospects.id == match.prospect_id
            ).first()
            
            if prospect:
                result.append({
                    'match_id': match.id,
                    'prospect_id': match.prospect_id,
                    'prospect_name': f"{prospect.first_name or ''} {prospect.last_name or ''}".strip(),
                    'job_title': prospect.job_title,
                    'company_name': prospect.company_name,
                    'country': prospect.country,
                    'email': prospect.attendee_email,
                    'job_title_score': float(match.job_title_score) if match.job_title_score else 0,
                    'business_area_score': float(match.business_area_score) if match.business_area_score else 0,
                    'activity_score': float(match.activity_score) if match.activity_score else 0,
                    'overall_score': float(match.overall_score),
                    'match_rank': match.match_rank,
                    'status': match.status,
                    'matched_at': match.matched_at.isoformat() if match.matched_at else None
                })
        
        return result
    


    def _extract_target_companies(self, client: ClientUploadProfile) -> List[str]:
        """
        Extract list of target company names from client profile.
        
        Args:
            client: Client profile
            
        Returns:
            List of normalized company names (lowercase, stripped)
        """
        target_companies = []
        
        # Get companies from ClientCompany relationship
        if hasattr(client, 'companies') and client.companies:
            for company in client.companies:
                if company.company_name:
                    target_companies.append(company.company_name.strip().lower())
        
        logger.info(f"Found {len(target_companies)} target companies for client {client.id}")
        return target_companies


class MatchingStats:
    """Utility class for matching statistics."""
    
    @staticmethod
    def get_summary(db: Session) -> Dict:
        """Get overall matching statistics."""
        total_matches = db.query(ClientProspectMatch).count()
        
        avg_score = db.query(func.avg(ClientProspectMatch.overall_score)).scalar()
        
        clients_with_matches = db.query(
            func.count(func.distinct(ClientProspectMatch.client_profile_id))
        ).scalar()
        
        status_counts = db.query(
            ClientProspectMatch.status,
            func.count(ClientProspectMatch.id)
        ).group_by(ClientProspectMatch.status).all()
        
        return {
            'total_matches': total_matches,
            'average_score': float(avg_score) if avg_score else 0,
            'clients_with_matches': clients_with_matches,
            'status_breakdown': {status: count for status, count in status_counts}
        }