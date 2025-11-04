# """
# Optimized Docling OCR PDF Parser - Fast Markdown Export with Caching
# =====================================================================
# High-performance PDF parsing with intelligent caching and post-processing page exclusion
# """

# import logging
# import hashlib
# from pathlib import Path
# from typing import Literal, Optional, Dict, Any, Set
# from docling.document_converter import DocumentConverter, PdfFormatOption
# from docling.datamodel.base_models import InputFormat
# from docling.datamodel.pipeline_options import PdfPipelineOptions
# from docling.datamodel.pipeline_options import EasyOcrOptions
# from docling_core.types.doc import ImageRefMode
# import json
# import os
# import re
# from datetime import datetime, timedelta

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )
# log = logging.getLogger(__name__)


# class MarkdownPageFilter:
#     """Advanced filter for excluding specific pages from markdown content"""
    
#     @staticmethod
#     def parse_excluded_pages(excluded_str: str) -> Set[int]:
#         """Parse excluded pages string to set of page numbers (1-based)"""
#         if not excluded_str or not excluded_str.strip():
#             return set()
        
#         pages = set()
#         parts = excluded_str.split(',')
#         for part in parts:
#             part = part.strip()
#             if '-' in part:
#                 try:
#                     start, end = map(int, part.split('-'))
#                     pages.update(range(start, end + 1))
#                 except ValueError:
#                     log.warning(f"Invalid range in excluded pages: {part}")
#             else:
#                 try:
#                     pages.add(int(part))
#                 except ValueError:
#                     log.warning(f"Invalid page number: {part}")
#         return pages
    
#     @staticmethod
#     def filter_pages_from_markdown(md_content: str, excluded_pages: Set[int]) -> str:
#         """
#         Filter out excluded pages from markdown with page markers.
#         """
#         if not excluded_pages:
#             return md_content
        
#         log.info(f"🚫 Filtering {len(excluded_pages)} excluded pages: {sorted(excluded_pages)}")
        
#         lines = md_content.split('\n')
#         filtered_lines = []
#         current_page = 0
#         skip_mode = False
#         lines_removed = 0
        
#         # Primary pattern: ## Page N
#         page_pattern = re.compile(r'^##\s+Page\s+(\d+)\s*$', re.IGNORECASE)
        
#         for line in lines:
#             # Check for page marker
#             match = page_pattern.match(line.strip())
            
#             if match:
#                 current_page = int(match.group(1))
#                 skip_mode = current_page in excluded_pages
                
#                 if skip_mode:
#                     log.debug(f"🚫 Skipping page {current_page}")
#                     lines_removed += 1
#                     continue  # Don't add the page marker line
#                 else:
#                     log.debug(f"✅ Including page {current_page}")
            
#             # Add line if not in skip mode
#             if not skip_mode:
#                 filtered_lines.append(line)
#             else:
#                 lines_removed += 1
        
#         filtered_content = '\n'.join(filtered_lines)
#         removed_chars = len(md_content) - len(filtered_content)
        
#         if removed_chars > 0:
#             log.info(f"✂️  Removed {removed_chars:,} characters ({lines_removed} lines) from {len(excluded_pages)} page(s)")
#         else:
#             log.warning(f"⚠️  No content removed - page markers not found or format mismatch")
#             log.warning(f"💡 First 500 chars of content:\n{md_content[:500]}")
        
#         return filtered_content
    

# class OptimizedDoclingParser:
#     """High-performance PDF parser with caching and optimizations"""
    
#     def __init__(
#         self,
#         ocr_enabled: bool = True,
#         image_scale: float = 1.0,
#         extract_tables: bool = True,
#         extract_images: bool = False,
#         parallel_processing: bool = True,
#         max_workers: int = 4
#     ):
#         """Initialize optimized parser"""
#         self.ocr_enabled = ocr_enabled
#         self.image_scale = image_scale
#         self.extract_tables = extract_tables
#         self.extract_images = extract_images
#         self.parallel_processing = parallel_processing
#         self.max_workers = max_workers
        
#         # Initialize page filter
#         self.page_filter = MarkdownPageFilter()
        
