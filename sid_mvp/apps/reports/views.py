from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from apps.tools.models import Tool, ToolMovement

@login_required
def simple_report(request):
    """Простой отчёт о наличии"""
    tools = Tool.objects.select_related('category', 'location')
    
    # Фильтрация по правам
    if request.user.role == 'foreman' and request.user.department:
        tools = tools.filter(location__name__icontains=request.user.department)
    
    context = {
        'tools': tools,
        'by_status': Tool.objects.values('status').annotate(
            count=Count('id'), 
            value=Sum('residual_cost')
        ),
        'by_category': Tool.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('category__name'),
    }
    return render(request, 'reports/simple_report.html', context)