from django.contrib import admin
from .models import Candidate, CandidatePost, CandidateEvent

admin.site.register(Candidate)
admin.site.register(CandidatePost)
admin.site.register(CandidateEvent)
