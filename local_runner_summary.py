#!/usr/bin/env python3
"""
Configuration Summary for Local GitLab Runner Setup
Shows current configuration status and next steps
"""

import os
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print('='*60)

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{title}")
    print('-' * len(title))

def check_file_exists(filepath, description):
    """Check if a file exists and print status."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (missing)")
        return False

def main():
    print_header("AI Code Reviewer - Local Runner Configuration Summary")
    
    print_section("📁 Configuration Files")
    files_to_check = [
        ("/workspaces/code-reviewer/.gitlab-ci.yml", "GitLab CI Configuration"),
        ("/workspaces/code-reviewer/local-runner-setup.md", "Setup Guide"),
        ("/workspaces/code-reviewer/setup_local_runner_env.sh", "Environment Setup Script"),
        ("/workspaces/code-reviewer/check_local_runner.py", "Configuration Checker"),
        ("/workspaces/code-reviewer/docker-compose.runner.yml", "Docker Compose Runner"),
        ("/workspaces/code-reviewer/.env.runner.template", "Environment Template"),
    ]
    
    all_files_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    print_section("🔧 Current GitLab CI Configuration")
    try:
        with open("/workspaces/code-reviewer/.gitlab-ci.yml", 'r') as f:
            content = f.read()
            if "local-runner" in content and "ai-review" in content:
                print("✅ GitLab CI configured for local runner with tags: local-runner, ai-review")
            else:
                print("⚠️  GitLab CI may not be properly configured for local runner")
    except Exception as e:
        print(f"❌ Error reading GitLab CI config: {e}")
    
    print_section("🗂️  Environment Configuration")
    env_locations = [
        "/etc/gitlab-runner/env/ai-reviewer.env",
        f"{os.path.expanduser('~')}/.gitlab-runner-env",
        "/workspaces/code-reviewer/.env.runner"
    ]
    
    env_found = False
    for env_path in env_locations:
        if os.path.exists(env_path):
            print(f"✅ Environment file found: {env_path}")
            env_found = True
        else:
            print(f"⚪ Environment file not found: {env_path}")
    
    if not env_found:
        print("ℹ️  No environment files found - run setup_local_runner_env.sh to create")
    
    print_section("🤖 LLM Configuration")
    try:
        with open("/workspaces/code-reviewer/config.py", 'r') as f:
            content = f.read()
            if "DATABRICKS_TOKEN" in content and "LLM_CONFIG" in content:
                print("✅ Configuration updated to support Databricks LLM")
            else:
                print("⚠️  Configuration may not support Databricks LLM properly")
    except Exception as e:
        print(f"❌ Error reading config.py: {e}")
    
    print_section("📋 Setup Steps Summary")
    print("""
1. 🏗️  Install PostgreSQL and GitLab Runner:
   • Windows: Follow instructions in windows-runner-setup.md
   • Linux/macOS: Follow instructions in local-runner-setup.md

2. 🗄️  Set up Local Database:
   • Create PostgreSQL database 'rules'
   • Run: python verify_local_database.py

3. 🔐 Configure Environment Variables:
   • Windows: Run setup_windows_runner_env.ps1 as Administrator
   • Linux: Run sudo ./setup_local_runner_env.sh

4. 📝 Register GitLab Runner:
   • Get registration token from GitLab project settings
   • Use tags: ai-code-reviewer
   • Windows: shell executor, Linux: docker executor

5. ✅ Test Configuration:
   • Run: python check_local_runner.py
   • Verify all connections work

6. 🚀 Test Pipeline:
   • Create a merge request with SQL changes
   • Verify it runs on your local runner
   • Check AI review comments are posted
""")
    
    print_section("🔗 Important URLs")
    print("""
• GitLab Runner Docs: https://docs.gitlab.com/runner/
• Project Runners: [Your GitLab Project] → Settings → CI/CD → Runners
• Databricks Workspace: [Your Databricks URL]
• Local Setup Guide: ./local-runner-setup.md
""")
    
    print_section("⚠️  Security Notes")
    print("""
• Environment files contain sensitive tokens - keep them secure
• Never commit .env files to version control (they're in .gitignore)
• Use GitLab CI/CD variables for production deployments
• Consider network isolation for production runners
""")
    
    print_header("Next Steps")
    if all_files_exist:
        print("🎉 All configuration files are in place!")
        print("\n🚀 Ready to set up your local GitLab runner:")
        print("   1. Run: sudo ./setup_local_runner_env.sh")
        print("   2. Follow local-runner-setup.md for runner installation")
        print("   3. Test with: python3 check_local_runner.py")
    else:
        print("⚠️  Some configuration files are missing.")
        print("Please ensure all files are created before proceeding.")
    
    print(f"\n📚 For detailed instructions, see: local-runner-setup.md")

if __name__ == "__main__":
    main()
