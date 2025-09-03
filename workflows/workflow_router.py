"""
Workflow Router for DeepCode and ZENALTO Integration

This module provides intelligent routing between different workflow types:
- DeepCode: Research paper analysis and code generation
- ZENALTO: Social media content creation and management
- Hybrid: Mixed workflows that combine both capabilities

The router analyzes input data to automatically detect the appropriate workflow
or uses explicit workflow mode specifications when provided.
"""

from typing import Dict, Any, List
import logging


class WorkflowRouter:
    """
    Intelligent workflow router for determining the appropriate processing pipeline.

    Analyzes user requests, file types, and context to route between:
    - DeepCode workflows (research-to-code)
    - ZENALTO workflows (social media management)
    - Hybrid workflows (combined functionality)
    """

    def __init__(self, logger: logging.Logger = None):
        """
        Initialize the workflow router.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

        # Keywords that indicate DeepCode workflow
        self.deepcode_indicators = [
            "research paper",
            "implement",
            "code",
            "algorithm",
            "github",
            "repository",
            "pdf",
            "academic",
            "paper",
            "analysis",
            "implementation",
            "reproduction",
            "codebase",
            "programming",
            "development",
            "software",
            "technical",
        ]

        # Keywords that indicate ZENALTO workflow
        self.zenalto_indicators = [
            "post",
            "tweet",
            "linkedin",
            "instagram",
            "social media",
            "facebook",
            "youtube",
            "hashtag",
            "engagement",
            "followers",
            "content creation",
            "social content",
            "campaign",
            "marketing",
            "audience",
            "brand",
            "viral",
            "influencer",
            "share",
        ]

        # File extensions associated with DeepCode workflows
        self.deepcode_file_types = [
            ".pdf",
            ".tex",
            ".py",
            ".js",
            ".md",
            ".txt",
            ".html",
            ".cpp",
            ".java",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".ipynb",
            ".rst",
            ".docx",
            ".doc",
        ]

        # File extensions associated with ZENALTO workflows
        self.zenalto_file_types = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".mp4",
            ".mov",
            ".avi",
            ".csv",
            ".xlsx",
            ".json",  # For analytics data
        ]

    async def detect_workflow_type(self, input_data: Dict[str, Any]) -> str:
        """
        Intelligently detect which workflow type to use based on input analysis.

        Args:
            input_data: Dictionary containing user request and context information
                - user_request: str - The user's request text
                - file_types: List[str] - File extensions if files are provided
                - workflow_mode: str - Explicit workflow specification
                - context: Dict - Additional context information
                - platform_context: Dict - Social platform connection status

        Returns:
            str: Detected workflow type ('deepcode', 'zenalto', or 'hybrid')
        """
        try:
            # Extract relevant information from input
            user_request = input_data.get("user_request", "").lower()
            file_types = input_data.get("file_types", [])
            explicit_mode = input_data.get("workflow_mode")
            platform_context = input_data.get("platform_context", {})

            self.logger.info(
                f"Analyzing workflow type for request: {user_request[:100]}..."
            )

            # 1. Check for explicit mode specification first
            if explicit_mode in ["deepcode", "zenalto", "hybrid"]:
                self.logger.info(f"Using explicit workflow mode: {explicit_mode}")
                return explicit_mode

            # 2. Check file types for strong indicators
            file_type_score = self._analyze_file_types(file_types)
            if file_type_score["deepcode"] > 0 and file_type_score["zenalto"] == 0:
                self.logger.info("DeepCode workflow detected based on file types")
                return "deepcode"
            elif file_type_score["zenalto"] > 0 and file_type_score["deepcode"] == 0:
                self.logger.info("ZENALTO workflow detected based on file types")
                return "zenalto"

            # 3. Analyze request content for keywords
            content_score = self._analyze_request_content(user_request)

            # 4. Check platform context (connected social platforms suggest ZENALTO)
            platform_score = self._analyze_platform_context(platform_context)

            # 5. Calculate total scores
            total_deepcode_score = (
                file_type_score["deepcode"] * 3  # File types weighted higher
                + content_score["deepcode"] * 2  # Content analysis
                + 0  # No platform bonus for deepcode
            )

            total_zenalto_score = (
                file_type_score["zenalto"] * 3  # File types weighted higher
                + content_score["zenalto"] * 2  # Content analysis
                + platform_score * 1  # Platform context bonus
            )

            self.logger.info(
                f"Workflow scores - DeepCode: {total_deepcode_score}, ZENALTO: {total_zenalto_score}"
            )

            # 6. Determine workflow based on scores
            if total_deepcode_score > total_zenalto_score:
                if total_zenalto_score > 0:
                    self.logger.info("Hybrid workflow detected (mixed indicators)")
                    return "hybrid"
                else:
                    self.logger.info("DeepCode workflow detected")
                    return "deepcode"
            elif total_zenalto_score > total_deepcode_score:
                if total_deepcode_score > 0:
                    self.logger.info("Hybrid workflow detected (mixed indicators)")
                    return "hybrid"
                else:
                    self.logger.info("ZENALTO workflow detected")
                    return "zenalto"
            else:
                # Default to deepcode for ambiguous cases
                self.logger.info("Ambiguous request, defaulting to DeepCode workflow")
                return "deepcode"

        except Exception as e:
            self.logger.error(f"Error in workflow detection: {str(e)}")
            # Safe fallback to deepcode
            return "deepcode"

    def _analyze_file_types(self, file_types: List[str]) -> Dict[str, int]:
        """
        Analyze file types to determine workflow preference.

        Args:
            file_types: List of file extensions

        Returns:
            Dict with deepcode and zenalto scores based on file types
        """
        deepcode_score = 0
        zenalto_score = 0

        for file_type in file_types:
            if file_type.lower() in self.deepcode_file_types:
                deepcode_score += 1
            elif file_type.lower() in self.zenalto_file_types:
                zenalto_score += 1

        return {"deepcode": deepcode_score, "zenalto": zenalto_score}

    def _analyze_request_content(self, request_text: str) -> Dict[str, int]:
        """
        Analyze request content for workflow indicators.

        Args:
            request_text: User's request text (lowercased)

        Returns:
            Dict with deepcode and zenalto scores based on content analysis
        """
        deepcode_score = sum(
            1 for indicator in self.deepcode_indicators if indicator in request_text
        )
        zenalto_score = sum(
            1 for indicator in self.zenalto_indicators if indicator in request_text
        )

        return {"deepcode": deepcode_score, "zenalto": zenalto_score}

    def _analyze_platform_context(self, platform_context: Dict[str, Any]) -> int:
        """
        Analyze platform context for ZENALTO workflow indicators.

        Args:
            platform_context: Dictionary of platform connection status

        Returns:
            int: Score bonus for ZENALTO workflow based on connected platforms
        """
        if not platform_context:
            return 0

        # Count connected social media platforms
        connected_platforms = sum(
            1
            for status in platform_context.values()
            if isinstance(status, dict) and status.get("connected", False)
        )

        # Bonus points for having connected social platforms
        return min(connected_platforms, 3)  # Cap at 3 points max

    def get_workflow_description(self, workflow_type: str) -> str:
        """
        Get human-readable description of the workflow type.

        Args:
            workflow_type: The workflow type identifier

        Returns:
            str: Human-readable workflow description
        """
        descriptions = {
            "deepcode": "Research Paper Analysis and Code Generation",
            "zenalto": "Social Media Content Creation and Management",
            "hybrid": "Combined Research and Social Media Workflow",
        }

        return descriptions.get(workflow_type, "Unknown Workflow Type")

    def validate_workflow_input(
        self, workflow_type: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that input data is appropriate for the selected workflow type.

        Args:
            workflow_type: The detected/selected workflow type
            input_data: Input data to validate

        Returns:
            Dict containing validation results with 'valid' boolean and any 'warnings'
        """
        validation_result = {"valid": True, "warnings": []}

        try:
            if workflow_type == "deepcode":
                # Check for research-related content
                user_request = input_data.get("user_request", "")
                file_types = input_data.get("file_types", [])

                if not user_request and not file_types:
                    validation_result["warnings"].append(
                        "DeepCode workflow requires either research content or files"
                    )

            elif workflow_type == "zenalto":
                # Check for social media context
                user_request = input_data.get("user_request", "")
                platform_context = input_data.get("platform_context", {})

                if not user_request:
                    validation_result["warnings"].append(
                        "ZENALTO workflow requires content creation request"
                    )

                if not platform_context:
                    validation_result["warnings"].append(
                        "Consider connecting social media platforms for better ZENALTO experience"
                    )

            elif workflow_type == "hybrid":
                # Hybrid workflows need both types of content
                validation_result["warnings"].append(
                    "Hybrid workflow detected - will process both research and social media components"
                )

        except Exception as e:
            validation_result["valid"] = False
            validation_result["warnings"].append(f"Validation error: {str(e)}")

        return validation_result
