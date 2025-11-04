"""
Optimized LLM Processor - Reduced output tokens with common fields extraction
"""

import os
import json
import re
import logging
from typing import List, Dict, Optional
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_LLM_CONFIG = {
    "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.0")),
    "max_output_tokens": 8192,
    "api_key": os.getenv("GEMINI_API_KEY", "AIzaSyBCPYNth70Sm4cjryP6PMZ55YaVnPWE3DI"),
}

def initialize_llm(config: dict = None) -> Optional[ChatGoogleGenerativeAI]:
    """Initialize the Gemini LLM model using LangChain wrapper."""
    cfg = {**DEFAULT_LLM_CONFIG, **(config or {})}
    
    try:
        model = ChatGoogleGenerativeAI(
            model=cfg["model"],
            temperature=cfg["temperature"],
            max_output_tokens=cfg["max_output_tokens"],
            google_api_key=cfg["api_key"]
        )
        logger.info(f"✅ Gemini model initialized: {cfg['model']}")
        return model
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini model: {e}")
        return None


# def create_extraction_prompt(md_content: str, bucket: str) -> str:
#     """
#     Create optimized prompt that separates common fields from company-specific data.
#     """
#     prompt = f"""Extract company targeting data from this business briefing document.

# DOCUMENT TYPE: {bucket.upper()}

# EXTRACT IN TWO PARTS:

# PART 1 - COMMON FIELDS (Apply to ALL companies):
# - Excluded_Countries: Countries/regions to exclude (from document text)
# - Target_Job_Titles: All target job titles (from Q7.0 and Q7.1)
# - Company_Main_Activities: Selected company types/industries (from Q5.0)
# - Companies_To_Exclude: Companies to exclude (from Q6.0)
# - Business_Areas: Functional departments/areas (from Q7.0)
# - Key_Interests: Core value propositions - keep brief 100-150 chars (from Q3.0)

# PART 2 - COMPANY-SPECIFIC DATA (from Q4.0):
# - Only extract: Company_Name and Country for each target company

# OUTPUT FORMAT - Return ONLY valid JSON in this EXACT structure:

# {{
#   "Common_Fields": {{
#     "Excluded_Countries": "string",
#     "Target_Job_Titles": ["string"],
#     "Company_Main_Activities": "string",
#     "Companies_To_Exclude": "string",
#     "Business_Areas": "string",
#     "Key_Interests": "string"
#   }},
#   "Target_Companies": [
#     {{
#       "Company_Name": "string",
#       "Country": "string"
#     }}
#   ]
# }}

# CRITICAL RULES:
# - Use double quotes for ALL strings
# - Add commas between array items (NOT after last item)
# - No trailing commas
# - Empty fields: "" for strings, [] for arrays
# - NO markdown, NO code blocks, NO explanations
# - Process the COMPLETE document - don't skip or summarize any sections

# DOCUMENT CONTENT:
# {md_content}

# RESPOND WITH VALID JSON ONLY:"""
    
#     return prompt



