from django.db.models import Count, Sum
from .models import Tool, ToolMovement

def get_dashboard_stats(user):
    """Статистика для дашборда с учётом прав доступа"""
    queryset = Tool.objects.all()
    
    # Прорабы видят только инструменты на своих участках
    if user.role == 'foreman' and user.department:
        queryset = queryset.filter(location__name__icontains=user.department)
    
    stats = {
        'total': queryset.count(),
        'in_stock': queryset.filter(status='in_stock').count(),
        'issued': queryset.filter(status='issued').count(),
        'verification': queryset.filter(status='verification').count(),
        'total_value': queryset.aggregate(Sum('residual_cost'))['residual_cost__sum'] or 0,
    }
    
    # Последние 5 операций
    recent = ToolMovement.objects.select_related('tool', 'employee', 'performed_by').order_by('-operation_date')[:5]
    stats['recent_movements'] = recent
    
    return stats