# """
# FastAPI Endpoints for Client-Prospect Matching
# """

# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
# from sqlalchemy.orm import Session
# from pydantic import BaseModel, Field
# from typing import Optional, List
# import logging
# from datetime import datetime
# from database.config import get_db
# from database.models import (
#     ClientProspectMatch, 
#     ClientUploadProfile, 
#     Prospects
# )

# from database.config import get_db
# from matching.matching_engine import MatchingEngine, MatchingStats

# logger = logging.getLogger(__name__)

# router = APIRouter()


# # ============================================
# # REQUEST/RESPONSE MODELS
# # ============================================

# class MatchingRequest(BaseModel):
#     """Request model for matching"""
#     client_id: int = Field(..., description="Client profile ID to match")
#     max_matches: Optional[int] = Field(15, ge=1, le=50)
#     max_per_company: Optional[int] = Field(3, ge=1, le=10)
#     min_score: Optional[float] = Field(0.5, ge=0.0, le=1.0)
#     force_rematch: bool = Field(False, description="Regenerate even if matches exist")
#     weight_job_title: Optional[float] = Field(0.40, ge=0.0, le=1.0)
#     weight_business_area: Optional[float] = Field(0.30, ge=0.0, le=1.0)
#     weight_activity: Optional[float] = Field(0.30, ge=0.0, le=1.0)


# class MatchAllRequest(BaseModel):
#     """Request model for matching all clients"""
#     max_matches: Optional[int] = Field(15, ge=1, le=50)
#     max_per_company: Optional[int] = Field(3, ge=1, le=10)
#     min_score: Optional[float] = Field(0.5, ge=0.0, le=1.0)
#     force_rematch: bool = Field(False)


# class MatchResponse(BaseModel):
#     """Response model for matching result"""
#     success: bool
#     client_id: int
#     matches_found: int
#     average_score: Optional[float] = None
#     message: str


# class MatchResultItem(BaseModel):
#     """Single match result"""
#     match_id: int
#     prospect_id: int
#     prospect_name: str
#     job_title: Optional[str]
#     company_name: str
#     country: Optional[str]
#     email: Optional[str]
#     job_title_score: float
#     business_area_score: float
#     activity_score: float
#     overall_score: float
#     match_rank: int
#     status: str
#     matched_at: Optional[str]


# class MatchResultsResponse(BaseModel):
#     """Response model for match results"""
#     client_id: int
#     total_matches: int
#     matches: List[MatchResultItem]


# class UpdateMatchStatusRequest(BaseModel):
#     """Request to update match status"""
#     status: str = Field(..., description="Status: pending, contacted, meeting_scheduled, rejected")
#     notes: Optional[str] = None
#     rejection_reason: Optional[str] = None



# class ClientDetailResponse(BaseModel):
#     """Client profile details for match verification"""
#     client_id: int
#     key_interests: Optional[str]
#     target_job_titles: Optional[list]
#     business_areas: Optional[str]
#     company_main_activities: Optional[str]
#     companies_to_exclude: Optional[str]
#     excluded_countries: Optional[str]


# class ProspectDetailResponse(BaseModel):
#     """Prospect profile details for match verification"""
#     prospect_id: int
#     first_name: Optional[str]
#     last_name: Optional[str]
#     attendee_email: Optional[str]
#     job_title: Optional[str]
#     company_name: str
#     country: Optional[str]
#     region: Optional[str]
#     job_function: Optional[str]
#     responsibility: Optional[str]
#     company_main_activity: Optional[str]
#     area_of_interests: Optional[str]


# class MatchDetailResponse(BaseModel):
#     """Comprehensive match details for verification"""
#     match_id: int
#     client: ClientDetailResponse
#     prospect: ProspectDetailResponse
    
#     # Scoring details
#     job_title_score: float
#     business_area_score: float
#     activity_score: float
#     overall_score: float
#     match_rank: int
    
#     # Match metadata
#     status: str
#     notes: Optional[str]
#     rejection_reason: Optional[str]
#     matched_at: Optional[str]
#     contacted_at: Optional[str]
#     updated_at: Optional[str]



# # ============================================
# # BACKGROUND TASK FUNCTIONS
# # ============================================

# def match_all_clients_task(
#     db: Session,
#     max_matches: int,
#     max_per_company: int,
#     min_score: float,
#     weights: dict
# ):
#     """Background task to match all clients"""
#     try:
#         logger.info("Starting background matching for all clients")
        
#         engine = MatchingEngine(
#             db=db,
#             max_matches=max_matches,
#             max_per_company=max_per_company,
#             min_score=min_score,
#             **weights
#         )
        
#         result = engine.match_all_clients()
#         logger.info(f"Background matching completed: {result}")
        
#     except Exception as e:
#         logger.error(f"Error in background matching task: {e}", exc_info=True)
#     finally:
#         db.close()


# # ============================================
# # ENDPOINTS
# # ============================================

# @router.post(
#     "/matching/run",
#     response_model=MatchResponse,
#     summary="Match a single client to prospects",
#     description="Find and rank top prospects for a specific client"
# )
# async def run_matching(
#     request: MatchingRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Run matching algorithm for a single client.
    
#     - **client_id**: Client profile ID to match
#     - **max_matches**: Maximum number of matches to return (default: 15)
#     - **max_per_company**: Max prospects from same company (default: 3)
#     - **min_score**: Minimum similarity score threshold (default: 0.5)
#     - **force_rematch**: Regenerate matches even if they exist
#     - **weights**: Custom weights for scoring components
#     """
#     try:
#         # Validate weights sum to 1.0
#         total_weight = request.weight_job_title + request.weight_business_area + request.weight_activity
#         if abs(total_weight - 1.0) > 0.01:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Weights must sum to 1.0 (currently: {total_weight})"
#             )
        
#         # Initialize matching engine with custom parameters
#         engine = MatchingEngine(
#             db=db,
#             max_matches=request.max_matches,
#             max_per_company=request.max_per_company,
#             min_score=request.min_score,
#             weight_job_title=request.weight_job_title,
#             weight_business_area=request.weight_business_area,
#             weight_activity=request.weight_activity
#         )
        
#         # Check if matches already exist and force_rematch is False
#         if not request.force_rematch:
#             existing_matches = engine.get_client_matches(request.client_id, limit=1)
#             if existing_matches:
#                 logger.info(f"Matches already exist for client {request.client_id}")
#                 all_matches = engine.get_client_matches(request.client_id)
#                 avg_score = sum(m['overall_score'] for m in all_matches) / len(all_matches)
                
