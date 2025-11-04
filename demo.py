#!/usr/bin/env python3
"""
Optimized Docling OCR PDF Parser - Fast Markdown Export
========================================================
High-performance PDF parsing optimized for Markdown output and LLM analysis
"""

import logging
from pathlib import Path
from typing import Literal, Optional
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import ImageRefMode, TableItem
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


class OptimizedDoclingParser:
    """High-performance PDF parser optimized for Markdown output"""
    
    def __init__(
        self,
        ocr_enabled: bool = True,
        image_scale: float = 1.5,  # Reduced from 2.0 for speed
        extract_tables: bool = True,
        extract_images: bool = False,  # Disabled by default for speed
        parallel_processing: bool = True,
        max_workers: int = 4
    ):
        """
        Initialize optimized parser
        
        Args:
            ocr_enabled: Enable OCR for scanned documents
            image_scale: Image resolution (lower = faster, 1.5 is optimal)
            extract_tables: Extract table structures
            extract_images: Extract images (disabled for speed)
            parallel_processing: Enable parallel page processing
            max_workers: Number of parallel workers
        """
        self.ocr_enabled = ocr_enabled
        self.image_scale = image_scale
        self.extract_tables = extract_tables
        self.extract_images = extract_images
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers
        self.converter = self._setup_converter()
    
    def _setup_converter(self) -> DocumentConverter:
        """Setup optimized Docling converter"""
        log.info("🔧 Setting up optimized converter...")
        
        # Optimized pipeline settings
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = self.ocr_enabled
        pipeline_options.do_table_structure = self.extract_tables
        pipeline_options.images_scale = self.image_scale
        
        # Disable image generation for speed (unless explicitly needed)
        pipeline_options.generate_page_images = self.extract_images
        pipeline_options.generate_picture_images = self.extract_images
        
        # Enable text-focused features
        pipeline_options.do_code_enrichment = True
        pipeline_options.do_formula_enrichment = False  # Disabled for speed
        
        # OCR is controlled by do_ocr flag only
        # Additional OCR options are handled internally by Docling
        
        # Create converter with optimized settings
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )
        
        log.info(f"✅ Converter ready (OCR: {self.ocr_enabled}, Parallel: {self.parallel_processing})")
        return converter
    
    def _enhance_markdown_for_llm(self, md_content: str, doc_metadata: dict) -> str:
        """
        Enhance markdown with metadata for better LLM analysis
        
        Args:
            md_content: Original markdown content
            doc_metadata: Document metadata
        
        Returns:
            Enhanced markdown with metadata header
        """
        header = f"""---
Document Metadata
---
Source: {doc_metadata.get('filename', 'Unknown')}
Pages: {doc_metadata.get('pages', 0)}
Processing Date: {doc_metadata.get('processing_date', 'N/A')}
Tables Extracted: {doc_metadata.get('tables', 0)}
OCR Enabled: {doc_metadata.get('ocr_enabled', False)}
---

"""
        return header + md_content
    
    def parse_document(
        self,
        input_path: str,
        output_dir: Optional[str] = None,
        add_llm_metadata: bool = True,
        save_json_backup: bool = False
    ) -> dict:
        """
        Parse document and export to Markdown (optimized)
        
        Args:
            input_path: Path to input PDF
            output_dir: Output directory (auto-created if None)
            add_llm_metadata: Add metadata header for LLM analysis
            save_json_backup: Also save JSON backup (slower)
        
        Returns:
            Dictionary with parsing results
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        # Setup output directory
        if output_dir is None:
            output_dir = Path("docling_output") / input_path.stem
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        log.info("=" * 70)
        log.info(f"📄 Parsing: {input_path.name}")
        log.info(f"📁 Output: {output_dir}")
        log.info(f"⚡ Mode: Fast Markdown Export")
        log.info("=" * 70)
        
        # Convert document
        log.info("🔄 Processing document...")
        try:
            conv_result = self.converter.convert(str(input_path))
            document = conv_result.document
        except Exception as e:
            log.error(f"❌ Conversion failed: {e}")
            raise
        
        # Collect metadata
        metadata = {
            'filename': input_path.name,
            'pages': len(document.pages),
            'ocr_enabled': self.ocr_enabled,
            'processing_date': '',  # Add timestamp if needed
            'tables': len(document.tables) if hasattr(document, 'tables') else 0,
            'images': len(document.pictures) if hasattr(document, 'pictures') else 0
        }
        
        # Document statistics
        log.info("📊 Document Statistics:")
        log.info(f"   📄 Pages: {metadata['pages']}")
        log.info(f"   📋 Tables: {metadata['tables']}")
        log.info(f"   🖼️  Images: {metadata['images']}")
        
        # Export results
        results = {
            "input_file": str(input_path),
            "output_dir": str(output_dir),
            "metadata": metadata,
            "files": {}
        }
        
        doc_name = input_path.stem
        
        # Export Markdown (primary output)
        md_path = output_dir / f"{doc_name}.md"
        log.info(f"💾 Exporting Markdown to {md_path.name}...")
        try:
            # Save basic markdown
            document.save_as_markdown(
                md_path,
                image_mode=ImageRefMode.REFERENCED if self.extract_images else ImageRefMode.PLACEHOLDER
            )
            
            # Enhance markdown for LLM if requested
            if add_llm_metadata:
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                enhanced_md = self._enhance_markdown_for_llm(md_content, metadata)
                
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_md)
                
                log.info("✨ Enhanced markdown with LLM-friendly metadata")
            
            results["files"]["markdown"] = str(md_path)
            log.info(f"✅ Markdown exported: {md_path}")
        except Exception as e:
            log.error(f"❌ Markdown export failed: {e}")
            raise
        
        # Optional: Export JSON backup
        if save_json_backup:
            json_path = output_dir / f"{doc_name}.json"
            log.info(f"💾 Saving JSON backup to {json_path.name}...")
            try:
                document.save_as_json(
                    json_path,
                    image_mode=ImageRefMode.REFERENCED
                )
                results["files"]["json"] = str(json_path)
                log.info(f"✅ JSON backup saved: {json_path}")
            except Exception as e:
                log.warning(f"⚠️  JSON backup failed: {e}")
        
        # Export images if enabled
        if self.extract_images and hasattr(document, 'pictures') and document.pictures:
            log.info(f"🖼️  Exporting {len(document.pictures)} images...")
            images_dir = output_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            def save_image(args):
                i, picture = args
                try:
                    image = picture.get_image(document)
                    if image:
                        image_path = images_dir / f"image_{i+1}.png"
                        with image_path.open("wb") as f:
                            image.save(f, "PNG")
                        return True
                except Exception:
                    return False
                return False
            
            # Parallel image export
            if self.parallel_processing and len(document.pictures) > 3:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    results_list = list(executor.map(save_image, enumerate(document.pictures)))
                    exported_count = sum(results_list)
            else:
                exported_count = sum(save_image((i, pic)) for i, pic in enumerate(document.pictures))
            
            log.info(f"✅ Exported {exported_count} images to {images_dir}")
            results["images_exported"] = exported_count
        
        # Export tables if enabled
        if self.extract_tables and hasattr(document, 'tables') and document.tables:
            log.info(f"📋 Exporting {len(document.tables)} table images...")
            tables_dir = output_dir / "tables"
            tables_dir.mkdir(exist_ok=True)
            
            def save_table(args):
                i, table = args
                try:
                    table_image = table.get_image(document)
                    if table_image:
                        table_path = tables_dir / f"table_{i+1}.png"
                        with table_path.open("wb") as f:
                            table_image.save(f, "PNG")
                        return True
                except Exception:
                    return False
                return False
            
            # Parallel table export
            if self.parallel_processing and len(document.tables) > 2:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    results_list = list(executor.map(save_table, enumerate(document.tables)))
                    exported_count = sum(results_list)
            else:
                exported_count = sum(save_table((i, tbl)) for i, tbl in enumerate(document.tables))
            
            log.info(f"✅ Exported {exported_count} tables to {tables_dir}")
            results["tables_exported"] = exported_count
        
        log.info("=" * 70)
        log.info("🎉 Processing Complete!")
        log.info(f"📁 Markdown file: {md_path.absolute()}")
        log.info("=" * 70)
        
        return results
    
    def batch_process(
        self,
        pdf_paths: list[str],
        output_base_dir: str = "docling_output",
        add_llm_metadata: bool = True
    ) -> list[dict]:
        """
        Process multiple PDFs in batch
        
        Args:
            pdf_paths: List of PDF file paths
            output_base_dir: Base output directory
            add_llm_metadata: Add LLM-friendly metadata
        
        Returns:
            List of results for each PDF
        """
        results = []
        
        log.info(f"📦 Batch processing {len(pdf_paths)} PDFs...")
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            log.info(f"\n[{i}/{len(pdf_paths)}] Processing: {Path(pdf_path).name}")
            try:
                result = self.parse_document(
                    pdf_path,
                    output_dir=f"{output_base_dir}/{Path(pdf_path).stem}",
                    add_llm_metadata=add_llm_metadata
                )
                results.append({"status": "success", "result": result})
            except Exception as e:
                log.error(f"❌ Failed: {e}")
                results.append({"status": "failed", "error": str(e), "file": pdf_path})
        
        log.info(f"\n✅ Batch complete: {sum(1 for r in results if r['status'] == 'success')}/{len(pdf_paths)} successful")
        return results


def parse_pdf_fast(
    pdf_path: str,
    output_dir: Optional[str] = None,
    enable_ocr: bool = True,
    add_llm_metadata: bool = True
) -> dict:
    """
    Fast PDF parsing for Markdown export
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory (optional)
        enable_ocr: Enable OCR for scanned documents
        add_llm_metadata: Add metadata for LLM analysis
    
    Returns:
        Dictionary with parsing results
    """
    parser = OptimizedDoclingParser(
        ocr_enabled=enable_ocr,
        extract_images=False,  # Disabled for speed
        parallel_processing=True
    )
    return parser.parse_document(pdf_path, output_dir, add_llm_metadata)


# Example usage
if __name__ == "__main__":
    # Example 1: Fast Markdown export (optimized for LLM)
    pdf_path = "/home/atharva/Downloads/LotusFlare Briefing Document.pdf"
    
    # try:
    #     results = parse_pdf_fast(
    #         pdf_path,
    #         enable_ocr=True,
    #         add_llm_metadata=True  # Adds metadata header for LLM
    #     )
    #     print(f"\n✅ Success! Markdown file created:")
    #     print(f"   📄 {results['files']['markdown']}")
    #     print(f"\n📊 Document info:")
    #     print(f"   Pages: {results['metadata']['pages']}")
    #     print(f"   Tables: {results['metadata']['tables']}")
    
    # except FileNotFoundError:
    #     print(f"❌ File not found: {pdf_path}")
    #     print("📝 Please update the pdf_path variable")
    
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    # Example 2: Batch processing multiple PDFs
    """
    pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    
    parser = OptimizedDoclingParser(ocr_enabled=True)
    results = parser.batch_process(pdf_files, add_llm_metadata=True)
    
    for result in results:
        if result['status'] == 'success':
            print(f"✅ {result['result']['files']['markdown']}")
    """
    
    # Example 3: Custom configuration with all features
    
    parser = OptimizedDoclingParser(
        ocr_enabled=True,
        image_scale=1.0,  # Higher quality (slower)
        extract_tables=True,
        extract_images=False,  # Enable image extraction
        parallel_processing=True,
        max_workers=4
    )
    
    results = parser.parse_document(
        pdf_path,
        output_dir="/home/atharva/Sales_Explorer",
        add_llm_metadata=True,
        save_json_backup=True  # Also save JSON
    )
    