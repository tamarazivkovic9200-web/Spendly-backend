from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime

from .models import Category, Transaction, Budget, Goal
from .serializers import (
    CategorySerializer,
    TransactionSerializer,
    BudgetSerializer,
    GoalSerializer
)


# category

class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


# transaction

class TransactionListCreate(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


# budget
class BudgetListCreate(generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


# goal
class GoalListCreate(generics.ListCreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)


# dashbord


class MonthlySummary(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")

        if not month or not year:
            return Response({"error": "month and year required"}, status=400)

        month = int(month)
        year = int(year)

        transactions = Transaction.objects.filter(
            user=request.user,
            date__month=month,
            date__year=year
        )

        total_income = transactions.filter(type="income").aggregate(Sum("amount"))["amount__sum"] or 0
        total_expense = transactions.filter(type="expense").aggregate(Sum("amount"))["amount__sum"] or 0

        balance = total_income - total_expense

        return Response({
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        })
