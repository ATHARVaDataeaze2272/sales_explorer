





from pydantic import BaseModel, Field
from typing import Optional, Literal
from matching.embeddings import EmbeddingService
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
from pathlib import Path
import io
import zipfile
import logging
import re
import csv
import concurrent.futures
from typing import Dict, List
import os
from datetime import datetime
import pandas as pd
import hashlib
import enum
import mammoth
from weasyprint import HTML
import tempfile
from pathlib import Path
from docx2pdf import convert
import tempfile
import shutil
from fastapi.responses import FileResponse
import tempfile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime


# Adjusted import paths
from ocr.parser import OptimizedDoclingParser,parse_pdf_fast
from llm.llm_processor import process_md
from excel_generator import generate_excel_report

# Database imports
from database.config import init_database, get_db, db_manager
from database.repository import (
    DocumentRepository, 
    ClientCompanyRepository, 
    ClientUploadProfileRepository,
    ProspectRepository,
    get_company_repository
)
from database.models import DocumentStatus, DocumentType, ClientUploadProfile, Prospects,ClientProspectMatch

from api.matching_endpoints import router as matching_router
from matching.embeddings import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="Document Processing API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MAX_FILE_SIZE = 50 * 1024 * 1024  

# Create directories
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OCR_CACHE_DIR = Path("./ocr_cache")
OCR_CACHE_DIR.mkdir(exist_ok=True)






# def convert_docx_to_pdf(docx_path: str) -> str:
#     """
#     Convert DOCX to PDF using mammoth (docx->html) + weasyprint (html->pdf)
#     Returns: Path to generated PDF file
#     """
#     try:
#         docx_path = Path(docx_path)
#         temp_dir = tempfile.mkdtemp()
        
#         # Step 1: Convert DOCX to HTML using mammoth
#         with open(docx_path, 'rb') as docx_file:
#             result = mammoth.convert_to_html(docx_file)
#             html_content = result.value
            
#             if result.messages:
#                 log.warning(f"Mammoth warnings: {result.messages}")
        
#         # Step 2: Add basic styling to HTML
#         styled_html = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <style>
#                 body {{
#                     font-family: Arial, sans-serif;
#                     margin: 40px;
#                     line-height: 1.6;
#                 }}
#                 table {{
#                     border-collapse: collapse;
#                     width: 100%;
#                     margin: 20px 0;
#                 }}
#                 th, td {{
#                     border: 1px solid #ddd;
#                     padding: 8px;
#                     text-align: left;
#                 }}
#                 th {{
#                     background-color: #f2f2f2;
#                 }}
#             </style>
#         </head>
#         <body>
#             {html_content}
#         </body>
#         </html>
#         """
        
#         # Step 3: Convert HTML to PDF using weasyprint
#         pdf_filename = docx_path.stem + '.pdf'
#         pdf_path = Path(temp_dir) / pdf_filename
        
#         HTML(string=styled_html).write_pdf(str(pdf_path))
        
#         if not pdf_path.exists():
#             raise Exception(f"PDF file not created: {pdf_path}")
        
#         log.info(f"✅ Successfully converted DOCX to PDF using mammoth+weasyprint")
#         return str(pdf_path)
        
