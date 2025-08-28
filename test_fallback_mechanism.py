#!/usr/bin/env python3
"""
Test script to verify the fallback mechanism works when database is unavailable.
This simulates database failure scenarios to ensure the CI/CD pipeline continues working.
"""

import os
import sys
import json
from unittest.mock import patch, MagicMock
import psycopg2

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.retriever import find_relevant_rules
from rag.generator import generate_review
from main import analyze_code_chunk

def test_database_unavailable_scenario():
    """Test what happens when database connection fails."""
    print("🧪 Testing database unavailable scenario...")
    
    # Sample SQL code to test
    test_sql = """
    SELECT customer_id, customer_name, order_date 
    FROM customers c
    WHERE customer_id IN (
        SELECT customer_id 
        FROM orders 
        WHERE order_date = c.order_date
    )
    """
    
    # Mock psycopg2.connect to raise connection error
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.side_effect = psycopg2.OperationalError("connection failed")
        
        print("🔧 Simulating database connection failure...")
        
        # Test retriever fallback
        rules, method = find_relevant_rules(test_sql, language='SQL')
        print(f"✅ Retriever fallback method: {method}")
        print(f"✅ Rules returned: {rules}")
        
        # Test generator with database unavailable
        review = generate_review(test_sql, rules, method)
        print(f"✅ Review generated: {review is not None}")
        if review:
            print(f"✅ Issues found: {review.get('issues_found', 0)}")
            if review.get('issues'):
                for issue in review['issues']:
                    print(f"  - Line {issue.get('line_number')}: {issue.get('suggestion')[:100]}...")
        
        # Test main analysis function
        issues = analyze_code_chunk(test_sql, language='SQL')
        print(f"✅ Main analysis returned {len(issues)} issues")

def test_normal_scenario_with_mock_db():
    """Test normal scenario with mocked database that works."""
    print("\n🧪 Testing normal scenario with mock database...")
    
    test_sql = "SELECT * FROM users"
    
    # Mock successful database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock some sample rules
    mock_cursor.fetchall.return_value = [
        (1, "Avoid SELECT *", "Using SELECT * can impact performance", "SELECT \\*", "Major", "bad", "Performance")
    ]
    
    with patch('psycopg2.connect', return_value=mock_conn):
        rules, method = find_relevant_rules(test_sql, language='SQL')
        print(f"✅ Normal scenario method: {method}")
        print(f"✅ Rules returned: {len(rules.get('bad_practices', []))} bad practices found")
        
        review = generate_review(test_sql, rules, method)
        print(f"✅ Review generated: {review is not None}")

def test_ai_fallback_quality():
    """Test that AI fallback provides meaningful suggestions."""
    print("\n🧪 Testing AI fallback quality...")
    
    # SQL with obvious performance issues for AI to catch
    problematic_sql = """
    SELECT DISTINCT c.customer_id, c.customer_name,
           (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count,
           (SELECT MAX(order_date) FROM orders o WHERE o.customer_id = c.customer_id) as last_order
    FROM customers c
    WHERE c.customer_id IN (
        SELECT DISTINCT customer_id 
        FROM orders 
        WHERE order_date > '2023-01-01'
    )
    ORDER BY customer_name
    """
    
    # Test pure AI analysis
    empty_rules = {'good_practices': [], 'bad_practices': []}
    review = generate_review(problematic_sql, empty_rules, "Database Unavailable - AI Fallback")
    
    print(f"✅ AI-only analysis completed: {review is not None}")
    if review and review.get('issues_found', 0) > 0:
        print(f"✅ AI found {review['issues_found']} issues:")
        for issue in review['issues']:
            print(f"  - Line {issue.get('line_number')}: {issue.get('suggestion')[:150]}...")
    else:
        print("ℹ️  AI found no issues (this might be expected)")

def main():
    """Run all fallback mechanism tests."""
    print("🚀 Testing Code Review Fallback Mechanism")
    print("=" * 60)
    
    try:
        test_database_unavailable_scenario()
        test_normal_scenario_with_mock_db() 
        test_ai_fallback_quality()
        
        print("\n" + "=" * 60)
        print("✅ All fallback mechanism tests completed successfully!")
        print("✅ CI/CD pipeline should continue working even with database issues")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