#                 return MatchResponse(
#                     success=True,
#                     client_id=request.client_id,
#                     matches_found=len(all_matches),
#                     average_score=avg_score,
#                     message="Matches already exist (use force_rematch=true to regenerate)"
#                 )
        
#         # Run matching
#         logger.info(f"Running matching for client {request.client_id}")
#         matches = engine.match_client_to_prospects(
#             client_id=request.client_id,
#             store_results=True
#         )
        
#         if not matches:
#             return MatchResponse(
#                 success=False,
#                 client_id=request.client_id,
#                 matches_found=0,
#                 message="No suitable matches found for this client"
#             )
        
#         # Calculate average score
#         avg_score = sum(m['overall_score'] for m in matches) / len(matches)
        
#         return MatchResponse(
#             success=True,
#             client_id=request.client_id,
#             matches_found=len(matches),
#             average_score=round(avg_score, 4),
#             message=f"Successfully matched {len(matches)} prospects"
#         )
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error running matching: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post(
#     "/matching/run-all",
#     summary="Match all clients to prospects",
#     description="Run matching for all clients with embeddings (background task)"
# )
# async def run_matching_all(
#     request: MatchAllRequest,
#     background_tasks: BackgroundTasks,
#     use_background: bool = True,
#     db: Session = Depends(get_db)
# ):
#     """
#     Run matching algorithm for all clients.
    
#     - **max_matches**: Maximum number of matches per client
#     - **max_per_company**: Max prospects from same company
#     - **min_score**: Minimum similarity score threshold
#     - **force_rematch**: Regenerate all matches
#     - **use_background**: Run in background (recommended for large datasets)
#     """
#     try:
#         # Validate weights (using defaults)
#         weights = {
#             'weight_job_title': 0.40,
#             'weight_business_area': 0.30,
#             'weight_activity': 0.30
#         }
        
#         if use_background:
#             # Run in background
#             background_tasks.add_task(
#                 match_all_clients_task,
#                 db=db,
#                 max_matches=request.max_matches,
#                 max_per_company=request.max_per_company,
#                 min_score=request.min_score,
#                 weights=weights
#             )
            
#             return {
#                 "success": True,
#                 "message": "Matching started in background",
#                 "status": "running"
#             }
#         else:
#             # Run synchronously (use with caution for large datasets)
#             engine = MatchingEngine(
#                 db=db,
#                 max_matches=request.max_matches,
#                 max_per_company=request.max_per_company,
#                 min_score=request.min_score,
#                 **weights
#             )
            
#             result = engine.match_all_clients()
            
#             return {
#                 "success": True,
#                 "message": "Matching completed",
#                 "status": "completed",
#                 **result
#             }
        
#     except Exception as e:
#         logger.error(f"Error running matching for all clients: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/matching/results/{client_id}",
#     response_model=MatchResultsResponse,
#     summary="Get match results for a client",
#     description="Retrieve stored match results with prospect details"
# )
# async def get_match_results(
#     client_id: int,
#     limit: Optional[int] = Query(15, ge=1, le=50),
#     min_score: Optional[float] = Query(None, ge=0.0, le=1.0),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get match results for a specific client.
    
#     - **client_id**: Client profile ID
#     - **limit**: Maximum number of results to return
#     - **min_score**: Filter matches by minimum score
#     """
#     try:
#         engine = MatchingEngine(db=db)
#         matches = engine.get_client_matches(client_id, limit=limit)
        
#         # Filter by score if specified
#         if min_score is not None:
#             matches = [m for m in matches if m['overall_score'] >= min_score]
        
#         # Convert to response model
#         match_items = [
#             MatchResultItem(
#                 match_id=m['match_id'],
#                 prospect_id=m['prospect_id'],
#                 prospect_name=m['prospect_name'],
#                 job_title=m['job_title'],
#                 company_name=m['company_name'],
#                 country=m['country'],
#                 email=m['email'],
#                 job_title_score=m['job_title_score'],
#                 business_area_score=m['business_area_score'],
#                 activity_score=m['activity_score'],
#                 overall_score=m['overall_score'],
#                 match_rank=m['match_rank'],
#                 status=m['status'],
#                 matched_at=m['matched_at']
#             )
#             for m in matches
#         ]
        
#         return MatchResultsResponse(
#             client_id=client_id,
#             total_matches=len(match_items),
#             matches=match_items
#         )
        
#     except Exception as e:
#         logger.error(f"Error getting match results: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.put(
#     "/matching/results/{match_id}",
#     summary="Update match status",
#     description="Update status and notes for a specific match"
# )
# async def update_match_status(
#     match_id: int,
#     request: UpdateMatchStatusRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Update the status of a match.
    
#     - **match_id**: Match ID to update
#     - **status**: New status (pending, contacted, meeting_scheduled, rejected)
#     - **notes**: Optional notes
#     - **rejection_reason**: Required if status is 'rejected'
#     """
#     try:
#         from database.models import ClientProspectMatch
        
#         # Validate status
#         valid_statuses = ["pending", "contacted", "meeting_scheduled", "rejected"]
#         if request.status not in valid_statuses:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid status. Must be one of: {valid_statuses}"
#             )
        
#         # Get match
#         match = db.query(ClientProspectMatch).filter(
#             ClientProspectMatch.id == match_id
#         ).first()
        
#         if not match:
#             raise HTTPException(404, f"Match {match_id} not found")
        
#         # Update status
#         match.status = request.status
#         if request.notes:
#             match.notes = request.notes
#         if request.rejection_reason:
#             match.rejection_reason = request.rejection_reason
        
#         # Update contacted timestamp if status is contacted
#         if request.status == "contacted" and not match.contacted_at:
#             match.contacted_at = datetime.utcnow()
        
#         match.updated_at = datetime.utcnow()
        
#         db.commit()
#         db.refresh(match)
        
#         logger.info(f"Updated match {match_id} status to {request.status}")
        
#         return {
#             "success": True,
#             "match_id": match_id,
#             "updated_status": match.status,
#             "message": f"Match status updated to {match.status}"
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error updating match status: {e}", exc_info=True)
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))


# @router.delete(
#     "/matching/results/{match_id}",
#     summary="Delete a match",
#     description="Remove a specific match from the database"
# )
# async def delete_match(
#     match_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Delete a specific match.
    
#     - **match_id**: Match ID to delete
#     """
#     try:
#         from database.models import ClientProspectMatch
        
#         match = db.query(ClientProspectMatch).filter(
#             ClientProspectMatch.id == match_id
#         ).first()
        
#         if not match:
#             raise HTTPException(404, f"Match {match_id} not found")
        
