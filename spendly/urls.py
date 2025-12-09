from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CategoryListCreate, CategoryDetail,
    TransactionListCreate, TransactionDetail,
    BudgetListCreate, BudgetDetail,
    GoalListCreate, GoalDetail,
    MonthlySummary,
    RegisterView, LoginView,
    CreateDefaultCategories,
)

urlpatterns = [
    # Create default categories (POST)
    path("categories/create-defaults/", CreateDefaultCategories.as_view()),

    # Category
    path("categories/", CategoryListCreate.as_view()),
    path("categories/<int:pk>/", CategoryDetail.as_view()),

    # Transaction
    path("transactions/", TransactionListCreate.as_view()),
    path("transactions/<int:pk>/", TransactionDetail.as_view()),

    # Budget
    path("budgets/", BudgetListCreate.as_view()),
    path("budgets/<int:pk>/", BudgetDetail.as_view()),

    # Goal
    path("goals/", GoalListCreate.as_view()),
    path("goals/<int:pk>/", GoalDetail.as_view()),

    # Dashboard summary
    path("summary/", MonthlySummary.as_view()),

    # Auth
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
]
