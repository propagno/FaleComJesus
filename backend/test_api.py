#!/usr/bin/env python
"""
Script to test the API endpoints.
"""
import requests
import json


def test_api():
    """Test the API endpoints."""
    base_url = 'http://localhost:5000'

    # Get a test token
    print("Getting test token...")
    response = requests.get(f'{base_url}/test-token')
    if response.status_code != 200:
        print(f"Error getting test token: {response.status_code}")
        return

    token_data = response.json()
    token = token_data.get('access_token')
    print(f"Token: {token[:20]}...")

    # Test daily message endpoint
    print("\nTesting daily message endpoint...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{base_url}/api/v1/daily-messages/today', headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data.get('message')}")
        print(f"Bible verse: {data.get('bible_verse')}")
        print(f"Bible reference: {data.get('bible_reference')}")
    else:
        print(f"Error: {response.text}")

    # Test prompt templates endpoint
    print("\nTesting prompt templates endpoint...")
    response = requests.get(f'{base_url}/api/prompts', headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Number of templates: {data.get('count')}")
        for template in data.get('templates', [])[:2]:  # Show only first 2 templates
            print(f"- {template.get('name')}: {template.get('description')}")
    else:
        print(f"Error: {response.text}")

    # Test conversations endpoint
    print("\nTesting conversations endpoint...")
    response = requests.get(f'{base_url}/api/conversations', headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Number of conversations: {data.get('count')}")
        # Show only first 2 conversations
        for conversation in data.get('conversations', [])[:2]:
            print(f"- {conversation.get('title')} (ID: {conversation.get('id')})")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    test_api()