#         self.converter = self._setup_converter()


#     def _setup_converter(self) -> DocumentConverter:
#         """Setup optimized Docling converter"""
#         log.info("🔧 Setting up ultra-fast converter...")
        
#         # Maximum performance settings
#         pipeline_options = PdfPipelineOptions()
#         pipeline_options.do_ocr = self.ocr_enabled
#         pipeline_options.do_table_structure = self.extract_tables
#         pipeline_options.images_scale = self.image_scale
        
#         # Disable all non-essential features for maximum speed
#         pipeline_options.generate_page_images = False
#         pipeline_options.generate_picture_images = False
#         pipeline_options.do_code_enrichment = False  # DISABLED for speed
#         pipeline_options.do_formula_enrichment = False
        
#         # Optimize OCR settings if enabled
#         # Optimize OCR settings if enabled
#         # Optimize OCR settings if enabled
#         if self.ocr_enabled:
#             try:
#                 # Try TesseractCLI first (best quality)
#                 from docling.datamodel.pipeline_options import TesseractCliOcrOptions
#                 pipeline_options.ocr_options = TesseractCliOcrOptions(
#                     force_full_page_ocr=True,
#                     lang=["eng"],
#                     tesseract_cmd="tesseract"
#                 )
#                 log.info("✅ Using TesseractCLI OCR")
#             except (ImportError, FileNotFoundError):
#                 # Fallback to RapidOCR (no system dependencies)
#                 try:
#                     from docling.datamodel.pipeline_options import RapidOcrOptions
#                     pipeline_options.ocr_options = RapidOcrOptions(
#                         force_full_page_ocr=True,
#                         lang=["en"]
#                     )
#                     log.warning("⚠️ Tesseract not found, using RapidOCR fallback")
#                 except ImportError:
#                     # Final fallback to EasyOCR
#                     from docling.datamodel.pipeline_options import EasyOcrOptions
#                     pipeline_options.ocr_options = EasyOcrOptions(
#                         force_full_page_ocr=True,
#                         lang=["en"]
#                     )
#                     log.warning("⚠️ Using EasyOCR fallback")
        
#         # Create converter
#         converter = DocumentConverter(
#             format_options={
#                 InputFormat.PDF: PdfFormatOption(
#                     pipeline_options=pipeline_options
#                 )
#             }
#         )
        
#         log.info(f"✅ Ultra-fast converter ready (Scale: {self.image_scale}, OCR: {self.ocr_enabled})")
#         return converter
    
#     def _validate_markdown_structure(self, md_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Validate markdown structure and log statistics
#         """
#         stats = {
#             'total_chars': len(md_content),
#             'total_lines': md_content.count('\n'),
#             'tables_found': md_content.count('|'),  # Simple table detection
#             'headers_found': len(re.findall(r'^#+\s+', md_content, re.MULTILINE)),
#             'pages_detected': len(re.findall(r'Page\s+\d+', md_content, re.IGNORECASE))
#         }
        
#         log.info("📊 Markdown Structure Analysis:")
#         log.info(f"   📄 Total Characters: {stats['total_chars']:,}")
#         log.info(f"   📝 Total Lines: {stats['total_lines']:,}")
#         log.info(f"   📋 Tables Detected: {stats['tables_found']}")
#         log.info(f"   📑 Headers Found: {stats['headers_found']}")
#         log.info(f"   📖 Pages Detected: {stats['pages_detected']}")
        
#         # Validate completeness
#         expected_pages = metadata.get('pages', 0)
#         if stats['pages_detected'] < expected_pages:
#             log.warning(f"⚠️  Page count mismatch! Expected {expected_pages}, found {stats['pages_detected']}")
        
#         return stats
    
#     def _enhance_markdown_for_llm(self, md_content: str, doc_metadata: Dict[str, Any]) -> str:
#         """Enhanced markdown with comprehensive metadata"""
#         header = f"""---
# Document Metadata
# ---
# Source: {doc_metadata.get('filename', 'Unknown')}
# Total Pages: {doc_metadata.get('pages', 0)}
# Excluded Pages: {doc_metadata.get('excluded_pages', 'None')}
# Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Tables Extracted: {doc_metadata.get('tables', 0)}
# OCR Enabled: {doc_metadata.get('ocr_enabled', False)}
# Content Length: {len(md_content):,} characters
# ---

