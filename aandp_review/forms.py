import this
from django.forms import ModelForm

from .models import AssessedPublication, Publication


class AdjustPublicationModelForm(ModelForm):
    class Meta:
        model = Publication
        fields = ['pub_title', 'abstract', 'position_num', 'publication_type',
                  'percent_contribution', 'author_position', 'document_path', 'citation_text']


class AssessedPublicationModelForm(ModelForm):
    class Meta:
        model = AssessedPublication
        fields = ['score', 'review']

        # fields = '__all__'

    def AssessedPublicationModelForm(publication):
        this.publication = publication
