from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField()
    image = models.URLField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="news_items")
    views = models.IntegerField(default=0)
    publish_time = models.DateTimeField()

    class Meta:
        ordering = ["-publish_time", "-id"]
        indexes = [
            models.Index(fields=["category"], name="news_category_idx"),
            models.Index(fields=["publish_time"], name="news_publish_idx"),
        ]

    def __str__(self):
        return self.title

