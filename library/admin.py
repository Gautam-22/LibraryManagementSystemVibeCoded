from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone
from .models import Book, Member, Transaction, Fine

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'total_qty', 'available_qty')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('author',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'membership_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_filter = ('membership_date',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'issue_date', 'due_date', 'return_date', 'calculate_fine')
    list_filter = ('issue_date', 'due_date', 'return_date')
    search_fields = ('member__user__username', 'book__title')
    actions = ['return_book']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and not request.user.groups.filter(name='Librarian').exists():
            return qs.filter(member__user=request.user)
        return qs
    
    def return_book(self, request, queryset):
        queryset.update(return_date=timezone.now().date())
        
        for transaction in queryset:
            transaction.book.available_qty += 1
            transaction.book.save()
            
            if transaction.calculate_fine > 0:
                Fine.objects.get_or_create(
                    transaction=transaction,
                    defaults={'amount': transaction.calculate_fine}
                )
        self.message_user(request, f"Returned {queryset.count()} book(s)")
    
    return_book.short_description = "Return selected books"

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'amount', 'paid_status', 'created_date')
    list_filter = ('paid_status', 'created_date')
    search_fields = ('transaction__member__user__username',)
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(paid_status=True)
        self.message_user(request, f"Marked {queryset.count()} fine(s) as paid")
    
    mark_as_paid.short_description = "Mark selected fines as paid"