def create_extraction_prompt(md_content: str, bucket: str) -> str:
    """
    Create optimized prompt that separates common fields from company-specific data.
    """
    prompt = f"""Extract company targeting data from this business briefing document.

DOCUMENT TYPE: {bucket.upper()}

EXTRACT IN TWO PARTS:

PART 1 - COMMON FIELDS (Apply to ALL companies):
- Excluded_Countries: Countries/regions to exclude (from document text) - return as comma-separated list, expanding any grouped regions into individual countries
- Target_Job_Titles: All target job titles (from Q7.0 and Q7.1)
- Company_Main_Activities: Selected company types/industries (from Q5.0)
- Companies_To_Exclude: Companies to exclude (from Q6.0)
- Business_Areas: Functional departments/areas (from Q7.0)
- Key_Interests: Core value propositions - keep brief 100-150 chars (from Q3.0)

PART 2 - COMPANY-SPECIFIC DATA (from Q4.0):
- Extract Company_Name and Country for each target company
- For Company_Name: Remove country/region suffixes UNLESS they are part of the official company name
  Examples:
  * "Orange France" → "Orange" (France is location, not part of name)
  * "Vodafone NZ" → "Vodafone" (NZ is location, not part of name)
  * "Bank of America" → "Bank of America" (America is part of official name)
  * "Air France" → "Air France" (France is part of official name)

OUTPUT FORMAT - Return ONLY valid JSON in this EXACT structure:

{{
  "Common_Fields": {{
    "Excluded_Countries": "string",
    "Target_Job_Titles": ["string"],
    "Company_Main_Activities": "string",
    "Companies_To_Exclude": "string",
    "Business_Areas": "string",
    "Key_Interests": "string"
  }},
  "Target_Companies": [
    {{
      "Company_Name": "string",
      "Country": "string"
    }}
  ]
}}

CRITICAL RULES:
- Excluded_Countries: Expand all grouped regions into comma-separated individual countries
  Example: "former Soviet bloc (Russia, Ukraine, Belarus etc.)" → "Russia, Ukraine, Belarus"
  Example: "Africa, Central Asia, China" → keep as "Africa, Central Asia, China"
- Use double quotes for ALL strings
- Add commas between array items (NOT after last item)
- No trailing commas
- Empty fields: "" for strings, [] for arrays
- NO markdown, NO code blocks, NO explanations
- Process the COMPLETE document - don't skip or summarize any sections

DOCUMENT CONTENT:
{md_content}

RESPOND WITH VALID JSON ONLY:"""
    
    return prompt





def repair_json(json_text: str) -> str:
    """Repair common JSON syntax errors."""
    if not json_text:
        return '{"Common_Fields": {}, "Target_Companies": []}'
    
    json_text = re.sub(r'```(?:json)?\s*', '', json_text)
    json_text = json_text.replace('```', '')
    json_text = re.sub(r'\}\s*\n\s*\{', '},\n    {', json_text)
    
    open_square = json_text.count('[')
    close_square = json_text.count(']')
    if open_square > close_square:
        json_text += ']' * (open_square - close_square)
    
    open_curly = json_text.count('{')
    close_curly = json_text.count('}')
    if open_curly > close_curly:
        json_text += '}' * (open_curly - close_curly)
    
    json_text = re.sub(r',(\s*[\]}])', r'\1', json_text)
    json_text = json_text.replace('\n', ' ')
    json_text = re.sub(r'\s+', ' ', json_text)
    
    return json_text.strip()


def extract_json_from_response(response_text: str) -> str:
    """Extract and repair JSON from LLM response."""
    if not response_text or not response_text.strip():
        return '{"Common_Fields": {}, "Target_Companies": []}'
    
    response_text = response_text.strip()
    
    json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        json_text = json_match.group(1).strip()
    elif re.search(r'\{[\s\S]*"Target_Companies"[\s\S]*', response_text, re.DOTALL):
        json_match = re.search(r'\{[\s\S]*\}', response_text, re.DOTALL)
        json_text = json_match.group(0).strip() if json_match else response_text
    else:
        json_text = response_text
    
    repaired_json = repair_json(json_text)
    
    try:
        json.loads(repaired_json)
        return repaired_json
    except json.JSONDecodeError:
        return '{"Common_Fields": {}, "Target_Companies": []}'


