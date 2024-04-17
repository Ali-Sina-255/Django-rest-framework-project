from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey



class Tag(models.Model):
	lable  = models.CharField(max_length=255)


class TaggedItem(models.Model):
	# what tag applied to what object
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)	
	object_id = models.PositiveIntegerField()