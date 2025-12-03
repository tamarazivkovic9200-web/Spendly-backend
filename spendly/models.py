from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'

    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f'{self.name} ({self.type})'


class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'

    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateField()
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} {self.amount} ({self.type})"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()  # 1–12
    year = models.IntegerField()

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')

    def __str__(self):
        return f"{self.user.username} - {self.category.name} Budget ({self.month}/{self.year})"


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"
