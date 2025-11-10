"""
Unit tests for add_book_to_catalog function
Tests R1: Book Catalog Management functionality
"""

import pytest
from unittest.mock import patch
from services.library_service import add_book_to_catalog


def test_add_book_valid_input():
    # Test adding a book with valid input.
    with patch('services.library_service.get_book_by_isbn', return_value=None), \
         patch('services.library_service.insert_book', return_value=True):
        
        success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
        
        assert success == True
        assert "successfully added" in message.lower()


def test_add_book_empty_title():
    # Test adding a book with empty title.
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "Title is required" in message


def test_add_book_title_too_long():
    # Test adding a book with title exceeding 200 characters.
    long_title = "A" * 201
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "Title must be less than 200 characters" in message


def test_add_book_isbn_wrong_length():
    # Test adding a book with wrong ISBN length.
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "ISBN must be exactly 13 digits" in message


def test_add_book_zero_copies():
    # Test adding a book with zero copies.
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success == False
    assert "Total copies must be a positive integer" in message


def test_add_book_duplicate_isbn():
    # Test adding a book with duplicate ISBN.
    with patch('services.library_service.get_book_by_isbn', return_value={"id": 1, "title": "Existing Book"}):
        success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
        
        assert success == False
        assert "A book with this ISBN already exists" in message
