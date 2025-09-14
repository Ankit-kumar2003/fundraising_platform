from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Campaign, Donation, DonorProfile, Expense
from .forms import CampaignForm, DonationForm, DonorProfileForm, ExpenseForm
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string


def home(request):
    active_campaigns = Campaign.objects.filter(
        is_active=True, end_date__gte=timezone.now().date()
    ).order_by("-created_at")

    # Impact Stats
    total_funds_raised = (
        Donation.objects.filter(status="COMPLETED").aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )
    donor_count = (
        Donation.objects.filter(status="COMPLETED").values("donor").distinct().count()
    )
    projects_completed_count = Campaign.objects.filter(
        is_active=False, collected_amount__gte=models.F("target_amount")
    ).count()

    context = {
        "active_campaigns": active_campaigns,
        "total_funds_raised": total_funds_raised,
        "donor_count": donor_count,
        "projects_completed_count": projects_completed_count,
    }
    return render(request, "features/home.html", context)


def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    donations = Donation.objects.filter(
        campaign=campaign, status="COMPLETED", anonymous=False
    ).order_by("-donation_date")[:10]

    context = {
        "campaign": campaign,
        "donations": donations,
        "form": DonationForm() if request.user.is_authenticated else None,
    }
    return render(request, "features/campaign_detail.html", context)


@login_required
def make_donation(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.campaign = campaign
            donation.save()

            # Update campaign collected amount
            campaign.collected_amount += donation.amount
            campaign.save()

            # Update donor profile
            profile, created = DonorProfile.objects.get_or_create(user=request.user)
            profile.total_donations += donation.amount
            profile.last_donation_date = timezone.now()
            profile.save()

            # Send thank you email
            subject = "Thank you for your donation!"
            message = render_to_string(
                "features/email/thank_you.html",
                {"donation": donation, "campaign": campaign, "user": request.user},
            )
            send_mail(
                subject,
                "",
                "noreply@villagefunds.com",
                [request.user.email],
                html_message=message,
            )

            messages.success(
                request,
                "Thank you for your donation! A receipt has been sent to your email.",
            )
            return redirect("campaign_detail", campaign_id=campaign.id)
    else:
        form = DonationForm()

    return render(
        request, "features/make_donation.html", {"form": form, "campaign": campaign}
    )


@login_required
def donor_profile(request):
    profile, created = DonorProfile.objects.get_or_create(user=request.user)
    donations = Donation.objects.filter(donor=request.user).order_by("-donation_date")

    if request.method == "POST":
        form = DonorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("features:donor_profile")
    else:
        form = DonorProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
        "donations": donations,
    }
    return render(request, "features/donor_profile.html", context)


@login_required
def campaign_list(request):
    campaigns = Campaign.objects.all().order_by("-created_at")
    return render(request, "features/campaign_list.html", {"campaigns": campaigns})


@login_required
def add_campaign(request):
    if request.method == "POST":
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, "Campaign created successfully!")
            return redirect("campaign_detail", campaign_id=campaign.id)
    else:
        form = CampaignForm()

    return render(request, "features/add_campaign.html", {"form": form})


@login_required
def add_expense(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)

    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.campaign = campaign
            expense.approved_by = request.user
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect("campaign_detail", campaign_id=campaign.id)
    else:
        form = ExpenseForm()

    return render(
        request, "features/add_expense.html", {"form": form, "campaign": campaign}
    )


def project_list(request):
    campaigns = Campaign.objects.all().order_by("-created_at")
    return render(request, "features/project_list.html", {"campaigns": campaigns})


def fund_usage(request):
    donations = Donation.objects.filter(status="COMPLETED").order_by("-donation_date")[
        :50
    ]
    expenses = Expense.objects.all().order_by("-date")[:50]
    return render(
        request,
        "features/fund_usage.html",
        {"donations": donations, "expenses": expenses},
    )


def about(request):
    return render(request, "features/about.html")


def gallery(request):
    # Placeholder: pass empty list for now
    gallery_items = []
    return render(request, "features/gallery.html", {"gallery_items": gallery_items})


def contact(request):
    if request.method == "POST":
        # In a real app, process the form and send email/notification
        messages.success(
            request, "Thank you for contacting us! We will get back to you soon."
        )
        return redirect("features:contact")
    return render(request, "features/contact.html")


def faq(request):
    return render(request, "features/faq.html")
