from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from .models import User, UserProfile, PhoneVerification, RequestData, AddressBookItem, \
Document, DocumentCategory, EmailVerification, ResetPasswordVerification, TempUser, TempUserProfile, \
OnboardingLink, AccountMergeRequest, ProfileComment, ProfileLike, TempUserStatus


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'date_of_birth')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'date_of_birth', 'is_active', 'is_admin', 'active', 'verified_by_antro', 'verified_by_user', 'verified_by_organisation')

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'phone_number', 'date_of_birth', 'is_admin')
    list_filter = ('is_admin', )
    fieldsets = (
        (None, {'fields': ('user_id','email', 'phone_number', 'password')}),
        ('Account Verification', {'fields': ('email_verified', 'phone_verified')}),
        ('Personal info', {'fields': ('date_of_birth', 'first_name', 'last_name', 'organisation', 'verified_by_antro', 'verified_by_user', 'verified_by_organisation')}),
        ('Permissions', {'fields': ('is_admin','is_staff', 'active')}),
    )
    readonly_fields = ('user_id',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'date_of_birth', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(PhoneVerification)
admin.site.register(EmailVerification)
admin.site.register(ResetPasswordVerification)
admin.site.register(AccountMergeRequest)
admin.site.register(RequestData)
admin.site.register(AddressBookItem)
admin.site.register(DocumentCategory)
admin.site.register(Document)
admin.site.register(TempUser)
admin.site.register(TempUserProfile)
admin.site.register(OnboardingLink)
admin.site.register(ProfileComment)
admin.site.register(ProfileLike)
admin.site.register(TempUserStatus)
