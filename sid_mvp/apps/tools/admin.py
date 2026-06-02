from django.contrib import admin
from .models import Tool, ToolMovement, Location, ToolCategory

@admin.register(ToolCategory)
class ToolCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name', 'address']

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['inventory_number', 'name', 'brand', 'category', 'status', 'location', 'residual_cost']
    list_filter = ['status', 'category', 'location']
    search_fields = ['name', 'inventory_number', 'brand', 'model']
    readonly_fields = ['qr_code', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.qr_code:
            obj.generate_qr_code()
        super().save_model(request, obj, form, change)

@admin.register(ToolMovement)
class ToolMovementAdmin(admin.ModelAdmin):
    list_display = ['operation_date', 'tool', 'operation_type', 'employee', 'performed_by']
    list_filter = ['operation_type', 'operation_date']
    readonly_fields = ['operation_date', 'performed_by']
    
    def save_model(self, request, obj, form, change):
        if not obj.performed_by_id:
            obj.performed_by = request.user
        super().save_model(request, obj, form, change)