"""
Text Template System for Embedding Generation
Formats client and prospect data into text suitable for semantic embeddings
"""

import json
from typing import Optional, List
import re


def sanitize_text(text: Optional[str]) -> str:
    """
    Clean and sanitize text for embedding generation.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text string
    """
    if not text or text.strip() == "":
        return ""
    
    # Convert to string if needed
    text = str(text)
    
    # Remove null bytes and control characters
    text = text.replace('\x00', '')
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove excessive punctuation
    text = re.sub(r'([.!?]){2,}', r'\1', text)
    
    return text.strip()


def parse_json_array(text: Optional[str]) -> List[str]:
    """
    Parse JSON array string safely.
    
    Args:
        text: JSON array string, comma-separated text, or list
        
    Returns:
        List of strings
    """
    if not text:
        return []
    
    # FIXED: Handle if already a list
    if isinstance(text, list):
        return [sanitize_text(str(item)) for item in text if item]
    
    try:
        # Try parsing as JSON array
        if text.strip().startswith('['):
            items = json.loads(text)
            return [sanitize_text(item) for item in items if item]
        else:
            # Treat as comma-separated
            return [sanitize_text(item) for item in text.split(',') if item.strip()]
    except:
        # Fallback to comma-separated
        return [sanitize_text(item) for item in text.split(',') if item.strip()]


# ============================================
# CLIENT TEXT TEMPLATES
# ============================================

def format_client_job_title_text(profile) -> str:
    """
    Format client profile data focused on job titles and roles.
    
    Template includes:
    - Target job titles
    - Key interests related to roles
    
    Args:
        profile: ClientUploadProfile SQLAlchemy object
        
    Returns:
        Formatted text string for embedding
    """
    parts = []
    
    # Target job titles
    if profile.target_job_titles:
        job_titles = parse_json_array(profile.target_job_titles)
        if job_titles:
            parts.append(f"Looking for professionals with these job titles: {', '.join(job_titles)}.")
    
    # Key interests (filter for role-related terms)
    if profile.key_interests:
        interests = sanitize_text(profile.key_interests)
        if interests:
            parts.append(f"Key professional interests: {interests}.")
    
    if not parts:
        return "Professional seeking relevant connections."
    
    return " ".join(parts)


def format_client_business_area_text(profile) -> str:
    """
    Format client profile data focused on business areas and industries.
    
    Template includes:
    - Business areas of interest
    - Industry focus
    - Company activities
    
    Args:
        profile: ClientUploadProfile SQLAlchemy object
        
    Returns:
        Formatted text string for embedding
    """
    parts = []
    
    # Business areas
    if profile.business_areas:
        business_areas = sanitize_text(profile.business_areas)
        if business_areas:
            parts.append(f"Interested in these business areas: {business_areas}.")
    
    # Company main activities (if relevant to business area)
    if profile.company_main_activities:
        activities = sanitize_text(profile.company_main_activities)
        if activities:
            parts.append(f"Industry focus: {activities}.")
    
    if not parts:
        return "Open to various business areas and industries."
    
    return " ".join(parts)


def format_client_activity_text(profile) -> str:
    """
    Format client profile data focused on company activities and operations.
    
    Template includes:
    - Company main activities
    - Operational focus areas
    - Specific expertise sought
    
    Args:
        profile: ClientUploadProfile SQLAlchemy object
        
    Returns:
        Formatted text string for embedding
    """
    parts = []
    
    # Company main activities
    if profile.company_main_activities:
        activities = sanitize_text(profile.company_main_activities)
        if activities:
            parts.append(f"Company activities and expertise: {activities}.")
    
    # Key interests (filter for activity-related terms)
    if profile.key_interests:
        interests = sanitize_text(profile.key_interests)
        if interests:
            parts.append(f"Areas of operational interest: {interests}.")
    
    if not parts:
        return "Seeking connections with relevant operational expertise."
    
    return " ".join(parts)


# ============================================
# PROSPECT TEXT TEMPLATES
# ============================================

