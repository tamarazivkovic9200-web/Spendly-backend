from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from .serializers import IncomeSettingSerializer
from .models import IncomeSetting
from .serializers import UserSettingsSerializer

from .models import Category, Transaction, Budget, Goal
from .serializers import (
    CategorySerializer,
    TransactionSerializer,
    BudgetSerializer,
    GoalSerializer
)

# =============================
# AUTH
# =============================

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username,
            "message": "User registered successfully"
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.filter(username=username).first()

        if user is None:
            return Response({"error": "Invalid username"}, status=400)

        if not user.check_password(password):
            return Response({"error": "Invalid password"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username
        })


# =============================
# CATEGORY
# =============================

class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


# =============================
# TRANSACTION
# =============================

class TransactionListCreate(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


# =============================
# BUDGET
# =============================

class BudgetListCreate(generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"error": "Budget for this category and month already exists."}
            )

class BudgetDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


# =============================
# GOALS
# =============================

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


# =============================
# DASHBOARD SUMMARY
# =============================

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

        total_income = transactions.filter(type="income").aggregate(total=Sum("amount"))["total"] or 0
        total_expense = transactions.filter(type="expense").aggregate(total=Sum("amount"))["total"] or 0

        balance = total_income - total_expense

        return Response({
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        })


# =============================
# CREATE DEFAULT CATEGORIES
# =============================

class CreateDefaultCategories(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        default_categories = [
            ("Salary", "income"), ("Bonus", "income"), ("Gift", "income"),
            ("Refund", "income"), ("Investment", "income"), ("Business", "income"),
            ("Food", "expense"), ("Groceries", "expense"), ("Coffee", "expense"),
            ("Restaurants", "expense"), ("Shopping", "expense"), ("Clothes", "expense"),
            ("Entertainment", "expense"), ("Movies", "expense"), ("Travel", "expense"),
            ("Transport", "expense"), ("Fuel", "expense"), ("Car Repair", "expense"),
            ("Health", "expense"), ("Pharmacy", "expense"), ("Gym", "expense"),
            ("Beauty", "expense"), ("Hairdresser", "expense"), ("Home", "expense"),
            ("Rent", "expense"), ("Electricity", "expense"), ("Water", "expense"),
            ("Internet", "expense"), ("Phone", "expense"), ("Pets", "expense"),
            ("Kids", "expense"), ("Education", "expense"),
        ]

        created = 0

        for name, ctype in default_categories:
            obj, was_created = Category.objects.get_or_create(name=name, type=ctype)
            if was_created:
                created += 1

        return Response({
            "message": "Default categories created",
            "created_count": created
        })


class IncomeSettingDetail(generics.RetrieveUpdateAPIView):
    serializer_class = IncomeSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, created = IncomeSetting.objects.get_or_create(user=self.request.user)
        return obj


class UserSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        print("\n===== PUT DATA =====")
        print(request.data)
        print("===== END DATA =====\n")
        return super().update(request, *args, **kwargs)


# =============================
# CHANGE PASSWORD
# =============================

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        new_password = request.data.get("new_password")

        if not new_password:
            return Response({"error": "New password is required"}, status=400)

        user = request.user
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully"})


# =============================
# DELETE ACCOUNT
# =============================

class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Account deleted"}, status=204)
