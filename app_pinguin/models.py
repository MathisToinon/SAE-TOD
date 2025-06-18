from django.db import models


class Iris(models.Model):
    CODE_IRIS = models.CharField(max_length=10,unique=True)
    LIB_IRIS = models.CharField(max_length=255)
    TYP_IRIS = models.CharField(max_length=50)
    GRD_QUART = models.CharField(max_length=100)
    DEPCOM = models.CharField(max_length=10)
    LIBCOM = models.CharField(max_length=255)
    UU2020 = models.CharField(max_length=10)
    REG = models.CharField(max_length=100)
    DEP = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.CODE_IRIS} ({self.LIB_IRIS}) - REG : {self.REG} - DEP : {self.LIB_IRIS}"


class Naf2(models.Model):
    CODE = models.CharField(max_length=5,unique = True,null=True, blank=True)
    LIBELLE = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.CODE} ({self.LIBELLE})"


class Electricite(models.Model):
    OPERATEUR  = models.CharField(max_length=100)
    ANNEE = models.CharField(max_length=100)
    FILIERE = models.CharField(max_length=100)
    IRIS_CODE = models.ForeignKey(Iris, to_field="CODE_IRIS", on_delete=models.SET_NULL, null=True, blank=True)
    CODE_CATEGORIE_CONSOMMATION = models.CharField(max_length=100)
    CODE_SECTEUR_NAF2 = models.ForeignKey(Naf2, to_field="CODE", on_delete=models.PROTECT,null=True, blank=True)
    CODE_GRAND_SECTEUR = models.CharField(max_length=100)
    CONSO = models.FloatField()
    PDL = models.FloatField()
    INDQUAL = models.FloatField()

    def __str__(self):
        return f"{self.OPERATEUR} - {self.ANNEE} - {self.IRIS_CODE} - {self.CONSO} - {self.PDL} - {self.INDQUAL}"


class Gaz(models.Model):
    OPERATEUR = models.CharField(max_length=100)
    ANNEE = models.CharField(max_length=100)
    FILIERE = models.CharField(max_length=100)
    IRIS_CODE = models.ForeignKey(Iris, to_field="CODE_IRIS", on_delete=models.SET_NULL, null=True, blank=True)
    CODE_CATEGORIE_CONSOMMATION = models.CharField(max_length=100)
    CODE_SECTEUR_NAF2 = models.ForeignKey(Naf2, to_field="CODE", on_delete=models.PROTECT,null=True, blank=True)
    CONSO = models.FloatField()
    PDL = models.FloatField()
    INDQUAL = models.FloatField()

    def __str__(self):
        return f"{self.OPERATEUR} - {self.ANNEE} - {self.IRIS_CODE} - {self.CONSO} - {self.PDL} - {self.INDQUAL}"
    
class Chaleur(models.Model):
    OPERATEUR = models.CharField(max_length=100)
    ANNEE = models.CharField(max_length=10)
    FILIERE = models.CharField(max_length=100)
    IRIS_CODE = models.ForeignKey(Iris, to_field="CODE_IRIS", on_delete=models.SET_NULL, null=True, blank=True)
    CONSO = models.FloatField()
    PDL = models.FloatField()

    def __str__(self):
        return f"{self.OPERATEUR} - {self.ANNEE} - {self.IRIS_CODE} - {self.CONSO} - {self.PDL}"