#         db.delete(match)
#         db.commit()
        
#         logger.info(f"Deleted match {match_id}")
        
#         return {
#             "success": True,
#             "message": f"Match {match_id} deleted successfully"
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error deleting match: {e}", exc_info=True)
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))


# @router.delete(
#     "/matching/results/client/{client_id}",
#     summary="Delete all matches for a client",
#     description="Remove all matches for a specific client"
# )
# async def delete_client_matches(
#     client_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Delete all matches for a specific client.
    
#     - **client_id**: Client profile ID
#     """
#     try:
#         from database.models import ClientProspectMatch
        
#         deleted_count = db.query(ClientProspectMatch).filter(
#             ClientProspectMatch.client_profile_id == client_id
#         ).delete()
        
#         db.commit()
        
#         logger.info(f"Deleted {deleted_count} matches for client {client_id}")
        
#         return {
#             "success": True,
#             "message": f"Deleted {deleted_count} matches for client {client_id}",
#             "deleted_count": deleted_count
#         }
        
#     except Exception as e:
#         logger.error(f"Error deleting client matches: {e}", exc_info=True)
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/matching/stats",
#     summary="Get matching statistics",
#     description="Get overall matching statistics and metrics"
# )
# async def get_matching_stats(db: Session = Depends(get_db)):
#     """
#     Get overall matching statistics.
    
#     Returns:
#     - Total matches
#     - Average score
#     - Clients with matches
#     - Status breakdown
#     """
#     try:
#         stats = MatchingStats.get_summary(db)
        
#         return {
#             "success": True,
#             **stats
#         }
        
#     except Exception as e:
#         logger.error(f"Error getting matching stats: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/matching/health",
#     summary="Health check for matching system",
#     description="Verify matching system is operational"
# )
# async def matching_health_check(db: Session = Depends(get_db)):
#     """
#     Health check for matching system.
    
#     Verifies:
#     - Database connectivity
#     - Embeddings exist
#     - Matching engine can be initialized
#     """
#     try:
#         from database.models import ClientEmbedding, ProspectEmbedding
        
#         # Check embeddings exist
#         client_emb_count = db.query(ClientEmbedding).count()
#         prospect_emb_count = db.query(ProspectEmbedding).count()
        
#         if client_emb_count == 0 or prospect_emb_count == 0:
#             return {
#                 "status": "degraded",
#                 "message": "Missing embeddings. Run /api/embeddings/generate first",
#                 "client_embeddings": client_emb_count,
#                 "prospect_embeddings": prospect_emb_count
#             }
        
#         # Try to initialize engine
#         engine = MatchingEngine(db=db)
        
#         # Get stats
#         stats = MatchingStats.get_summary(db)
        
#         return {
#             "status": "healthy",
#             "message": "Matching system operational",
#             "client_embeddings": client_emb_count,
#             "prospect_embeddings": prospect_emb_count,
#             "total_matches": stats['total_matches']
#         }
        
#     except Exception as e:
#         logger.error(f"Matching health check failed: {e}", exc_info=True)
#         return {
#             "status": "unhealthy",
#             "message": str(e)
#         }
    





# @router.get(
#     "/matching/match-detail/{match_id}",
#     response_model=MatchDetailResponse,
#     summary="Get detailed match information",
#     description="Retrieve comprehensive details about a specific match for verification"
# )
# async def get_match_detail(
#     match_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Get detailed information about a specific match.
    
#     This endpoint provides comprehensive information about both the client 
#     and prospect, along with all scoring details, to help verify if the 
#     match is appropriate.
    
#     Parameters:
#     - **match_id**: The ID of the match to retrieve
    
#     Returns:
#     - Complete client profile information
#     - Complete prospect profile information
#     - Detailed scoring breakdown
#     - Match metadata and status
#     """
#     try:
#         # Query match with joined client and prospect profiles
#         match = db.query(ClientProspectMatch).filter(
#             ClientProspectMatch.id == match_id
#         ).first()
        
#         if not match:
#             raise HTTPException(
#                 status_code=404, 
#                 detail=f"Match with ID {match_id} not found"
#             )
        
#         # Get client profile
#         client = db.query(ClientUploadProfile).filter(
#             ClientUploadProfile.id == match.client_profile_id
#         ).first()
        
#         if not client:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Client profile {match.client_profile_id} not found"
#             )
        
#         # Get prospect profile
#         prospect = db.query(Prospects).filter(
#             Prospects.id == match.prospect_id
#         ).first()
        
#         if not prospect:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Prospect profile {match.prospect_profile_id} not found"
#             )
        
#         # Build response
#         client_detail = ClientDetailResponse(
#             client_id=client.id,
#             key_interests=client.key_interests,
#             target_job_titles=client.target_job_titles,
#             business_areas=client.business_areas,
#             company_main_activities=client.company_main_activities,
#             companies_to_exclude=client.companies_to_exclude,
#             excluded_countries=client.excluded_countries
#         )
        
#         prospect_detail = ProspectDetailResponse(
#             prospect_id=prospect.id,
#             first_name=prospect.first_name,
#             last_name=prospect.last_name,
#             attendee_email=prospect.attendee_email,
#             job_title=prospect.job_title,
#             company_name=prospect.company_name,
#             country=prospect.country,
#             region=prospect.region,
#             job_function=prospect.job_function,
#             responsibility=prospect.responsibility,
#             company_main_activity=prospect.company_main_activity,
#             area_of_interests=prospect.area_of_interests
#         )
        
#         response = MatchDetailResponse(
#             match_id=match.id,
#             client=client_detail,
#             prospect=prospect_detail,
#             job_title_score=match.job_title_score,
#             business_area_score=match.business_area_score,
#             activity_score=match.activity_score,
#             overall_score=match.overall_score,
#             match_rank=match.match_rank,
#             status=match.status,
#             notes=match.notes,
#             rejection_reason=match.rejection_reason,
#             matched_at=match.matched_at.isoformat() if match.matched_at else None,
#             contacted_at=match.contacted_at.isoformat() if match.contacted_at else None,
#             updated_at=match.updated_at.isoformat() if match.updated_at else None
#         )
        
#         logger.info(f"Retrieved detailed information for match {match_id}")
        
#         return response
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error retrieving match detail: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to retrieve match details: {str(e)}"
#         )


# @router.get(
#     "/matching/compare/{match_id}",
#     summary="Get side-by-side comparison",
#     description="Get a formatted comparison view for match verification"
# )
# async def get_match_comparison(
#     match_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Get a side-by-side comparison of client and prospect for verification.
    
