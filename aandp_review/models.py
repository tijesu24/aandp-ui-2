
import uuid  # Required for unique assessed pubs
from django.db import models
from datetime import datetime
from .constants import ACADEMIC_POSITIONS, PUBLICATION_TYPES
from django.contrib.auth.models import User


class Applicant(models.Model):
    """Model representing application information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # user = models.ForeignKey(
    #     User, on_delete=models.SET_NULL, null=True, blank=True)

    YEARS = [(str(x), str(x)) for x in range(2016, datetime.now().year+1)]

    promotion_year = models.CharField(
        max_length=4,
        choices=YEARS,
        blank=True,
        default='m',
        help_text='Promotion year',
    )

    position_applying_to = models.CharField(
        max_length=30,
        choices=ACADEMIC_POSITIONS,
        default='Select',
        help_text='Position being applied for',
    )

    assessors_assigned = models.ManyToManyField(
        'Assessor', help_text="Select Assessors", blank=True,
    )

    h_index = models.IntegerField(blank=True, null=True)
    num_of_citations = models.IntegerField(blank=True, null=True)
    combined_doc_path = models.CharField(
        max_length=200, blank=True, null=True)

    def __str__(self):
        """Return the surname and initials in format SURNAME F.M."""
        return (self.last_name.capitalize()+' ' + self.first_name[0].upper()+"." +
                # TODO: Check if trimming of string is needed
                self.middle_name[0].upper() + ".")

    class Meta:
        permissions = (("can_edit_applicant_details",
                       "Edit Applicant details"),)


class Publication(models.Model):
    position_num = models.IntegerField(default=0)
    # TODO: Might need to adjust this

    applicant = models.ForeignKey(
        Applicant, on_delete=models.RESTRICT, null=True, related_name="publications")

    pub_title = models.CharField(max_length=150)
    abstract = models.TextField(blank=True)
    document_path = models.CharField(max_length=200, blank=True)
    publication_type = models.CharField(
        max_length=30,
        choices=PUBLICATION_TYPES,
        default='Select',
        help_text='Type of Publication'
    )
    percent_contribution = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    author_position = models.IntegerField()
    citation_text = models.CharField(max_length=50, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        if len(self.pub_title) > 20:
            title_ellipses = self.pub_title + "..."
            return title_ellipses
        else:
            return self.pub_title

    class Meta:
        permissions = (("can_edit_publication_list", "Edit Publication List"),)


class Assessor(models.Model):
    """Model representing assessor information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=20)
    applicants_assigned = models.ManyToManyField(
        Applicant, help_text="Select Applicants", blank=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """String for representing the Model object.
        Return the surname and initials in format SURNAME F.M."""
        return (self.last_name.capitalize()+' ' + self.first_name[0].upper()+"." +
                # TODO: Check if trimming of string is needed
                self.middle_name[0].upper() + ".")

    class Meta:
        permissions = (("can_edit_assessor_details", "Edit Assessor details"),)


class AssessedPublication(models.Model):
    # Model representing the assessments per publication for each assessor
    assessor = models.ForeignKey(
        # TODO: Might have problems with ondelete
        Assessor, on_delete=models.RESTRICT, null=True)
    applicant = models.ForeignKey(
        Applicant, on_delete=models.RESTRICT, null=True)
    publication = models.ForeignKey(
        Publication, on_delete=models.RESTRICT, null=True)
    score = models.DecimalField(decimal_places=1, max_digits=3)
    review = models.TextField()

    def __str__(self):
        # String for representing the Model object.
        return str(self.id)

    class Meta:
        permissions = (("can_edit_publication_assessment",
                       "Edit Publication Assessment"),)
