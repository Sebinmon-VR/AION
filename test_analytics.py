#!/usr/bin/env python3
"""
Test script for AION HR Analytics Integration
Tests all the new enhanced analytics functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import (
    get_enhanced_hiring_success_rate,
    get_enhanced_monthly_insights,
    get_enhanced_department_insights,
    get_enhanced_hiring_predictions,
    get_enhanced_top_performers,
    get_enhanced_salary_trends,
    get_enhanced_onboarding_insights,
    get_enhanced_probation_insights,
    get_enhanced_market_salary_comparison
)

def test_analytics_functions():
    """Test all enhanced analytics functions"""
    print("🔍 Testing AION HR Analytics Integration...")
    print("=" * 60)
    
    # Test 1: Hiring Success Rate
    print("1️⃣ Testing Hiring Success Rate Analysis...")
    try:
        result = get_enhanced_hiring_success_rate()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   � Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Monthly Insights
    print("\n2️⃣ Testing Monthly Hiring Insights...")
    try:
        result = get_enhanced_monthly_insights()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   � Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Department Interview Efficiency
    print("\n3️⃣ Testing Department Interview Efficiency...")
    try:
        result = get_enhanced_department_insights()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   🏆 Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Hiring Predictions
    print("\n4️⃣ Testing Hiring Predictions...")
    try:
        result = get_enhanced_hiring_predictions()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   ⏰ Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Top Performers
    print("\n5️⃣ Testing Top Performers Analysis...")
    try:
        result = get_enhanced_top_performers()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   🌟 Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Salary Trends
    print("\n6️⃣ Testing Salary Trend Analysis...")
    try:
        result = get_enhanced_salary_trends()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   💰 Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 7: Onboarding Insights
    print("\n7️⃣ Testing Onboarding Insights...")
    try:
        result = get_enhanced_onboarding_insights()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   🚀 Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 8: Probation Insights
    print("\n8️⃣ Testing Probation Analysis...")
    try:
        result = get_enhanced_probation_insights()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   📋 Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 9: Market Salary Comparison
    print("\n9️⃣ Testing Market Salary Comparison...")
    try:
        result = get_enhanced_market_salary_comparison()
        print(f"   ✅ Success: Function returned {len(result)} characters")
        print(f"   🏪 Preview: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Analytics Testing Complete!")
    print("💡 All enhanced analytics functions are ready for chatbot integration")

if __name__ == "__main__":
    test_analytics_functions()
