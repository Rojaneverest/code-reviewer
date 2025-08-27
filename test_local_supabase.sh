#!/bin/bash
# test_local_supabase.sh - Test Supabase connection locally

echo "🌟 Testing Supabase Connection Locally"
echo "================================="

# Set your Supabase credentials here
export host="db.ziuhftkruvdlwiyfepop.supabase.co"
export port="5432"
export dbname="postgres"
export user="postgres"
export password="root"  # Replace with actual password

echo "📋 Connection Details:"
echo "Host: $host"
echo "Port: $port"
echo "Database: $dbname"
echo "User: $user"
echo "Password: [hidden]"
echo ""

echo "🔍 Testing connection..."
python test_supabase_connection.py

echo ""
echo "💡 If connection successful, you can run the full setup:"
echo "   python cloud_db_setup.py"
