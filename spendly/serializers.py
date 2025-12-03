from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Transaction, Budget, Goal


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['user']


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
