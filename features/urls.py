from django.urls import path
from . import views

app_name = "features"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("projects/", views.project_list, name="project_list"),
    path("fund-usage/", views.fund_usage, name="fund_usage"),
    path("gallery/", views.gallery, name="gallery"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/add/", views.add_campaign, name="add_campaign"),
    path("campaigns/<int:campaign_id>/", views.campaign_detail, name="campaign_detail"),
    path(
        "campaigns/<int:campaign_id>/donate/", views.make_donation, name="make_donation"
    ),
    path(
        "campaigns/<int:campaign_id>/expense/add/",
        views.add_expense,
        name="add_expense",
    ),
    path("profile/", views.donor_profile, name="donor_profile"),

]
