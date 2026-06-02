from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw

User = get_user_model()

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'locations'
        verbose_name = 'Местонахождение'
        verbose_name_plural = 'Местонахождения'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ToolCategory(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'tool_categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Tool(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'На складе'),
        ('issued', 'Выдан'),
        ('verification', 'На поверке'),
        ('written_off', 'Списан'),
    ]
    
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    inventory_number = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(ToolCategory, on_delete=models.PROTECT)
    
    purchase_date = models.DateField()
    initial_cost = models.DecimalField(max_digits=12, decimal_places=2)
    residual_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tools'
        verbose_name = 'Инструмент'
        verbose_name_plural = 'Инструменты'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.inventory_number})"
    
    def generate_qr_code(self):
        """Генерация крупного читаемого QR-кода"""
        qr = qrcode.QRCode(version=1, box_size=20, border=4)
        qr_data = f"{self.inventory_number}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Добавляем текст с инвентарным номером под QR
        border = 40
        img_with_text = Image.new('RGB', (img.size[0], img.size[1] + border), 'white')
        img_with_text.paste(img, (0, 0))
        draw = ImageDraw.Draw(img_with_text)
        draw.text((img.size[0]//2, img.size[1] + 10), self.inventory_number, 
                 fill='black', anchor='mt', font_size=20)
        
        buffer = BytesIO()
        img_with_text.save(buffer, format='PNG')
        
        filename = f"qr_{self.inventory_number}.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        buffer.close()
        return filename

class ToolMovement(models.Model):
    OPERATION_TYPES = [
        ('issue', 'Выдача'),
        ('return', 'Возврат'),
        ('transfer', 'Передача'),
        ('write_off', 'Списание'),
    ]
    
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='movements')
    employee = models.ForeignKey(User, on_delete=models.PROTECT)
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='from_movements')
    to_location = models.ForeignKey(Location, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='to_movements')
    
    operation_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT, 
                                    related_name='performed_movements')
    
    class Meta:
        db_table = 'tool_movements'
        verbose_name = 'Операция'
        verbose_name_plural = 'Движение инструментов'
        ordering = ['-operation_date']
    
    def __str__(self):
        return f"{self.get_operation_type_display()}: {self.tool.inventory_number} ({self.operation_date.strftime('%d.%m.%Y')})"