#     This endpoint returns the data in a format optimized for displaying
#     similarities and differences between the matched profiles.
#     """
#     try:
#         # Get the full match detail
#         detail = await get_match_detail(match_id, db)
        
#         # Create comparison structure
#         comparison = {
#             "match_id": match_id,
#             "overall_score": detail.overall_score,
#             "match_rank": detail.match_rank,
#             "status": detail.status,
#             "fields": [
#                 {
#                     "field": "Profile ID",
#                     "client_value": str(detail.client.client_id),
#                     "prospect_value": f"{detail.prospect.first_name} {detail.prospect.last_name}".strip()
#                 },
#                 {
#                     "field": "Job Title",
#                     "client_value": ', '.join(detail.client.target_job_titles) if detail.client.target_job_titles else "N/A",
#                     "prospect_value": detail.prospect.job_title or "N/A",
#                     "similarity_score": detail.job_title_score
#                 },
#                 {
#                     "field": "Company",
#                     "client_value": "Multiple target companies",
#                     "prospect_value": detail.prospect.company_name
#                 },
#                 {
#                     "field": "Business Area",
#                     "client_value": detail.client.business_areas or "N/A",
#                     "prospect_value": detail.prospect.company_main_activity or "N/A",
#                     "similarity_score": detail.business_area_score
#                 },
#                 {
#                     "field": "Country",
#                     "client_value": detail.client.excluded_countries or "All countries",
#                     "prospect_value": detail.prospect.country or "N/A"
#                 },
#                 {
#                     "field": "Activity/Interests",
#                     "client_value": detail.client.key_interests or "N/A",
#                     "prospect_value": detail.prospect.area_of_interests or "N/A",
#                     "similarity_score": detail.activity_score
#                 }
#             ],
#             "scores": {
#                 "job_title": detail.job_title_score,
#                 "business_area": detail.business_area_score,
#                 "activity": detail.activity_score,
#                 "overall": detail.overall_score
#             },
#             "metadata": {
#                 "notes": detail.notes,
#                 "rejection_reason": detail.rejection_reason,
#                 "matched_at": detail.matched_at,
#                 "contacted_at": detail.contacted_at
#             }
#         }
        
#         return comparison
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error creating comparison: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to create comparison: {str(e)}"
#         )
































