from django.contrib import admin
from .models import Mouse, Session
# Register your models here.



class SessionInline(admin.TabularInline):
    model = Session
    extra = 0

class MouseAdmin(admin.ModelAdmin):

    inlines = [SessionInline]

admin.site.register(Mouse, MouseAdmin)
