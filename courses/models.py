import os

from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.text import slugify

class Institution(models.Model):

    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if Offering.objects.filter(course__institution=self,
                                   active=False) \
                           .exists():
            return reverse('courses:archive_institution',
                            kwargs={'institution_slug': self.slug})
        raise NoReverseMatch(f'{self} has no archived offerings')

    class Meta:
        ordering = ['slug']

class Course(models.Model):

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=80)

    def __str__(self):
        return f'{self.title} ({self.name})'

    def get_absolute_url(self):
        if Offering.objects.filter(course=self, active=False).exists():
            return reverse('courses:archive_course', kwargs={
                'institution_slug': self.institution.slug,
                'course_slug': self.slug,
            })
        raise NoReverseMatch(f'{self} has no archived offerings')

    class Meta:
        ordering = ['slug']

class Offering(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    start = models.DateField()
    active = models.BooleanField()

    def __str__(self):
        return f'{self.name} {self.course}'

    def get_absolute_url(self):
        if self.active:
            return reverse('courses:course', kwargs={'course_slug': self.course.slug})
        else:
            return reverse('courses:archive_offering', kwargs={
                'institution_slug': self.course.institution.slug,
                'course_slug': self.course.slug,
                'offering_slug': self.slug,
            })

    class Meta:
        ordering = ['-start', 'slug']
