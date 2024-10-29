from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from api.models import *
from django.contrib.auth.models import Group
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from unfold.decorators import action, display
# from django.contrib.auth.admin import UserAdmin
# Register your models here.
# admin.site.unregister(User)
from unfold.contrib.forms.widgets import WysiwygWidget
# from unfold.contrib.forms.

admin.site.unregister(Group)

class ContestProblemInline(TabularInline):
    model = ContestProblem
    extra = 1  # Number of empty forms displayed to add new problems
    fields = ['problem']  # Fields to display in the inline
    
class TestCaseInline(TabularInline):
    model = Problem
    extra = 1  # Number of empty forms displayed to add new problems
    fields = ['']  # Fields to display in the inline

# Register Contest with ContestProblemInline
@admin.register(Contest)
class ContestAdmin(ModelAdmin):
    inlines = [ContestProblemInline]
    list_display = ('name', 'start_time', 'end_time')  # Customize as needed
    search_fields = ['name']

@admin.register(Problem)
class ProblemAdmin(ModelAdmin):
#     form = ProblemAdminForm
    list_display = ['title']  # Customize as needed
    search_fields = ['title']
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         form.test_cases_formset = TestCaseFormSet
#         return form

#     def save_formset(self, request, form, formset, change):
#         # Ensure the formset for test cases is saved
#         if formset.is_valid():
#             form.instance.test_cases = form.cleaned_data['test_cases']
#         super().save_formset(request, form, formset, change)

# Optionally, register ContestProblem if you want to manage it separately
# @admin.register(ContestProblem)
# class ContestProblemAdmin(ModelAdmin):
#     list_display = ('contest', 'problem')
#     list_filter = ('contest',)

# class ProblemForm(forms.ModelForm):
#     pass

@admin.register(User)
class AccountAdmin(BaseUserAdmin,ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = [
        "display_header",
        "is_active",
        "display_staff",
        "display_superuser",
        "display_created",
    ]
    ordering =()
    add_fieldsets = (
        (_("Add User"), {"fields": ["email","password","password2"]}),
    )
    fieldsets = (
        (
            _("Personal info"),
            {
                "fields": (("first_name", "last_name"), "email"),
                "classes": ["tab"],
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["tab"],
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login", "date_joined"),
                # "classes": ["tab"],
            },
        ),
        (None, {"fields": ["password"]}),
    )
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    # formfield_overrides = {
    #     models.TextField: {
    #         "widget": WysiwygWidget,
    #     }
    # }
    readonly_fields = ["last_login", "date_joined"]

    @display(description=_("User"))
    def display_header(self, instance: User):
        return f"{instance.first_name} {instance.last_name}"

    @display(description=_("Staff"), boolean=True)
    def display_staff(self, instance: User):
        return instance.is_staff

    @display(description=_("Superuser"), boolean=True)
    def display_superuser(self, instance: User):
        return instance.is_superuser

    @display(description=_("Created"))
    def display_created(self, instance: User):
        return instance.date_joined
    
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

# admin.site.register(ContestProblem)