def expand_companies_with_common_fields(data: Dict) -> List[Dict]:
    """
    Expand companies by applying common fields to each company.
    This converts the optimized structure back to the full format if needed.
    """
    if not isinstance(data, dict):
        return []
    
    common_fields = data.get("Common_Fields", {})
    companies = data.get("Target_Companies", [])
    
    if not isinstance(companies, list):
        return []
    
    expanded_companies = []
    for company in companies:
        if not isinstance(company, dict):
            continue
        
        company_name = str(company.get("Company_Name", "")).strip()
        if not company_name:
            continue
        
        expanded_company = {
            "Company_Name": company_name,
            "Country": str(company.get("Country", "")).strip(),
            "Excluded_Countries": str(common_fields.get("Excluded_Countries", "")).strip(),
            "Target_Job_Titles": common_fields.get("Target_Job_Titles", []),
            "Company_Main_Activities": str(common_fields.get("Company_Main_Activities", "")).strip(),
            "Companies_To_Exclude": str(common_fields.get("Companies_To_Exclude", "")).strip(),
            "Business_Areas": str(common_fields.get("Business_Areas", "")).strip(),
            "Key_Interests": str(common_fields.get("Key_Interests", "")).strip()
        }
        
        expanded_companies.append(expanded_company)
    
    logger.info(f"✅ Expanded {len(expanded_companies)} companies with common fields")
    return expanded_companies


def process_md(md_content: str, bucket: str, llm_config: dict = None, 
               max_retries: int = 3, return_optimized: bool = False) -> Dict:
    """
    Process Markdown content and extract company targeting data.
    
    Args:
        md_content: Full markdown document content
        bucket: Document category/type
        llm_config: Optional LLM configuration overrides
        max_retries: Number of retry attempts
        return_optimized: If True, returns optimized structure with common fields separate
                         If False, returns expanded list with common fields applied to each company
    
    Returns:
        If return_optimized=True: Dict with "Common_Fields" and "Target_Companies"
        If return_optimized=False: List of company dicts with all fields
    """
    if not md_content or not md_content.strip():
        logger.warning("Empty markdown content provided")
        return {"Common_Fields": {}, "Target_Companies": []} if return_optimized else []
    
    logger.info(f"{'='*60}")
    logger.info(f"🚀 Starting Company Targeting Extraction")
    logger.info(f"📁 Document Type: {bucket}")
    logger.info(f"📄 Content Size: {len(md_content)} chars")
    logger.info(f"{'='*60}")
    
    model = initialize_llm(llm_config)
    if not model:
        logger.error("❌ No LLM model available")
        return {"Common_Fields": {}, "Target_Companies": []} if return_optimized else []
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                logger.info(f"🔄 Retry attempt {attempt + 1}/{max_retries}")
            
            prompt = create_extraction_prompt(md_content, bucket)
            
            logger.info("🔄 Calling Gemini API...")
            response = model.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"✅ Response received: {len(response_text)} chars")
            
            with open("/home/atharva/Sales_Explorer/backend/llm_output.txt", "w") as f:
                logger.info("Writing LLM output to llm_output.txt")
                f.write(response_text)
            json_text = extract_json_from_response(response_text)
            
            try:
                parsed_data = json.loads(json_text)
                
                if isinstance(parsed_data, dict):
                    companies = parsed_data.get("Target_Companies", [])
                    num_companies = len(companies)
                    
                    if num_companies > 0:
                        logger.info(f"✅ Extracted {num_companies} companies")
                        
                        common = parsed_data.get("Common_Fields", {})
                        logger.info(f"📋 Common Fields:")
                        logger.info(f"   • Job Titles: {len(common.get('Target_Job_Titles', []))}")
                        logger.info(f"   • Excluded Countries: {common.get('Excluded_Countries', '')[:50]}")
                        
                        if return_optimized:
                            return parsed_data
                        else:
                            return expand_companies_with_common_fields(parsed_data)
                    else:
                        logger.warning(f"⚠️ No companies found")
                        if attempt < max_retries - 1:
                            continue
                        return {"Common_Fields": {}, "Target_Companies": []} if return_optimized else []
            
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON Parse Error: {e}")
                if attempt < max_retries - 1:
                    continue
                return {"Common_Fields": {}, "Target_Companies": []} if return_optimized else []
        
        except Exception as e:
            logger.error(f"❌ Error during processing: {e}")
            if attempt < max_retries - 1:
                continue
            return {"Common_Fields": {}, "Target_Companies": []} if return_optimized else []
    
    logger.info(f"{'='*60}\n")
    return {"Common_Fields": {}, "Target_Companies": []} if return_optimized else []