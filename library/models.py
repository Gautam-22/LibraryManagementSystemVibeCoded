from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.validators import RegexValidator

FINE_RATE = 10  # ₹10 per day

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    total_qty = models.PositiveIntegerField()
    available_qty = models.PositiveIntegerField()
    
    def clean(self):
        if self.available_qty > self.total_qty:
            raise ValueError("Available quantity cannot exceed total quantity")
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Phone number must be 10 digits.')]
    )
    membership_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    class Meta:
        ordering = ['-membership_date']


class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New transaction (first save)
            self.due_date = self.issue_date + timedelta(days=14)
            self.book.available_qty -= 1
            self.book.save()
        super().save(*args, **kwargs)
    
    @property
    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            overdue_days = (self.return_date - self.due_date).days
            return overdue_days * FINE_RATE
        return 0
    
    def __str__(self):
        return f"{self.member.user.username} - {self.book.title}"
    
    class Meta:
        ordering = ['-issue_date']


class Fine(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid_status = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"₹{self.amount} - {self.transaction.member.user.username}"
    
    class Meta:
        ordering = ['-created_date']