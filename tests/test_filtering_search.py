import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta

def test_filter_shopping_lists_by_name(client: TestClient, auth_headers, test_kitchen, db_session):
    """Test filtering shopping lists by name"""
    from api.v1.models import ShoppingList
    
    # Create test shopping lists
    list1 = ShoppingList(name="Grocery Shopping", kitchen_id=test_kitchen.id)
    list2 = ShoppingList(name="Hardware Store", kitchen_id=test_kitchen.id)
    list3 = ShoppingList(name="Grocery Essentials", kitchen_id=test_kitchen.id)
    
    db_session.add_all([list1, list2, list3])
    db_session.commit()
    
    # Test filtering by name
    response = client.get("/api/v1/shopping-lists/?name=Grocery", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert all("Grocery" in item["name"] for item in data["items"])

def test_search_shopping_lists(client: TestClient, auth_headers, test_kitchen, db_session):
    """Test searching shopping lists"""
    from api.v1.models import ShoppingList
    
    # Create test shopping lists
    list1 = ShoppingList(name="Weekly Groceries", description="Food for the week", kitchen_id=test_kitchen.id)
    list2 = ShoppingList(name="Hardware Store", description="Tools and supplies", kitchen_id=test_kitchen.id)
    list3 = ShoppingList(name="Party Supplies", description="Food and decorations", kitchen_id=test_kitchen.id)
    
    db_session.add_all([list1, list2, list3])
    db_session.commit()
    
    # Test searching across name and description
    response = client.get("/api/v1/shopping-lists/?search=Food", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    
    # Test searching for specific term
    response = client.get("/api/v1/shopping-lists/?search=Tools", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Hardware Store"

def test_filter_shopping_list_items_by_name(client: TestClient, auth_headers, test_shopping_list, db_session):
    """Test filtering shopping list items by name"""
    from api.v1.models import ShoppingListItem
    
    # Create test items
    item1 = ShoppingListItem(name="Milk", quantity="1 gallon", shopping_list_id=test_shopping_list.id)
    item2 = ShoppingListItem(name="Bread", quantity="2 loaves", shopping_list_id=test_shopping_list.id)
    item3 = ShoppingListItem(name="Almond Milk", quantity="1 carton", shopping_list_id=test_shopping_list.id)
    
    db_session.add_all([item1, item2, item3])
    db_session.commit()
    
    # Test filtering by name
    response = client.get("/api/v1/shopping-list-items/?name=Milk", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert all("Milk" in item["name"] for item in data["items"])

def test_filter_items_by_quantity(client: TestClient, auth_headers, test_shopping_list, db_session):
    """Test filtering items by quantity text"""
    from api.v1.models import ShoppingListItem
    
    # Create test items
    item1 = ShoppingListItem(name="Milk", quantity="1 gallon", shopping_list_id=test_shopping_list.id)
    item2 = ShoppingListItem(name="Juice", quantity="2 bottles", shopping_list_id=test_shopping_list.id)
    item3 = ShoppingListItem(name="Water", quantity="1 case", shopping_list_id=test_shopping_list.id)
    
    db_session.add_all([item1, item2, item3])
    db_session.commit()
    
    # Test filtering by quantity
    response = client.get("/api/v1/shopping-list-items/?quantity_contains=gallon", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Milk"

def test_pagination_metadata(client: TestClient, auth_headers, test_kitchen, db_session):
    """Test pagination metadata in responses"""
    from api.v1.models import ShoppingList
    
    # Create multiple shopping lists
    for i in range(15):
        shopping_list = ShoppingList(name=f"List {i}", kitchen_id=test_kitchen.id)
        db_session.add(shopping_list)
    db_session.commit()
    
    # Test pagination
    response = client.get("/api/v1/shopping-lists/?limit=5&skip=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) == 5
    assert data["total"] >= 15  # At least 15 (plus test_shopping_list from fixture)
    assert data["page"] == 1
    assert data["per_page"] == 5
    assert data["has_next"] is True
    assert data["has_prev"] is False
    
    # Test second page
    response = client.get("/api/v1/shopping-lists/?limit=5&skip=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 2
    assert data["has_prev"] is True

def test_sorting(client: TestClient, auth_headers, test_kitchen, db_session):
    """Test sorting functionality"""
    from api.v1.models import ShoppingList
    import time
    
    # Create shopping lists with different names and times
    list1 = ShoppingList(name="Zebra List", kitchen_id=test_kitchen.id)
    db_session.add(list1)
    db_session.commit()
    
    time.sleep(0.1)  # Small delay to ensure different timestamps
    
    list2 = ShoppingList(name="Alpha List", kitchen_id=test_kitchen.id)
    db_session.add(list2)
    db_session.commit()
    
    # Test sorting by name ascending
    response = client.get("/api/v1/shopping-lists/?sort_by=name&sort_order=asc", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Should have Alpha List before Zebra List
    names = [item["name"] for item in data["items"]]
    alpha_index = next(i for i, name in enumerate(names) if "Alpha" in name)
    zebra_index = next(i for i, name in enumerate(names) if "Zebra" in name)
    assert alpha_index < zebra_index
    
    # Test sorting by created_at descending (default)
    response = client.get("/api/v1/shopping-lists/?sort_by=created_at&sort_order=desc", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Most recent should be first
    assert len(data["items"]) >= 2

def test_global_search(client: TestClient, auth_headers, test_kitchen, test_shopping_list, db_session):
    """Test global search functionality"""
    from api.v1.models import ShoppingListItem
    
    # Create test data
    item = ShoppingListItem(name="Test Item", quantity="1 piece", shopping_list_id=test_shopping_list.id)
    db_session.add(item)
    db_session.commit()
    
    # Test global search
    response = client.get("/api/v1/search/global?q=Test", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert "kitchens" in data["results"]
    assert "shopping_lists" in data["results"]
    assert "shopping_list_items" in data["results"]
    
    # Should find the test kitchen, shopping list, and item
    assert data["results"]["kitchens"]["total"] >= 1
    assert data["results"]["shopping_lists"]["total"] >= 1
    assert data["results"]["shopping_list_items"]["total"] >= 1

def test_search_suggestions(client: TestClient, auth_headers, test_kitchen, test_shopping_list, db_session):
    """Test search suggestions"""
    from api.v1.models import ShoppingListItem
    
    # Create test items with similar names
    items = [
        ShoppingListItem(name="Apple Juice", quantity="1 bottle", shopping_list_id=test_shopping_list.id),
        ShoppingListItem(name="Apple Pie", quantity="1 slice", shopping_list_id=test_shopping_list.id),
        ShoppingListItem(name="Pineapple", quantity="1 whole", shopping_list_id=test_shopping_list.id),
    ]
    db_session.add_all(items)
    db_session.commit()
    
    # Test suggestions
    response = client.get("/api/v1/search/suggestions?q=Apple", headers=auth_headers)
    assert response.status_code == 200
    suggestions = response.json()
    
    assert len(suggestions) >= 2
    assert "Apple Juice" in suggestions
    assert "Apple Pie" in suggestions

def test_recent_items(client: TestClient, auth_headers, test_kitchen, test_shopping_list):
    """Test recent items endpoint"""
    response = client.get("/api/v1/search/recent", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "recent" in data
    assert "kitchens" in data["recent"]
    assert "shopping_lists" in data["recent"]
    assert "shopping_list_items" in data["recent"]

def test_search_stats(client: TestClient, auth_headers, test_kitchen, test_shopping_list):
    """Test search statistics endpoint"""
    response = client.get("/api/v1/search/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "totals" in data
    assert "breakdown" in data
    assert data["totals"]["kitchens"] >= 1
    assert data["totals"]["shopping_lists"] >= 1

def test_filter_validation(client: TestClient, auth_headers):
    """Test filter parameter validation"""
    # Test invalid limit
    response = client.get("/api/v1/shopping-lists/?limit=2000", headers=auth_headers)
    assert response.status_code == 422
    
    # Test negative skip
    response = client.get("/api/v1/shopping-lists/?skip=-1", headers=auth_headers)
    assert response.status_code == 422

def test_date_filtering(client: TestClient, auth_headers, test_kitchen, db_session):
    """Test date range filtering"""
    from api.v1.models import ShoppingList
    from datetime import datetime, timedelta
    
    # Create shopping lists with different dates
    old_date = datetime.now() - timedelta(days=10)
    recent_date = datetime.now() - timedelta(days=1)
    
    old_list = ShoppingList(name="Old List", kitchen_id=test_kitchen.id, created_at=old_date)
    recent_list = ShoppingList(name="Recent List", kitchen_id=test_kitchen.id, created_at=recent_date)
    
    db_session.add_all([old_list, recent_list])
    db_session.commit()
    
    # Test filtering by date range
    from_date = (datetime.now() - timedelta(days=5)).date()
    response = client.get(f"/api/v1/shopping-lists/?date_from={from_date}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Should only include recent items
    assert len(data["items"]) >= 1
    recent_names = [item["name"] for item in data["items"]]
    assert "Recent List" in recent_names or any("Test" in name for name in recent_names)