# # DOCUMENT CONTENT

# {md_content}

# ---
# END OF DOCUMENT
# ---
# """
#         return header
    


#     def _add_page_markers(self, document, md_content: str) -> str:
#         """
#         Add explicit page markers to markdown based on document structure.
#         This enables accurate page-based filtering.
#         """
#         if not hasattr(document, 'pages') or not document.pages:
#             log.warning("⚠️  Document has no page information")
#             return md_content
        
#         # Strategy: Split content by estimated page boundaries
#         # Docling processes pages sequentially, so we can estimate boundaries
        
#         lines = md_content.split('\n')
#         total_lines = len(lines)
#         num_pages = len(document.pages)
        
#         # Calculate approximate lines per page
#         lines_per_page = total_lines // num_pages if num_pages > 0 else total_lines
        
#         marked_lines = []
#         current_line = 0
        
#         for page_num in range(1, num_pages + 1):
#             # Add page marker
#             marked_lines.append(f"\n## Page {page_num}\n")
            
#             # Add lines for this page
#             start_idx = current_line
#             end_idx = min(current_line + lines_per_page, total_lines)
            
#             # For last page, include all remaining lines
#             if page_num == num_pages:
#                 end_idx = total_lines
            
#             marked_lines.extend(lines[start_idx:end_idx])
#             current_line = end_idx
        
#         marked_content = '\n'.join(marked_lines)
        
#         log.info(f"✅ Inserted {num_pages} page markers into markdown")
#         return marked_content
    
#     def parse_document(
#         self,
#         input_path: str,
#         output_dir: Optional[str] = None,
#         excluded_pages: str = ""
#     ) -> Dict[str, Any]:
#         """
#         Parse document with simple file-based caching
#         """
#         input_path = Path(input_path)
        
#         if not input_path.exists():
#             raise FileNotFoundError(f"File not found: {input_path}")
        
#         # Setup output directory
#         if output_dir is None:
#             output_dir = Path("./docling_output")
#         else:
#             output_dir = Path(output_dir)
#         output_dir.mkdir(parents=True, exist_ok=True)
        
#         # Simple cache: check if MD file exists with same name
#         cached_md_path = output_dir / f"{input_path.stem}.md"
        
#         if cached_md_path.exists():
#             log.info(f"🚀 Using cached OCR result: {cached_md_path.name}")
#             with open(cached_md_path, 'r', encoding='utf-8') as f:
#                 full_md_content = f.read()
#         else:
#             log.info(f"🔄 Processing document with OCR: {input_path.name}")
            
#             # Process document
#             try:
#                 conv_result = self.converter.convert(str(input_path))
#                 document = conv_result.document
#             except Exception as e:
#                 log.error(f"❌ Conversion failed: {e}")
#                 raise
            
#             # Export to markdown
#             temp_md_path = output_dir / f"temp_{input_path.stem}.md"
#             document.save_as_markdown(
#                 temp_md_path,
#                 image_mode=ImageRefMode.PLACEHOLDER
#             )
            
#             # Read and add page markers
#             with open(temp_md_path, 'r', encoding='utf-8') as f:
#                 full_md_content = f.read()
            
#             full_md_content = self._add_page_markers(document, full_md_content)
            
#             # Save to cache file
#             with open(cached_md_path, 'w', encoding='utf-8') as f:
#                 f.write(full_md_content)
            
#             log.info(f"💾 Saved OCR result: {cached_md_path.name}")
            
#             # Clean up temp
#             temp_md_path.unlink(missing_ok=True)
        
#         # Apply page exclusion
#         excluded_set = self.page_filter.parse_excluded_pages(excluded_pages)
#         filtered_md_content = full_md_content
        
