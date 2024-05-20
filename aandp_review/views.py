from django.views.generic.edit import CreateView, UpdateView, DeleteView
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from itertools import count
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from aandp_review.forms import AdjustPublicationModelForm, AssessedPublicationModelForm
from .constants import PUBLICATION_TYPES
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.
from .models import Applicant, Assessor, Publication, AssessedPublication
# , AssessedPublication

# Customized template for html
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def index(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html')


def applicant_view(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    # applicant = Applicant.objects.first()
    request.session['applicant_id'] = str(applicant.id)
    request.session.modified = True

    # Get all publications of applicant
    publications = applicant.publications.all()
    context = {
        'applicant': applicant,
        'publications': publications
    }
    # return render(request, "applicant-pages/applicant-landing.html", context=context)
    return render(request, "aandp_review/applicant_views/applicant_page.html", context=context)


def form_apcvmaker_add(request):
    context = {

    }
    return render(request, "aandp_review/applicant_views/add_from_apcvmaker_form.html", context=context)


def apcvmaker_result_list(request):
    context = {

    }
    return render(request, "aandp_review/applicant_views/add_from_apcvmaker_form.html", context=context)


@permission_required('aandp_review.can_edit_publication_list')
def publication_list_view(request):

    # applicant = Applicant.objects.all().filter(id= request.session.get('applicant_id')) #TODO: Allow this to be based on the session
    applicant = get_object_or_404(Applicant, pk=uuid.UUID(
        request.session.get('applicant_id')))

    context = {
        'applicant': applicant,
        'PUBLICATION_TYPES': PUBLICATION_TYPES

    }
    return render(request, "aandp_review/applicant_views/applicant_manual_pub_add.html", context=context)


class ApplicantListView(generic.ListView):
    model = Applicant
    # your own name for the list as a template variable
    context_object_name = 'obj_list'
    queryset = Applicant.objects.all()  # Get all applicants
    cnt = queryset.count()
    # template_name = '/aandp_review/applicant_views/applicants_list.html'  # Specify your own template name/location
    # Specify your own template name/location
    template_name = 'aandp_review/applicant_views/applicants_list.html'
    # paginate_by =2


class AssessorListView(generic.ListView):
    model = Assessor
    # your own name for the list as a template variable
    context_object_name = 'obj_list'
    queryset = Assessor.objects.all()  # Get all applicants
    cnt = queryset.count()
    # template_name = '/aandp_review/applicant_views/applicants_list.html'  # Specify your own template name/location
    # Specify your own template name/location
    template_name = 'aandp_review/assessor_views/assessor_list.html'
    # paginate_by =2

# Assessor section


def assessor_view(request, pk):
    assessor_instance = get_object_or_404(Assessor, pk=pk)
    # assessor = Assessor.objects.first()
    request.session['assessor_id'] = str(assessor_instance.id)
    request.session.modified = True
    assigned_applicants = assessor_instance.applicants_assigned.all()
    cnt = assigned_applicants.count()
    print(cnt)
    context = {
        'assessor': assessor_instance,
        'applicants_assigned': assigned_applicants
    }
    return render(request, "aandp_review/landing_pages/assessor_page.html", context=context)


def assessed_applicant_view(request, pk):
    applicant_instance = get_object_or_404(Applicant, pk=pk)
    current_assessor = Assessor.objects.all().filter(
        id=request.session['assessor_id'])[:1].get()
    # applicant = Applicant.objects.first()
    request.session['applicant_id'] = str(applicant_instance.id)
    request.session.modified = True

    pubs_of_applicant = applicant_instance.publication_set.all()
    for publication in pubs_of_applicant:
        if (AssessedPublication.objects.all().filter(publication=publication).count() == 0):
            # If assessedpublication object does not exist for pub, create it
            assessed_publication = AssessedPublication(publication=publication, applicant=applicant_instance,
                                                       assessor=current_assessor)
            assessed_publication.save()

    assessed_publications = AssessedPublication.objects.all().filter(assessor=current_assessor,
                                                                     applicant=applicant_instance).order_by('publication__position_num')

    context = {
        'applicant': applicant_instance,
        'assessed_publications': assessed_publications
    }
    return render(request, "aandp_review/assessor_views/assessed_applicant_pub_list.html", context=context)


# Publication stuff

class PublicationCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'aandp.can_edit_publication_list'
    model = Publication
    fields = ['pub_title', 'abstract', 'publication_type',
              'percent_contribution', 'position_num', 'document_path', 'citation_text']


def create_publication(request):

    applicant = get_object_or_404(Applicant, pk=uuid.UUID(
        request.session.get('applicant_id')))

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = AdjustPublicationModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            new_publication = Publication(applicant=applicant)

            new_publication.pub_title = form.cleaned_data['pub_title']
            new_publication.abstract = form.cleaned_data['abstract']
            new_publication.publication_type = form.cleaned_data['publication_type']
            new_publication.percent_contribution = form.cleaned_data['percent_contribution']
            new_publication.author_position = form.cleaned_data['author_position']
            new_publication.document_path = form.cleaned_data['document_path']
            new_publication.citation_text = form.cleaned_data['citation_text']
            new_publication.position_num = Publication.objects.all().filter(
                applicant=applicant).count() + 1
            new_publication.applicant = applicant

            new_publication.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('publication-list'))

    # If this is a GET (or any other method) create the default form.
    else:
        form = AdjustPublicationModelForm()

    context = {
        'form': form,
        # 'book_instance': book_instance,
        "applicant": applicant,
        "isnew": True,
    }

    return render(request, 'aandp_review/applicant_views/create_new_publication.html', context)


def update_publication(request, pk):

    applicant = get_object_or_404(Applicant, pk=uuid.UUID(
        request.session.get('applicant_id')))
    publications_filtered = Publication.objects.all().filter(
        position_num=pk, applicant=applicant)
    publication = publications_filtered.first()

    if (publications_filtered.count() == 0 or publications_filtered.count() != 1):
        # TODO:Separate the not found and no access into separate pages
        raise Http404(
            "No publication selected or no access or multiple pubs satisfy criteria")

    # If this is a POST request then process the Form data
    elif request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = AdjustPublicationModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)

            publication.pub_title = form.cleaned_data['pub_title']
            publication.abstract = form.cleaned_data['abstract']
            publication.publication_type = form.cleaned_data['publication_type']
            publication.percent_contribution = form.cleaned_data['percent_contribution']
            publication.author_position = form.cleaned_data['author_position']
            publication.document_path = form.cleaned_data['document_path']
            publication.citation_text = form.cleaned_data['citation_text']
            publication.position_num = form.cleaned_data["position_num"]
            # publication.applicant = applicant

            publication.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('publication-list'))

        # If this is a GET (or any other method) create the default form.
    else:
        form = AdjustPublicationModelForm(initial={
            'pub_title': publication.pub_title,
            'abstract': publication.abstract,
            'publication_type': publication.publication_type,
            'percent_contribution': publication.percent_contribution,
            'author_position': publication.author_position,
            'document_path': publication.document_path,
            'citation_text': publication.citation_text,
            'position_num': publication.position_num,
            'applicant': publication.applicant
        })

    context = {
        'form': form,
        # 'book_instance': book_instance,
        "applicant": applicant,
        "publication": publication,
        "isnew": False,
        "total_publications": Publication.objects.all().filter(applicant=applicant).count()
    }

    return render(request, 'aandp_review/applicant_views/update_publication.html', context)


class PublicationUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'aandp_review.can_edit_publication_list'
    model = Publication
    fields = ['pub_title', 'abstract', 'publication_type',
              'percent_contribution', 'position_num', 'document_path', 'citation_text']


class PublicationDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = 'aandp_review.can_edit_publication_list'
    model = Publication
    success_url = reverse_lazy('publications')


# Assessed Publications part
class AssessedPublicationCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'aandp_review.can_edit_publication_assessment'
    model = AssessedPublication
    fields = ['publication', 'score']


class AssessedPublicationUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'aandp_review.can_edit_publication_assessment'
    model = AssessedPublication
    fields = ['pub_title', 'abstract', 'publication_type',
              'percent_contribution', 'position_num', 'document_path', 'citation_text']


def update_assess_publication(request, pk):
    assessed_publication = ""

    applicant = get_object_or_404(Applicant, pk=uuid.UUID(
        request.session.get('applicant_id')))
    current_assessor = get_object_or_404(
        Assessor, pk=uuid.UUID(request.session.get('assessor_id')))
    assessed_publication = get_object_or_404(
        AssessedPublication, publication__position_num=pk, applicant=applicant, assessor=current_assessor)

    if (assessed_publication == ""):
        # TODO:Separate the not found and no access into separate pages
        raise Http404(
            "No publication selected or no access or multiple pubs satisfy criteria")

    # If this is a POST request then process the Form data
    elif request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = AssessedPublicationModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)

            assessed_publication.score = form.cleaned_data['score']
            assessed_publication.review = form.cleaned_data['review']

            assessed_publication.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('assessed-applicant', args=[str(applicant.id)]))

        # If this is a GET (or any other method) create the default form.
    else:
        form = AssessedPublicationModelForm(initial={
            'score': assessed_publication.score, 'review': assessed_publication.review
        })

    context = {
        'form': form,
        "applicant": applicant,
        "assessed_publication": assessed_publication,
        "isnew": False,
        "total_assessments": AssessedPublication.objects.all().filter(applicant=applicant).count()
    }

    return render(request, 'aandp_review/assessor_views/update_assessed_publication.html', context)


# @permission_required('aandp_review.can_edit_publication_assessment')
# @login_required
def table_of_scores_page(request):
    current_assessor = Assessor.objects.all().get(
        id=uuid.UUID(request.session.get('assessor_id')))
    applicant = Applicant.objects.all().get(
        id=uuid.UUID(request.session.get('applicant_id')))

    # First check if the applicant is part of those assigned to this assessor

    # Get all assessedpublications
    assessed_publications = AssessedPublication.objects.filter(
        assessor=current_assessor, applicant=applicant)

    # Generate additional columns (normalised_percent, weighted_score)
    additional_columns = {}
    for assessment in assessed_publications:
        additional_columns[assessment.id] = {}  # I need to set default first
        additional_columns[assessment.id]["normalised_percent"] = assessment.publication.percent_contribution/100

        if (assessment.score != None):
            additional_columns[assessment.id]["weighted_score"] = additional_columns[
                assessment.id]["normalised_percent"] * assessment.score
        else:
            additional_columns[assessment.id]["weighted_score"] = 0

        additional_columns[assessment.id]["maximum_score"] = "max"

    # Generate total rows
    total_row = {}
    total_row["total_weighted"] = sum(
        [x['weighted_score'] for x in additional_columns.values()])

    context = {
        "assessed_publications": assessed_publications,
        "applicant": applicant,
        "additional_columns": additional_columns,
        "total_row": total_row
    }

    return render(request, "aandp_review/applicant_views/table_of_scores.html", context=context)
