#!/usr/bin/env python3
"""
ZenAlto Conversion Demo Script

This script demonstrates the conversion from DeepCode to ZenAlto,
showing how the same multi-agent architecture now handles social media management.
"""

import asyncio
import json
from datetime import datetime

# Import ZenAlto components (simplified for demo)
from tools.content_intent_server import ContentIntentServer


class MockSocialServer:
    """Mock social media server for demo purposes"""

    async def get_platform_status(self):
        return {
            "success": True,
            "platform_status": {
                "twitter": {
                    "connected": True,
                    "last_check": datetime.now().isoformat(),
                },
                "instagram": {
                    "connected": False,
                    "last_check": datetime.now().isoformat(),
                },
                "linkedin": {
                    "connected": True,
                    "last_check": datetime.now().isoformat(),
                },
                "facebook": {
                    "connected": False,
                    "last_check": datetime.now().isoformat(),
                },
                "youtube": {
                    "connected": False,
                    "last_check": datetime.now().isoformat(),
                },
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def schedule_post(self, platform, content, scheduled_time):
        return {
            "success": True,
            "schedule_result": {
                "schedule_id": f"schedule_{platform}_{int(datetime.now().timestamp())}",
                "platform": platform,
                "scheduled_time": scheduled_time,
                "content_preview": content.get("text", "")[:50] + "...",
                "status": "scheduled",
            },
            "timestamp": datetime.now().isoformat(),
        }


class ZenAltoDemo:
    """
    Demonstration of ZenAlto's social media management capabilities
    """

    def __init__(self):
        self.intent_server = None
        self.social_server = None

    async def initialize(self):
        """Initialize ZenAlto components"""
        print("🚀 Initializing ZenAlto - AI Social Media Management Platform")
        print("=" * 60)

        # Initialize components
        self.social_server = MockSocialServer()
        self.intent_server = ContentIntentServer()

        print("✅ Components initialized successfully")
        print()

    async def demonstrate_intent_analysis(self):
        """Demonstrate content intent analysis"""
        print("🎯 Content Intent Analysis Demo")
        print("-" * 40)

        sample_request = "Create an engaging post about AI automation for my tech company on LinkedIn and Twitter"

        print(f"User Request: {sample_request}")
        print()

        # Analyze intent
        intent_result = await self.intent_server.analyze_intent(sample_request)

        if intent_result["success"]:
            analysis = intent_result["intent_analysis"]
            print("📊 Intent Analysis Results:")
            print(f"  • Summary: {analysis['intent_summary']}")
            print(f"  • Platforms: {', '.join(analysis['platforms'])}")
            print(f"  • Audience: {analysis['audience']}")
            print(f"  • Content Type: {analysis['content_type']}")
            print(f"  • Tone: {analysis['tone']}")
            print(f"  • Urgency: {analysis['urgency']}")
        else:
            print("❌ Intent analysis failed")

        print()

    async def demonstrate_platform_status(self):
        """Demonstrate platform connection status"""
        print("📱 Platform Connection Status")
        print("-" * 40)

        status_result = await self.social_server.get_platform_status()

        if status_result["success"]:
            print("🔗 Platform Status:")
            for platform, status in status_result["platform_status"].items():
                connected = "✅ Connected" if status["connected"] else "❌ Disconnected"
                print(f"  • {platform.capitalize()}: {connected}")
        else:
            print("❌ Failed to get platform status")

        print()

    async def demonstrate_content_generation(self):
        """Demonstrate content generation workflow"""
        print("🧠 Content Generation Demo")
        print("-" * 40)

        # Simulate content generation for LinkedIn
        content_request = {
            "platform": "linkedin",
            "topic": "AI automation in business",
            "tone": "professional",
            "audience": "business professionals",
        }

        print(f"Generating content for: {content_request['platform']}")
        print(f"Topic: {content_request['topic']}")
        print(f"Tone: {content_request['tone']}")
        print()

        # Get content suggestions
        suggestions = await self.intent_server.get_content_suggestions(
            user_id="demo_user",
            topic=content_request["topic"],
            platform=content_request["platform"],
        )

        if suggestions["success"]:
            suggestion_data = suggestions["suggestions"]
            print("💡 Content Suggestions:")
            print(f"  • Recommended Tone: {suggestion_data['recommended_tone']}")
            print(
                f"  • Suggested Hashtags: {', '.join(suggestion_data['suggested_hashtags'])}"
            )
            print()
            print("📝 Sample Content Ideas:")
            for idea in suggestion_data["suggested_content"][:2]:  # Show first 2
                print(f"  • {idea['content']}")
        else:
            print("❌ Content generation failed")

        print()

    async def demonstrate_scheduling(self):
        """Demonstrate content scheduling"""
        print("📅 Content Scheduling Demo")
        print("-" * 40)

        # Schedule a post
        schedule_request = {
            "platform": "twitter",
            "content": {
                "text": "Excited to share how AI is transforming business processes! #AI #Automation"
            },
            "scheduled_time": "2025-01-15T10:00:00Z",
        }

        print(f"Scheduling post for: {schedule_request['platform']}")
        print(f"Scheduled time: {schedule_request['scheduled_time']}")
        print()

        schedule_result = await self.social_server.schedule_post(
            schedule_request["platform"],
            schedule_request["content"],
            schedule_request["scheduled_time"],
        )

        if schedule_result["success"]:
            print("✅ Post scheduled successfully!")
            print(
                f"  • Schedule ID: {schedule_result['schedule_result']['schedule_id']}"
            )
            print(f"  • Status: {schedule_result['schedule_result']['status']}")
        else:
            print("❌ Scheduling failed")

        print()

    async def run_full_demo(self):
        """Run complete ZenAlto demonstration"""
        print("🎬 ZenAlto Full Demo")
        print("=" * 60)
        print("Converting DeepCode's architecture for social media management...")
        print()

        await self.initialize()
        await self.demonstrate_intent_analysis()
        await self.demonstrate_platform_status()
        await self.demonstrate_content_generation()
        await self.demonstrate_scheduling()

        print("🎉 ZenAlto Demo Complete!")
        print("=" * 60)
        print("✅ Successfully converted DeepCode to ZenAlto")
        print("✅ Multi-agent architecture adapted for social media")
        print("✅ MCP tools replaced with social media integrations")
        print("✅ Conversational AI interface ready")
        print()
        print("🚀 ZenAlto is now ready for social media management!")


async def main():
    """Main demo function"""
    demo = ZenAltoDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    print("ZenAlto - AI Social Media Management Platform")
    print("Conversion Demo from DeepCode")
    print()

    # Run async demo
    asyncio.run(main())
