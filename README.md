# Library Management System (Django)

A minimal LMS built in Django.  
Features:

* Books, members, transactions & automated fine calculation.
* Librarian (full CRUD) / member (view own history) roles.
* Admin‑panel UI, SQLite backend – no external DB required.

---

## Prerequisites

* Python 3.11+ (3.13 used here)
* virtualenv (optional but recommended)
* Windows PowerShell / Command Prompt

---

## Setup

```powershell
# 1. clone/open workspace in VS Code
cd c:\Users\Gautam\OneDrive\Desktop\LibraryManagementSystem

# 2. create & activate virtual environment
python -m venv lms_env
lms_env\Scripts\activate

# 3. install dependencies
pip install django mysqlclient   # mysqlclient is harmless; SQLite is used

# 4. ensure ‘library’ app is listed in INSTALLED_APPS
#    (already done in settings.py)

# 5. generate database schema
python manage.py makemigrations library
python manage.py migrate
```

> **Note**  
> SQLite is configured by default (`db.sqlite3` in project root).  
> If you prefer MySQL, adjust `DATABASES` in `library_config/settings.py`
> and install the appropriate driver.

---

## Admin user & groups

```powershell
# create an administrator account
python manage.py createsuperuser
# follow prompts for username/email/password

# optionally, open the shell to create “Librarian” / “Member” groups
python manage.py shell
```

```python
from django.contrib.auth.models import Group, Permission
from library.models import Book, Member, Transaction, Fine

librarian, _ = Group.objects.get_or_create(name='Librarian')
librarian.permissions.set(
    Permission.objects.filter(content_type__app_label='library')
)

member, _ = Group.objects.get_or_create(name='Member')
member.permissions.set(
    Permission.objects.filter(
        codename__in=['view_transaction','view_fine'],
        content_type__app_label='library'
    )
)
exit()
```

Members created via **Users** in the admin should be linked from **Members**.

---

## Running the server

```powershell
# start development server
python manage.py runserver

# visit in browser:
http://127.0.0.1:8000/admin/
```

Log in with your superuser credentials, add books/members/transactions, and
use the custom actions (“Return selected books”, “Mark selected fines as paid”).

---

## Tests

The app includes unit tests covering validation, inventory logic and fines.

```powershell
python manage.py test library
```

---

## Useful commands

* `python manage.py shell` – interactive Django shell
* `python manage.py makemigrations` / `migrate` – sync models
* `python manage.py createsuperuser` – add staff account
* `python manage.py test` – run all tests

---

## Notes

* Phone field enforces 10‑digit numeric strings.
* `Transaction.save()` auto‑sets due date (+14 days) and decrements
  `Book.available_qty`.
* `calculate_fine` property returns ₹10/day for overdue returns.
* Fine objects are created by the admin action when a book is returned.
* Members see only their own transactions via the admin queryset filter.

Enjoy exploring and extending the system!# Library Management System (Django)

A minimal LMS built in Django.  
Features:

* Books, members, transactions & automated fine calculation.
* Librarian (full CRUD) / member (view own history) roles.
* Admin‑panel UI, SQLite backend – no external DB required.
* 90‑minute sprint implementation.

---

## Prerequisites

* Python 3.11+ (3.13 used here)
* virtualenv (optional but recommended)
* Windows PowerShell / Command Prompt

---

## Setup

```powershell
# 1. clone/open workspace in VS Code
cd c:\Users\Gautam\OneDrive\Desktop\LibraryManagementSystem

# 2. create & activate virtual environment
python -m venv lms_env
lms_env\Scripts\activate

# 3. install dependencies
pip install django mysqlclient   # mysqlclient is harmless; SQLite is used

# 4. ensure ‘library’ app is listed in INSTALLED_APPS
#    (already done in settings.py)

# 5. generate database schema
python manage.py makemigrations library
python manage.py migrate
```

> **Note**  
> SQLite is configured by default (`db.sqlite3` in project root).  
> If you prefer MySQL, adjust `DATABASES` in `library_config/settings.py`
> and install the appropriate driver.

---

## Admin user & groups

```powershell
# create an administrator account
python manage.py createsuperuser
# follow prompts for username/email/password

# optionally, open the shell to create “Librarian” / “Member” groups
python manage.py shell
```

```python
from django.contrib.auth.models import Group, Permission
from library.models import Book, Member, Transaction, Fine

librarian, _ = Group.objects.get_or_create(name='Librarian')
librarian.permissions.set(
    Permission.objects.filter(content_type__app_label='library')
)

member, _ = Group.objects.get_or_create(name='Member')
member.permissions.set(
    Permission.objects.filter(
        codename__in=['view_transaction','view_fine'],
        content_type__app_label='library'
    )
)
exit()
```

Members created via **Users** in the admin should be linked from **Members**.

---

## Running the server

```powershell
# start development server
python manage.py runserver

# visit in browser:
http://127.0.0.1:8000/admin/
```

Log in with your superuser credentials, add books/members/transactions, and
use the custom actions (“Return selected books”, “Mark selected fines as paid”).

---

## Tests

The app includes unit tests covering validation, inventory logic and fines.

```powershell
python manage.py test library
```

---

## Useful commands

* `python manage.py shell` – interactive Django shell
* `python manage.py makemigrations` / `migrate` – sync models
* `python manage.py createsuperuser` – add staff account
* `python manage.py test` – run all tests

---

## Notes

* Phone field enforces 10‑digit numeric strings.
* `Transaction.save()` auto‑sets due date (+14 days) and decrements
  `Book.available_qty`.
* `calculate_fine` property returns ₹10/day for overdue returns.
* Fine objects are created by the admin action when a book is returned.
* Members see only their own transactions via the admin queryset filter.

Enjoy exploring and extending the system!
