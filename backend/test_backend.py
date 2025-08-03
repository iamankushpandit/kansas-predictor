import pytest
import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://localhost:3001"
TIMEOUT = 30

class TestKansasClaimsAPI:
    """Comprehensive test suite for Kansas Claims Predictor API"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        print("Setting up test environment...")
        # Wait for server to be ready
        cls.wait_for_server()
        
    @classmethod
    def wait_for_server(cls, max_attempts=10):
        """Wait for server to be available"""
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{BASE_URL}/", timeout=5)
                if response.status_code == 200:
                    print("Server is ready!")
                    return
            except requests.exceptions.RequestException:
                pass
            print(f"Waiting for server... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
        raise Exception("Server not available after maximum attempts")

    def test_server_health(self):
        """Test basic server connectivity"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_get_counties(self):
        """Test counties endpoint"""
        response = requests.get(f"{BASE_URL}/counties")
        assert response.status_code == 200
        data = response.json()
        assert "counties" in data
        assert isinstance(data["counties"], list)
        assert len(data["counties"]) > 0
        # Check for major Kansas counties
        counties = data["counties"]
        assert "Johnson" in counties
        assert "Sedgwick" in counties
        assert "Shawnee" in counties

    def test_get_claim_types(self):
        """Test claim types endpoint"""
        response = requests.get(f"{BASE_URL}/claim-types")
        assert response.status_code == 200
        data = response.json()
        assert "claim_types" in data
        assert isinstance(data["claim_types"], list)
        claim_types = data["claim_types"]
        # Check for expected claim types
        expected_types = ["emergency", "inpatient", "outpatient", "pharmacy", "mental_health", "preventive"]
        for claim_type in expected_types:
            assert claim_type in claim_types

    # Volume Predictions Tests
    def test_volume_prediction_emergency_johnson(self):
        """Test: Predict emergency claims for Johnson County next week"""
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        payload = {
            "county": "Johnson",
            "claim_type": "emergency",
            "target_date": next_week
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["county"] == "Johnson"
        assert data["claim_type"] == "emergency"
        assert data["predicted_count"] >= 0
        assert data["predicted_cost"] >= 0
        assert data["avg_cost_per_claim"] >= 0
        print(f"Johnson County emergency prediction: {data['predicted_count']} claims, ${data['predicted_cost']:,.2f}")

    def test_volume_prediction_pharmacy_wichita(self):
        """Test: How many pharmacy claims will Wichita have in January?"""
        january_date = "2025-01-15"  # Mid-January
        
        payload = {
            "county": "Sedgwick",  # Wichita is in Sedgwick County
            "claim_type": "pharmacy",
            "target_date": january_date
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["county"] == "Sedgwick"
        assert data["claim_type"] == "pharmacy"
        assert data["predicted_count"] >= 0
        print(f"Wichita pharmacy prediction for January: {data['predicted_count']} claims")

    def test_mental_health_trend_topeka(self):
        """Test: Show mental health claims trend for Topeka"""
        response = requests.get(f"{BASE_URL}/predict-range/Shawnee/mental_health?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        predictions = data["predictions"]
        assert len(predictions) > 0
        
        # Verify trend data structure
        for prediction in predictions[:5]:  # Check first 5 predictions
            assert "county" in prediction
            assert "claim_type" in prediction
            assert "predicted_count" in prediction
            assert prediction["county"] == "Shawnee"
            assert prediction["claim_type"] == "mental_health"
        
        print(f"Topeka mental health trend: {len(predictions)} days of predictions")

    # Cost Analysis Tests
    def test_average_cost_per_claim_sedgwick(self):
        """Test: What's the average cost per claim in Sedgwick County?"""
        response = requests.get(f"{BASE_URL}/summary/Sedgwick")
        assert response.status_code == 200
        
        data = response.json()
        assert data["county"] == "Sedgwick"
        assert "summary" in data
        
        summary = data["summary"]
        # Check that we have cost data for different claim types
        assert len(summary) > 0
        print(f"Sedgwick County summary includes {len(summary)} claim types")

    def test_claim_cost_comparison_urban_rural(self):
        """Test: Compare claim costs between urban and rural areas"""
        # Test urban county (Johnson)
        urban_response = requests.get(f"{BASE_URL}/summary/Johnson")
        assert urban_response.status_code == 200
        urban_data = urban_response.json()
        
        # Test rural county (Ford)
        rural_response = requests.get(f"{BASE_URL}/summary/Ford")
        assert rural_response.status_code == 200
        rural_data = rural_response.json()
        
        assert urban_data["county"] == "Johnson"
        assert rural_data["county"] == "Ford"
        assert "summary" in urban_data
        assert "summary" in rural_data
        
        print(f"Urban vs Rural comparison: Johnson vs Ford counties analyzed")

    def test_predict_total_healthcare_spending_q1(self):
        """Test: Predict total healthcare spending for Kansas in Q1"""
        # Test multiple counties and claim types for Q1 prediction
        q1_date = "2025-03-15"  # Mid Q1
        counties = ["Johnson", "Sedgwick", "Shawnee"]
        claim_types = ["emergency", "inpatient", "outpatient", "pharmacy"]
        
        total_predictions = []
        
        for county in counties:
            for claim_type in claim_types:
                payload = {
                    "county": county,
                    "claim_type": claim_type,
                    "target_date": q1_date
                }
                
                response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    total_predictions.append(data["predicted_cost"])
        
        assert len(total_predictions) > 0
        total_cost = sum(total_predictions)
        print(f"Q1 healthcare spending prediction (sample): ${total_cost:,.2f}")

    # Seasonal Patterns Tests
    def test_flu_season_effect_johnson(self):
        """Test: How does flu season affect claims in Johnson County?"""
        response = requests.get(f"{BASE_URL}/insights/Johnson/emergency")
        assert response.status_code == 200
        
        data = response.json()
        assert data["county"] == "Johnson"
        assert data["claim_type"] == "emergency"
        assert "insights" in data
        
        insights = data["insights"]
        assert "monthly_patterns" in insights
        assert "day_of_week_patterns" in insights
        
        monthly_patterns = insights["monthly_patterns"]
        assert "claim_count" in monthly_patterns
        print(f"Johnson County seasonal insights available for emergency claims")

    def test_seasonal_trends_emergency_visits(self):
        """Test: Show seasonal trends for emergency visits"""
        # Test seasonal patterns for multiple counties
        counties = ["Johnson", "Sedgwick", "Shawnee"]
        
        for county in counties:
            response = requests.get(f"{BASE_URL}/insights/{county}/emergency")
            assert response.status_code == 200
            
            data = response.json()
            assert "insights" in data
            insights = data["insights"]
            assert "monthly_patterns" in insights
        
        print(f"Seasonal emergency trends analyzed for {len(counties)} counties")

    def test_mental_health_claims_peak_times(self):
        """Test: When are mental health claims highest?"""
        response = requests.get(f"{BASE_URL}/insights/Johnson/mental_health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["claim_type"] == "mental_health"
        assert "insights" in data
        
        insights = data["insights"]
        monthly_patterns = insights["monthly_patterns"]["claim_count"]
        
        # Find peak month
        peak_month = max(monthly_patterns.items(), key=lambda x: x[1])
        print(f"Mental health claims peak in month {peak_month[0]} with {peak_month[1]:.1f} average claims")

    # Geographic Comparisons Tests
    def test_compare_wichita_vs_topeka_volumes(self):
        """Test: Compare Wichita vs Topeka claim volumes"""
        test_date = "2025-01-15"
        
        # Wichita (Sedgwick County)
        wichita_payload = {
            "county": "Sedgwick",
            "claim_type": "emergency",
            "target_date": test_date
        }
        
        wichita_response = requests.post(f"{BASE_URL}/predict", json=wichita_payload, timeout=TIMEOUT)
        assert wichita_response.status_code == 200
        wichita_data = wichita_response.json()
        
        # Topeka (Shawnee County)
        topeka_payload = {
            "county": "Shawnee",
            "claim_type": "emergency",
            "target_date": test_date
        }
        
        topeka_response = requests.post(f"{BASE_URL}/predict", json=topeka_payload, timeout=TIMEOUT)
        assert topeka_response.status_code == 200
        topeka_data = topeka_response.json()
        
        print(f"Wichita vs Topeka comparison:")
        print(f"  Wichita: {wichita_data['predicted_count']} claims, ${wichita_data['predicted_cost']:,.2f}")
        print(f"  Topeka: {topeka_data['predicted_count']} claims, ${topeka_data['predicted_cost']:,.2f}")

    def test_highest_claim_costs_counties(self):
        """Test: Which Kansas counties have highest claim costs?"""
        counties = ["Johnson", "Sedgwick", "Shawnee", "Wyandotte", "Douglas"]
        county_costs = {}
        
        for county in counties:
            response = requests.get(f"{BASE_URL}/summary/{county}")
            if response.status_code == 200:
                data = response.json()
                # Calculate total cost across all claim types
                summary = data["summary"]
                total_cost = 0
                for claim_type_data in summary.values():
                    if isinstance(claim_type_data, dict) and "total_cost_sum" in claim_type_data:
                        total_cost += claim_type_data["total_cost_sum"]
                county_costs[county] = total_cost
        
        assert len(county_costs) > 0
        highest_cost_county = max(county_costs.items(), key=lambda x: x[1])
        print(f"Highest cost county analysis completed for {len(county_costs)} counties")
        print(f"Sample result: {highest_cost_county[0]} has high total costs")

    def test_rural_vs_urban_utilization_patterns(self):
        """Test: Show rural vs urban healthcare utilization patterns"""
        # Urban counties
        urban_counties = ["Johnson", "Sedgwick"]
        # Rural counties  
        rural_counties = ["Ford", "Finney"]
        
        urban_data = []
        rural_data = []
        
        for county in urban_counties:
            response = requests.get(f"{BASE_URL}/summary/{county}")
            if response.status_code == 200:
                urban_data.append(response.json())
        
        for county in rural_counties:
            response = requests.get(f"{BASE_URL}/summary/{county}")
            if response.status_code == 200:
                rural_data.append(response.json())
        
        assert len(urban_data) > 0
        assert len(rural_data) > 0
        print(f"Rural vs Urban analysis: {len(urban_data)} urban, {len(rural_data)} rural counties")

    # Business Planning Tests
    def test_winter_months_reserves_planning(self):
        """Test: Should we increase reserves for winter months?"""
        # Test winter months predictions
        winter_months = ["2025-12-15", "2025-01-15", "2025-02-15"]
        winter_predictions = []
        
        for date in winter_months:
            payload = {
                "county": "Johnson",
                "claim_type": "emergency",
                "target_date": date
            }
            
            response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                winter_predictions.append(data["predicted_cost"])
        
        assert len(winter_predictions) > 0
        avg_winter_cost = sum(winter_predictions) / len(winter_predictions)
        print(f"Winter months reserve planning: Average cost ${avg_winter_cost:,.2f}")

    def test_staffing_needs_prediction(self):
        """Test: Predict staffing needs for claims processing"""
        # Get volume predictions for next 30 days
        response = requests.get(f"{BASE_URL}/predict-range/Johnson/emergency?days=30")
        assert response.status_code == 200
        
        data = response.json()
        predictions = data["predictions"]
        
        total_claims = sum(p["predicted_count"] for p in predictions)
        avg_daily_claims = total_claims / len(predictions)
        
        print(f"Staffing needs analysis: {avg_daily_claims:.1f} average daily claims")
        print(f"Total 30-day volume: {total_claims} claims")

    def test_mental_health_claims_increase_analysis(self):
        """Test: What's driving the increase in mental health claims?"""
        # Get mental health insights for major counties
        counties = ["Johnson", "Sedgwick", "Shawnee"]
        mental_health_data = []
        
        for county in counties:
            response = requests.get(f"{BASE_URL}/insights/{county}/mental_health")
            if response.status_code == 200:
                data = response.json()
                mental_health_data.append(data)
        
        assert len(mental_health_data) > 0
        print(f"Mental health trend analysis completed for {len(mental_health_data)} counties")

    # Chat Interface Tests
    def test_chat_volume_prediction_query(self):
        """Test chat interface with volume prediction query"""
        payload = {
            "message": "Predict emergency claims for Johnson County next week"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "context" in data
        assert "usage" in data
        
        # Check usage info
        usage = data["usage"]
        assert "groq_requests_used" in usage
        assert "groq_requests_limit" in usage
        assert usage["groq_requests_limit"] == 100
        
        print(f"Chat response: {data['response'][:100]}...")
        print(f"Groq usage: {usage['groq_requests_used']}/{usage['groq_requests_limit']}")

    def test_chat_cost_analysis_query(self):
        """Test chat interface with cost analysis query"""
        payload = {
            "message": "What's the average cost per claim in Sedgwick County?"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "usage" in data
        print(f"Chat cost analysis response received")

    def test_chat_seasonal_pattern_query(self):
        """Test chat interface with seasonal pattern query"""
        payload = {
            "message": "How does flu season affect claims in Johnson County?"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "usage" in data
        print(f"Chat seasonal pattern response received")

    # Error Handling Tests
    def test_invalid_county(self):
        """Test handling of invalid county"""
        payload = {
            "county": "InvalidCounty",
            "claim_type": "emergency",
            "target_date": "2025-01-15"
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        # Invalid inputs properly return 500 with error message
        assert response.status_code == 500
        assert "No model found" in response.json()["detail"]

    def test_invalid_claim_type(self):
        """Test handling of invalid claim type"""
        payload = {
            "county": "Johnson",
            "claim_type": "invalid_type",
            "target_date": "2025-01-15"
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        # Invalid inputs properly return 500 with error message
        assert response.status_code == 500
        assert "No model found" in response.json()["detail"]

    def test_invalid_date_format(self):
        """Test handling of invalid date format"""
        payload = {
            "county": "Johnson",
            "claim_type": "emergency",
            "target_date": "invalid-date"
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
        # Invalid date format returns 400 with proper error message
        assert response.status_code == 400
        assert "Invalid input" in response.json()["detail"]

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])