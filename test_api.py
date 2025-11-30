"""
Test the FastAPI endpoints
Run this after starting the API server
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def test_api():
    print("=" * 70)
    print("🧪 TESTING FASTAPI ENDPOINTS")
    print("=" * 70)

    # Test 1: Health check
    print("\n1️⃣  Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Root endpoint
    print("\n2️⃣  Testing / endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Endpoints available: {len(response.json()['endpoints'])}")

    # Test 3: Process single article
    print("\n3️⃣  Testing /process endpoint...")
    test_article = {
        "title": "HDFC Bank announces 15% dividend",
        "content": "HDFC Bank announced a 15% dividend payout to shareholders. This is positive news for the banking sector.",
        "source": "Test API",
        "url": "https://example.com/test"
    }

    response = requests.post(f"{BASE_URL}/process", json=test_article)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Article processed successfully")
        print(f"   ID: {data['id']}")
        print(f"   Is duplicate: {data['is_duplicate']}")
        print(f"   Entities: {len(data['entities'])}")
        print(f"   Stock impacts: {len(data['stock_impacts'])}")

    # Test 4: Query
    print("\n4️⃣  Testing /query endpoint...")
    query_request = {
        "query": "HDFC Bank news",
        "limit": 5
    }

    response = requests.post(f"{BASE_URL}/query", json=query_request)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Query successful")
        print(f"   Results found: {data['total_results']}")
        print(f"   Processing time: {data['processing_time'] * 1000:.2f}ms")

    # Test 5: Stats
    print("\n5️⃣  Testing /stats endpoint...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Stats retrieved")
        print(f"   Total stories: {data['total_stories']}")
        print(f"   Total entities: {data['total_entities']}")

    # Test 6: Get all stories
    print("\n6️⃣  Testing /stories endpoint...")
    response = requests.get(f"{BASE_URL}/stories?limit=10")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Stories retrieved")
        print(f"   Total: {data['total']}")
        print(f"   Returned: {len(data['stories'])}")

    print("\n" + "=" * 70)
    print("✅ ALL API TESTS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    print("\n⚠️  Make sure the API server is running!")
    print("   Start it with: python main.py")
    print("\nPress Enter to continue with tests...")
    input()

    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("   Make sure to start the server first: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")