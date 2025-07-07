# tools/email/templates.py
"""
Placeholder for EmailTemplateManager module to satisfy import requirements.
This is a temporary solution to allow Atlas to launch while the actual implementation is developed.
"""

import logging

logger = logging.getLogger(__name__)
logger.warning("Using placeholder for EmailTemplateManager module")


class EmailTemplateManager:
    def __init__(self, *args, **kwargs):
        logger.info("Initialized placeholder EmailTemplateManager")
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, name):
        def method(*args, **kwargs):
            logger.warning(
                f"Called unimplemented method {name} on placeholder EmailTemplateManager"
            )
            return None

        return method
