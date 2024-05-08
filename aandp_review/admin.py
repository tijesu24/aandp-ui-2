from django.contrib import admin

# Register your models here.
from .models import Applicant, AssessedPublication, Publication, Assessor
# , AssessedPublication

# admin.site.register(Applicant)
admin.site.register(Publication)
admin.site.register(Assessor)
# admin.site.register(AssessedPublication)

# Add inlines


class PublicationInline(admin.TabularInline):
    model = Publication
    extra = 0


class ApplicantInline(admin.TabularInline):
    model = Applicant
    extra = 0


class AssessedPublicationInline(admin.TabularInline):
    model = AssessedPublication
    extra = 0


@admin.register(Applicant)
# Def the Applicant admin class
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name',
                    'promotion_year', 'position_applying_to')
    inlines = [PublicationInline]


@admin.register(AssessedPublication)
# Def the AssessedPubs admin class
class AssessedPublicationAdmin(admin.ModelAdmin):
    list_display = ('publication', 'applicant', 'assessor', 'score')
    # inlines = [PublicationInline]
