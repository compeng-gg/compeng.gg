from django.contrib import admin
from .models import (
    QuercusToken,
    QuercusUser,
)

@admin.register(QuercusToken)
class QuercusTokenAdmin(admin.ModelAdmin):
    pass

@admin.register(QuercusUser)
class QuercusUserAdmin(admin.ModelAdmin):
    pass
