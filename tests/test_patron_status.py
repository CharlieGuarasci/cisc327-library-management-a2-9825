"""
Unit tests for get_patron_status_report function (incomplete)
Tests R7: Patron Status Report functionality
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from services.library_service import get_patron_status_report


def test_patron_status_no_borrowed_books():
    """Test status for patron with no borrowed books"""
    with patch('services.library_service.get_patron_borrowed_books', return_value = []):
        result = get_patron_status_report("123456")
        

        assert result['patron_id'] == "123456"
        assert result['total_books_borrowed'] == 0
        assert result['total_late_fees'] == 0.00
        assert result['overdue_books'] == []
        assert "currently_borrowed_books" in result


def test_patron_status_with_borrowed_books():
    """Test status for patron with borrowed books(none overdue)"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
    
        due_date = datetime.now() + timedelta(days=3) # not overdue
        mock_get_borrowed.return_value = [
            {"book_id": 1, "title": "Book One", "due_date": due_date},
            {"book_id": 2, "title": "Book Two", "due_date": due_date}
        ]

        result = get_patron_status_report("123456")
        assert result['patron_id'] == "123456"
        assert result['total_books_borrowed'] == 2
        assert result['total_late_fees'] == 0.00
        assert len(result['overdue_books']) == 0


def test_patron_status_with_overdue_books():
    """Test status for patron with overdue books"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
        current_time = datetime.now()
        overdue_due_date = current_time - timedelta(days=5) # 5 days overdue
        not_overdue = current_time + timedelta(days=1) 

        mock_get_borrowed.return_value = [{
            "book_id": 1, "title": "Book One", "due_date": overdue_due_date
        }, {
            "book_id": 2, "title": "Book Two", "due_date": not_overdue
        }]
        
        result = get_patron_status_report("123456")
        assert result['patron_id'] == "123456"
        assert result['total_books_borrowed'] == 2
        assert result['total_late_fees'] == 2.50
        assert len(result['overdue_books']) == 1
        assert result['overdue_books'][0]['title'] == 'Book One'



def test_patron_status_with_many_overdue_books():
    """Test status for patron with two overdue books"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
        current_time = datetime.now()
        overdue_due_date = current_time - timedelta(days=5) # 5 days overdue

        mock_get_borrowed.return_value = [{
            "book_id": 1, "title": "Book One", "due_date": overdue_due_date
        }, {
            "book_id": 2, "title": "Book Two", "due_date": overdue_due_date
        }]
        
        result = get_patron_status_report("123456")
        assert result['patron_id'] == "123456"
        assert result['total_books_borrowed'] == 2
        assert result['total_late_fees'] == 5.00
        assert len(result['overdue_books']) == 2


def test_patron_status_empty_borrowed_list():
    """Test status for patron with empty borrowed list"""
    with patch('services.library_service.get_patron_borrowed_books', return_value = []):
        result = get_patron_status_report("123456")
        
        assert result['patron_id'] == "123456"
        assert result['total_books_borrowed'] == 0
        assert result['total_late_fees'] == 0.00
        assert result['overdue_books'] == []

