"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'


#  Assignment 2 implementations

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements

    The system shall provide a return interface that includes:
        - Accepts patron ID and book ID as form parameters
        - Verifies the book was borrowed by the patron
        - Updates available copies and records return date
        - Calculates and displays any late fees owed
    """

    # Verify patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check to see if the book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book does not exist."
    
    # get the list of books borrowed by the patron
    borrowed = get_patron_borrowed_books(patron_id)
    book_found = False
    due_date = None

    for borrowed_book in borrowed:
        if borrowed_book['book_id'] == book_id:
            book_found = True
            due_date = borrowed_book['due_date']
            break
    if not book_found:
        return False, f'Book "{book["title"]}" was not borrowed by patron ID {patron_id}.'
    
    # 4. Calculate late fees
    return_date = datetime.now()
    days_overdue = max(0, (return_date - due_date).days)
    
    if days_overdue == 0:
        late_fee = 0.00
    elif days_overdue <= 7:
        late_fee = days_overdue * 0.50
    else:
        late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
    late_fee = min(late_fee, 15.00)  # Cap at $15
    
    # update the borrow record with the return date
    update_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not update_success:
        return False, "Database error occurred while updating return date."
    
    # update the book availability
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    # calculate any fees owed
    if late_fee > 0.00:
        return True, f'Book "{book["title"]}" returned. Late fee owed: ${late_fee:.2f}.'
    else:
        return True, f'Book "{book["title"]}" returned successfully. No late fees owed.'
    

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 

    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    # get number of books borrowed by patron 
    borrowed = get_patron_borrowed_books(patron_id)

    # calculate any late fees
    for book in borrowed:
        if book['book_id'] == book_id:
            current_date = datetime.now()
            due_date = book['due_date']
            days_overdue = max(0, (current_date - due_date).days)
            if days_overdue == 0:
                return {
                    'fee_amount': 0.00,
                    'days_overdue': 0,
                    'status': 'No late fee. Book is not overdue.'
                }
            if days_overdue <= 7:
                fee_amount = days_overdue * 0.50
            else:
                fee_amount = (7 * .50) + ((days_overdue - 7) * 1.00)
            fee_amount = min(fee_amount, 15.00)

            return {
                'fee_amount': fee_amount,
                'days_overdue': days_overdue,
                'status': 'Late fee calculated successfully.'
            }
        
    return {
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'No borrow record found related to the patron.'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """

    # validate the search
    if not search_term or not search_term.strip():
        return []

    if search_type not in ['title', 'author', 'isbn']:
        return []
    

    # get all books
    all_books = get_all_books()
    results = []



    search_term = search_term.strip().lower()

    if search_type == 'title':
        for book in all_books:
            if search_term in book['title'].lower():
                results.append(book)
    
    elif search_type == 'author':
        for book in all_books:
            if search_term in book['author'].lower():
                results.append(book)
    
    elif search_type == 'isbn':
        for book in all_books:
            if search_term == book['isbn']:
                results.append(book)
    
    return results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """

    # Verify patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'error': "Invalid patron ID."
        }
    
    borrowed = get_patron_borrowed_books(patron_id)

    total_late_fees = 0.00
    books_with_fees = []

    for book in borrowed:
        fee_info = calculate_late_fee_for_book(patron_id, book['book_id'])
        if fee_info['fee_amount'] > 0:
            total_late_fees += fee_info['fee_amount']
            books_with_fees.append({ 
                'book_id': book['book_id'], 
                 'title': book['title'], 
                 'days_overdue': fee_info['days_overdue'], 
                 'fee_amount': fee_info['fee_amount'] 
            })
            
    return {
        'patron_id': patron_id,
        'total_late_fees': total_late_fees,
        'overdue_books': books_with_fees,
        'total_books_borrowed': len(borrowed),
        'currently_borrowed_books': borrowed
    }
