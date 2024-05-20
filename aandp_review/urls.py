from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #     path('applicant/', views.applicant_view, name='applicant'),
    path('publication-list/', views.publication_list_view, name='publication-list'),

    # Applicant urls
    path("applicant/<uuid:pk>", views.applicant_view, name='applicant-home'),
    path('applicants/', views.ApplicantListView.as_view(),
         name='all-applicants'),
    path('apcvmaker-add/', views.form_apcvmaker_add,
         name='form-apcvmaker-add'),
    path('apcvmaker-result-list/', views.apcvmaker_result_list,
         name='text-added-from-apcvmaker'),


    path('assessors/', views.AssessorListView.as_view(), name='all-assessors'),
    path("assessor/<uuid:pk>", views.assessor_view, name='assessor'),
    path("assessed_applicant/<uuid:pk>",
         views.assessed_applicant_view, name='assessed-applicant'),
    path("table-of-scores/", views.table_of_scores_page,
         name="table-of-scores"),

    path('publication/create/', views.create_publication,
         name='publication-create'),
    path('publication/<int:pk>/update/',
         views.update_publication, name='publication-update'),
    path('publication/<int:pk>/delete/',
         views.PublicationDelete.as_view(), name='publication-delete'),

    path('assessment/<int:pk>/update/',
         views.update_assess_publication, name='assessment-update'),
    path('assessment/<int:pk>/update/',
         views.AssessedPublicationUpdate.as_view(), name='assessment-update'),


]
