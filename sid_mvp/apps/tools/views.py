# apps/tools/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from .models import Tool, ToolMovement, Location, ToolCategory
from .forms import ToolForm, IssueReturnForm
from .utils import get_dashboard_stats


def is_authorized(user):
    return user.is_authenticated


@login_required
def dashboard(request):
    stats = get_dashboard_stats(request.user)
    return render(request, 'tools/dashboard.html', {'stats': stats})


@login_required
def tool_list(request):
    tools = Tool.objects.select_related('category', 'location').all()
    
    # Фильтрация по правам
    if request.user.role == 'foreman' and request.user.department:
        tools = tools.filter(
            Q(location__name__icontains=request.user.department) | 
            Q(status='in_stock')
        )
    
    # Поиск
    query = request.GET.get('q')
    if query:
        tools = tools.filter(
            Q(name__icontains=query) | 
            Q(inventory_number__icontains=query) |
            Q(brand__icontains=query)
        )
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status:
        tools = tools.filter(status=status)
    
    return render(request, 'tools/tool_list.html', {'tools': tools, 'query': query})


@login_required
@user_passes_test(lambda u: u.can_manage_tools)
def tool_create(request):
    if request.method == 'POST':
        form = ToolForm(request.POST)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.generate_qr_code()
            tool.save()
            messages.success(request, f'Инструмент {tool.inventory_number} зарегистрирован')
            return redirect('tools:tool_detail', pk=tool.pk)
    else:
        form = ToolForm()
    return render(request, 'tools/tool_form.html', {'form': form, 'title': 'Новый инструмент'})


@login_required
def tool_detail(request, pk):
    tool = get_object_or_404(Tool.objects.select_related('category', 'location'), pk=pk)
    movements = tool.movements.select_related('employee', 'performed_by').order_by('-operation_date')[:10]
    
    # Проверка прав на операцию
    can_operate = request.user.can_issue_return if tool.status in ['in_stock', 'issued'] else False
    
    return render(request, 'tools/tool_detail.html', {
        'tool': tool, 
        'movements': movements, 
        'can_operate': can_operate
    })


@login_required
@user_passes_test(lambda u: u.can_manage_tools)
def tool_edit(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    if request.method == 'POST':
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные обновлены')
            return redirect('tools:tool_detail', pk=tool.pk)
    else:
        form = ToolForm(instance=tool)
    return render(request, 'tools/tool_form.html', {'form': form, 'title': 'Редактирование'})


@login_required
@user_passes_test(lambda u: u.can_issue_return)
def tool_operation(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    
    if tool.status == 'written_off':
        messages.error(request, 'Нельзя выполнить операцию со списанным инструментом')
        return redirect('tools:tool_detail', pk=pk)
    
    if request.method == 'POST':
        form = IssueReturnForm(request.POST, tool=tool)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.tool = tool
            movement.performed_by = request.user
            
            # Получаем тип операции
            operation_type = form.cleaned_data.get('operation_type')
            movement.operation_type = operation_type
            
            # Автозаполнение локаций и обновление статуса инструмента
            if operation_type == 'issue':
                movement.from_location = tool.location
                tool.status = 'issued'
                tool.location = movement.to_location
            elif operation_type == 'return':
                movement.to_location = tool.location  # Возврат всегда на склад
                tool.status = 'in_stock'
            
            tool.save(update_fields=['status', 'location', 'updated_at'])
            movement.save()
            
            messages.success(request, f'✅ Операция "{movement.get_operation_type_display()}" выполнена успешно')
            return redirect('tools:tool_detail', pk=tool.pk)
        else:
            # Выводим ошибки формы для отладки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        initial = {'employee': request.user if request.user.role == 'foreman' else None}
        form = IssueReturnForm(tool=tool, initial=initial)
    
    return render(request, 'tools/issue_return.html', {'form': form, 'tool': tool})


@login_required
@user_passes_test(lambda u: u.can_manage_tools)
def tool_write_off(request, pk):
    """
    Списание инструмента.
    Доступно только пользователям с правами управления инструментами.
    """
    tool = get_object_or_404(Tool, pk=pk)
    
    if tool.status == 'written_off':
        messages.warning(request, 'Инструмент уже списан')
        return redirect('tools:tool_detail', pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        
        if not reason:
            messages.error(request, 'Необходимо указать причину списания')
            return render(request, 'tools/write_off.html', {'tool': tool})
        
        # Запоминаем текущее местоположение до изменения статуса
        old_location = tool.location
        
        # 1. Меняем статус и обнуляем стоимость
        tool.status = 'written_off'
        tool.residual_cost = 0
        tool.save(update_fields=['status', 'residual_cost', 'updated_at'])
        
        # 2. Создаем запись в истории движений
        ToolMovement.objects.create(
            tool=tool,
            employee=request.user,
            operation_type='write_off',
            from_location=old_location,
            to_location=None,
            performed_by=request.user,
            notes=f"Списание. Причина: {reason}"
        )
        
        messages.success(request, f'✅ Инструмент {tool.inventory_number} успешно списан')
        return redirect('tools:tool_detail', pk=pk)
    
    return render(request, 'tools/write_off.html', {'tool': tool})


@login_required
def qr_print(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    if not tool.qr_code:
        tool.generate_qr_code()
        tool.save()
    return render(request, 'tools/qr_print.html', {'tool': tool})