"""
FastAPI Endpoints for Client-Prospect Matching with Priority/Discovery Pools
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
from datetime import datetime
from database.config import get_db
from database.models import (
    ClientProspectMatch,
    ClientUploadProfile,
    Prospects,
)
from matching.matching_engine import MatchingEngine, MatchingStats

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================


class MatchingRequest(BaseModel):
    """Request model for matching"""
    client_id: int = Field(..., description="Client profile ID to match")
    max_matches: Optional[int] = Field(15, ge=1, le=100)  # Increased limit
    max_per_company: Optional[int] = Field(3, ge=1, le=10)
    min_score: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    force_rematch: bool = Field(False, description="Regenerate even if matches exist")
    weight_job_title: Optional[float] = Field(0.40, ge=0.0, le=1.0)
    weight_business_area: Optional[float] = Field(0.30, ge=0.0, le=1.0)
    weight_activity: Optional[float] = Field(0.30, ge=0.0, le=1.0)

class MatchAllRequest(BaseModel):
    """Request model for matching all clients"""
    max_matches: Optional[int] = Field(15, ge=1, le=50)
    max_per_company: Optional[int] = Field(3, ge=1, le=10)
    min_score: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    force_rematch: bool = Field(False)


class MatchResponse(BaseModel):
    """Response model for matching result"""
    success: bool
    client_id: int
    priority_matches: int
    discovery_matches: int
    total_matches: int
    priority_avg_score: Optional[float] = None
    discovery_avg_score: Optional[float] = None
    message: str


class MatchResultItem(BaseModel):
    """Single match result"""
    match_id: int
    prospect_id: int
    prospect_name: str
    job_title: Optional[str]
    company_name: str
    country: Optional[str]
    email: Optional[str]
    job_title_score: float
    business_area_score: float
    activity_score: float
    overall_score: float
    match_rank: int
    match_type: str
    status: str
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    matched_at: Optional[str] = None
    contacted_at: Optional[str] = None
    updated_at: Optional[str] = None


class MatchResultsResponse(BaseModel):
    """Response model for match results"""
    client_id: int
    priority_matches: List[MatchResultItem]
    discovery_matches: List[MatchResultItem]
    total_priority: int
    total_discovery: int
    total_matches: int


class UpdateMatchStatusRequest(BaseModel):
    """Request to update match status"""
    status: str = Field(..., description="Status: pending, contacted, meeting_scheduled, rejected")
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class ClientDetailResponse(BaseModel):
    """Client profile details for match verification"""
    client_id: int
    key_interests: Optional[str]
    target_job_titles: Optional[List[str]]
    business_areas: Optional[str]
    company_main_activities: Optional[str]
    companies_to_exclude: Optional[str]
    excluded_countries: Optional[str]
    target_companies: Optional[List[str]]


class ProspectDetailResponse(BaseModel):
    """Prospect profile details for match verification"""
    prospect_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    attendee_email: Optional[str]
    job_title: Optional[str]
    company_name: str
    country: Optional[str]
    region: Optional[str]
    job_function: Optional[str]
    responsibility: Optional[str]
    company_main_activity: Optional[str]
    area_of_interests: Optional[str]


class MatchDetailResponse(BaseModel):
    """Comprehensive match details for verification"""
    match_id: int
    client: ClientDetailResponse
    prospect: ProspectDetailResponse

    # Scoring details
    job_title_score: float
    business_area_score: float
    activity_score: float
    overall_score: float
    match_rank: int
    match_type: str

    # Match metadata
    status: str
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    matched_at: Optional[str] = None
    contacted_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================
# BACKGROUND TASK FUNCTIONS
# ============================================

def match_all_clients_task(
    db: Session,
    max_matches: int,
    max_per_company: int,
    min_score: float,
    weights: dict
):
    """Background task to match all clients"""
    try:
        logger.info("Starting background matching for all clients")

        engine = MatchingEngine(
            db=db,
            max_matches=max_matches,
            max_per_company=max_per_company,
            min_score=min_score,
            **weights
        )

        result = engine.match_all_clients()
        logger.info(f"Background matching completed: {result}")

    except Exception as e:
        logger.error(f"Error in background matching task: {e}", exc_info=True)
    # Do NOT call db.close() here — session is dependency-managed by FastAPI.


# ============================================
# ENDPOINTS
# ============================================



@router.post(
    "/matching/run",
    response_model=MatchResponse,
    summary="Match a single client to prospects",
    description="Find and rank top prospects in priority (target companies) and discovery pools"
)
async def run_matching(
    request: MatchingRequest,
    db: Session = Depends(get_db)
):
    """
    Run matching algorithm for a single client with separate priority/discovery pools.
    """
    try:
        # Remove or comment out the weight validation since priority pool doesn't use weighted scoring
        # total_weight = float(request.weight_job_title) + float(request.weight_business_area) + float(request.weight_activity)
        # if abs(total_weight - 1.0) > 0.01:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Weights must sum to 1.0 (currently: {total_weight})"
        #     )

        # Initialize matching engine (ensure integers are passed)
        engine = MatchingEngine(
            db=db,
            max_matches=int(request.max_matches),
            max_per_company=int(request.max_per_company),
            min_score=float(request.min_score),
            weight_job_title=float(request.weight_job_title),
            weight_business_area=float(request.weight_business_area),
            weight_activity=float(request.weight_activity)
        )

        # Check if matches exist
        if not request.force_rematch:
            existing = db.query(ClientProspectMatch).filter(
                ClientProspectMatch.client_profile_id == request.client_id
            ).first()

            if existing:
                priority_count = db.query(ClientProspectMatch).filter(
                    ClientProspectMatch.client_profile_id == request.client_id,
                    ClientProspectMatch.match_type == 'priority'
                ).count()

                discovery_count = db.query(ClientProspectMatch).filter(
                    ClientProspectMatch.client_profile_id == request.client_id,
                    ClientProspectMatch.match_type == 'discovery'
                ).count()

                return MatchResponse(
                    success=True,
                    client_id=request.client_id,
                    priority_matches=priority_count,
                    discovery_matches=discovery_count,
                    total_matches=priority_count + discovery_count,
                    message="Matches already exist (use force_rematch=true to regenerate)"
                )

        # Run matching
        logger.info(f"Running matching for client {request.client_id}")
        result = engine.match_client_to_prospects(
            client_id=request.client_id,
            store_results=True
        )

        # FIXED: Handle the new dictionary structure with separate pools
        priority_matches = result.get('priority_matches', [])
        discovery_matches = result.get('discovery_matches', [])

        if not priority_matches and not discovery_matches:
            return MatchResponse(
                success=False,
                client_id=request.client_id,
                priority_matches=0,
                discovery_matches=0,
                total_matches=0,
                message="No suitable matches found for this client"
            )

        # Calculate average scores
        priority_avg = sum(m['overall_score'] for m in priority_matches) / len(priority_matches) if priority_matches else None
        discovery_avg = sum(m['overall_score'] for m in discovery_matches) / len(discovery_matches) if discovery_matches else None

        return MatchResponse(
            success=True,
            client_id=request.client_id,
            priority_matches=len(priority_matches),
            discovery_matches=len(discovery_matches),
            total_matches=len(priority_matches) + len(discovery_matches),
            priority_avg_score=round(priority_avg, 4) if priority_avg else None,
            discovery_avg_score=round(discovery_avg, 4) if discovery_avg else None,
            message=f"Found {len(priority_matches)} priority and {len(discovery_matches)} discovery matches"
        )

    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error running matching: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post(
    "/matching/run-all",
    summary="Match all clients to prospects",
    description="Run matching for all clients with embeddings (background task)"
)
async def run_matching_all(
    request: MatchAllRequest,
    background_tasks: BackgroundTasks,
    use_background: bool = True,
    db: Session = Depends(get_db)
):
    """
    Run matching algorithm for all clients with priority/discovery pools.
    """
    try:
        weights = {
            'weight_job_title': 0.40,
            'weight_business_area': 0.30,
            'weight_activity': 0.30
        }

        if use_background:
            background_tasks.add_task(
                match_all_clients_task,
                db=db,
                max_matches=int(request.max_matches),
                max_per_company=int(request.max_per_company),
                min_score=float(request.min_score),
                weights=weights
            )

            return {
                "success": True,
                "message": "Matching started in background for all clients",
                "status": "running"
            }
        else:
            engine = MatchingEngine(
                db=db,
                max_matches=int(request.max_matches),
                max_per_company=int(request.max_per_company),
                min_score=float(request.min_score),
                **weights
            )

            result = engine.match_all_clients()

            return {
                "success": True,
                "message": "Matching completed for all clients",
                "status": "completed",
                **(result or {})
            }

    except Exception as e:
        logger.error(f"Error running matching for all clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/matching/results/{client_id}",
    response_model=MatchResultsResponse,
    summary="Get match results for a client",
    description="Retrieve stored match results separated into priority and discovery pools"
)
async def get_match_results(
    client_id: int,
    match_type: Optional[str] = Query(None, regex="^(priority|discovery|all)$", description="Filter by match type"),
    limit_per_type: Optional[int] = Query(None, ge=1, le=50, description="Limit results per type"),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Filter by minimum score"),
    db: Session = Depends(get_db)
):
    """
    Get match results for a specific client with priority/discovery separation.
    """
    try:
        # Base query
        query = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.client_profile_id == client_id
        )

        # Filter by match type if specified
        if match_type and match_type != 'all':
            query = query.filter(ClientProspectMatch.match_type == match_type)

        # Filter by score
        if min_score is not None:
            query = query.filter(ClientProspectMatch.overall_score >= min_score)

        # Order by type (priority first) then rank
        # Assuming 'priority' > 'discovery' lexically may not hold; use case expression if needed.
        query = query.order_by(
            ClientProspectMatch.match_type.desc(),
            ClientProspectMatch.match_rank
        )

        matches = query.all()

        # Get prospect details
        prospect_ids = [m.prospect_id for m in matches]
        prospects = db.query(Prospects).filter(Prospects.id.in_(prospect_ids)).all() if prospect_ids else []
        prospects_dict = {p.id: p for p in prospects}

        # Separate into priority and discovery
        priority_items = []
        discovery_items = []

        priority_count = 0
        discovery_count = 0

        for match in matches:
            prospect = prospects_dict.get(match.prospect_id)
            if not prospect:
                continue

            match_item = MatchResultItem(
                match_id=match.id,
                prospect_id=match.prospect_id,
                prospect_name=f"{prospect.first_name or ''} {prospect.last_name or ''}".strip(),
                job_title=prospect.job_title,
                company_name=prospect.company_name,
                country=prospect.country,
                email=prospect.attendee_email,
                job_title_score=float(match.job_title_score) if match.job_title_score is not None else 0.0,
                business_area_score=float(match.business_area_score) if match.business_area_score is not None else 0.0,
                activity_score=float(match.activity_score) if match.activity_score is not None else 0.0,
                overall_score=float(match.overall_score) if match.overall_score is not None else 0.0,
                match_rank=match.match_rank,
                match_type=match.match_type or 'discovery',
                status=match.status,
                notes=match.notes,
                rejection_reason=match.rejection_reason,
                matched_at=match.matched_at.isoformat() if getattr(match, 'matched_at', None) else None,
                contacted_at=match.contacted_at.isoformat() if getattr(match, 'contacted_at', None) else None,
                updated_at=match.updated_at.isoformat() if getattr(match, 'updated_at', None) else None
            )

            if match.match_type == 'priority':
                if limit_per_type is None or priority_count < limit_per_type:
                    priority_items.append(match_item)
                    priority_count += 1
            else:
                if limit_per_type is None or discovery_count < limit_per_type:
                    discovery_items.append(match_item)
                    discovery_count += 1

        return MatchResultsResponse(
            client_id=client_id,
            priority_matches=priority_items,
            discovery_matches=discovery_items,
            total_priority=len(priority_items),
            total_discovery=len(discovery_items),
            total_matches=len(priority_items) + len(discovery_items)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/matching/compare/{match_id}",
    summary="Get side-by-side comparison",
    description="Get a formatted comparison view for match verification"
)
async def get_match_comparison(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a side-by-side comparison of client and prospect for verification.
    Includes match type (priority/discovery) indication.
    """
    try:
        detail = await get_match_detail(match_id, db)

        # Determine if this is a target company match
        is_target_company = False
        if detail.client.target_companies and detail.prospect.company_name:
            target_companies_lower = [c.lower().strip() for c in detail.client.target_companies]
            is_target_company = detail.prospect.company_name.lower().strip() in target_companies_lower

        comparison = {
            "match_id": match_id,
            "match_type": detail.match_type,
            "is_target_company": is_target_company,
            "overall_score": detail.overall_score,
            "match_rank": detail.match_rank,
            "status": detail.status,
            "fields": [
                {
                    "field": "Profile ID",
                    "client_value": str(detail.client.client_id),
                    "prospect_value": f"{detail.prospect.first_name or ''} {detail.prospect.last_name or ''}".strip()
                },
                {
                    "field": "Match Type",
                    "client_value": "Priority" if detail.match_type == 'priority' else "Discovery",
                    "prospect_value": "Target Company" if is_target_company else "Other Company",
                    "highlight": detail.match_type == 'priority'
                },
                {
                    "field": "Job Title",
                    "client_value": ', '.join(detail.client.target_job_titles) if detail.client.target_job_titles else "N/A",
                    "prospect_value": detail.prospect.job_title or "N/A",
                    "similarity_score": detail.job_title_score
                },
                {
                    "field": "Company",
                    "client_value": ', '.join(detail.client.target_companies[:3]) if detail.client.target_companies else "Multiple targets",
                    "prospect_value": detail.prospect.company_name,
                    "highlight": is_target_company
                },
                {
                    "field": "Business Area",
                    "client_value": detail.client.business_areas or "N/A",
                    "prospect_value": detail.prospect.company_main_activity or "N/A",
                    "similarity_score": detail.business_area_score
                },
                {
                    "field": "Country",
                    "client_value": f"Excluded: {detail.client.excluded_countries}" if detail.client.excluded_countries else "All countries",
                    "prospect_value": detail.prospect.country or "N/A"
                },
                {
                    "field": "Activity/Interests",
                    "client_value": detail.client.key_interests or "N/A",
                    "prospect_value": detail.prospect.area_of_interests or "N/A",
                    "similarity_score": detail.activity_score
                },
                {
                    "field": "Job Function",
                    "client_value": "N/A",
                    "prospect_value": detail.prospect.job_function or "N/A"
                },
                {
                    "field": "Responsibility",
                    "client_value": "N/A",
                    "prospect_value": detail.prospect.responsibility or "N/A"
                }
            ],
            "scores": {
                "job_title": detail.job_title_score,
                "business_area": detail.business_area_score,
                "activity": detail.activity_score,
                "overall": detail.overall_score
            },
            "metadata": {
                "notes": detail.notes,
                "rejection_reason": detail.rejection_reason,
                "matched_at": detail.matched_at,
                "contacted_at": detail.contacted_at,
                "updated_at": detail.updated_at
            }
        }

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comparison: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/matching/client/{client_id}/summary",
    summary="Get client matching summary",
    description="Get summary of matches for a client with pool breakdown"
)
async def get_client_match_summary(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a summary of all matches for a client with pool breakdown.
    """
    try:
        # Verify client exists
        client = db.query(ClientUploadProfile).filter(
            ClientUploadProfile.id == client_id
        ).first()

        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")

        # Get all matches
        matches = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.client_profile_id == client_id
        ).all()

        if not matches:
            return {
                "client_id": client_id,
                "total_matches": 0,
                "priority_matches": 0,
                "discovery_matches": 0,
                "message": "No matches found for this client"
            }

        # Separate by type
        priority_matches = [m for m in matches if m.match_type == 'priority']
        discovery_matches = [m for m in matches if m.match_type != 'priority']

        # Calculate statistics
        priority_avg = sum(float(m.overall_score) for m in priority_matches) / len(priority_matches) if priority_matches else 0
        discovery_avg = sum(float(m.overall_score) for m in discovery_matches) / len(discovery_matches) if discovery_matches else 0

        # Status breakdown
        priority_status: Dict[str, int] = {}
        discovery_status: Dict[str, int] = {}

        for match in priority_matches:
            priority_status[match.status] = priority_status.get(match.status, 0) + 1

        for match in discovery_matches:
            discovery_status[match.status] = discovery_status.get(match.status, 0) + 1

        # Top companies by pool
        from collections import Counter

        priority_prospect_ids = [m.prospect_id for m in priority_matches]
        discovery_prospect_ids = [m.prospect_id for m in discovery_matches]

        priority_prospects = db.query(Prospects).filter(
            Prospects.id.in_(priority_prospect_ids)
        ).all() if priority_prospect_ids else []

        discovery_prospects = db.query(Prospects).filter(
            Prospects.id.in_(discovery_prospect_ids)
        ).all() if discovery_prospect_ids else []

        priority_companies = Counter([p.company_name for p in priority_prospects])
        discovery_companies = Counter([p.company_name for p in discovery_prospects])

        return {
            "client_id": client_id,
            "total_matches": len(matches),
            "priority_pool": {
                "count": len(priority_matches),
                "average_score": round(priority_avg, 4),
                "status_breakdown": priority_status,
                "top_companies": dict(priority_companies.most_common(10))
            },
            "discovery_pool": {
                "count": len(discovery_matches),
                "average_score": round(discovery_avg, 4),
                "status_breakdown": discovery_status,
                "top_companies": dict(discovery_companies.most_common(10))
            },
            "overall_status": {
                status: priority_status.get(status, 0) + discovery_status.get(status, 0)
                for status in set(list(priority_status.keys()) + list(discovery_status.keys()))
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/matching/client/{client_id}/target-companies",
    summary="Get client's target companies",
    description="List all companies the client wants to meet"
)
async def get_client_target_companies(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of target companies for a client.
    Shows which ones have matches and which don't.
    """
    try:
        client = db.query(ClientUploadProfile).filter(
            ClientUploadProfile.id == client_id
        ).first()

        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")

        # Get target companies
        from database.models import ClientCompany
        target_companies = db.query(ClientCompany).filter(
            ClientCompany.profile_id == client_id
        ).all()

        if not target_companies:
            return {
                "client_id": client_id,
                "target_companies": [],
                "message": "No target companies defined for this client"
            }

        # Get priority matches
        priority_matches = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.client_profile_id == client_id,
            ClientProspectMatch.match_type == 'priority'
        ).all()

        # Get prospect companies
        prospect_ids = [m.prospect_id for m in priority_matches]
        prospects = db.query(Prospects).filter(Prospects.id.in_(prospect_ids)).all() if prospect_ids else []

        matched_companies = {p.company_name.lower().strip(): p.company_name for p in prospects if p.company_name}

        # Build response
        companies_info = []
        for company in target_companies:
            company_lower = (company.company_name or "").lower().strip()
            has_match = company_lower in matched_companies
            match_count = sum(1 for p in prospects if (p.company_name or "").lower().strip() == company_lower)

            companies_info.append({
                "company_name": company.company_name,
                "country": getattr(company, "country", None),
                "city": getattr(company, "city", None),
                "has_matches": has_match,
                "match_count": match_count,
                "matched_as": matched_companies.get(company_lower)
            })

        total_companies = len(companies_info)
        companies_with_matches = sum(1 for c in companies_info if c['has_matches'])
        companies_without_matches = total_companies - companies_with_matches

        return {
            "client_id": client_id,
            "total_target_companies": total_companies,
            "companies_with_matches": companies_with_matches,
            "companies_without_matches": companies_without_matches,
            "coverage_percentage": round((companies_with_matches / total_companies * 100), 2) if total_companies > 0 else 0,
            "target_companies": companies_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting target companies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/matching/move-to-priority/{match_id}",
    summary="Move discovery match to priority",
    description="Manually promote a discovery match to priority pool"
)
async def move_to_priority(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Move a discovery match to priority pool.
    Useful when a discovery match turns out to be valuable.
    """
    try:
        match = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.id == match_id
        ).first()

        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")

        if match.match_type == 'priority':
            return {
                "success": True,
                "message": "Match is already in priority pool",
                "match_id": match_id
            }

        match.match_type = 'priority'
        match.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(match)

        return {
            "success": True,
            "message": "Match moved to priority pool",
            "match_id": match_id,
            "new_type": match.match_type
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving match to priority: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/matching/move-to-discovery/{match_id}",
    summary="Move priority match to discovery",
    description="Manually demote a priority match to discovery pool"
)
async def move_to_discovery(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Move a priority match to discovery pool.
    """
    try:
        match = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.id == match_id
        ).first()

        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")

        if match.match_type == 'discovery':
            return {
                "success": True,
                "message": "Match is already in discovery pool",
                "match_id": match_id
            }

        match.match_type = 'discovery'
        match.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(match)

        return {
            "success": True,
            "message": "Match moved to discovery pool",
            "match_id": match_id,
            "new_type": match.match_type
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving match to discovery: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/matching/results/{client_id}/by-type/{match_type}",
    summary="Get matches by specific type",
    description="Get only priority or only discovery matches"
)
async def get_matches_by_type(
    client_id: int,
    match_type: str,
    limit: Optional[int] = Query(15, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get matches of a specific type only.
    """
    if match_type not in ['priority', 'discovery']:
        raise HTTPException(status_code=400, detail="match_type must be 'priority' or 'discovery'")

    try:
        matches = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.client_profile_id == client_id,
            ClientProspectMatch.match_type == match_type
        ).order_by(ClientProspectMatch.match_rank).limit(limit).all()

        prospect_ids = [m.prospect_id for m in matches]
        prospects = db.query(Prospects).filter(Prospects.id.in_(prospect_ids)).all() if prospect_ids else []
        prospects_dict = {p.id: p for p in prospects}

        results = []
        for match in matches:
            prospect = prospects_dict.get(match.prospect_id)
            if prospect:
                results.append({
                    'match_id': match.id,
                    'prospect_id': match.prospect_id,
                    'prospect_name': f"{prospect.first_name or ''} {prospect.last_name or ''}".strip(),
                    'job_title': prospect.job_title,
                    'company_name': prospect.company_name,
                    'country': prospect.country,
                    'email': prospect.attendee_email,
                    'overall_score': float(match.overall_score) if match.overall_score is not None else 0.0,
                    'match_rank': match.match_rank,
                    'match_type': match.match_type,
                    'status': match.status
                })

        return {
            'client_id': client_id,
            'match_type': match_type,
            'count': len(results),
            'matches': results
        }

    except Exception as e:
        logger.error(f"Error getting matches by type: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/matching/results/{match_id}",
    summary="Update match status",
    description="Update status and notes for a specific match"
)
async def update_match_status(
    match_id: int,
    request: UpdateMatchStatusRequest,
    db: Session = Depends(get_db)
):
    """
    Update the status of a match.
    """
    try:
        valid_statuses = ["pending", "contacted", "meeting_scheduled", "rejected"]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )

        match = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.id == match_id
        ).first()

        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")

        match.status = request.status
        if request.notes is not None:
            match.notes = request.notes
        if request.rejection_reason is not None:
            match.rejection_reason = request.rejection_reason

        if request.status == "contacted" and not match.contacted_at:
            match.contacted_at = datetime.utcnow()

        match.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(match)

        logger.info(f"Updated match {match_id} status to {request.status}")

        return {
            "success": True,
            "match_id": match_id,
            "updated_status": match.status,
            "match_type": match.match_type,
            "message": f"Match status updated to {match.status}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating match status: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/matching/results/{match_id}",
    summary="Delete a match",
    description="Remove a specific match from the database"
)
async def delete_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific match."""
    try:
        match = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.id == match_id
        ).first()

        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")

        match_type = match.match_type
        db.delete(match)
        db.commit()

        logger.info(f"Deleted {match_type} match {match_id}")

        return {
            "success": True,
            "match_id": match_id,
            "match_type": match_type,
            "message": f"Match {match_id} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting match: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/matching/results/client/{client_id}",
    summary="Delete all matches for a client",
    description="Remove all matches (both priority and discovery) for a specific client"
)
async def delete_client_matches(
    client_id: int,
    match_type: Optional[str] = Query(None, regex="^(priority|discovery)$"),
    db: Session = Depends(get_db)
):
    """
    Delete matches for a specific client.
    """
    try:
        query = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.client_profile_id == client_id
        )

        if match_type:
            query = query.filter(ClientProspectMatch.match_type == match_type)

        deleted_count = query.delete(synchronize_session=False)
        db.commit()

        type_msg = f"{match_type} " if match_type else ""
        logger.info(f"Deleted {deleted_count} {type_msg}matches for client {client_id}")

        return {
            "success": True,
            "client_id": client_id,
            "match_type": match_type or "all",
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} {type_msg}matches"
        }

    except Exception as e:
        logger.error(f"Error deleting client matches: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/matching/stats",
    summary="Get matching statistics",
    description="Get overall matching statistics with priority/discovery breakdown"
)
async def get_matching_stats(db: Session = Depends(get_db)):
    """
    Get overall matching statistics with pool breakdown.
    """
    try:
        total_matches = db.query(ClientProspectMatch).count()

        priority_count = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.match_type == 'priority'
        ).count()

        discovery_count = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.match_type == 'discovery'
        ).count()

        avg_priority_score = db.query(
            func.avg(ClientProspectMatch.overall_score)
        ).filter(
            ClientProspectMatch.match_type == 'priority'
        ).scalar()

        avg_discovery_score = db.query(
            func.avg(ClientProspectMatch.overall_score)
        ).filter(
            ClientProspectMatch.match_type == 'discovery'
        ).scalar()

        clients_with_matches = db.query(
            func.count(func.distinct(ClientProspectMatch.client_profile_id))
        ).scalar()

        status_counts = db.query(
            ClientProspectMatch.status,
            func.count(ClientProspectMatch.id)
        ).group_by(ClientProspectMatch.status).all()

        return {
            "success": True,
            "total_matches": total_matches,
            "priority_matches": priority_count,
            "discovery_matches": discovery_count,
            "priority_avg_score": float(avg_priority_score) if avg_priority_score else 0.0,
            "discovery_avg_score": float(avg_discovery_score) if avg_discovery_score else 0.0,
            "clients_with_matches": clients_with_matches,
            "status_breakdown": {status: count for status, count in status_counts}
        }

    except Exception as e:
        logger.error(f"Error getting matching stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/matching/health",
    summary="Health check for matching system"
)
async def matching_health_check(db: Session = Depends(get_db)):
    """Health check for matching system."""
    try:
        from database.models import ClientEmbedding, ProspectEmbedding

        client_emb_count = db.query(ClientEmbedding).count()
        prospect_emb_count = db.query(ProspectEmbedding).count()

        if client_emb_count == 0 or prospect_emb_count == 0:
            return {
                "status": "degraded",
                "message": "Missing embeddings",
                "client_embeddings": client_emb_count,
                "prospect_embeddings": prospect_emb_count
            }

        priority_matches = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.match_type == 'priority'
        ).count()

        discovery_matches = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.match_type == 'discovery'
        ).count()

        return {
            "status": "healthy",
            "message": "Matching system operational with priority/discovery pools",
            "client_embeddings": client_emb_count,
            "prospect_embeddings": prospect_emb_count,
            "priority_matches": priority_matches,
            "discovery_matches": discovery_matches
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": str(e)
        }