#         if excluded_set:
#             filtered_md_content = self.page_filter.filter_pages_from_markdown(
#                 full_md_content, excluded_set
#             )
#             log.info(f"✂️ Excluded pages: {sorted(excluded_set)}")
        
#         log.info(f"✅ Processing complete: {len(filtered_md_content):,} chars")
        
#         return {
#             "input_file": str(input_path),
#             "output_dir": str(output_dir),
#             "markdown_content": filtered_md_content,
#             "cached_md_path": str(cached_md_path)
#         }
    
#     def batch_process(
#         self,
#         pdf_paths: list[str],
#         output_base_dir: str = "docling_output",
#         add_llm_metadata: bool = True
#     ) -> list[Dict[str, Any]]:
#         """Process multiple PDFs in batch with caching"""
#         results = []
        
#         log.info(f"📦 Batch processing {len(pdf_paths)} PDFs...")
        
#         for i, pdf_path in enumerate(pdf_paths, 1):
#             log.info(f"\n[{i}/{len(pdf_paths)}] Processing: {Path(pdf_path).name}")
#             try:
#                 result = self.parse_document(
#                     pdf_path,
#                     output_dir=f"{output_base_dir}/{Path(pdf_path).stem}",
#                     add_llm_metadata=add_llm_metadata
#                 )
#                 results.append({"status": "success", "result": result})
#             except Exception as e:
#                 log.error(f"❌ Failed: {e}")
#                 results.append({"status": "failed", "error": str(e), "file": pdf_path})
        
#         successful = sum(1 for r in results if r['status'] == 'success')
#         log.info(f"\n✅ Batch complete: {successful}/{len(pdf_paths)} successful")
#         return results


# def parse_pdf_fast(
#     pdf_path: str,
#     output_dir: Optional[str] = None,
#     enable_ocr: bool = True,
#     excluded_pages: str = ""
# ) -> Dict[str, Any]:
#     """
#     Fast PDF parsing with simple file-based caching
#     """
#     parser = OptimizedDoclingParser(
#         ocr_enabled=enable_ocr,
#         image_scale=1.0,
#         extract_images=False,
#         parallel_processing=True
#     )
#     return parser.parse_document(
#         pdf_path,
#         output_dir,
#         excluded_pages=excluded_pages
#     )

















"""
Optimized Docling OCR PDF Parser - Fast Markdown Export with Caching
=====================================================================
High-performance PDF parsing with intelligent caching and post-processing page exclusion
Enhanced with improved OCR detection
"""

import logging
import hashlib
from pathlib import Path
from typing import Literal, Optional, Dict, Any, Set
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import ImageRefMode
import json
import os
import re
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


class MarkdownPageFilter:
    """Advanced filter for excluding specific pages from markdown content"""
    
    @staticmethod
    def parse_excluded_pages(excluded_str: str) -> Set[int]:
        """Parse excluded pages string to set of page numbers (1-based)"""
        if not excluded_str or not excluded_str.strip():
            return set()
        
        pages = set()
        parts = excluded_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    pages.update(range(start, end + 1))
                except ValueError:
                    log.warning(f"Invalid range in excluded pages: {part}")
            else:
                try:
                    pages.add(int(part))
                except ValueError:
                    log.warning(f"Invalid page number: {part}")
        return pages
    
    @staticmethod
    def filter_pages_from_markdown(md_content: str, excluded_pages: Set[int]) -> str:
        """
        Filter out excluded pages from markdown with page markers.
        """
        if not excluded_pages:
            return md_content
        
        log.info(f"🚫 Filtering {len(excluded_pages)} excluded pages: {sorted(excluded_pages)}")
        
        lines = md_content.split('\n')
        filtered_lines = []
        current_page = 0
        skip_mode = False
        lines_removed = 0
        
        # Primary pattern: ## Page N
        page_pattern = re.compile(r'^##\s+Page\s+(\d+)\s*$', re.IGNORECASE)
        
        for line in lines:
            # Check for page marker
            match = page_pattern.match(line.strip())
            
            if match:
                current_page = int(match.group(1))
                skip_mode = current_page in excluded_pages
                
                if skip_mode:
                    log.debug(f"🚫 Skipping page {current_page}")
                    lines_removed += 1
                    continue  # Don't add the page marker line
                else:
                    log.debug(f"✅ Including page {current_page}")
            
            # Add line if not in skip mode
            if not skip_mode:
                filtered_lines.append(line)
            else:
                lines_removed += 1
        
        filtered_content = '\n'.join(filtered_lines)
        removed_chars = len(md_content) - len(filtered_content)
        
        if removed_chars > 0:
            log.info(f"✂️  Removed {removed_chars:,} characters ({lines_removed} lines) from {len(excluded_pages)} page(s)")
        else:
            log.warning(f"⚠️  No content removed - page markers not found or format mismatch")
            log.warning(f"💡 First 500 chars of content:\n{md_content[:500]}")
        
        return filtered_content