def format_prospect_job_title_text(prospect) -> str:
    """
    Format prospect data focused on job title and role.
    
    Template includes:
    - Job title
    - Job function
    - Responsibility level
    
    Args:
        prospect: Prospects SQLAlchemy object
        
    Returns:
        Formatted text string for embedding
    """
    parts = []
    
    # Job title
    if prospect.job_title:
        job_title = sanitize_text(prospect.job_title)
        if job_title:
            parts.append(f"Job title: {job_title}.")
    
    # Job function
    if prospect.job_function:
        job_function = sanitize_text(prospect.job_function)
        if job_function:
            parts.append(f"Function: {job_function}.")
    
    # Responsibility
    if prospect.responsibility:
        responsibility = sanitize_text(prospect.responsibility)
        if responsibility:
            parts.append(f"Responsibility: {responsibility}.")
    
    if not parts:
        return f"Professional at {sanitize_text(prospect.company_name) if prospect.company_name else 'company'}."
    
    return " ".join(parts)


def format_prospect_business_area_text(prospect) -> str:
    """
    Format prospect data focused on business area and industry.
    
    Template includes:
    - Company name
    - Country/Region
    - Company main activity
    
    Args:
        prospect: Prospects SQLAlchemy object
        
    Returns:
        Formatted text string for embedding
    """
    parts = []
    
    # Company and location
    company_info = []
    if prospect.company_name:
        company_info.append(sanitize_text(prospect.company_name))
    if prospect.country:
        company_info.append(sanitize_text(prospect.country))
    
    if company_info:
        parts.append(f"Works at: {', '.join(company_info)}.")
    
    # Company main activity
    if prospect.company_main_activity:
        activity = sanitize_text(prospect.company_main_activity)
        if activity:
            parts.append(f"Company operates in: {activity}.")
    
    # Region/Continent for broader context
    if prospect.region and prospect.region != prospect.country:
        region = sanitize_text(prospect.region)
        if region:
            parts.append(f"Region: {region}.")
    
    if not parts:
        return "Professional in business sector."
    
    return " ".join(parts)


def format_prospect_expertise_text(prospect) -> str:
    """
    Format prospect data focused on expertise and interests.
    
    Template includes:
    - Area of interests
    - Company main activity (for expertise context)
    - Job function (for skill context)
    
    Args:
        prospect: Prospects SQLAlchemy object
        
    Returns:
        Formatted text string for embedding
    """
    parts = []
    
    # Area of interests
    if prospect.area_of_interests:
        interests = sanitize_text(prospect.area_of_interests)
        if interests:
            parts.append(f"Areas of expertise and interest: {interests}.")
    
    # Company activity (for expertise context)
    if prospect.company_main_activity:
        activity = sanitize_text(prospect.company_main_activity)
        if activity:
            parts.append(f"Professional experience in: {activity}.")
    
    # Job function (for skill context)
    if prospect.job_function:
        function = sanitize_text(prospect.job_function)
        if function:
            parts.append(f"Functional expertise: {function}.")
    
    if not parts:
        return "Professional with diverse expertise."
    
    return " ".join(parts)


# ============================================
# UTILITY FUNCTIONS
# ============================================

def validate_text_for_embedding(text: str, min_length: int = 10) -> bool:
    """
    Validate that text is suitable for embedding generation.
    
    Args:
        text: Text to validate
        min_length: Minimum required length
        
    Returns:
        True if text is valid, False otherwise
    """
    if not text or len(text.strip()) < min_length:
        return False
    
    # Check if text is not just punctuation or numbers
    alphanumeric = re.sub(r'[^a-zA-Z0-9]', '', text)
    if len(alphanumeric) < min_length:
        return False
    
    return True


def get_text_statistics(text: str) -> dict:
    """
    Get basic statistics about text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with statistics
    """
    words = text.split()
    return {
        "character_count": len(text),
        "word_count": len(words),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "is_valid": validate_text_for_embedding(text)
    }