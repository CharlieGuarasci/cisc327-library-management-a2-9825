"""
Unit tests for pay_late_fees function
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway



def test_pay_late_fees_successful():
    """Test successful payment of late fees."""
    # Stub database functions
    with patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.0}), \
         patch('services.library_service.get_book_by_id', return_value={'title': 'Test Book'}):
        
        # Mock PaymentGateway
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, 'txn_123', 'Success')

        success, message, transaction_id = pay_late_fees('123456', 1, mock_gateway)

        assert success is True
        assert 'Payment successful' in message
        assert transaction_id == 'txn_123'
        mock_gateway.process_payment.assert_called_once_with(patron_id='123456', amount=10.0, description="Late fees for 'Test Book'")


def test_pay_late_fees_declined():
    """Test payment declined by the gateway."""
    with patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.0}), \
         patch('services.library_service.get_book_by_id', return_value={'title': 'Test Book'}):
        
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (False, None, 'Payment declined')

        success, message, transaction_id = pay_late_fees('123456', 1, mock_gateway)

        assert success is False
        assert 'Payment failed' in message
        assert transaction_id is None
        mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_invalid_patron_id():
    """Test with an invalid patron ID."""
    mock_gateway = Mock(spec=PaymentGateway)
    success, message, transaction_id = pay_late_fees('123', 1, mock_gateway)

    assert success is False
    assert 'Invalid patron ID' in message
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_fees():
    """Test when there are no late fees to pay."""
    with patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 0.0}):
        mock_gateway = Mock(spec=PaymentGateway)

        success, message, transaction_id = pay_late_fees('123456', 1, mock_gateway)

        assert success is False
        assert 'No late fees to pay' in message
        mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error():
    """Test handling of a network error from the payment gateway."""
    with patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.0}), \
         patch('services.library_service.get_book_by_id', return_value={'title': 'Test Book'}):
        
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = ConnectionError('Network error')

        success, message, transaction_id = pay_late_fees('123456', 1, mock_gateway)

        assert success is False
        assert 'Payment processing error' in message
        mock_gateway.process_payment.assert_called_once()

# Test cases for refund_late_fee_payment
def test_refund_late_fee_payment_successful():
    """Test a successful refund."""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, 'Refund successful')

    success, message = refund_late_fee_payment('txn_123', 10.0, mock_gateway)

    assert success is True
    assert 'Refund successful' in message
    mock_gateway.refund_payment.assert_called_once_with('txn_123', 10.0)

def test_refund_late_fee_payment_invalid_transaction_id():
    """Test refund with an invalid transaction ID."""
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment('invalid_id', 10.0, mock_gateway)

    assert success is False
    assert 'Invalid transaction ID' in message
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_negative_amount():
    """Test refund with a negative amount."""
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment('txn_123', -10.0, mock_gateway)

    assert success is False
    assert 'Refund amount must be greater than 0' in message
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_zero_amount():
    """Test refund with a zero amount."""
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment('txn_123', 0.0, mock_gateway)

    assert success is False
    assert 'Refund amount must be greater than 0' in message
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_exceeds_max():
    """Test refund amount exceeding the maximum."""
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment('txn_123', 20.0, mock_gateway)

    assert success is False
    assert 'Refund amount exceeds maximum late fee' in message
    mock_gateway.refund_payment.assert_not_called()