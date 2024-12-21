from django.contrib import admin
from .models import User, Organization, Cluster, Deployment

admin.site.register(User)
admin.site.register(Organization)
admin.site.register(Cluster)
admin.site.register(Deployment)
