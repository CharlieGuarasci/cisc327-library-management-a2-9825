"""
Unit tests for return_book_by_patron function (incomplete)
Tests R4: Book Return Processing functionality
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from library_service import return_book_by_patron


def test_return_book_valid_no_late_fee():
    """Test successful retuen with no late fees"""
    with patch('library_service.get_book_by_id') as mock_get_book, \
        patch('library_service.get_patron_borrowed_books') as mock_get_borrowed, \
        patch('library_service.update_borrow_record_return_date', return_value = True), \
        patch('library_service.update_book_availability', return_value = True):

        mock_get_book.return_value = {
            "id": 1, 
            "title": "Test Book",
            "available_copies": 0,
        }
        due_date = datetime.now() + timedelta(days=1) # not overdue
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]

        success, message = return_book_by_patron("123456", 1)

        assert success == True
        assert "returned successfully" in message.lower()
        assert "no late fees" in message.lower()


def test_return_book_with_late_fee():
    """Test return with late fee calculation"""
        
    with patch('library_service.get_book_by_id') as mock_get_book, \
        patch('library_service.get_patron_borrowed_books') as mock_get_borrowed, \
        patch('library_service.update_borrow_record_return_date', return_value = True), \
        patch('library_service.update_book_availability', return_value = True):
        mock_get_book.return_value = {
            "id": 1, 
            "title": "Test Book",
            "available_copies": 0,
        }
        due_date = datetime.now() - timedelta(days=5) # 5 days overdue
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]

        success, message = return_book_by_patron("123456", 1)
        assert success == True
        assert "late fee owed" in message.lower()
        assert "2.50" in message # 5 days * $0.50/day



def test_return_book_late_fee_cap():
    """Test return with the fee cap($15)"""

    with patch('library_service.get_book_by_id') as mock_get_book, \
        patch('library_service.get_patron_borrowed_books') as mock_get_borrowed, \
        patch('library_service.update_borrow_record_return_date', return_value = True), \
        patch('library_service.update_book_availability', return_value = True):
        mock_get_book.return_value = {
            "id": 1, 
            "title": "Test Book",
            "available_copies": 0,
        }
        due_date = datetime.now() - timedelta(days=40) # 40 days overdue
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]
        success, message = return_book_by_patron("123456", 1)
        assert success == True
        assert "15.00" in message # fee capped at $15


def test_return_book_invalid_patron_id():
    # Test with invalid patron ID format.
    success, message = return_book_by_patron("12345", 1) # 5 digits 
    
    assert success == False
    assert "invalid patron id" in message.lower()


def test_return_book_not_found():
    """Test return of non existent book"""
    with patch('library_service.get_book_by_id', return_value = None):
        success, message = return_book_by_patron("123456", 999) # non existent book ID
        
        assert success == False
        assert "book does not exist" in message.lower()



def test_return_book_not_borrowed_by_patron():
    """Test returning book of not borrowed by patron"""
    with patch('library_service.get_book_by_id') as mock_get_book, \
        patch('library_service.get_patron_borrowed_books', return_value = []):
        mock_get_book.return_value = {
            "id": 1, 
            "title": "Test Book",
            "available_copies": 3,
        }

        success, message = return_book_by_patron("123456", 1) # book ID 1 not borrowed by patron
        assert success == False
        assert "was not borrowed by patron" in message.lower()
        


def test_return_book_database_error():
    """Test return when database update fails"""
    with patch('library_service.get_book_by_id') as mock_get_book, \
         patch('library_service.get_patron_borrowed_books') as mock_get_borrowed, \
         patch('library_service.update_borrow_record_return_date', return_value=False):
        
        mock_get_book.return_value = {
            "id": 1, 
            "title": "Test Book", 
            "available_copies": 0
            }
        due_date = datetime.now() + timedelta(days=1)
        mock_get_borrowed.return_value = [{
            "book_id": 1, 
            "title": "Test Book", 
            "due_date": due_date
            }]
        
        success, message = return_book_by_patron("123456", 1)
        
        assert success == False
        assert "database error" in message.lower()