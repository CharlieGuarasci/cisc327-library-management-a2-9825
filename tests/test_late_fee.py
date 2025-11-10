"""
Unit tests for calculate_late_fee_for_book function (incomplete)
Tests R5: Late Fee Calculation functionality
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from services.library_service import calculate_late_fee_for_book


def test_late_fee_no_borrow_record():
    """Test when no borrow record exists"""
    with patch('services.library_service.get_patron_borrowed_books', return_value = []):
        result = calculate_late_fee_for_book("123456", 1)
        
        assert result['fee_amount'] == 0.00
        assert result['days_overdue'] == 0
        assert "no borrow record found" in result['status'].lower()


def test_late_fee_not_overdue():
    """Test when book is not overdue"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
        due_date = datetime.now() + timedelta(days=2) # not overdue
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]
        
        result = calculate_late_fee_for_book("123456", 1)
        
        assert result['fee_amount'] == 0.00
        assert result['days_overdue'] == 0
        assert "not overdue" in result['status'].lower()


def test_late_fee_overdue_within_7_days():
    """Test late fee calculation within 7 days"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
        due_date = datetime.now() - timedelta(days=5) # 5 days overdue
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]
        
        result = calculate_late_fee_for_book("123456", 1)
        
        assert result['fee_amount'] == 2.50  # 5 days * $0.50/day
        assert result['days_overdue'] == 5
        assert "late fee calculated" in result['status'].lower()


def test_late_fee_after_week():
    """Test late fee calculation after 7 days"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
        due_date = datetime.now() - timedelta(days=10) # 10 days overdue
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]
        
        result = calculate_late_fee_for_book("123456", 1)
        
        assert result['fee_amount'] == 6.50  # (7 * $0.50) + (3 * $1.00)
        assert result['days_overdue'] == 10
        assert "late fee calculated" in result['status'].lower()

def test_late_fee_cap():
    """Test late fee cap at $15"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
        due_date = datetime.now() - timedelta(days=40)
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]

        result = calculate_late_fee_for_book("123456", 1)
        assert result['fee_amount'] == 15.00
        assert result['days_overdue'] == 40


def test_late_fee_due_today():
    """Test when book is due today (not overdue)"""
    with patch('services.library_service.get_patron_borrowed_books') as mock_get_borrowed:
        due_date = datetime.now()
        mock_get_borrowed.return_value = [{
            "book_id": 1,
            "title": "Test Book",
            "due_date": due_date
        }]

        result = calculate_late_fee_for_book("123456", 1)
        assert result['fee_amount'] == 0.00
        assert result['days_overdue'] == 0

