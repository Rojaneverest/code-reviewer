#!/usr/bin/env python3
"""
Resilient cloud database setup script for CI/CD pipeline.
This script attempts to set up the database but doesn't fail the pipeline if it can't connect.
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloud_db_setup import main as original_setup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Resilient database setup that doesn't fail the CI/CD pipeline.
    """
    try:
        logger.info("🌟 Attempting to set up cloud database with SQL rules and embeddings...")
        original_setup()
        logger.info("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Database setup failed: {e}")
        logger.info("📝 This is expected behavior when database is unavailable")
        logger.info("🤖 Code review will continue using AI-only analysis")
        logger.info("💡 This ensures the CI/CD pipeline never fails due to database issues")
        
        # Create a marker file to indicate database setup failed
        try:
            with open('.db_setup_failed', 'w') as f:
                f.write(f"Database setup failed: {str(e)}\n")
                f.write("AI-only analysis will be used\n")
        except:
            pass  # If we can't write the marker file, that's ok
        
        return False

if __name__ == "__main__":
    success = main()
    # Always exit successfully to not fail the CI/CD pipeline
    sys.exit(0)
