from django.urls import path, re_path
from django.views.generic import RedirectView
from . import views

app_name = "features"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    # Redirect projects to campaigns to consolidate functionality
    re_path(r'^projects(/.*)?$', RedirectView.as_view(pattern_name='features:campaign_list', permanent=True)),
    path("fund-usage/", views.fund_usage, name="fund_usage"),
    path("gallery/", views.gallery, name="gallery"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/add/", views.add_campaign, name="add_campaign"),
    path("campaigns/<int:campaign_id>/", views.campaign_detail, name="campaign_detail"),
    path("campaigns/<int:campaign_id>/donate/", views.make_donation, name="make_donation"),
    path("campaigns/<int:campaign_id>/expenses/add/", views.add_expense, name="add_expense"),
    path("campaigns/<int:campaign_id>/download-donations/", views.download_campaign_donations, name="download_campaign_donations"),
    path("donor-profile/", views.donor_profile, name="donor_profile"),
    path("donor-profiles/", views.donor_profile_list, name="donor_profile_list"),
    path("donations/", views.donation_list, name="donation_list"),
]
