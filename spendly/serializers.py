from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Transaction, Budget, Goal
from django.db.models import Sum
from .models import IncomeSetting


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
    spent_amount = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['user']

    def get_spent_amount(self, obj):
        from django.db.models import Sum
        total_spent = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            type="expense",
            date__month=obj.month,
            date__year=obj.year
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        return float(total_spent)



class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class IncomeSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSetting
        fields = ['id', 'monthly_income']
        read_only_fields = ['id']

class UserSettingsSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(
        source="profile.avatar",
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ["first_name", "username", "email", "avatar"]

    def update(self, instance, validated_data):
        # Extract nested profile data
        profile_data = validated_data.pop("profile", {})
        avatar = profile_data.get("avatar", None)

        # Update User fields
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()

        # Update profile avatar if provided
        if avatar:
            instance.profile.avatar = avatar
            instance.profile.save()

        return instance