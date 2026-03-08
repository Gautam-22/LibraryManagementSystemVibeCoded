from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Book, Member, Transaction, Fine

class LibraryTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.member = Member.objects.create(user=self.user, phone='1234567890')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            total_qty=5,
            available_qty=5
        )

    def test_book_creation(self):
        """Test book creation with valid data"""
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.available_qty, 5)

    def test_book_invalid_qty(self):
        """Test book with available_qty > total_qty raises error"""
        with self.assertRaises(ValueError):
            book = Book(
                title='Invalid Book',
                author='Author',
                isbn='1234567890124',
                total_qty=3,
                available_qty=5
            )
            book.full_clean()

    def test_member_phone_validation_valid(self):
        """Test valid phone number"""
        user2 = User.objects.create_user(username='testuser2', password='pass')
        member = Member(user=user2, phone='9876543210')
        member.full_clean()  # Should not raise
        member.save()
        self.assertEqual(member.phone, '9876543210')

    def test_member_phone_validation_letters(self):
        """Test phone number with letters raises error"""
        user3 = User.objects.create_user(username='testuser3', password='pass')
        with self.assertRaises(ValidationError):
            invalid_member = Member(user=user3, phone='abcdefghij')
            invalid_member.full_clean()

    def test_member_phone_validation_short(self):
        """Test phone number too short raises error"""
        user4 = User.objects.create_user(username='testuser4', password='pass')
        with self.assertRaises(ValidationError):
            short_member = Member(user=user4, phone='123')
            short_member.full_clean()

    def test_transaction_creation(self):
        """Test transaction creation decreases book qty"""
        initial_qty = self.book.available_qty
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today()
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_qty, initial_qty - 1)
        self.assertEqual(transaction.due_date, date.today() + timedelta(days=14))

    def test_fine_calculation_no_overdue(self):
        """Test no fine when returned on time"""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today()
        )
        transaction.return_date = date.today() + timedelta(days=10)
        self.assertEqual(transaction.calculate_fine, 0)

    def test_fine_calculation_overdue(self):
        """Test fine calculation for overdue returns"""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today()
        )
        transaction.return_date = transaction.due_date + timedelta(days=3)
        self.assertEqual(transaction.calculate_fine, 30)  # 3 days * 10

    def test_fine_calculation_exact_due_date(self):
        """Test no fine when returned exactly on due date"""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today()
        )
        transaction.return_date = transaction.due_date
        self.assertEqual(transaction.calculate_fine, 0)

    def test_fine_creation_on_return(self):
        """Test fine is created when book is returned overdue"""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today()
        )
        transaction.return_date = transaction.due_date + timedelta(days=5)
        transaction.save()
        
        # Simulate return action
        transaction.book.available_qty += 1
        transaction.book.save()
        Fine.objects.get_or_create(
            transaction=transaction,
            defaults={'amount': transaction.calculate_fine}
        )
        
        fine = Fine.objects.get(transaction=transaction)
        self.assertEqual(fine.amount, 50)  # 5 days * 10

    def test_inventory_return(self):
        """Test book qty increases on return"""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today()
        )
        initial_qty = self.book.available_qty
        transaction.return_date = date.today()
        transaction.book.available_qty += 1
        transaction.book.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_qty, initial_qty + 1)

    def test_multiple_transactions(self):
        """Test multiple issues and returns"""
        # Issue 3 books
        for _ in range(3):
            Transaction.objects.create(
                book=self.book,
                member=self.member,
                issue_date=date.today()
            )
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_qty, 2)  # 5 - 3

        # Return 2 books
        transactions = Transaction.objects.all()[:2]
        for t in transactions:
            t.return_date = date.today()
            t.book.available_qty += 1
            t.book.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_qty, 4)  # 2 + 2

    def test_fine_paid_status(self):
        """Test fine paid status"""
        transaction = Transaction.objects.create(
            book=self.book,
            member=self.member,
            issue_date=date.today()
        )
        transaction.return_date = transaction.due_date + timedelta(days=2)
        Fine.objects.create(transaction=transaction, amount=20)
        
        fine = Fine.objects.get(transaction=transaction)
        self.assertFalse(fine.paid_status)
        fine.paid_status = True
        fine.save()
        self.assertTrue(fine.paid_status)