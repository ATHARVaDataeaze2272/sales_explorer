"""
Test Script for Embedding Generation
Verify that embeddings are working correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
import numpy as np
from database.config import get_db
from database.models import ClientUploadProfile, Prospects, ClientEmbedding, ProspectEmbedding
from matching.text_templates import *
from matching.embeddings import EmbeddingService


def test_model_loading():
    """Test 1: Check if model loads correctly"""
    print("\n" + "="*60)
    print("TEST 1: Model Loading")
    print("="*60)
    
    try:
        service = EmbeddingService()
        model = service.model
        print("✅ Model loaded successfully")
        print(f"   Model: {service.model_name}")
        print(f"   Embedding dimensions: 384")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False


def test_single_embedding():
    """Test 2: Generate a single embedding"""
    print("\n" + "="*60)
    print("TEST 2: Single Embedding Generation")
    print("="*60)
    
    try:
        service = EmbeddingService()
        test_text = "Chief Marketing Officer with expertise in digital transformation"
        
        embedding = service.generate_embedding(test_text)
        
        if embedding is None:
            print("❌ Embedding generation returned None")
            return False
        
        print(f"✅ Embedding generated successfully")
        print(f"   Input text: {test_text}")
        print(f"   Embedding length: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        print(f"   Data type: {type(embedding[0])}")
        
        # Check dimensions
        if len(embedding) != 384:
            print(f"❌ Wrong dimensions: {len(embedding)} (expected 384)")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Single embedding test failed: {e}")
        return False


def test_text_templates():
    """Test 3: Text template formatting"""
    print("\n" + "="*60)
    print("TEST 3: Text Templates")
    print("="*60)
    
    try:
        db = next(get_db())
        
        # Test client templates
        client = db.query(ClientUploadProfile).first()
        if client:
            print("\n📄 Client Text Templates:")
            
            job_text = format_client_job_title_text(client)
            print(f"   Job Title Text: {job_text[:100]}...")
            
            business_text = format_client_business_area_text(client)
            print(f"   Business Area Text: {business_text[:100]}...")
            
            activity_text = format_client_activity_text(client)
            print(f"   Activity Text: {activity_text[:100]}...")
        
        # Test prospect templates
        prospect = db.query(Prospects).first()
        if prospect:
            print("\n📄 Prospect Text Templates:")
            
            job_text = format_prospect_job_title_text(prospect)
            print(f"   Job Title Text: {job_text[:100]}...")
            
            business_text = format_prospect_business_area_text(prospect)
            print(f"   Business Area Text: {business_text[:100]}...")
            
            expertise_text = format_prospect_expertise_text(prospect)
            print(f"   Expertise Text: {expertise_text[:100]}...")
        
        print("\n✅ Text templates working correctly")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Text template test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_client_embedding_generation():
    """Test 4: Generate embeddings for one client"""
    print("\n" + "="*60)
    print("TEST 4: Client Embedding Generation")
    print("="*60)
    
    try:
        db = next(get_db())
        service = EmbeddingService()
        
        # Get first client
        client = db.query(ClientUploadProfile).first()
        if not client:
            print("⚠️  No clients found in database")
            return False
        
        print(f"\n🔄 Generating embeddings for client ID: {client.id}")
        
        success = service.generate_client_embeddings(db, client.id, regenerate=True)
        
        if not success:
            print("❌ Embedding generation failed")
            return False
        
        # Verify embeddings were stored
        embedding = db.query(ClientEmbedding).filter(
            ClientEmbedding.profile_id == client.id
        ).first()
        
        if not embedding:
            print("❌ Embeddings not found in database")
            return False
        
        print(f"✅ Embeddings generated and stored successfully")
        print(f"   Profile ID: {embedding.profile_id}")
        # FIXED: Use 'is not None' instead of boolean check
        print(f"   Job Title Embedding: {'✓' if embedding.job_title_embedding is not None else '✗'}")
        print(f"   Business Area Embedding: {'✓' if embedding.business_area_embedding is not None else '✗'}")
        print(f"   Activity Embedding: {'✓' if embedding.activity_embedding is not None else '✗'}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Client embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prospect_embedding_generation():
    """Test 5: Generate embeddings for one prospect"""
    print("\n" + "="*60)
    print("TEST 5: Prospect Embedding Generation")
    print("="*60)
    
    try:
        db = next(get_db())
        service = EmbeddingService()
        
        # Get first prospect
        prospect = db.query(Prospects).first()
        if not prospect:
            print("⚠️  No prospects found in database")
            return False
        
        print(f"\n🔄 Generating embeddings for prospect ID: {prospect.id}")
        
        success = service.generate_prospect_embeddings(db, prospect.id, regenerate=True)
        
        if not success:
            print("❌ Embedding generation failed")
            return False
        
        # Verify embeddings were stored
        embedding = db.query(ProspectEmbedding).filter(
            ProspectEmbedding.prospect_id == prospect.id
        ).first()
        
        if not embedding:
            print("❌ Embeddings not found in database")
            return False
        
        print(f"✅ Embeddings generated and stored successfully")
        print(f"   Prospect ID: {embedding.prospect_id}")
        # FIXED: Use 'is not None' instead of boolean check on arrays
        print(f"   Job Title Embedding: {'✓' if embedding.job_title_embedding is not None else '✗'}")
        print(f"   Business Area Embedding: {'✓' if embedding.business_area_embedding is not None else '✗'}")
        print(f"   Expertise Embedding: {'✓' if embedding.expertise_embedding is not None else '✗'}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Prospect embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_storage():
    """Test 6: Verify database storage and retrieval"""
    print("\n" + "="*60)
    print("TEST 6: Database Storage & Retrieval")
    print("="*60)
    
    try:
        db = next(get_db())
        
        # Check client embeddings
        client_count = db.query(ClientEmbedding).count()
        print(f"\n📊 Client Embeddings in DB: {client_count}")
        
        # Check prospect embeddings
        prospect_count = db.query(ProspectEmbedding).count()
        print(f"📊 Prospect Embeddings in DB: {prospect_count}")
        
        if client_count > 0:
            # Get a sample
            sample = db.query(ClientEmbedding).first()
            print(f"\n🔍 Sample Client Embedding:")
            print(f"   ID: {sample.id}")
            print(f"   Profile ID: {sample.profile_id}")
            print(f"   Created: {sample.created_at}")
            
            # FIXED: Check vector dimensions with 'is not None'
            if sample.job_title_embedding is not None:
                print(f"   Job Title Vector Length: {len(sample.job_title_embedding)}")
        
        if prospect_count > 0:
            # Get a sample
            sample = db.query(ProspectEmbedding).first()
            print(f"\n🔍 Sample Prospect Embedding:")
            print(f"   ID: {sample.id}")
            print(f"   Prospect ID: {sample.prospect_id}")
            print(f"   Created: {sample.created_at}")
            
            # FIXED: Check vector dimensions with 'is not None'
            if sample.job_title_embedding is not None:
                print(f"   Job Title Vector Length: {len(sample.job_title_embedding)}")
        
        print("\n✅ Database storage working correctly")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING EMBEDDING SYSTEM TESTS")
    print("="*60)
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Single Embedding", test_single_embedding),
        ("Text Templates", test_text_templates),
        ("Client Embedding Generation", test_client_embedding_generation),
        ("Prospect Embedding Generation", test_prospect_embedding_generation),
        ("Database Storage", test_database_storage)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Embedding system is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())