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
echo "⏳ Please wait while we test the database connection..."
echo ""

# Run the Python script and capture its exit code
python test_supabase_connection.py
exit_code=$?

echo ""
echo "================================="

# Check the result
if [ $exit_code -eq 0 ]; then
    echo "✅ Connection test PASSED!"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Set the same credentials in GitLab CI/CD Variables"
    echo "   2. Run full setup: python cloud_db_setup.py"
    echo "   3. Test your GitLab CI/CD pipeline"
else
    echo "❌ Connection test FAILED!"
    echo ""
    echo "🔧 Please check:"
    echo "   1. Your Supabase password is correct"
    echo "   2. Network connectivity to Supabase"
    echo "   3. Supabase project is active"
    echo ""
    echo "💡 Update the password in this script and try again."
fi

echo ""
echo "🎯 Script completed with exit code: $exit_code"
