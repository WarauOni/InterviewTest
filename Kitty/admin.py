from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Kitty, Adoption, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

@admin.register(Kitty)
class KittyAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'age', 'date_of_birth', 'history')
    list_filter = ('species',)
    search_fields = ('name', 'species')
    
    # Allow editing all fields in the model
    def get_readonly_fields(self, request, obj=None):
        return []

    # Add a custom link in the admin header to an external page (if needed)
    def changelist_view(self, request, extra_context=None):
        # Add a custom link to the custom "Add Kitty" page
        extra_context = extra_context or {}
        extra_context['custom_button'] = format_html(
            '<a class="button" href="{}">Go to Custom Add Kitty Page</a>',
            reverse('add_kitty')  # Ensure this URL name matches the custom site's view for adding a kitty
        )
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ('adopt_id', 'user', 'kitty', 'adopt_date', 'status')
    list_filter = ('status', 'adopt_date')
    search_fields = ('adopt_id', 'user__username', 'kitty__name')
    readonly_fields = ('adopt_date', 'adopt_id')  # Make non-editable fields read-only

    # Allow editing of other fields
    def get_readonly_fields(self, request, obj=None):
        if obj:  # If an adoption record already exists, make 'adopt_id' read-only
            return ['adopt_id', 'adopt_date']  # Read-only for these fields
        return []

    # Custom admin actions for status updates
    actions = ['approve_adoptions', 'reject_adoptions']

    def approve_adoptions(self, request, queryset):
        updated = queryset.update(status='APPROVED')
        self.message_user(request, f"{updated} adoption(s) successfully approved.")
    approve_adoptions.short_description = "Approve selected adoptions"

    def reject_adoptions(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, f"{updated} adoption(s) successfully rejected.")
    reject_adoptions.short_description = "Reject selected adoptions"

    # Ensure deletions work fine, cascading or nullifying related data
    def get_actions(self, request):
        actions = super().get_actions(request)
        return actions


class UserAdmin(BaseUserAdmin):
    # Fields to display in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'gender')

    # Allow editing of user-related fields
    def get_readonly_fields(self, request, obj=None):
        return []

    # Fieldsets for organizing the detail view
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'ic_no', 'picture', 'no_tel')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )

    # Fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')


# Register the User model with the custom UserAdmin
admin.site.register(User, UserAdmin)
