from wagtail.models import Page
from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet # transforme le modèle django classique en snippet wagtail
from modelcluster.fields import ParentalKey
#ParentalKey : comme un ForeignKey, mais pensé pour les contenus "enfants" d'une page
#(ici, les champs du formulaire appartiennent a une page Contact precise)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField


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

class CoursPage(Page):
    def get_context(self, request): #get context permet de construire les données envoyées à cette page 
        context = super().get_context(request)
        context["cours_list"] = Cour.objects.all()
        context["formule_list"] = Formule.objects.all()
        context["faq_list"] = faq.objects.order_by("order") # envoie les fiches au template, triées selon le champ order (du plus petit au plus grand), contrairement à .all() qui ne précise aucun tri
        return context # renvoie les données complet

class FormField(AbstractFormField):
    # AbstractFormField fournit deja tout ce qu'il faut pour decrire UN champ
    # quelconque (label, type de champ, obligatoire ou non...). On ajoute juste
    # le lien vers la page Contact. Les vrais champs (Nom, Email, Message) ne sont
    # PAS ecrits ici : ils seront crees comme des donnees, depuis l'admin (etape 5).
    page = ParentalKey(
        "ContactPage",
        on_delete=models.CASCADE,   # si la page Contact est supprimee, ses champs le sont aussi
        related_name="form_fields",
    )

class ContactPage(AbstractEmailForm):
    # On remplace Page par AbstractEmailForm : ContactPage reste une page (AbstractEmailForm
    # herite de Page), mais une page qui sait aussi envoyer un email a chaque reponse.
    intro = RichTextField(blank=True)          # texte affiche au-dessus du formulaire
    thankyoutext = RichTextField(blank=True)  # message affiche apres l'envoi
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        # InlinePanel : widget d'admin qui affiche la liste des FormField de cette page,
        # avec un bouton pour en ajouter, en retirer, ou changer leur ordre
        FieldPanel("thankyoutext"),
        FieldPanel("to_address"),    # l'email de Max, qui recevra chaque message
        FieldPanel("from_address"),  # l'adresse "expediteur" affichee sur l'email recu
        FieldPanel("subject"),       # le sujet de l'email envoye
    ]

@register_snippet
class Footer(models.Model):

    name = models.CharField(max_length=100)
    link = models.URLField()

    panels = [
        FieldPanel("name"),
        FieldPanel("link")
    ]

    def __str__(self):
        return self.name