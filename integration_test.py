"""
Integration test for ZENALTO OAuth and Social Media functionality

Run this to test the complete integration works properly.
"""

import asyncio
import sys
import logging
from datetime import datetime

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_complete_integration():
    """Test the complete OAuth and social media integration"""
    
    print("🧪 ZENALTO Integration Test Suite")
    print("=" * 50)
    
    test_results = {
        "imports": False,
        "oauth_manager": False,
        "platform_clients": False,
        "social_models": False,
        "secure_storage": False,
        "rate_limiter": False,
        "social_server": False,
        "end_to_end": False
    }
    
    # Test 1: Import all modules
    print("\n1️⃣ Testing imports...")
    try:
        from utils.oauth_manager import OAuthManager
        from utils.secure_storage import SecureStorage
        from utils.rate_limiter import RateLimiter
        from models.social_models import PlatformConnection
        from social_apis.twitter_client import TwitterClient
        # from social_apis.linkedin_client import LinkedInClient  # Unused
        from tools.social_media_server import SocialMediaServer
        
        print("✅ All imports successful")
        test_results["imports"] = True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return test_results
    
    # Test 2: OAuth Manager functionality
    print("\n2️⃣ Testing OAuth Manager...")
    try:
        oauth_manager = OAuthManager()
        
        # Test OAuth URL generation
        user_id = "test_user_integration"
        oauth_result = await oauth_manager.initiate_oauth_flow("twitter", user_id)
        
        assert "auth_url" in oauth_result
        assert "state" in oauth_result
        assert oauth_result["platform"] == "twitter"
        
        print("✅ OAuth Manager working")
        test_results["oauth_manager"] = True
    except Exception as e:
        print(f"❌ OAuth Manager failed: {e}")
    
    # Test 3: Platform Clients
    print("\n3️⃣ Testing Platform Clients...")
    try:
        twitter_client = TwitterClient("twitter", oauth_manager, user_id)
        # linkedin_client = LinkedInClient("linkedin", oauth_manager, user_id)  # Unused, commented out
        
        # Test client properties
        assert twitter_client.platform == "twitter"
        assert twitter_client.user_id == user_id
        assert twitter_client._get_api_base_url() == "https://api.twitter.com/2"
        
        print("✅ Platform clients working")
        test_results["platform_clients"] = True
    except Exception as e:
        print(f"❌ Platform clients failed: {e}")
    
    # Test 4: Social Models
    print("\n4️⃣ Testing Social Models...")
    try:
        from models.social_models import PlatformType, ConnectionStatus
        
        # Test model creation
        connection = PlatformConnection(
            platform=PlatformType.TWITTER,
            user_id=user_id,
            status=ConnectionStatus.CONNECTED
        )
        
        assert connection.platform == PlatformType.TWITTER
        assert connection.is_active()
        
        # Test model serialization
        connection_dict = connection.to_dict()
        assert "platform" in connection_dict
        assert connection_dict["platform"] == "twitter"
        
        print("✅ Social models working")
        test_results["social_models"] = True
    except Exception as e:
        print(f"❌ Social models failed: {e}")
    
    # Test 5: Secure Storage
    print("\n5️⃣ Testing Secure Storage...")
    try:
        storage = SecureStorage()
        
        # Test store and retrieve
        test_data = {"test": "value", "timestamp": datetime.now().isoformat()}
        await storage.store("integration_test", test_data, ttl=3600)
        
        retrieved_data = await storage.retrieve("integration_test")
        assert retrieved_data["test"] == "value"
        
        # Clean up
        await storage.delete("integration_test")
        
        print("✅ Secure storage working")
        test_results["secure_storage"] = True
    except Exception as e:
        print(f"❌ Secure storage failed: {e}")
    
    # Test 6: Rate Limiter
    print("\n6️⃣ Testing Rate Limiter...")
    try:
        rate_limiter = RateLimiter("twitter")
        
        # Test rate limit status
        status = rate_limiter.get_rate_limit_status()
        assert "platform" in status
        assert status["platform"] == "twitter"
        
        # Test request recording
        rate_limiter.record_request(success=True)
        updated_status = rate_limiter.get_rate_limit_status()
        assert updated_status["requests_made"] == 1
        
        print("✅ Rate limiter working")
        test_results["rate_limiter"] = True
    except Exception as e:
        print(f"❌ Rate limiter failed: {e}")
    
    # Test 7: Social Media Server
    print("\n7️⃣ Testing Social Media Server...")
    try:
        server = SocialMediaServer()
        
        # Test server initialization
        assert hasattr(server, "oauth_manager")
        assert hasattr(server, "platform_clients")
        
        # Test platform connections check
        connections = await server.get_platform_connections(user_id)
        assert connections["success"]
        assert "connections" in connections
        
        print("✅ Social Media Server working")
        test_results["social_server"] = True
    except Exception as e:
        print(f"❌ Social Media Server failed: {e}")
    
    # Test 8: End-to-End OAuth Flow (without real credentials)
    print("\n8️⃣ Testing End-to-End OAuth Flow...")
    try:
        # Initiate OAuth
        oauth_result = await server.oauth_manager.initiate_oauth_flow("linkedin", user_id)
        
        # Test that we get proper OAuth URL structure
        auth_url = oauth_result["auth_url"]
        assert "linkedin.com" in auth_url
        assert "client_id" in auth_url
        assert "redirect_uri" in auth_url
        assert "state" in auth_url
        
        # Test OAuth state management
        state = oauth_result["state"]
        assert state in server.oauth_manager.oauth_states
        oauth_state = server.oauth_manager.oauth_states[state]
        assert oauth_state["platform"] == "linkedin"
        assert oauth_state["user_id"] == user_id
        
        print("✅ End-to-end OAuth flow structure working")
        test_results["end_to_end"] = True
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, passed_test in test_results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("🚀 ZENALTO OAuth integration is ready for production")
    else:
        print("⚠️  Some tests failed. Review the errors above.")
    
    return test_results


async def test_oauth_security():
    """Test OAuth security features"""
    
    print("\n🔒 Testing OAuth Security Features")
    print("-" * 40)
    
    try:
        from utils.oauth_manager import OAuthManager
        oauth_manager = OAuthManager()
        
        # Test state generation is random
        state1 = oauth_manager._generate_secure_state()
        state2 = oauth_manager._generate_secure_state()
        assert state1 != state2
        assert len(state1) > 20  # Should be reasonably long
        print("✅ Secure state generation working")
        
        # Test PKCE code generation
        verifier = oauth_manager._generate_code_verifier()
        challenge = oauth_manager._generate_code_challenge(verifier)
        assert verifier != challenge
        assert len(verifier) > 40
        print("✅ PKCE code generation working")
        
        # Test encryption key generation
        key = oauth_manager._get_or_create_encryption_key()
        assert len(key) == 44  # Fernet key length
        print("✅ Encryption key management working")
        
        print("🔒 All security tests passed!")
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")


if __name__ == "__main__":
    print("🎭 Starting ZENALTO Integration Test Suite")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python {sys.version.split()[0]}")
    
    async def run_all_tests():
        results = await test_complete_integration()
        await test_oauth_security()
        return results
    
    results = asyncio.run(run_all_tests())
    
    # Exit with proper code
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        print("\n✅ All tests passed - Integration successful!")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} tests failed")
        sys.exit(1)