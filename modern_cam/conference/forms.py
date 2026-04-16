from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import (
    Author,
    CopyEditAssignment,
    CopyEditRecord,
    ProgramSession,
    ProgramSlot,
    Review,
    ReviewAssignment,
    Submission,
)
from .roles import COPY_EDITOR_GROUP, REVIEWER_GROUP, users_in_group
from .services import count_words


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label="Email address",
        widget=forms.EmailInput(attrs={"placeholder": "name@institution.org", "autocomplete": "email"}),
    )
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "given-name"}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "family-name"}))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Create a password"}),
        help_text="Use at least 8 characters.",
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Repeat password"}),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with that email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.email = email
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.Form):
    institution = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "University, institute, or organization"}),
    )
    country = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Country"}),
    )


class SubmissionForm(forms.ModelForm):
    certify_authors_approved = forms.BooleanField(
        required=False,
        label="I confirm that all listed authors have reviewed and approved this abstract for submission.",
        help_text="Required when submitting for review.",
    )

    class Meta:
        model = Submission
        fields = ["title", "presentation_type", "abstract_text", "topics"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "A concise, specific abstract title",
                    "maxlength": "300",
                    "data-character-target": "title",
                }
            ),
            "presentation_type": forms.Select(),
            "abstract_text": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Paste the current abstract text here.",
                    "data-word-target": "abstract",
                }
            ),
            "topics": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["abstract_text"].help_text = (
            f"Keep the body at or under {settings.ABSTRACT_WORD_LIMIT} words. "
            "Word count updates live while you edit."
        )

    def clean_abstract_text(self):
        abstract_text = self.cleaned_data["abstract_text"].strip()
        word_count = count_words(abstract_text)
        if word_count > settings.ABSTRACT_WORD_LIMIT:
            raise forms.ValidationError(
                f"Please keep the abstract to {settings.ABSTRACT_WORD_LIMIT} words or fewer. "
                f"Current count: {word_count}."
            )
        return abstract_text


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = [
            "order",
            "first_name",
            "middle_initial",
            "last_name",
            "email",
            "institution",
            "department",
            "address",
            "country",
            "corresponding",
            "presenting",
        ]


AuthorFormSet = inlineformset_factory(
    Submission,
    Author,
    form=AuthorForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ReviewerAssignmentForm(forms.ModelForm):
    class Meta:
        model = ReviewAssignment
        fields = ["reviewer", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reviewer"].queryset = users_in_group(REVIEWER_GROUP)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["score", "recommendation", "suggested_topic", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 8, "placeholder": "Add a focused, constructive review."}),
        }


class CopyEditAssignmentForm(forms.ModelForm):
    class Meta:
        model = CopyEditAssignment
        fields = ["editor", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["editor"].queryset = users_in_group(COPY_EDITOR_GROUP)


class CopyEditRecordForm(forms.ModelForm):
    class Meta:
        model = CopyEditRecord
        fields = ["edited_text", "notes"]
        widgets = {
            "edited_text": forms.Textarea(attrs={"rows": 14}),
            "notes": forms.Textarea(attrs={"rows": 6, "placeholder": "Optional editorial notes or rationale."}),
        }


class ProgramSessionForm(forms.ModelForm):
    class Meta:
        model = ProgramSession
        fields = ["name", "room", "chair_name", "starts_at", "ends_at", "description"]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned = super().clean()
        starts_at = cleaned.get("starts_at")
        ends_at = cleaned.get("ends_at")
        if starts_at and ends_at and ends_at <= starts_at:
            self.add_error("ends_at", "Session end must be after the start time.")
        return cleaned


class ScheduleSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProgramSlot
        fields = ["session", "starts_at", "order"]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["session"].queryset = ProgramSession.objects.order_by("starts_at", "name")


class PresenterConfirmationForm(forms.Form):
    author = forms.ModelChoiceField(queryset=Author.objects.none(), empty_label=None)

    def __init__(self, submission, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["author"].queryset = submission.authors.all()


class PrizeChoiceForm(forms.Form):
    CHOICES = (
        ("yes", "Yes, include this abstract in the prize competition"),
        ("no", "No, skip prize consideration"),
    )
    participating = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)


class PosterUploadForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["poster_pdf"]

    def clean_poster_pdf(self):
        poster = self.cleaned_data["poster_pdf"]
        if poster.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Please keep poster uploads under 10 MB.")
        return poster
