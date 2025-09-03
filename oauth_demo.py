"""
OAuth Demo for ZENALTO Social Media Integration

This demonstrates the OAuth 2.0 flow for connecting social media platforms.
Run this as a standalone script to test OAuth functionality.
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

async def demo_oauth_flow():
    """Demonstrate the complete OAuth flow for social media platforms"""
    
    print("🚀 ZENALTO Social Media OAuth Demo")
    print("=" * 50)
    
    try:
        # Import our OAuth components
        from tools.social_media_server import SocialMediaServer
        
        # Create server instance
        server = SocialMediaServer()
        print("✅ Social Media Server initialized")
        
        # Test user
        test_user_id = f"demo_user_{int(datetime.now().timestamp())}"
        print(f"👤 Using test user ID: {test_user_id}")
        
        # Get current platform connections
        print("\n🔍 Checking current platform connections...")
        connections = await server.get_platform_connections(test_user_id)
        
        print("Platform connection status:")
        for platform, status in connections["connections"].items():
            connected_icon = "✅" if status["connected"] else "❌"
            print(f"  {connected_icon} {platform.upper()}: {status.get('message', 'Not connected')}")
        
        # Demo OAuth initiation for Twitter
        print("\n🐦 Initiating Twitter OAuth flow...")
        try:
            twitter_oauth = await server.oauth_manager.initiate_oauth_flow("twitter", test_user_id)
            
            if twitter_oauth.get("auth_url"):
                print("✅ OAuth URL generated!")
                print(f"🔗 Authorization URL: {twitter_oauth['auth_url'][:100]}...")
                print(f"🔑 State: {twitter_oauth['state']}")
                print(f"⏰ Expires in: {twitter_oauth['expires_in']} seconds")
            else:
                print("❌ Failed to generate OAuth URL")
                
        except Exception as e:
            print(f"❌ Twitter OAuth error: {e}")
        
        # Demo OAuth for LinkedIn
        print("\n💼 Initiating LinkedIn OAuth flow...")
        try:
            linkedin_oauth = await server.oauth_manager.initiate_oauth_flow("linkedin", test_user_id)
            
            if linkedin_oauth.get("auth_url"):
                print("✅ LinkedIn OAuth URL generated!")
                print(f"🔗 Authorization URL: {linkedin_oauth['auth_url'][:100]}...")
            else:
                print("❌ Failed to generate LinkedIn OAuth URL")
                
        except Exception as e:
            print(f"❌ LinkedIn OAuth error: {e}")
        
        # Show what would happen after user authorization
        print("\n🔄 OAuth Callback Simulation...")
        print("After user authorizes, the callback would:")
        print("  1. Receive authorization code")
        print("  2. Exchange code for access/refresh tokens") 
        print("  3. Encrypt and store tokens securely")
        print("  4. Test API connection")
        print("  5. Return success status to user")
        
        # Demo platform client creation
        print("\n🔧 Testing Platform Client Creation...")
        try:
            # This will fail without tokens, but shows the interface
            await server._get_platform_client("twitter", test_user_id)  # twitter_client unused
            print("✅ Twitter client created (no auth)")
            
            await server._get_platform_client("linkedin", test_user_id)  # linkedin_client unused 
            print("✅ LinkedIn client created (no auth)")
            
        except Exception as e:
            print(f"❌ Client creation error: {e}")
        
        # Demo what would happen with valid tokens
        print("\n📊 What happens with valid tokens:")
        print("  🐦 Twitter: Post tweets, get analytics, manage profile")
        print("  💼 LinkedIn: Post to feed, get connections, company pages")
        print("  📸 Instagram: View media, get basic analytics") 
        print("  📘 Facebook: Manage pages, post content, get insights")
        print("  🎥 YouTube: Upload videos, get channel stats")
        
        print("\n" + "=" * 50)
        print("✅ OAuth Demo completed successfully!")
        print("🔧 To use with real credentials:")
        print("   1. Set up apps on each platform")
        print("   2. Configure environment variables")
        print("   3. Set proper redirect URIs") 
        print("   4. Run the Streamlit app with OAuth UI")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


async def demo_rate_limiter():
    """Demonstrate the rate limiter functionality"""
    
    print("\n🚦 Rate Limiter Demo")
    print("-" * 30)
    
    try:
        from utils.rate_limiter import RateLimiter
        
        # Create rate limiter for Twitter
        twitter_limiter = RateLimiter("twitter")
        print("✅ Twitter rate limiter created")
        
        # Show rate limit status
        status = twitter_limiter.get_rate_limit_status()
        print("📊 Rate limit status:")
        print(f"   Requests made: {status['requests_made']}/{status['requests_made'] + status['requests_remaining']}")
        print(f"   Window resets in: {status['window_reset_in']:.1f} seconds")
        print(f"   Min interval: {status['min_interval']} seconds")
        
        # Simulate some API requests
        print("\n🔄 Simulating API requests...")
        for i in range(3):
            await twitter_limiter.wait_if_needed()
            twitter_limiter.record_request(success=True)
            print(f"   ✅ Request {i+1} completed")
        
        # Show updated status
        updated_status = twitter_limiter.get_rate_limit_status()
        print("\n📊 Updated status:")
        print(f"   Requests made: {updated_status['requests_made']}")
        print(f"   Success rate: {updated_status['success_rate']:.1%}")
        
    except Exception as e:
        print(f"❌ Rate limiter demo failed: {e}")


async def demo_secure_storage():
    """Demonstrate secure storage functionality"""
    
    print("\n🔐 Secure Storage Demo")
    print("-" * 25)
    
    try:
        from utils.secure_storage import SecureStorage
        
        storage = SecureStorage()
        print("✅ Secure storage initialized")
        
        # Store some test data
        test_data = {
            "platform": "twitter",
            "user_id": "demo_user",
            "access_token": "fake_token_123",
            "created_at": datetime.now().isoformat()
        }
        
        await storage.store("test_key", test_data, ttl=3600)
        print("✅ Test data stored with 1-hour TTL")
        
        # Retrieve the data
        retrieved_data = await storage.retrieve("test_key")
        if retrieved_data:
            print("✅ Data retrieved successfully")
            print(f"   Platform: {retrieved_data['platform']}")
            print(f"   User ID: {retrieved_data['user_id']}")
            print(f"   Created: {retrieved_data['created_at']}")
        else:
            print("❌ Failed to retrieve data")
        
        # Clean up
        await storage.delete("test_key")
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Secure storage demo failed: {e}")


async def main():
    """Run all demos"""
    await demo_oauth_flow()
    await demo_rate_limiter()
    await demo_secure_storage()


if __name__ == "__main__":
    print("🎭 Starting ZENALTO OAuth Integration Demo")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run the demo
    asyncio.run(main())