#     except Exception as e:
#         log.error(f"Failed to convert DOCX to PDF: {e}")
#         raise

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    log.info("🚀 Starting application...")
    try:
        init_database()
        log.info("✅ Database initialized successfully")
    except Exception as e:
        log.error(f"❌ Failed to initialize database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    log.info("🛑 Shutting down application...")
    db_manager.close()

# def validate_excluded_pages(excluded_pages_json: str) -> Dict[str, str]:
#     """Validate and parse excluded pages JSON"""
#     try:
#         cleaned_json = re.sub(r"'([^']*)'", r'"\1"', excluded_pages_json)
#         excluded_pages = json.loads(cleaned_json)
#         if not isinstance(excluded_pages, dict):
#             raise ValueError("excluded_pages_json must be a dict")
#         return excluded_pages
#     except (json.JSONDecodeError, ValueError) as e:
#         log.error(f"Invalid excluded_pages_json: {e}")
#         raise HTTPException(400, f"Invalid excluded_pages_json: {e}")
    


# def generate_embeddings_for_document(
#     document_id: int,
#     document_type: str,
#     profile_id: Optional[int] = None,
#     prospect_ids: Optional[List[int]] = None
# ):
#     """
#     Background task to generate embeddings after document processing.
    
#     Args:
#         document_id: Document ID
#         document_type: 'clients' or 'prospects'
#         profile_id: Client profile ID (for clients)
#         prospect_ids: List of prospect IDs (for prospects)
#     """
#     db = db_manager.get_session()
#     try:
#         service = EmbeddingService(batch_size=32)
        
#         if document_type == "clients" and profile_id:
#             log.info(f"🔄 Generating embeddings for client profile {profile_id}")
#             success = service.generate_client_embeddings(
#                 db=db,
#                 profile_id=profile_id,
#                 regenerate=False
#             )
#             if success:
#                 log.info(f"✅ Client embeddings generated for profile {profile_id}")
#             else:
#                 log.error(f"❌ Failed to generate client embeddings for profile {profile_id}")
        
#         elif document_type == "prospects" and prospect_ids:
#             log.info(f"🔄 Generating embeddings for {len(prospect_ids)} prospects")
#             success_count = 0
#             for prospect_id in prospect_ids:
#                 success = service.generate_prospect_embeddings(
#                     db=db,
#                     prospect_id=prospect_id,
#                     regenerate=False
#                 )
#                 if success:
#                     success_count += 1
            
#             log.info(f"✅ Generated embeddings for {success_count}/{len(prospect_ids)} prospects")
    
#     except Exception as e:
#         log.error(f"❌ Error generating embeddings for document {document_id}: {e}")
#         import traceback
#         log.error(f"Traceback:\n{traceback.format_exc()}")
#     finally:
#         db.close()


# @app.post("/api/process-documents")
# async def process_documents(
#     background_tasks: BackgroundTasks,
#     files: List[UploadFile] = File(...),
#     bucket: str = Form(...),
#     excluded_pages_json: str = Form(...)
# ):
#     """
#     Process uploaded PDFs with database tracking.
#     Returns ZIP file with Excel reports.
#     """
#     if not files:
#         raise HTTPException(400, "No files uploaded")

#     if bucket not in ["clients", "prospects"]:
#         raise HTTPException(400, "Invalid bucket: must be 'clients' or 'prospects'")

#     log.info(f"📦 Received {len(files)} files for processing ({bucket})")
#     excluded_pages = validate_excluded_pages(excluded_pages_json)

#     uploaded_file_paths = []
#     zip_buffer = io.BytesIO()
#     zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)



#     def process_single_file(file: UploadFile, excluded_str: str, background_tasks: BackgroundTasks):
#         """Process a single file with database tracking and deduplication"""
#         db = db_manager.get_session()
        
#         try:
#             file_ext = file.filename.lower()
#             is_pdf = file_ext.endswith('.pdf')
#             is_docx = file_ext.endswith('.docx') or file_ext.endswith('.doc')
            
#             if not (is_pdf or is_docx):
#                 log.warning(f"Skipping unsupported file: {file.filename}")
#                 return None
            
#             original_filename = file.filename
#             original_basename = Path(file.filename).stem

#             file_content = file.file.read()
#             file_size = len(file_content)
#             file.file.seek(0)

#             file_hash = hashlib.sha256(file_content).hexdigest()
#             existing_doc = DocumentRepository.check_duplicate(db=db, file_hash=file_hash)
#             if existing_doc:
#                 log.warning(f"⚠️ Duplicate file detected: {file.filename} (matches Document ID={existing_doc.id})")
#                 return {
#                     'skipped': True,
#                     'reason': 'duplicate',
#                     'original_document_id': existing_doc.id,
#                     'original_filename': existing_doc.original_filename,
#                     'filename': file.filename,
#                     'message': f'File already processed as Document ID {existing_doc.id}'
#                 }

#             doc_record = DocumentRepository.create(
#                 db=db,
#                 filename=file.filename,
#                 original_filename=file.filename,
#                 document_type=bucket,
#                 file_size=file_size,
#                 file_content=file_content,
#                 excluded_pages=excluded_str
#             )
#             log.info(f"📝 Created DB record: Document ID={doc_record.id}")

#             DocumentRepository.update_processing_status(
#                 db=db,
#                 document_id=doc_record.id,
#                 status=DocumentStatus.PROCESSING
#             )

#             uploaded_path = UPLOAD_DIR / file.filename
#             if uploaded_path.exists():
#                 timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#                 stem = uploaded_path.stem
#                 suffix = uploaded_path.suffix
#                 uploaded_path = UPLOAD_DIR / f"{stem}_{timestamp}{suffix}"

#             try:
#                 with open(uploaded_path, 'wb') as f:
#                     f.write(file_content)
#                 uploaded_file_paths.append(uploaded_path)
#                 log.info(f"💾 Saved file: {uploaded_path.name}")
#             except Exception as e:
#                 log.error(f"Failed to save file: {e}")
#                 DocumentRepository.update_processing_status(
#                     db=db,
#                     document_id=doc_record.id,
#                     status=DocumentStatus.FAILED,
#                     error_message=str(e)
#                 )
#                 return None

#             log.info(f"🔄 Processing {uploaded_path.name}")

#             processing_path = uploaded_path
#             converted_from_docx = False
            
#             if is_docx:
#                 log.info(f"🔄 Converting DOCX to PDF: {file.filename}")
#                 try:
#                     pdf_path = convert_docx_to_pdf(str(uploaded_path))
#                     processing_path = Path(pdf_path)
#                     converted_from_docx = True 
#                     log.info(f"✅ Converted to PDF: {processing_path.name}")
#                 except Exception as e:
#                     log.error(f"DOCX conversion failed: {e}")
#                     DocumentRepository.update_processing_status(
#                         db=db,
#                         document_id=doc_record.id,
#                         status=DocumentStatus.FAILED,
#                         error_message=f"DOCX conversion failed: {str(e)}"
#                     )
#                     return None

#             try:
#                 parser = OptimizedDoclingParser(
#                     ocr_enabled=True,
#                     image_scale=2.0,
#                     extract_images=False,
#                     parallel_processing=True
#                 )

#                 ocr_result = parser.parse_document(
#                     str(uploaded_path),
#                     output_dir=str(OCR_CACHE_DIR),
#                     excluded_pages=excluded_str
#                 )

#                 md_content = ocr_result.get('markdown_content', '')
#                 cached_md_path = ocr_result.get('cached_md_path', '')

#                 DocumentRepository.update_processing_status(
#                     db=db,
#                     document_id=doc_record.id,
#                     status=DocumentStatus.PROCESSING,
#                     ocr_cached=Path(cached_md_path).exists() if cached_md_path else False,
#                     ocr_cache_path=cached_md_path,
#                     markdown_length=len(md_content)
#                 )

#                 if not md_content:
#                     raise ValueError("No content extracted from document")

#                 log.info(f"📄 Markdown length: {len(md_content)} chars")

#                 file_data = process_md(md_content, bucket)

#                 if not file_data or len(file_data) == 0:
#                     log.warning(f"⚠️ No entities extracted from {uploaded_path.name}")
#                     DocumentRepository.update_processing_status(
#                         db=db,
#                         document_id=doc_record.id,
#                         status=DocumentStatus.COMPLETED,
#                         entities_extracted=0,
#                         extraction_success=False
#                     )
#                     return None

#                 log.info(f"✅ Extracted {len(file_data)} entities")

#                 excel_data = []
#                 if bucket == "clients":
#                     profile = ClientUploadProfileRepository.create(
#                         db=db,
#                         document_id=doc_record.id,
#                         common_data={
#                             'Key_Interests': file_data[0].get('Key_Interests', ''),
#                             'Target_Job_Titles': file_data[0].get('Target_Job_Titles', []),
#                             'Business_Areas': file_data[0].get('Business_Areas', ''),
#                             'Company_Main_Activities': file_data[0].get('Company_Main_Activities', ''),
#                             'Companies_To_Exclude': file_data[0].get('Companies_To_Exclude', ''),
#                             'Excluded_Countries': file_data[0].get('Excluded_Countries', '')
#                         }
#                     )
#                     log.info(f"✅ Created client profile: ID={profile.id}")

#                     # Schedule embedding generation in background
#                     background_tasks.add_task(
#                         generate_embeddings_for_document,
#                         document_id=doc_record.id,
#                         document_type="clients",
#                         profile_id=profile.id,
#                         prospect_ids=None
#                     )
#                     log.info(f"📋 Scheduled embedding generation for client profile {profile.id}")

#                     companies = ClientCompanyRepository.bulk_create(
#                         db=db,
#                         profile_id=profile.id,
#                         companies_data=[
#                             {
#                                 'Company_Name': item.get('Company_Name', ''),
#                                 'Country': item.get('Country', ''),
#                                 'City': item.get('City', ''),
#                                 'source_file': file.filename
#                             }
#                             for item in file_data
#                         ]
#                     )

#                     for company in companies:
#                         excel_data.append({
#                             'Company_Name': company.company_name,
#                             'Country': company.country,
#                             'City': company.city if hasattr(company, 'city') else '',
#                             'Key_Interests': profile.key_interests,
#                             'Target_Job_Titles': profile.target_job_titles,
#                             'Business_Areas': profile.business_areas,
#                             'Company_Main_Activities': profile.company_main_activities,
#                             'Companies_To_Exclude': profile.companies_to_exclude,
#                             'Excluded_Countries': profile.excluded_countries,
#                             'source_file': file.filename
#                         })
#                 else:  # prospects
#                     prospects_data = [
#                         {
#                             'Reg ID': item.get('Reg_ID', ''),
#                             'Reg Status': item.get('Reg_Status', ''),
#                             'Create Account Date': item.get('Create_Account_Date', None),
#                             'First Name': item.get('First_Name', ''),
#                             'Last Name': item.get('Last_Name', ''),
#                             'Second Last Name': item.get('Second_Last_Name', ''),
#                             'Attendee Email Address': item.get('Attendee_Email', ''),
#                             'Mobile': item.get('Mobile', ''),
#                             'Company': item.get('Company_Name', ''),
#                             'Job Title': item.get('Job_Title', ''),
#                             'Country': item.get('Country', ''),
#                             'Region': item.get('Region', ''),
#                             'Continent': item.get('Continent', ''),
#                             'Current and Latest Pass Type': item.get('Pass_Type', ''),
#                             'Networking / Show Me': item.get('Networking_Show_Me', ''),
#                             'Enhanced Networking': item.get('Enhanced_Networking', ''),
#                             'Job function': item.get('Job_Function', ''),
#                             'Responsibility': item.get('Responsibility', ''),
#                             'Company Main Activity': item.get('Company_Main_Activities', ''),
#                             'Area of Interests': item.get('Key_Interests', ''),
#                             'source_file': file.filename
#                         }
#                         for item in file_data
#                     ]

#                     prospects = ProspectRepository.bulk_create(
#                         db=db,
#                         document_id=doc_record.id,
#                         prospects_data=prospects_data
#                     )
                    
#                     # Schedule embedding generation in background
#                     prospect_ids = [p.id for p in prospects]
#                     background_tasks.add_task(
#                         generate_embeddings_for_document,
#                         document_id=doc_record.id,
#                         document_type="prospects",
#                         profile_id=None,
#                         prospect_ids=prospect_ids
#                     )
#                     log.info(f"📋 Scheduled embedding generation for {len(prospect_ids)} prospects")

#                     excel_data = [
#                         {
#                             'Reg ID': p.reg_id,
#                             'Reg Status': p.reg_status,
#                             'Create Account Date': p.create_account_date.isoformat() if p.create_account_date else '',
#                             'First Name': p.first_name,
#                             'Last Name': p.last_name,
#                             'Second Last Name': p.second_last_name,
#                             'Attendee Email Address': p.attendee_email,
#                             'Mobile': p.mobile,
#                             'Company': p.company_name,
#                             'Job Title': p.job_title,
#                             'Country': p.country,
#                             'Region': p.region,
#                             'Continent': p.continent,
#                             'Current and Latest Pass Type': p.pass_type,
#                             'Networking / Show Me': p.networking_show_me,
#                             'Enhanced Networking': p.enhanced_networking,
#                             'Job function': p.job_function,
#                             'Responsibility': p.responsibility,
#                             'Company Main Activity': p.company_main_activity,
#                             'Area of Interests': p.area_of_interests,
#                             'source_file': p.source_file
#                         }
#                         for p in prospects
#                     ]

#                 log.info(f"✅ Created {len(excel_data)} records")

#                 excel_filename = f"report_{original_basename}.xlsx"
#                 excel_path = generate_excel_report(excel_data, excel_filename)

#                 if not excel_path:
#                     raise ValueError("Excel generation failed")

#                 log.info(f"✅ Excel generated: {excel_filename}")

#                 DocumentRepository.update_processing_status(
#                     db=db,
#                     document_id=doc_record.id,
#                     status=DocumentStatus.COMPLETED,
#                     entities_extracted=len(excel_data),
#                     extraction_success=True,
#                     excel_filename=excel_filename,
#                     excel_path=str(excel_path)
#                 )

#                 return {
#                     'document_id': doc_record.id,
#                     'excel_path': excel_path,
#                     'excel_filename': excel_filename,
#                     'source_filename': original_filename,
#                     'original_basename': original_basename,
#                     'entities_count': len(excel_data),
#                     'skipped': False,
#                     'converted_from_docx': converted_from_docx
#                 }

#             except Exception as e:
#                 log.error(f"Failed to process {uploaded_path.name}: {e}")
#                 import traceback
#                 log.error(f"Traceback:\n{traceback.format_exc()}")
                
#                 DocumentRepository.update_processing_status(
#                     db=db,
#                     document_id=doc_record.id,
#                     status=DocumentStatus.FAILED,
#                     error_message=str(e)
#                 )
#                 return None
        
#         finally:
#             db.close()



#     try:
#         with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
#             futures = []
#             for file in files:
#                 excluded_str = excluded_pages.get(file.filename, "")
#                 futures.append(executor.submit(process_single_file, file, excluded_str, background_tasks))

#             excel_count = 0
#             processed_documents = []
            
#             for future in concurrent.futures.as_completed(futures):
#                 result = future.result()
                
#                 if result and result.get('skipped'):
#                     log.info(f"⏭️ Skipped duplicate: {result['filename']} (original: Document ID {result['original_document_id']})")
#                     continue
                
#                 if result and result.get('excel_path'):
#                     excel_path = result['excel_path']
#                     excel_filename = result['excel_filename']
                    
#                     log.info(f"📦 Adding {excel_filename} to ZIP")
                    
#                     with open(excel_path, 'rb') as f:
#                         zip_file.writestr(excel_filename, f.read())
                    
#                     excel_count += 1
#                     processed_documents.append({
#                         'document_id': result['document_id'],
#                         'filename': result['source_filename'],
#                         'entities': result['entities_count']
#                     })
                    
#                     Path(excel_path).unlink(missing_ok=True)

#             if excel_count == 0:
#                 raise HTTPException(500, "No Excel files were generated")

#             log.info(f"✅ Added {excel_count} Excel file(s) to ZIP")
#             log.info(f"📊 Processed documents: {processed_documents}")

#             zip_file.close()
#             zip_buffer.seek(0)

#         return StreamingResponse(
#             zip_buffer,
#             media_type="application/zip",
#             headers={
#                 "Content-Disposition": 'attachment; filename="reports.zip"',
#                 "Access-Control-Expose-Headers": "Content-Disposition",
#             }
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         log.error(f"Unexpected error: {e}")
#         import traceback
#         log.error(f"Traceback:\n{traceback.format_exc()}")
#         raise HTTPException(500, f"Processing failed: {str(e)}")

#     finally:
#         for path in uploaded_file_paths:
#             try:
#                 log.debug(f"🧹 Cleaned up {path.name}")
#             except Exception as e:
#                 log.warning(f"Failed to cleanup {path}: {e}")



def convert_docx_to_pdf(docx_path: str) -> str:
    """
    Fast DOCX to PDF conversion using docx2pdf
    Returns: Path to generated PDF file
    """
    try:
        from docx2pdf import convert
        
        docx_path = Path(docx_path)
        temp_dir = tempfile.mkdtemp()
        pdf_path = Path(temp_dir) / f"{docx_path.stem}.pdf"
        
        log.info(f"🔄 Converting DOCX to PDF: {docx_path.name}")
        
        # Much faster than mammoth + weasyprint
        convert(str(docx_path), str(pdf_path))
        
        if not pdf_path.exists():
            raise Exception(f"PDF file not created: {pdf_path}")
        
        log.info(f"✅ Successfully converted DOCX to PDF")
        return str(pdf_path)
        
    except ImportError:
        log.warning("docx2pdf not available, falling back to mammoth + weasyprint")
        return convert_docx_to_pdf_fallback(docx_path)
    except Exception as e:
        log.error(f"Failed to convert DOCX to PDF: {e}")
        raise


def convert_docx_to_pdf_fallback(docx_path: str) -> str:
    """
    Fallback DOCX to PDF conversion using mammoth + weasyprint
    """
    try:
        import mammoth
        from weasyprint import HTML
        import tempfile
        
        docx_path = Path(docx_path)
        temp_dir = tempfile.mkdtemp()
        
        # Convert DOCX to HTML
        with open(docx_path, 'rb') as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value
            
            if result.messages:
                log.warning(f"Mammoth warnings: {result.messages}")
        
        # Add basic styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        pdf_filename = docx_path.stem + '.pdf'
        pdf_path = Path(temp_dir) / pdf_filename
        
        HTML(string=styled_html).write_pdf(str(pdf_path))
        
        if not pdf_path.exists():
            raise Exception(f"PDF file not created: {pdf_path}")
        
        log.info(f"✅ Successfully converted DOCX to PDF using fallback method")
        return str(pdf_path)
        
    except Exception as e:
        log.error(f"Failed to convert DOCX to PDF with fallback: {e}")
        raise


def validate_excluded_pages(excluded_pages_json: str) -> Dict[str, str]:
    """Validate and parse excluded pages JSON"""
    try:
        cleaned_json = re.sub(r"'([^']*)'", r'"\1"', excluded_pages_json)
        excluded_pages = json.loads(cleaned_json)
        if not isinstance(excluded_pages, dict):
            raise ValueError("excluded_pages_json must be a dict")
        return excluded_pages
    except (json.JSONDecodeError, ValueError) as e:
        log.error(f"Invalid excluded_pages_json: {e}")
        raise HTTPException(400, f"Invalid excluded_pages_json: {e}")


def get_cached_ocr_content(file_hash: str, excluded_str: str) -> str:
    """
    Check if OCR result is cached and return it
    Returns empty string if not cached
    """
    try:
        cache_key = hashlib.md5(f"{file_hash}_{excluded_str}".encode()).hexdigest()
        cached_md_path = OCR_CACHE_DIR / f"{cache_key}.md"
        
        if cached_md_path.exists():
            log.info(f"📋 Using cached OCR result")
            return cached_md_path.read_text(encoding='utf-8')
        
        return ""
    except Exception as e:
        log.warning(f"Failed to read cache: {e}")
        return ""


def save_ocr_cache(file_hash: str, excluded_str: str, content: str) -> None:
    """Save OCR result to cache"""
    try:
        cache_key = hashlib.md5(f"{file_hash}_{excluded_str}".encode()).hexdigest()
        cached_md_path = OCR_CACHE_DIR / f"{cache_key}.md"
        cached_md_path.write_text(content, encoding='utf-8')
        log.info(f"💾 Cached OCR result")
    except Exception as e:
        log.warning(f"Failed to save cache: {e}")


def generate_embeddings_for_document(
    document_id: int,
    document_type: str,
    profile_id: Optional[int] = None,
    prospect_ids: Optional[List[int]] = None
):
    """
    Background task to generate embeddings after document processing.
    """
    db = db_manager.get_session()
    try:
        from matching.embeddings import EmbeddingService
        service = EmbeddingService(batch_size=32)
        
        if document_type == "clients" and profile_id:
            log.info(f"🔄 Generating embeddings for client profile {profile_id}")
            success = service.generate_client_embeddings(
                db=db,
                profile_id=profile_id,
                regenerate=False
            )
            if success:
                log.info(f"✅ Client embeddings generated for profile {profile_id}")
            else:
                log.error(f"❌ Failed to generate client embeddings for profile {profile_id}")
        
        elif document_type == "prospects" and prospect_ids:
            log.info(f"🔄 Generating embeddings for {len(prospect_ids)} prospects")
            success_count = 0
            for prospect_id in prospect_ids:
                success = service.generate_prospect_embeddings(
                    db=db,
                    prospect_id=prospect_id,
                    regenerate=False
                )
                if success:
                    success_count += 1
            
            log.info(f"✅ Generated embeddings for {success_count}/{len(prospect_ids)} prospects")
    
    except Exception as e:
        log.error(f"❌ Error generating embeddings for document {document_id}: {e}")
        import traceback
        log.error(f"Traceback:\n{traceback.format_exc()}")
    finally:
        db.close()


def process_single_file(file: UploadFile, excluded_str: str, bucket: str, background_tasks: BackgroundTasks):

    """
    Process a single file with database tracking, deduplication, and optimization

     Args:
        file: Uploaded file
        excluded_str: Pages to exclude from processing
        bucket: Document type ('clients' or 'prospects')
        background_tasks: FastAPI background tasks

    """
    db = db_manager.get_session()
    
    try:
        # Validate file type
        file_ext = file.filename.lower()
        is_pdf = file_ext.endswith('.pdf')
        is_docx = file_ext.endswith('.docx') or file_ext.endswith('.doc')
        
        if not (is_pdf or is_docx):
            log.warning(f"⏭️ Skipping unsupported file: {file.filename}")
            return None
        
        original_filename = file.filename
        original_basename = Path(file.filename).stem

        # Read file content
        file_content = file.file.read()
        file_size = len(file_content)
        file.file.seek(0)

        # Check file size limit
        if file_size > MAX_FILE_SIZE:
            log.error(f"❌ File too large: {file.filename} ({file_size} bytes)")
            return {
                'skipped': True,
                'reason': 'too_large',
                'filename': file.filename,
                'message': f'File exceeds {MAX_FILE_SIZE} bytes limit'
            }

        # Check for duplicates
        file_hash = hashlib.sha256(file_content).hexdigest()
        existing_doc = DocumentRepository.check_duplicate(db=db, file_hash=file_hash)
        
        if existing_doc:
            log.warning(f"⚠️ Duplicate file detected: {file.filename} (matches Document ID={existing_doc.id})")
            return {
                'skipped': True,
                'reason': 'duplicate',
                'original_document_id': existing_doc.id,
                'original_filename': existing_doc.original_filename,
                'filename': file.filename,
                'message': f'File already processed as Document ID {existing_doc.id}'
            }

        # Create database record
        doc_record = DocumentRepository.create(
            db=db,
            filename=file.filename,
            original_filename=file.filename,
            document_type=bucket,
            file_size=file_size,
            file_content=file_content,
            excluded_pages=excluded_str
        )
        log.info(f"📝 Created DB record: Document ID={doc_record.id}")

        # Update status to processing
        DocumentRepository.update_processing_status(
            db=db,
            document_id=doc_record.id,
            status=DocumentStatus.PROCESSING
        )

        # Save file to disk
        uploaded_path = UPLOAD_DIR / file.filename
        if uploaded_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            stem = uploaded_path.stem
            suffix = uploaded_path.suffix
            uploaded_path = UPLOAD_DIR / f"{stem}_{timestamp}{suffix}"

        try:
            with open(uploaded_path, 'wb') as f:
                f.write(file_content)
            log.info(f"💾 Saved file: {uploaded_path.name}")
        except Exception as e:
            log.error(f"Failed to save file: {e}")
            DocumentRepository.update_processing_status(
                db=db,
                document_id=doc_record.id,
                status=DocumentStatus.FAILED,
                error_message=str(e)
            )
            return None

        # Convert DOCX to PDF if needed
        processing_path = uploaded_path
        converted_from_docx = False
        
        if is_docx:
            log.info(f"🔄 Converting DOCX to PDF: {file.filename}")
            try:
                pdf_path = convert_docx_to_pdf(str(uploaded_path))
                processing_path = Path(pdf_path)
                converted_from_docx = True
                log.info(f"✅ Converted to PDF: {processing_path.name}")
            except Exception as e:
                log.error(f"DOCX conversion failed: {e}")
                DocumentRepository.update_processing_status(
                    db=db,
                    document_id=doc_record.id,
                    status=DocumentStatus.FAILED,
                    error_message=f"DOCX conversion failed: {str(e)}"
                )
                return None

        # Check OCR cache first
        md_content = get_cached_ocr_content(file_hash, excluded_str)
        cached_md_path = ""
        ocr_cached = False

        if md_content:
            log.info(f"✅ Using cached OCR content")
            ocr_cached = True
        else:
            # Run OCR processing
            log.info(f"🔄 Processing {processing_path.name}")
            try:
                parser = OptimizedDoclingParser(
                    ocr_enabled=True,
                    image_scale=1.0,  # Reduced from 2.0 for faster processing
                    extract_images=False,
                    parallel_processing=True
                )

                ocr_result = parser.parse_document(
                    str(processing_path),
                    output_dir=str(OCR_CACHE_DIR),
                    excluded_pages=excluded_str
                )

                md_content = ocr_result.get('markdown_content', '')
                cached_md_path = ocr_result.get('cached_md_path', '')
                
                # Save to cache
                if md_content:
                    save_ocr_cache(file_hash, excluded_str, md_content)

            except Exception as e:
                log.error(f"OCR processing failed: {e}")
                DocumentRepository.update_processing_status(
                    db=db,
                    document_id=doc_record.id,
                    status=DocumentStatus.FAILED,
                    error_message=f"OCR failed: {str(e)}"
                )
                return None

        # Update DB with OCR status
        DocumentRepository.update_processing_status(
            db=db,
            document_id=doc_record.id,
            status=DocumentStatus.PROCESSING,
            ocr_cached=ocr_cached,
            ocr_cache_path=cached_md_path,
            markdown_length=len(md_content)
        )

        if not md_content:
            raise ValueError("No content extracted from document")

        log.info(f"📄 Markdown length: {len(md_content)} chars")

        # LLM Processing
        file_data = process_md(md_content, bucket)

        if not file_data or len(file_data) == 0:
            log.warning(f"⚠️ No entities extracted from {processing_path.name}")
            DocumentRepository.update_processing_status(
                db=db,
                document_id=doc_record.id,
                status=DocumentStatus.COMPLETED,
                entities_extracted=0,
                extraction_success=False
            )
            return None

        log.info(f"✅ Extracted {len(file_data)} entities")

        # Save to database based on bucket type
        excel_data = []
        profile_id = None
        prospect_ids = []
        
        if bucket == "clients":
            # Create client profile
            profile = ClientUploadProfileRepository.create(
                db=db,
                document_id=doc_record.id,
                common_data={
                    'Key_Interests': file_data[0].get('Key_Interests', ''),
                    'Target_Job_Titles': file_data[0].get('Target_Job_Titles', []),
                    'Business_Areas': file_data[0].get('Business_Areas', ''),
                    'Company_Main_Activities': file_data[0].get('Company_Main_Activities', ''),
                    'Companies_To_Exclude': file_data[0].get('Companies_To_Exclude', ''),
                    'Excluded_Countries': file_data[0].get('Excluded_Countries', '')
                }
            )
            profile_id = profile.id
            log.info(f"✅ Created client profile: ID={profile.id}")

            # Create companies
            companies = ClientCompanyRepository.bulk_create(
                db=db,
                profile_id=profile.id,
                companies_data=[
                    {
                        'Company_Name': item.get('Company_Name', ''),
                        'Country': item.get('Country', ''),
                        'City': item.get('City', ''),
                        'source_file': file.filename
                    }
                    for item in file_data
                ]
            )

            # Prepare Excel data
            for company in companies:
                excel_data.append({
                    'Company_Name': company.company_name,
                    'Country': company.country,
                    'City': company.city if hasattr(company, 'city') else '',
                    'Key_Interests': profile.key_interests,
                    'Target_Job_Titles': profile.target_job_titles,
                    'Business_Areas': profile.business_areas,
                    'Company_Main_Activities': profile.company_main_activities,
                    'Companies_To_Exclude': profile.companies_to_exclude,
                    'Excluded_Countries': profile.excluded_countries,
                    'source_file': file.filename
                })
            
        else:  # prospects
            # Create prospects
            prospects_data = [
                {
                    'Reg ID': item.get('Reg_ID', ''),
                    'Reg Status': item.get('Reg_Status', ''),
                    'Create Account Date': item.get('Create_Account_Date', None),
                    'First Name': item.get('First_Name', ''),
                    'Last Name': item.get('Last_Name', ''),
                    'Second Last Name': item.get('Second_Last_Name', ''),
                    'Attendee Email Address': item.get('Attendee_Email', ''),
                    'Mobile': item.get('Mobile', ''),
                    'Company': item.get('Company_Name', ''),
                    'Job Title': item.get('Job_Title', ''),
                    'Country': item.get('Country', ''),
                    'Region': item.get('Region', ''),
                    'Continent': item.get('Continent', ''),
                    'Current and Latest Pass Type': item.get('Pass_Type', ''),
                    'Networking / Show Me': item.get('Networking_Show_Me', ''),
                    'Enhanced Networking': item.get('Enhanced_Networking', ''),
                    'Job function': item.get('Job_Function', ''),
                    'Responsibility': item.get('Responsibility', ''),
                    'Company Main Activity': item.get('Company_Main_Activities', ''),
                    'Area of Interests': item.get('Key_Interests', ''),
                    'source_file': file.filename
                }
                for item in file_data
            ]

            prospects = ProspectRepository.bulk_create(
                db=db,
                document_id=doc_record.id,
                prospects_data=prospects_data
            )
            
            prospect_ids = [p.id for p in prospects]
            
            # Prepare Excel data
            excel_data = [
                {
                    'Reg ID': p.reg_id,
                    'Reg Status': p.reg_status,
                    'Create Account Date': p.create_account_date.isoformat() if p.create_account_date else '',
                    'First Name': p.first_name,
                    'Last Name': p.last_name,
                    'Second Last Name': p.second_last_name,
                    'Attendee Email Address': p.attendee_email,
                    'Mobile': p.mobile,
                    'Company': p.company_name,
                    'Job Title': p.job_title,
                    'Country': p.country,
                    'Region': p.region,
                    'Continent': p.continent,
                    'Current and Latest Pass Type': p.pass_type,
                    'Networking / Show Me': p.networking_show_me,
                    'Enhanced Networking': p.enhanced_networking,
                    'Job function': p.job_function,
                    'Responsibility': p.responsibility,
                    'Company Main Activity': p.company_main_activity,
                    'Area of Interests': p.area_of_interests,
                    'source_file': p.source_file
                }
                for p in prospects
            ]

        log.info(f"✅ Created {len(excel_data)} records")

        # Schedule embedding generation in background
        background_tasks.add_task(
            generate_embeddings_for_document,
            document_id=doc_record.id,
            document_type=bucket,
            profile_id=profile_id,
            prospect_ids=prospect_ids
        )
        log.info(f"📋 Scheduled embedding generation")

        # Generate Excel report
        excel_filename = f"report_{original_basename}.xlsx"
        excel_path = generate_excel_report(excel_data, excel_filename)

        if not excel_path:
            raise ValueError("Excel generation failed")

        log.info(f"✅ Excel generated: {excel_filename}")

        # Update final status
        DocumentRepository.update_processing_status(
            db=db,
            document_id=doc_record.id,
            status=DocumentStatus.COMPLETED,
            entities_extracted=len(excel_data),
            extraction_success=True,
            excel_filename=excel_filename,
            excel_path=str(excel_path)
        )

        return {
            'document_id': doc_record.id,
            'excel_path': excel_path,
            'excel_filename': excel_filename,
            'source_filename': original_filename,
            'original_basename': original_basename,
            'entities_count': len(excel_data),
            'skipped': False,
            'converted_from_docx': converted_from_docx
        }

    except Exception as e:
        log.error(f"Failed to process file: {e}")
        import traceback
        log.error(f"Traceback:\n{traceback.format_exc()}")
        
        if 'doc_record' in locals():
            DocumentRepository.update_processing_status(
                db=db,
                document_id=doc_record.id,
                status=DocumentStatus.FAILED,
                error_message=str(e)
            )
        return None
    
    finally:
        db.close()


@app.post("/api/process-documents")
async def process_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    bucket: str = Form(...),
    excluded_pages_json: str = Form(...)
):
    """
    Process uploaded PDFs/DOCX with database tracking and optimization.
    Returns ZIP file with Excel reports.
    """
    if not files:
        raise HTTPException(400, "No files uploaded")

    if bucket not in ["clients", "prospects"]:
        raise HTTPException(400, "Invalid bucket: must be 'clients' or 'prospects'")

    log.info(f"📦 Received {len(files)} files for processing ({bucket})")
    excluded_pages = validate_excluded_pages(excluded_pages_json)

    uploaded_file_paths = []
    zip_buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)

    try:
        # Process files in parallel with limited workers
        max_workers = min(4, os.cpu_count() or 1)  # Limit to 4 workers max
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for file in files:
                excluded_str = excluded_pages.get(file.filename, "")
                futures.append(executor.submit(process_single_file, file, excluded_str,bucket, background_tasks))

            excel_count = 0
            processed_documents = []
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                
                if result and result.get('skipped'):
                    log.info(f"⏭️ Skipped: {result['filename']} - {result.get('message', 'Unknown reason')}")
                    continue
                
                if result and result.get('excel_path'):
                    excel_path = result['excel_path']
                    excel_filename = result['excel_filename']
                    
                    log.info(f"📦 Adding {excel_filename} to ZIP")
                    
                    with open(excel_path, 'rb') as f:
                        zip_file.writestr(excel_filename, f.read())
                    
                    excel_count += 1
                    processed_documents.append({
                        'document_id': result['document_id'],
                        'filename': result['source_filename'],
                        'entities': result['entities_count']
                    })
                    
                    # Cleanup Excel file
                    Path(excel_path).unlink(missing_ok=True)

            if excel_count == 0:
                raise HTTPException(500, "No Excel files were generated")

            log.info(f"✅ Added {excel_count} Excel file(s) to ZIP")
            log.info(f"📊 Processed documents: {processed_documents}")

            zip_file.close()
            zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": 'attachment; filename="reports.zip"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        import traceback
        log.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(500, f"Processing failed: {str(e)}")

    finally:
        # Cleanup uploaded files
        for path in uploaded_file_paths:
            try:
                path.unlink(missing_ok=True)
                log.debug(f"🧹 Cleaned up {path.name}")
            except Exception as e:
                log.warning(f"Failed to cleanup {path}: {e}")






