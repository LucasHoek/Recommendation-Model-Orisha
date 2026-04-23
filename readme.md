# Recommendation model
(Lucas Hoek - 220216) - 23/04/2026 
In deze branch bevindt zich de uiteindelijke prototype van het Recommendation model. Dit model is ontwikkeld 
In totaal bestaat het recommendation model uit twee onderdelen: 
### 1: het trainingsproces (Train.py)
Het trainingsproces is het proces van ophalen, trainen van een model en het uiteindelijk opslaan van een functioneel model dat voorspellingen kan maken. 
Er w
### 2: het recommendation model (Recommendation.py)
Hierin bevindt zich het proces van het ontvangen van een request om een recommendation te maken en het terugsturen van een ranglijst van producten. 




## Proces en Methodieken
Het proces van het maken van een recommendation gebeurt op op de volgende wijze. 
Het maken van een recommendation wordt uitgevoerd op de **Weighted hybrid** methode, een veelgebruikte methode die ook gebruikt wordt bij bedrijven zoals Spotify, Bol.com en Netflix voor het maken van aanbevelingen. 
het wordt uitgevoerd op basis door twee verschillende processen: Collaborative Filtering en Content based filtering, Uit deze twee processen wordt er een aanbevolingsscore berekend, en word op basis van de score van deze twee processen een uiteindeljk combineerde aanbeveling gemaakt.

### Collaborative Filtering
Collaborative Filtering is een salesproces waarbij er aanbevelingen gemaakt wordt voor een persoon op basis van analyse en het gedrag van andere klanten. Het idee van collaborative filtering is om klanten met een vergelijkbaar gedrag te zoeken en op basis van dat gedrag een aanbeveling te maken.
#### Voorbeeld:
Jij en andere mensen hebben fiets Y gekocht.
Andere klanten vonden ook fiets X gekocht → fiets X wordt aan jou aangeraden.

Binnen dit prototype is er de keuze gemaakt om gebruik te maken van een **Neuro Collaborative Filter** De reden dat dit is toegepast is om  in het proces het mogelijk te maken om op beide item- en gebruikersniveau patronen te herkennen. 

### Content based Filtering
Content based filtering is wanneer je aanbevelingen maakt op basis van eigen voorkeuren en op herkenbare items. 
#### Voorbeeld
Jij hebt eerder een fiets gekocht.
Een nieuwe fiets komt uit → deze wordt aan jou aangeraden.

Binnen deze prototype wordt dit proces uitgevoerd door woorden om te zetten tot numerieke waardes genaamd vectoren, en daarna  door middel van een matrix te bekeken wat de vergelijkbaarheid is tussen de twee woorden. 

## Hoe "hybride" een score wordt ontwikkeld