@router.get(
    "/matching/match-detail/{match_id}",
    response_model=MatchDetailResponse,
    summary="Get detailed match information"
)
async def get_match_detail(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive details about a specific match including match type.
    """
    try:
        match = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.id == match_id
        ).first()

        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")

        client = db.query(ClientUploadProfile).filter(
            ClientUploadProfile.id == match.client_profile_id
        ).first()

        if not client:
            raise HTTPException(status_code=404, detail=f"Client profile not found")

        prospect = db.query(Prospects).filter(
            Prospects.id == match.prospect_id
        ).first()

        if not prospect:
            raise HTTPException(status_code=404, detail=f"Prospect not found")

        # Get target companies
        target_companies = []
        if hasattr(client, 'companies') and client.companies:
            target_companies = [c.company_name for c in client.companies]

        client_detail = ClientDetailResponse(
            client_id=client.id,
            key_interests=getattr(client, "key_interests", None),
            target_job_titles=getattr(client, "target_job_titles", None),
            business_areas=getattr(client, "business_areas", None),
            company_main_activities=getattr(client, "company_main_activities", None),
            companies_to_exclude=getattr(client, "companies_to_exclude", None),
            excluded_countries=getattr(client, "excluded_countries", None),
            target_companies=target_companies
        )

        prospect_detail = ProspectDetailResponse(
            prospect_id=prospect.id,
            first_name=prospect.first_name,
            last_name=prospect.last_name,
            attendee_email=prospect.attendee_email,
            job_title=prospect.job_title,
            company_name=prospect.company_name,
            country=prospect.country,
            region=prospect.region,
            job_function=prospect.job_function,
            responsibility=prospect.responsibility,
            company_main_activity=prospect.company_main_activity,
            area_of_interests=prospect.area_of_interests
        )

        return MatchDetailResponse(
            match_id=match.id,
            client=client_detail,
            prospect=prospect_detail,
            job_title_score=float(match.job_title_score) if match.job_title_score is not None else 0.0,
            business_area_score=float(match.business_area_score) if match.business_area_score is not None else 0.0,
            activity_score=float(match.activity_score) if match.activity_score is not None else 0.0,
            overall_score=float(match.overall_score) if match.overall_score is not None else 0.0,
            match_rank=match.match_rank,
            match_type=match.match_type or 'discovery',
            status=match.status,
            notes=match.notes,
            rejection_reason=match.rejection_reason,
            matched_at=match.matched_at.isoformat() if getattr(match, 'matched_at', None) else None,
            contacted_at=match.contacted_at.isoformat() if getattr(match, 'contacted_at', None) else None,
            updated_at=match.updated_at.isoformat() if getattr(match, 'updated_at', None) else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching match detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