@app.get("/api/documents")
async def get_documents(
    document_type: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all processed documents with filters"""
    try:
        documents = DocumentRepository.get_all(
            db=db,
            document_type=document_type,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "count": len(documents),
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "document_type": doc.document_type.value,
                    "status": doc.status.value,
                    "file_size": doc.file_size,
                    "entities_extracted": doc.entities_extracted,
                    "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                    "processing_completed_at": doc.processing_completed_at.isoformat() if doc.processing_completed_at else None,
                    "error_message": doc.error_message
                }
                for doc in documents
            ]
        }
    except Exception as e:
        log.error(f"Failed to fetch documents: {e}")
        raise HTTPException(500, f"Failed to fetch documents: {str(e)}")

@app.get("/api/documents/{document_id}")
async def get_document_details(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific document"""
    try:
        doc = DocumentRepository.get_by_id(db=db, document_id=document_id)
        
        if not doc:
            raise HTTPException(404, f"Document {document_id} not found")
        
        companies = []
        if doc.document_type == DocumentType.CLIENT:
            repo = get_company_repository("clients")
            companies = repo.get_by_document(db=db, document_id=document_id)
            companies = [c.to_dict() for c in companies]
        elif doc.document_type == DocumentType.PROSPECT:
            repo = get_company_repository("prospects")
            companies = repo.get_by_document(db=db, document_id=document_id)
            companies = [c.to_dict() for c in companies]
        
        return {
            "document": {
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type.value,
                "status": doc.status.value,
                "file_size": doc.file_size,
                "excluded_pages": doc.excluded_pages,
                "entities_extracted": doc.entities_extracted,
                "extraction_success": doc.extraction_success,
                "excel_filename": doc.excel_filename,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                "processing_completed_at": doc.processing_completed_at.isoformat() if doc.processing_completed_at else None,
                "error_message": doc.error_message
            },
            "companies": companies,
            "companies_count": len(companies)
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to fetch document details: {e}")
        raise HTTPException(500, f"Failed to fetch document details: {str(e)}")

@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document and all associated companies"""
    try:
        success = DocumentRepository.delete(db=db, document_id=document_id)
        
        if not success:
            raise HTTPException(404, f"Document {document_id} not found")
        
        return {
            "success": True,
            "message": f"Document {document_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to delete document: {e}")
        raise HTTPException(500, f"Failed to delete document: {str(e)}")

@app.get("/api/companies/search")
async def search_companies(
    company_name: str = None,
    country: str = None,
    document_type: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search for companies across all documents"""
    try:
        if document_type and document_type not in ["clients", "prospects"]:
            raise HTTPException(400, "Invalid document_type: must be 'clients' or 'prospects'")
        
        results = []
        
        if not document_type or document_type == "clients":
            repo = get_company_repository("clients")
            client_results = repo.search(
                db=db,
                company_name=company_name,
                country=country,
                limit=limit
            )
            results.extend([{**c.to_dict(), "type": "client"} for c in client_results])
        
        if not document_type or document_type == "prospects":
            repo = get_company_repository("prospects")
            prospect_results = repo.search(
                db=db,
                company_name=company_name,
                country=country,
                limit=limit
            )
            results.extend([{**c.to_dict(), "type": "prospect"} for c in prospect_results])
        
        return {
            "count": len(results),
            "companies": results
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to search companies: {e}")
        raise HTTPException(500, f"Failed to search companies: {str(e)}")

@app.get("/api/profiles/client/{document_id}")
async def get_client_profile(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get client profile for a document"""
    try:
        profile = db.query(ClientUploadProfile).filter(
            ClientUploadProfile.document_id == document_id
        ).first()
        
        if not profile:
            raise HTTPException(404, f"Profile not found for document {document_id}")
        
        return {
            "profile": profile.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to fetch client profile: {e}")
        raise HTTPException(500, f"Failed to fetch profile: {str(e)}")

@app.put("/api/profiles/client/{profile_id}")
async def update_client_profile(
    profile_id: int,
    updated_data: dict,
    db: Session = Depends(get_db)
):
    """Update client profile"""
    try:
        profile = db.query(ClientUploadProfile).filter(
            ClientUploadProfile.id == profile_id
        ).first()
        
        if not profile:
            raise HTTPException(404, f"Profile {profile_id} not found")
        
        if 'business_areas' in updated_data:
            profile.business_areas = updated_data['business_areas']
        if 'company_main_activities' in updated_data:
            profile.company_main_activities = updated_data['company_main_activities']
        if 'key_interests' in updated_data:
            profile.key_interests = updated_data['key_interests']
        if 'target_job_titles' in updated_data:
            profile.target_job_titles = updated_data['target_job_titles']
        if 'companies_to_exclude' in updated_data:
            profile.companies_to_exclude = updated_data['companies_to_exclude']
        if 'excluded_countries' in updated_data:
            profile.excluded_countries = updated_data['excluded_countries']
        
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(profile)
        
        log.info(f"✅ Updated client profile {profile_id}")
        
        return {
            "success": True,
            "profile": profile.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to update client profile: {e}")
        db.rollback()
        raise HTTPException(500, f"Failed to update profile: {str(e)}")

@app.put("/api/companies/client/{company_id}")
async def update_client_company(
    company_id: int,
    updated_data: dict,
    db: Session = Depends(get_db)
):
    """Update client company"""
    try:
        company = db.query(ClientCompany).filter(
            ClientCompany.id == company_id
        ).first()
        
        if not company:
            raise HTTPException(404, f"Company {company_id} not found")
        
        if 'company_name' in updated_data:
            company.company_name = updated_data['company_name']
        if 'country' in updated_data:
            company.country = updated_data['country']
        if 'city' in updated_data:
            company.city = updated_data['city']
        
        company.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(company)
        
        log.info(f"✅ Updated client company {company_id}")
        
        return {
            "success": True,
            "company": company.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to update client company: {e}")
        db.rollback()
        raise HTTPException(500, f"Failed to update company: {str(e)}")

@app.delete("/api/companies/client/{company_id}")
async def delete_client_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Delete client company"""
    try:
        company = db.query(ClientCompany).filter(
            ClientCompany.id == company_id
        ).first()
        
        if not company:
            raise HTTPException(404, f"Company {company_id} not found")
        
        db.delete(company)
        db.commit()
        
        log.info(f"🗑️ Deleted client company {company_id}")
        
        return {
            "success": True,
            "message": f"Company {company_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to delete client company: {e}")
        db.rollback()
        raise HTTPException(500, f"Failed to delete company: {str(e)}")
    

@app.post("/api/upload-prospects-excel")
async def upload_prospects_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Only Excel files (.xlsx, .xls) are allowed")
    log.info(f"📊 Received Excel file: {file.filename}")
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        file_hash = hashlib.sha256(file_content).hexdigest()
        existing_doc = DocumentRepository.check_duplicate(db=db, file_hash=file_hash)
        if existing_doc:
            log.warning(f"⚠️ Duplicate file detected: {file.filename}")
            raise HTTPException(400, f"File already uploaded as Document ID {existing_doc.id}")
        
        df = pd.read_excel(io.BytesIO(file_content))
        if df.empty:
            raise HTTPException(400, "Excel file is empty")
        log.info(f"📊 Found {len(df)} rows in Excel")
        
        doc_record = DocumentRepository.create(
            db=db,
            filename=file.filename,
            original_filename=file.filename,
            document_type="prospects",
            file_size=file_size,
            file_content=file_content,
            excluded_pages=""
        )
        
        DocumentRepository.update_processing_status(
            db=db,
            document_id=doc_record.id,
            status=DocumentStatus.PROCESSING
        )
        
        prospects_data = []
        for _, row in df.iterrows():
            create_date = None
            if pd.notna(row.get('Create Account Date')):
                try:
                    create_date = pd.to_datetime(row['Create Account Date'])
                except Exception as e:
                    log.warning(f"Failed to parse date '{row['Create Account Date']}': {e}")
            if pd.isna(row.get('Company')) or pd.isna(row.get('Country')):
                raise HTTPException(400, "Excel file must contain non-empty 'Company' and 'Country' columns")
            prospects_data.append({
                'Reg ID': str(row.get('Reg ID', '')),
                'Reg Status': str(row.get('Reg Status', '')),
                'Create Account Date': create_date,
                'First Name': str(row.get('First Name', '')),
                'Last Name': str(row.get('Last Name', '')),
                'Second Last Name': str(row.get('Second Last Name', '')),
                'Attendee Email Address': str(row.get('Attendee Email Address', '')),
                'Mobile': str(row.get('Mobile', '')),
                'Company': str(row.get('Company', '')),
                'Job Title': str(row.get('Job Title', '')),
                'Country': str(row.get('Country', '')),
                'Region': str(row.get('Region', '')),
                'Continent': str(row.get('Continent', '')),
                'Current and Latest Pass Type': str(row.get('Current and Latest Pass Type', '')),
                'Networking / Show Me': str(row.get('Networking / Show Me', '')),
                'Enhanced Networking': str(row.get('Enhanced Networking', '')),
                'Job function': str(row.get('Job function', '')),
                'Responsibility': str(row.get('Responsibility', '')),
                'Company Main Activity': str(row.get('Company Main Activity', '')),
                'Area of Interests': str(row.get('Area of Interests', '')),
                'source_file': file.filename
            })
        
        prospects = ProspectRepository.bulk_create(
            db=db,
            document_id=doc_record.id,
            prospects_data=prospects_data
        )
        
        # Schedule embedding generation in background
        prospect_ids = [p.id for p in prospects]
        background_tasks.add_task(
            generate_embeddings_for_document,
            document_id=doc_record.id,
            document_type="prospects",
            profile_id=None,
            prospect_ids=prospect_ids
        )
        log.info(f"📋 Scheduled embedding generation for {len(prospect_ids)} prospects from Excel")
        
        DocumentRepository.update_processing_status(
            db=db,
            document_id=doc_record.id,
            status=DocumentStatus.COMPLETED,
            entities_extracted=len(prospects),
            extraction_success=True
        )
        
        log.info(f"✅ Successfully imported {len(prospects)} prospects from Excel")
        return {
            "success": True,
            "document_id": doc_record.id,
            "companies_imported": len(prospects),
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to process Excel: {e}")
        import traceback
        log.error(f"Traceback:\n{traceback.format_exc()}")
        if 'doc_record' in locals():
            DocumentRepository.update_processing_status(
                db=db,
                document_id=doc_record.id,
                status=DocumentStatus.FAILED,
                error_message=str(e)
            )
        raise HTTPException(500, f"Failed to process Excel: {str(e)}")




@app.get("/api/matching/export/{client_id}")
async def export_client_matches_csv(
    client_id: int,
    match_type: str = Query("all", regex="^(priority|discovery|all)$"),
    db: Session = Depends(get_db)
):
    """
    Export all matches for a client to CSV with complete prospect details.
    """
    try:
        # Get client profile
        client = db.query(ClientUploadProfile).filter(
            ClientUploadProfile.id == client_id
        ).first()

        if not client:
            raise HTTPException(404, f"Client profile {client_id} not found")

        # Build query for matches
        query = db.query(ClientProspectMatch).filter(
            ClientProspectMatch.client_profile_id == client_id
        )
        if match_type and match_type != "all":
            query = query.filter(ClientProspectMatch.match_type == match_type)

        matches = query.order_by(
            ClientProspectMatch.match_type.desc(),
            ClientProspectMatch.match_rank
        ).all()

        if not matches:
            raise HTTPException(404, "No matches found for this client")

        # Get prospect details
        prospect_ids = [m.prospect_id for m in matches]
        prospects = db.query(Prospects).filter(Prospects.id.in_(prospect_ids)).all()
        prospects_dict = {p.id: p for p in prospects}

        # Define CSV headers
        headers = [
            "Match Rank", "Match Type", "Overall Score",
            "Job Title Score", "Business Area Score", "Activity Score",
            "Status", "Reg ID", "First Name", "Last Name",
            "Email", "Mobile", "Job Title", "Company Name",
            "Country", "Region", "Continent", "Job Function",
            "Responsibility", "Company Main Activity", "Area of Interests",
            "Pass Type", "Networking/Show Me", "Enhanced Networking",
            "Reg Status", "Create Account Date", "Notes", "Rejection Reason",
            "Matched At", "Contacted At"
        ]

        # Create temp CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"client_{client_id}_matches_{timestamp}.csv"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8")

        writer = csv.writer(temp_file)
        writer.writerow(headers)

        for match in matches:
            prospect = prospects_dict.get(match.prospect_id)
            if not prospect:
                continue

            row = [
                match.match_rank,
                match.match_type or "discovery",
                float(match.overall_score) if match.overall_score else 0.0,
                float(match.job_title_score) if match.job_title_score else 0.0,
                float(match.business_area_score) if match.business_area_score else 0.0,
                float(match.activity_score) if match.activity_score else 0.0,
                match.status or "",
                prospect.reg_id or "",
                prospect.first_name or "",
                prospect.last_name or "",
                prospect.attendee_email or "",
                prospect.mobile or "",
                prospect.job_title or "",
                prospect.company_name or "",
                prospect.country or "",
                prospect.region or "",
                prospect.continent or "",
                prospect.job_function or "",
                prospect.responsibility or "",
                prospect.company_main_activity or "",
                prospect.area_of_interests or "",
                prospect.pass_type or "",
                prospect.networking_show_me or "",
                prospect.enhanced_networking or "",
                prospect.reg_status or "",
                prospect.create_account_date.isoformat() if prospect.create_account_date else "",
                match.notes or "",
                match.rejection_reason or "",
                match.matched_at.isoformat() if getattr(match, "matched_at", None) else "",
                match.contacted_at.isoformat() if getattr(match, "contacted_at", None) else "",
            ]

            writer.writerow(row)

        temp_file.close()

        log.info(f"✅ Exported {len(matches)} matches for client {client_id} to {filename}")

        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error exporting matches: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to export matches: {str(e)}")
    

@app.get("/")
async def root():
    return {
    "message": "Document Processing API with PostgreSQL is running!",
    "version": "2.0.0",
    "endpoints": {
        "process": "/api/process-documents",
        "documents": "/api/documents",
        "document_details": "/api/documents/{id}",
        "delete_document": "/api/documents/{id}",
        "search_companies": "/api/companies/search",
        "client_profile": "/api/profiles/client/{document_id}",
        "update_client_profile": "/api/profiles/client/{profile_id}",
        "update_client_company": "/api/companies/client/{company_id}",
        "delete_client_company": "/api/companies/client/{company_id}",
        "upload_prospects_excel": "/api/upload-prospects-excel",
        "generate_embeddings": "/api/embeddings/generate",
        "embedding_status": "/api/embeddings/status",
        "client_embedding": "/api/embeddings/client/{client_id}",
        "prospect_embedding": "/api/embeddings/prospect/{prospect_id}",
        "delete_all_embeddings": "/api/embeddings/all",
        "embedding_health": "/api/embeddings/health",
        "health": "/health"
    }
}
    

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connection test"""
    try:
        db.execute("SELECT 1")
        db_healthy = True
    except Exception as e:
        log.error(f"Database health check failed: {e}")
        db_healthy = False
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "upload_dir": str(UPLOAD_DIR),
        "ocr_cache_dir": str(OCR_CACHE_DIR),
        "upload_dir_exists": UPLOAD_DIR.exists(),
        "ocr_cache_exists": OCR_CACHE_DIR.exists()
    }




"""
FastAPI Endpoints for Embedding Management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Literal
import logging

from database.config import get_db
from matching.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class GenerateEmbeddingsRequest(BaseModel):
    """Request model for embedding generation"""
    type: Literal["all", "clients", "prospects"] = Field(
        default="all",
        description="Which embeddings to generate"
    )
    regenerate: bool = Field(
        default=False,
        description="Force regeneration even if embeddings exist"
    )
    batch_size: Optional[int] = Field(
        default=32,
        description="Batch size for processing",
        ge=1,
        le=100
    )


class EmbeddingGenerationResponse(BaseModel):
    """Response model for embedding generation"""
    success: bool
    message: str
    clients_processed: Optional[int] = None
    prospects_processed: Optional[int] = None
    clients_success: Optional[int] = None
    prospects_success: Optional[int] = None
    clients_errors: Optional[int] = None
    prospects_errors: Optional[int] = None
    clients_skipped: Optional[int] = None
    prospects_skipped: Optional[int] = None
    total_embeddings: Optional[int] = None


class EmbeddingStatusResponse(BaseModel):
    """Response model for embedding status"""
    clients: dict
    prospects: dict
    embedding_dimensions: int
    model_name: str


class SingleEntityRequest(BaseModel):
    """Request for single entity embedding"""
    entity_id: int = Field(..., description="ID of client profile or prospect")
    regenerate: bool = Field(default=False, description="Force regeneration")


# ============================================
# BACKGROUND TASK FUNCTIONS
# ============================================

def generate_embeddings_task(
    db: Session,
    embedding_type: str,
    regenerate: bool,
    batch_size: int
):
    """
    Background task to generate embeddings.
    This runs asynchronously to avoid blocking the API.
    """
    try:
        service = EmbeddingService(batch_size=batch_size)
        
        if embedding_type in ["all", "clients"]:
            logger.info("Starting client embedding generation in background")
            service.generate_all_client_embeddings(
                db=db,
                regenerate=regenerate,
                show_progress=False
            )
        
        if embedding_type in ["all", "prospects"]:
            logger.info("Starting prospect embedding generation in background")
            service.generate_all_prospect_embeddings(
                db=db,
                regenerate=regenerate,
                show_progress=False,
                batch_size=batch_size
            )
        
        logger.info("Background embedding generation completed")
        
    except Exception as e:
        logger.error(f"Error in background embedding task: {e}", exc_info=True)
    finally:
        db.close()


# ============================================
# ENDPOINTS
# ============================================

@router.post(
    "/embeddings/generate",
    response_model=EmbeddingGenerationResponse,
    summary="Generate embeddings for clients and/or prospects",
    description="Generate vector embeddings. Use background_tasks=true for async processing."
)
async def generate_embeddings(
    request: GenerateEmbeddingsRequest,
    background_tasks: BackgroundTasks,
    use_background: bool = False,
    db: Session = Depends(get_db)
):
    """
    Generate embeddings for clients and/or prospects.
    
    - **type**: 'all', 'clients', or 'prospects'
    - **regenerate**: Force regeneration even if embeddings exist
    - **batch_size**: Number of items to process at once
    - **use_background**: If true, run in background and return immediately
    """
    try:
        service = EmbeddingService(batch_size=request.batch_size)
        
        # Check current status
        status = service.check_missing_embeddings(db)
        
        # If using background tasks
        if use_background:
            background_tasks.add_task(
                generate_embeddings_task,
                db=db,
                embedding_type=request.type,
                regenerate=request.regenerate,
                batch_size=request.batch_size
            )
            
            return EmbeddingGenerationResponse(
                success=True,
                message="Embedding generation started in background",
                clients_processed=status['clients']['missing'] if request.type in ['all', 'clients'] else None,
                prospects_processed=status['prospects']['missing'] if request.type in ['all', 'prospects'] else None
            )
        
        # Synchronous processing
        results = {}
        
        # Generate client embeddings
        if request.type in ["all", "clients"]:
            logger.info("Generating client embeddings...")
            client_results = service.generate_all_client_embeddings(
                db=db,
                regenerate=request.regenerate,
                show_progress=False
            )
            results['clients'] = client_results
        
        # Generate prospect embeddings
        if request.type in ["all", "prospects"]:
            logger.info("Generating prospect embeddings...")
            prospect_results = service.generate_all_prospect_embeddings(
                db=db,
                regenerate=request.regenerate,
                show_progress=False,
                batch_size=request.batch_size
            )
            results['prospects'] = prospect_results
        
        # Calculate total embeddings (3 per entity)
        total_embeddings = 0
        if 'clients' in results:
            total_embeddings += results['clients']['success_count'] * 3
        if 'prospects' in results:
            total_embeddings += results['prospects']['success_count'] * 3
        
        return EmbeddingGenerationResponse(
            success=True,
            message="Embedding generation completed successfully",
            clients_processed=results.get('clients', {}).get('total'),
            prospects_processed=results.get('prospects', {}).get('total'),
            clients_success=results.get('clients', {}).get('success_count'),
            prospects_success=results.get('prospects', {}).get('success_count'),
            clients_errors=results.get('clients', {}).get('error_count'),
            prospects_errors=results.get('prospects', {}).get('error_count'),
            clients_skipped=results.get('clients', {}).get('skipped_count'),
            prospects_skipped=results.get('prospects', {}).get('skipped_count'),
            total_embeddings=total_embeddings
        )
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/embeddings/status",
    response_model=EmbeddingStatusResponse,
    summary="Get embedding status",
    description="Check how many entities have embeddings and how many are missing"
)
async def get_embedding_status(db: Session = Depends(get_db)):
    """
    Get current status of embeddings in the system.
    
    Returns counts of:
    - Total entities (clients/prospects)
    - Entities with embeddings
    - Entities missing embeddings
    """
    try:
        service = EmbeddingService()
        stats = service.get_embedding_stats(db)
        
        return EmbeddingStatusResponse(
            clients=stats['clients'],
            prospects=stats['prospects'],
            embedding_dimensions=stats['embedding_dimensions'],
            model_name=stats['model_name']
        )
        
    except Exception as e:
        logger.error(f"Error getting embedding status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/embeddings/client/{client_id}",
    summary="Generate embeddings for a single client",
    description="Generate embeddings for one specific client profile"
)
async def generate_client_embedding(
    client_id: int,
    regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Generate embeddings for a single client profile.
    
    - **client_id**: Client profile ID
    - **regenerate**: Force regeneration even if embeddings exist
    """
    try:
        service = EmbeddingService()
        
        success = service.generate_client_embeddings(
            db=db,
            profile_id=client_id,
            regenerate=regenerate
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate embeddings for client {client_id}"
            )
        
        return {
            "success": True,
            "message": f"Embeddings generated for client {client_id}",
            "client_id": client_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating client embedding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/embeddings/prospect/{prospect_id}",
    summary="Generate embeddings for a single prospect",
    description="Generate embeddings for one specific prospect"
)
async def generate_prospect_embedding(
    prospect_id: int,
    regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Generate embeddings for a single prospect.
    
    - **prospect_id**: Prospect ID
    - **regenerate**: Force regeneration even if embeddings exist
    """
    try:
        service = EmbeddingService()
        
        success = service.generate_prospect_embeddings(
            db=db,
            prospect_id=prospect_id,
            regenerate=regenerate
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate embeddings for prospect {prospect_id}"
            )
        
        return {
            "success": True,
            "message": f"Embeddings generated for prospect {prospect_id}",
            "prospect_id": prospect_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prospect embedding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/embeddings/all",
    summary="Delete all embeddings (DANGEROUS)",
    description="Delete all embeddings from database. Requires confirmation."
)
async def delete_all_embeddings(
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete all embeddings from the database.
    
    ⚠️ WARNING: This is a destructive operation!
    
    - **confirm**: Must be true to execute
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must set confirm=true to delete all embeddings"
        )
    
    try:
        service = EmbeddingService()
        result = service.delete_all_embeddings(db, confirm=True)
        
        return {
            "success": True,
            "message": "All embeddings deleted",
            **result
        }
        
    except Exception as e:
        logger.error(f"Error deleting embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/embeddings/health",
    summary="Health check for embedding system",
    description="Verify that embedding model and database are working"
)
async def embedding_health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify embedding system is operational.
    """
    try:
        service = EmbeddingService()
        
        # Test model loading
        test_text = "Test embedding generation"
        embedding = service.generate_embedding(test_text)
        
        if embedding is None or len(embedding) != 384:
            raise Exception("Embedding generation failed")
        
        # Test database connectivity
        stats = service.check_missing_embeddings(db)
        
        return {
            "status": "healthy",
            "model_loaded": True,
            "model_name": service.model_name,
            "embedding_dimensions": 384,
            "database_connected": True,
            "total_clients": stats['clients']['total'],
            "total_prospects": stats['prospects']['total']
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Embedding system unhealthy: {str(e)}"
        )
    
app.include_router(router, prefix="/api", tags=["embeddings"])
app.include_router(matching_router, prefix="/api", tags=["matching"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)