from wagtail.models import Page
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet # transforme le modèle django classique en snippet wagtail


class CoachPage(Page):
    photo = models.ForeignKey(
        "wagtailimages.Image",  #pointer vers  la bliblio d'images wagtail
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  #si l'img est supprimé, le champs redevient vide
        related_name="+"
    )

    content_panels = Page.content_panels + [
        FieldPanel("photo")
    ]

@register_snippet # je déclare mon décorateur snippet
class Cour(models.Model):  # dit à wagtail que ce modèle doit apparaitre dans l'admin et être administrateur avec form

    name = models.CharField(max_length=100)
    date = models.CharField(max_length=100,blank=True)
    level = models.CharField(max_length=100,blank=True)
    description = models.TextField(max_length=255,blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("date"),
        FieldPanel("level"),
        FieldPanel("description")
        #liste les champs visible dans le form admin de ce snippet "panels" et pas content panel parce qu'un snippet n'est pas une page -> ca exclu donc le slug, le btn publié etc

    ]

    def __str__(self):
        return self.name
    
@register_snippet
class Formule(models.Model):

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6,decimal_places=2,help_text="ex: 12.50 pas plus que 6 chiffres")
    description = models.TextField(max_length=255,blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("price"),
        FieldPanel("description")
            ]

    def __str__(self):
        return self.name

class CoursPage(Page):
    def get_context(self, request): #get context permet de construire les données envoyées à cette page 
        context = super().get_context(request)
        context["cours_list"] = Cour.objects.all()
        context["formule_list"] = Formule.objects.all()
        return context # renvoie les données complet

@register_snippet
class faq(models.Model):

    question = models.TextField(max_length=255)
    answer = models.TextField(max_length=255)
    order = models.IntegerField(default=0) # stocke la position de la fiche : le glisser-déposer de l'admin y enregistre l'ordre, ne pas le supprimer
    sort_order_field = "order" #Elle indique à Wagtail quel champ utiliser pour ranger les fiches. Ce n'est pas un champ de la base de données

    panels = [
        FieldPanel("question"),
        FieldPanel("answer")
    ]

    def __str__(self):
        return self.question

class ContactPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context["faq_list"] = faq.objects.order_by("order") # envoie les fiches au template, triées selon le champ order (du plus petit au plus grand), contrairement à .all() qui ne précise aucun tri
        return context