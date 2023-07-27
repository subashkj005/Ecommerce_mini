from django.db import models

from products.models import Category


class Offers(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    is_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Offers'
    def __str__(self):
        return self.name

