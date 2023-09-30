from django.db import models
from django.urls import reverse

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    description = models.TextField(max_length=255,blank=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        # changes the table name from its default name
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    # gets the url of a given category (known as slug) when called in store\urls.py using products_by_category
    def get_url(self):
        return reverse('products_by_category',args=[self.slug])

    def __str__(self):
        return self.category_name