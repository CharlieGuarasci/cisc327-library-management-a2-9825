"""
Unit tests for borrow_book_by_patron function
Tests R3: Book Borrowing functionality
"""

import pytest
from unittest.mock import patch
from services.library_service import borrow_book_by_patron


def test_borrow_book_valid_input():
    # Test borrowing a book with valid input.
    with patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Test Book", "available_copies": 2}), \
         patch('services.library_service.get_patron_borrow_count', return_value=2), \
         patch('services.library_service.insert_borrow_record', return_value=True), \
         patch('services.library_service.update_book_availability', return_value=True):
        
        success, message = borrow_book_by_patron("123456", 1)
        
        assert success == True
        assert "Successfully borrowed" in message


def test_borrow_book_invalid_patron_id():
    # Test borrowing with invalid patron ID.
    success, message = borrow_book_by_patron("12345", 1)  # Only 5 digits
    
    assert success == False
    assert "Invalid patron ID" in message


def test_borrow_book_nonexistent_book():
    # Test borrowing a book that doesn't exist.
    with patch('services.library_service.get_book_by_id', return_value=None):
        success, message = borrow_book_by_patron("123456", 999)
        
        assert success == False
        assert "Book not found" in message


def test_borrow_book_no_available_copies():
    # Test borrowing a book with no available copies.
    with patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Test Book", "available_copies": 0}):
        success, message = borrow_book_by_patron("123456", 1)
        
        assert success == False
        assert "not available" in message


def test_borrow_book_max_limit_reached():
    # Test borrowing when patron has reached maximum limit (6 books).
    with patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Test Book", "available_copies": 2}), \
         patch('services.library_service.get_patron_borrow_count', return_value=6):  # Over the limit (6 > 5)
        
        success, message = borrow_book_by_patron("123456", 1)
        
        assert success == False
        assert "maximum borrowing limit" in message


def test_borrow_book_at_max_limit():
    # Test borrowing when patron has exactly 5 books (should still be allowed).
    with patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Test Book", "available_copies": 2}), \
         patch('services.library_service.get_patron_borrow_count', return_value=5), \
         patch('services.library_service.insert_borrow_record', return_value=True), \
         patch('services.library_service.update_book_availability', return_value=True):
        
        success, message = borrow_book_by_patron("123456", 1)
        
        assert success == True
        assert "Successfully borrowed" in message


def test_borrow_book_database_error():
    # Test borrowing when database operation fails.
    with patch('services.library_service.get_book_by_id', return_value={"id": 1, "title": "Test Book", "available_copies": 2}), \
         patch('services.library_service.get_patron_borrow_count', return_value=2), \
         patch('services.library_service.insert_borrow_record', return_value=False):  # Database error
        
        success, message = borrow_book_by_patron("123456", 1)
        
        assert success == False
        assert "Database error" in message