class OptimizedDoclingParser:
    """High-performance PDF parser with caching and optimizations"""
    
    def __init__(
        self,
        ocr_enabled: bool = True,
        image_scale: float = 1.5,
        extract_tables: bool = True,
        extract_images: bool = False,
        parallel_processing: bool = True,
        max_workers: int = 4
    ):
        """Initialize optimized parser with improved OCR"""
        self.ocr_enabled = ocr_enabled
        self.image_scale = image_scale
        self.extract_tables = extract_tables
        self.extract_images = extract_images
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers
        
        # Initialize page filter
        self.page_filter = MarkdownPageFilter()
        
        self.converter = self._setup_converter()

    
    def _setup_converter(self) -> DocumentConverter:
        """Setup optimized Docling converter with forced RapidOCR."""
        log.info("🔧 Setting up optimized converter with RapidOCR...")

        # Configure pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = self.ocr_enabled
        pipeline_options.do_table_structure = self.extract_tables
        pipeline_options.images_scale = self.image_scale
        pipeline_options.generate_page_images = self.extract_images
        pipeline_options.generate_picture_images = self.extract_images
        pipeline_options.do_code_enrichment = True
        pipeline_options.do_formula_enrichment = False

        # ✅ FORCE RapidOCR - No fallback to ensure consistent results
        if self.ocr_enabled:
            try:
                from docling.datamodel.pipeline_options import RapidOcrOptions
                
                # Verify rapidocr is actually installed
                try:
                    import rapidocr
                    log.info("✅ RapidOCR module verified")
                except ImportError:
                    raise ImportError(
                        "RapidOCR is not installed in this Python environment!\n"
                        "Current Python: " + str(__import__('sys').executable) + "\n"
                        "Install with: pip install rapidocr onnxruntime"
                    )
                
                # Configure RapidOCR with optimal settings
                pipeline_options.ocr_options = RapidOcrOptions(
                    force_full_page_ocr=True,
                    lang=["en"]
                )
                log.info("✅ RapidOCR configured as primary OCR engine")
                
            except ImportError as e:
                log.error(f"❌ Failed to configure RapidOCR: {e}")
                raise

        # Initialize DocumentConverter with pipeline options
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )

        log.info(f"✅ Converter ready (Scale: {self.image_scale}, OCR Engine: RapidOCR)")
        return converter

    
    def _validate_markdown_structure(self, md_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate markdown structure and log statistics
        """
        stats = {
            'total_chars': len(md_content),
            'total_lines': md_content.count('\n'),
            'tables_found': md_content.count('|'),  # Simple table detection
            'headers_found': len(re.findall(r'^#+\s+', md_content, re.MULTILINE)),
            'pages_detected': len(re.findall(r'Page\s+\d+', md_content, re.IGNORECASE))
        }
        
        log.info("📊 Markdown Structure Analysis:")
        log.info(f"   📄 Total Characters: {stats['total_chars']:,}")
        log.info(f"   📝 Total Lines: {stats['total_lines']:,}")
        log.info(f"   📋 Tables Detected: {stats['tables_found']}")
        log.info(f"   📑 Headers Found: {stats['headers_found']}")
        log.info(f"   📖 Pages Detected: {stats['pages_detected']}")
        
        # Validate completeness
        expected_pages = metadata.get('pages', 0)
        if stats['pages_detected'] < expected_pages:
            log.warning(f"⚠️  Page count mismatch! Expected {expected_pages}, found {stats['pages_detected']}")
        
        return stats
    
    def _enhance_markdown_for_llm(self, md_content: str, doc_metadata: Dict[str, Any]) -> str:
        """Enhanced markdown with comprehensive metadata"""
        header = f"""---
Document Metadata
---
Source: {doc_metadata.get('filename', 'Unknown')}
Total Pages: {doc_metadata.get('pages', 0)}
Excluded Pages: {doc_metadata.get('excluded_pages', 'None')}
Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tables Extracted: {doc_metadata.get('tables', 0)}
OCR Enabled: {doc_metadata.get('ocr_enabled', False)}
Content Length: {len(md_content):,} characters
---

# DOCUMENT CONTENT

{md_content}

---
END OF DOCUMENT
---
"""
        return header

    def _add_page_markers(self, document, md_content: str) -> str:
        """
        Add explicit page markers to markdown based on document structure.
        This enables accurate page-based filtering.
        """
        if not hasattr(document, 'pages') or not document.pages:
            log.warning("⚠️  Document has no page information")
            return md_content
        
        # Strategy: Split content by estimated page boundaries
        # Docling processes pages sequentially, so we can estimate boundaries
        
        lines = md_content.split('\n')
        total_lines = len(lines)
        num_pages = len(document.pages)
        
        # Calculate approximate lines per page
        lines_per_page = total_lines // num_pages if num_pages > 0 else total_lines
        
        marked_lines = []
        current_line = 0
        
        for page_num in range(1, num_pages + 1):
            # Add page marker
            marked_lines.append(f"\n## Page {page_num}\n")
            
            # Add lines for this page
            start_idx = current_line
            end_idx = min(current_line + lines_per_page, total_lines)
            
            # For last page, include all remaining lines
            if page_num == num_pages:
                end_idx = total_lines
            
            marked_lines.extend(lines[start_idx:end_idx])
            current_line = end_idx
        
        marked_content = '\n'.join(marked_lines)
        
        log.info(f"✅ Inserted {num_pages} page markers into markdown")
        return marked_content
    
    def parse_document(
        self,
        input_path: str,
        output_dir: Optional[str] = None,
        excluded_pages: str = ""
    ) -> Dict[str, Any]:
        """
        Parse document with simple file-based caching and improved OCR
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        # Setup output directory
        if output_dir is None:
            output_dir = Path("./docling_output")
        else:
            output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Simple cache: check if MD file exists with same name
        cached_md_path = output_dir / f"{input_path.stem}.md"
        
        if cached_md_path.exists():
            log.info(f"🚀 Using cached OCR result: {cached_md_path.name}")
            with open(cached_md_path, 'r', encoding='utf-8') as f:
                full_md_content = f.read()
        else:
            log.info(f"🔄 Processing document with enhanced OCR: {input_path.name}")
            log.info("=" * 70)
            log.info(f"📄 Parsing: {input_path.name}")
            log.info(f"📁 Output: {output_dir}")
            log.info(f"⚡ Mode: Enhanced OCR Detection")
            log.info("=" * 70)
            
            # Process document
            try:
                log.info("🔄 Converting document...")
                conv_result = self.converter.convert(str(input_path))
                document = conv_result.document
            except Exception as e:
                log.error(f"❌ Conversion failed: {e}")
                raise
            
            # Document statistics
            metadata = {
                'filename': input_path.name,
                'pages': len(document.pages),
                'ocr_enabled': self.ocr_enabled,
                'tables': len(document.tables) if hasattr(document, 'tables') else 0,
                'images': len(document.pictures) if hasattr(document, 'pictures') else 0
            }
            
            log.info("📊 Document Statistics:")
            log.info(f"   📄 Pages: {metadata['pages']}")
            log.info(f"   📋 Tables: {metadata['tables']}")
            log.info(f"   🖼️  Images: {metadata['images']}")
            
            # Export to markdown
            temp_md_path = output_dir / f"temp_{input_path.stem}.md"
            log.info(f"💾 Exporting to Markdown...")
            document.save_as_markdown(
                temp_md_path,
                image_mode=ImageRefMode.PLACEHOLDER
            )
            
            # Read and add page markers
            with open(temp_md_path, 'r', encoding='utf-8') as f:
                full_md_content = f.read()
            
            full_md_content = self._add_page_markers(document, full_md_content)
            
            # Validate markdown structure
            self._validate_markdown_structure(full_md_content, metadata)
            
            # Save to cache file
            with open(cached_md_path, 'w', encoding='utf-8') as f:
                f.write(full_md_content)
            
            log.info(f"💾 Saved OCR result to cache: {cached_md_path.name}")
            
            # Clean up temp
            temp_md_path.unlink(missing_ok=True)
            
            log.info("=" * 70)
            log.info("🎉 Processing Complete!")
            log.info(f"📁 Markdown file: {cached_md_path.absolute()}")
            log.info("=" * 70)
        
        # Apply page exclusion
        excluded_set = self.page_filter.parse_excluded_pages(excluded_pages)
        filtered_md_content = full_md_content
        
        if excluded_set:
            filtered_md_content = self.page_filter.filter_pages_from_markdown(
                full_md_content, excluded_set
            )
            log.info(f"✂️ Excluded pages: {sorted(excluded_set)}")
        
        log.info(f"✅ Processing complete: {len(filtered_md_content):,} chars")
        
        return {
            "input_file": str(input_path),
            "output_dir": str(output_dir),
            "markdown_content": filtered_md_content,
            "cached_md_path": str(cached_md_path)
        }
    
    def batch_process(
        self,
        pdf_paths: list[str],
        output_base_dir: str = "docling_output",
        add_llm_metadata: bool = True
    ) -> list[Dict[str, Any]]:
        """Process multiple PDFs in batch with caching"""
        results = []
        
        log.info(f"📦 Batch processing {len(pdf_paths)} PDFs...")
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            log.info(f"\n[{i}/{len(pdf_paths)}] Processing: {Path(pdf_path).name}")
            try:
                result = self.parse_document(
                    pdf_path,
                    output_dir=f"{output_base_dir}/{Path(pdf_path).stem}"
                )
                results.append({"status": "success", "result": result})
            except Exception as e:
                log.error(f"❌ Failed: {e}")
                results.append({"status": "failed", "error": str(e), "file": pdf_path})
        
        successful = sum(1 for r in results if r['status'] == 'success')
        log.info(f"\n✅ Batch complete: {successful}/{len(pdf_paths)} successful")
        return results


def parse_pdf_fast(
    pdf_path: str,
    output_dir: Optional[str] = None,
    enable_ocr: bool = True,
    excluded_pages: str = ""
) -> Dict[str, Any]:
    """
    Fast PDF parsing with simple file-based caching and enhanced OCR
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory (optional)
        enable_ocr: Enable OCR for scanned documents
        excluded_pages: Pages to exclude (e.g., "1,3,5-7")
    
    Returns:
        Dictionary with parsing results
    """
    parser = OptimizedDoclingParser(
        ocr_enabled=enable_ocr,
        image_scale=2.0,  # Optimal balance between quality and speed
        extract_images=False,
        parallel_processing=True
    )
    return parser.parse_document(
        pdf_path,
        output_dir,
        excluded_pages=excluded_pages
    )


# Example usage
if __name__ == "__main__":
    # Example: Fast parsing with enhanced OCR and page exclusion
    pdf_path = "/home/atharva/Downloads/LotusFlare Briefing Document.pdf"
    
    try:
        results = parse_pdf_fast(
            pdf_path,
            enable_ocr=True,
            excluded_pages="2"  # Exclude pages 1 and 3
        )
        print(f"\n✅ Success! Markdown file created:")
        print(f"   📄 {results['cached_md_path']}")
        print(f"\n📊 Content length: {len(results['markdown_content']):,} characters")
    
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
        print("📝 Please update the pdf_path variable")
    
    except Exception as e:
        print(f"❌ Error: {e}")





