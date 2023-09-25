from django.contrib import admin

from .models import Group, BroadcastMessage, Organisation, Location, Branch, BranchBroadcastHistory

admin.site.register(Organisation)
admin.site.register(Group)
admin.site.register(BroadcastMessage)
admin.site.register(Location)
admin.site.register(Branch)
admin.site.register(BranchBroadcastHistory)