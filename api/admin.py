from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from api.models import *
from django.contrib.auth.models import Group
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from unfold.decorators import action, display
from unfold.contrib.forms.widgets import WysiwygWidget

admin.site.unregister(Group)

class ContestProblemInline(TabularInline):
    model = ContestProblem
    extra = 1  # Number of empty forms displayed to add new problems
    fields = ['problem']  # Fields to display in the inline
    
class TestCaseInline(TabularInline):
    model = TestCase
    extra = 1  # Number of empty forms displayed to add new problems
    fields = ['visible','input_data','expected_output']  # Fields to display in the inline

# Register Contest with ContestProblemInline
@admin.register(Contest)
class ContestAdmin(ModelAdmin):
    inlines = [ContestProblemInline]
    list_display = ('name', 'start_time', 'end_time')  # Customize as needed
    search_fields = ['name']

@admin.register(Problem)
class ProblemAdmin(ModelAdmin):
    inlines = [TestCaseInline]
#     form = ProblemAdminForm
    list_display = ['title']  # Customize as needed
    search_fields = ['title']
    # formfield_overrides = {
    #     models.TextField: {
    #         "widget": WysiwygWidget,
    #     }
    # }

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
    # add_fieldsets = (
    #     (_("Add User"), {"fields": ["username","password","password2"]}),
    # )
    fieldsets = (
        (
            _("Personal info"),
            {
                "fields": (("first_name", "last_name"), "email","phone"),
                # "classes": ["tab"],
            },
        ),
        (
            _("Academic data (Student only)"),
            {
                "fields": (("branch", "batch")),
                "classes": ["tab"],
            },
        ),
        (
            _("Permissions (Admin only)"),
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
        (_("Password"), {"fields": ["password"]}),
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

# admin.site.register(TestCase)
