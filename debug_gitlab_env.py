#!/usr/bin/env python3
# filepath: /workspaces/code-reviewer/debug_gitlab_env.py

import os
import subprocess
import sys

def debug_gitlab_environment():
    """Debug GitLab CI environment for PostgreSQL connectivity."""
    print("🔍 GitLab CI Environment Debug Information")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    pg_vars = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST_AUTH_METHOD']
    app_vars = ['dbname', 'user', 'password', 'host', 'port']
    
    for var in pg_vars + app_vars:
        value = os.getenv(var, 'NOT SET')
        if 'password' in var.lower():
            value = '•••••' if value != 'NOT SET' else value
        print(f"  {var}: {value}")
    
    # Check network connectivity
    print("\n🌐 Network Connectivity:")
    hosts_to_check = ['postgres', 'localhost', '127.0.0.1']
    
    for host in hosts_to_check:
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '3', host], 
                                  capture_output=True, text=True, timeout=5)
            status = "✅ Reachable" if result.returncode == 0 else "❌ Unreachable"
            print(f"  {host}: {status}")
        except Exception as e:
            print(f"  {host}: ❌ Error - {e}")
    
    # Check if PostgreSQL port is open
    print("\n🔌 Port Connectivity:")
    try:
        result = subprocess.run(['nc', '-z', '-v', 'postgres', '5432'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  postgres:5432 - ✅ Open")
        else:
            print("  postgres:5432 - ❌ Closed or filtered")
            print(f"  Error: {result.stderr}")
    except Exception as e:
        print(f"  postgres:5432 - ❌ Error checking port: {e}")
    
    # Check if PostgreSQL processes are running
    print("\n⚙️  Process Information:")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        postgres_processes = [line for line in result.stdout.split('\n') if 'postgres' in line.lower()]
        if postgres_processes:
            print("  PostgreSQL processes found:")
            for proc in postgres_processes[:5]:  # Show first 5
                print(f"    {proc}")
        else:
            print("  ❌ No PostgreSQL processes found")
    except Exception as e:
        print(f"  Error checking processes: {e}")

if __name__ == "__main__":
    debug_gitlab_environment()