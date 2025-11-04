"""
CLI Script for Generating Embeddings
Run this to generate embeddings for clients and prospects
"""

import sys
import argparse
import time
from pathlib import Path

# Add parent directory to path (more robust way)
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from database.config import get_db
from matching.embeddings import EmbeddingService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60)


def print_stats(title, stats):
    """Print statistics in formatted way"""
    print(f"\n📊 {title}:")
    print(f"   Total: {stats['total']}")
    print(f"   With embeddings: {stats['with_embeddings']}")
    print(f"   Missing: {stats['missing']}")


def print_results(title, results):
    """Print generation results"""
    print(f"\n✅ {title} Results:")
    print(f"   Success: {results['success_count']}")
    print(f"   Errors: {results['error_count']}")
    print(f"   Skipped: {results['skipped_count']}")
    print(f"   Total: {results['total']}")


def check_embedding_status(service, db):
    """Check and display current embedding status"""
    print_header("CURRENT EMBEDDING STATUS")
    
    stats = service.check_missing_embeddings(db)
    
    print_stats("Clients", stats['clients'])
    print_stats("Prospects", stats['prospects'])
    
    total_missing = stats['clients']['missing'] + stats['prospects']['missing']
    total_with = stats['clients']['with_embeddings'] + stats['prospects']['with_embeddings']
    total_all = stats['clients']['total'] + stats['prospects']['total']
    
    print(f"\n📈 Overall:")
    print(f"   Total entities: {total_all}")
    print(f"   With embeddings: {total_with}")
    print(f"   Missing embeddings: {total_missing}")
    
    if total_missing > 0:
        coverage = (total_with / total_all * 100) if total_all > 0 else 0
        print(f"   Coverage: {coverage:.1f}%")
    
    return stats


def generate_embeddings(service, db, args):
    """Generate embeddings based on arguments"""
    print_header("STARTING EMBEDDING GENERATION")
    print(f"Mode: {'Regenerate ALL' if args.regenerate else 'Generate MISSING only'}")
    print(f"Target: {args.type.upper()}")
    print(f"Batch size: {args.batch_size}")
    
    start_time = time.time()
    results = {}
    
    # Generate client embeddings
    if args.type in ['all', 'clients']:
        print("\n🔄 Generating CLIENT embeddings...")
        try:
            client_results = service.generate_all_client_embeddings(
                db=db,
                regenerate=args.regenerate,
                show_progress=True
            )
            results['clients'] = client_results
            print_results("Client", client_results)
        except Exception as e:
            logger.error(f"Error generating client embeddings: {e}")
            results['clients'] = {
                'success_count': 0,
                'error_count': 0,
                'skipped_count': 0,
                'total': 0
            }
    
    # Generate prospect embeddings
    if args.type in ['all', 'prospects']:
        print("\n🔄 Generating PROSPECT embeddings...")
        try:
            prospect_results = service.generate_all_prospect_embeddings(
                db=db,
                regenerate=args.regenerate,
                show_progress=True,
                batch_size=args.batch_size
            )
            results['prospects'] = prospect_results
            print_results("Prospect", prospect_results)
        except Exception as e:
            logger.error(f"Error generating prospect embeddings: {e}")
            results['prospects'] = {
                'success_count': 0,
                'error_count': 0,
                'skipped_count': 0,
                'total': 0
            }
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    print_header("GENERATION COMPLETE")
    print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.1f} minutes)")
    
    # Calculate totals
    total_success = sum(r.get('success_count', 0) for r in results.values())
    total_errors = sum(r.get('error_count', 0) for r in results.values())
    
    if total_success > 0:
        avg_time = elapsed_time / total_success
        print(f"Average time per embedding: {avg_time:.2f} seconds")
    
    return results


def show_final_status(service, db, initial_stats):
    """Show final status and compare with initial"""
    print_header("FINAL STATUS")
    
    final_stats = service.check_missing_embeddings(db)
    
    print_stats("Clients", final_stats['clients'])
    print_stats("Prospects", final_stats['prospects'])
    
    # Show improvements
    print("\n📈 Changes:")
    client_improvement = initial_stats['clients']['missing'] - final_stats['clients']['missing']
    prospect_improvement = initial_stats['prospects']['missing'] - final_stats['prospects']['missing']
    
    if client_improvement > 0:
        print(f"   Clients: +{client_improvement} embeddings created")
    if prospect_improvement > 0:
        print(f"   Prospects: +{prospect_improvement} embeddings created")
    
    # Final message
    if final_stats['clients']['missing'] == 0 and final_stats['prospects']['missing'] == 0:
        print("\n🎉 All embeddings generated successfully!")
        return True
    else:
        total_missing = final_stats['clients']['missing'] + final_stats['prospects']['missing']
        print(f"\n⚠️  {total_missing} embeddings still missing. Check logs for errors.")
        return False


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Generate vector embeddings for clients and prospects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_embeddings.py                    # Generate all missing embeddings
  python generate_embeddings.py --check-only       # Just check status
  python generate_embeddings.py --type clients     # Only generate client embeddings
  python generate_embeddings.py --regenerate       # Regenerate all embeddings
  python generate_embeddings.py --batch-size 64    # Use larger batch size
        """
    )
    
    parser.add_argument(
        '--type',
        choices=['all', 'clients', 'prospects'],
        default='all',
        help='Which embeddings to generate (default: all)'
    )
    
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate embeddings even if they exist'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for processing (default: 32)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check status, do not generate'
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Embedding Generation Script")
    print("="*60)
    
    try:
        # Initialize service
        logger.info("Initializing Embedding Service...")
        service = EmbeddingService(batch_size=args.batch_size)
        logger.info(f"Using model: {service.model_name}")
        
        # Get database session
        logger.info("Connecting to database...")
        db = next(get_db())
        logger.info("Database connected successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        print("\n❌ Initialization failed. Please check your configuration.")
        return 1
    
    try:
        # Check current status
        initial_stats = check_embedding_status(service, db)
        
        if args.check_only:
            print("\n✅ Status check complete (--check-only mode)")
            return 0
        
        # Ask for confirmation if regenerating
        if args.regenerate:
            total = initial_stats['clients']['total'] + initial_stats['prospects']['total']
            print(f"\n⚠️  WARNING: You are about to REGENERATE embeddings for {total} entities.")
            response = input("Are you sure? (yes/no): ")
            if response.lower() != 'yes':
                print("Operation cancelled.")
                return 0
        
        # Generate embeddings
        results = generate_embeddings(service, db, args)
        
        # Show final status
        success = show_final_status(service, db, initial_stats)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        logger.warning("Operation interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Error during embedding generation: {e}", exc_info=True)
        print(f"\n❌ An error occurred: {e}")
        return 1
    
    finally:
        try:
            db.close()
            logger.info("Database connection closed")
        except:
            pass


if __name__ == "__main__":
    sys.exit(main())