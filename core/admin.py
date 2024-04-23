from django.contrib import admin
from .models import User


class AdminUser(admin.ModelAdmin):
    add_fieldsets = (
        ('None', {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'password1', 'password2', 'email')
        })
    )


admin.site.register(User, AdminUser)
