"""
Unit tests for search_books_in_catalog function (incomplete)
Tests R6: Book Search functionality
"""

import pytest
from unittest.mock import patch
from library_service import search_books_in_catalog


def test_search_by_title():
    """Test searching by title"""
    with patch('library_service.get_all_books') as mock_get_all_books:
        mock_get_all_books.return_value = [
            {"id": 1, "title": "Python Programming", "author": "John Doe", "isbn": "1234567890123"},
            {"id": 2, "title": "Learning Java", "author": "Jane Smith", "isbn": "9876543210987"},
            {"id": 3, "title": "Advanced Python", "author": "Alice Johnson", "isbn": "1112223334445"},
        ]
        
        result = search_books_in_catalog("python", "title")
        
        assert len(result) == 2
        assert result[0]['title'] == "Python Programming"
        assert result[1]['title'] == "Advanced Python"


def test_search_by_author():
    """Test searching by author"""
    with patch('library_service.get_all_books') as mock_get_all_books:
        mock_get_all_books.return_value = [
            {"id": 1, "title": "Python Programming", "author": "John Doe", "isbn": "1234567890123"},
            {"id": 2, "title": "Learning Java", "author": "Jane Smith", "isbn": "9876543210987"},
            {"id": 3, "title": "Advanced Python", "author": "Alice Johnson", "isbn": "1112223334445"},
        ]
        
        result = search_books_in_catalog("jane", "author")
        
        assert len(result) == 1
        assert result[0]['author'] == "Jane Smith"


def test_search_by_isbn():
    """Test searching by exact ISBN"""
    with patch('library_service.get_all_books') as mock_get_all_books:
        mock_get_all_books.return_value = [
            {"id": 1, "title": "Python Programming", "author": "John Doe", "isbn": "1234567890123"},
            {"id": 2, "title": "Learning Java", "author": "Jane Smith", "isbn": "9876543210987"},
            {"id": 3, "title": "Advanced Python", "author": "Alice Johnson", "isbn": "1112223334445"},
        ]
        
        result = search_books_in_catalog("9876543210987", "isbn")
        
        assert len(result) == 1
        assert result[0]['isbn'] == "9876543210987"



def test_search_case_insensitive():
    """Test that search is case insensitive"""
    with patch('library_service.get_all_books') as mock_get_books:
        mock_get_books.return_value = [{
            "id": 1, 
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "isbn": "1234567890123", 
            "available_copies": 3
            }]
        
        results = search_books_in_catalog("GATSBY", "title")
        
        assert len(results) == 1
        assert results[0]["title"] == "The Great Gatsby"


def test_search_no_results():
    """Test search with no matching results"""
    with patch('library_service.get_all_books') as mock_get_books:
        mock_get_books.return_value = [{
            "id": 1, 
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "isbn": "1234567890123", 
            "available_copies": 3
            }]
        
        results = search_books_in_catalog("DNE", "title")
        
        assert len(results) == 0


def test_search_empty_term():
    """Test search with empty search term"""
    result = search_books_in_catalog("", "title")
    
    assert result == []


def test_with_invalid_type():
    """Test search with invalid search type"""
    result = search_books_in_catalog("test", "invalid_type")
    
    assert result == []
