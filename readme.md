# Recommendation model
(Lucas Hoek - 220216) - 23/04/2026 
In deze branch bevindt zich de uiteindelijke prototype van het Recommendation model. Dit model is ontwikkeld 
In totaal bestaat het recommendation model uit twee onderdelen: 
### 1: het trainingsproces (Train.py)
Het trainingsproces is het proces van ophalen, trainen van een model en het uiteindelijk opslaan van een functioneel model dat voorspellingen kan maken. 
### 2: het recommendation model (Recommendation.py)
Hierin bevindt zich het proces van het ontvangen van een request om een aanbeveling te maken en het terugsturen van een ranglijst van producten. 




## Proces en Methodieken
Het proces van het maken van een aanbeveling gebeurt op op de volgende wijze. 
Het maken van een aanbeveling wordt uitgevoerd op de **Weighted hybrid** methode, een veelgebruikte methode die ook gebruikt wordt bij bedrijven zoals Spotify, Bol.com en Netflix voor het maken van aanbevelingen. 
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
Om problemen zoals een "cold start" te voorkomen worden beiden modellen gebruikt en gezamelijk een score berekend om de uiteindelijke aanbeveling te maken.

Wanneer er een aanbeveling gemaakt wordt voor een klant, zal er een Top 5 voorspelling gemaakt worden door beide het Neuro Collaborative filter en door het content based filter. Bij het genereren van deze top 5 wordt bij beide processen een score voor elk product ontwikkeld op basis van de minimum en maximum scores die elk model kan scoren. dit is een cijfer tussen 0 en 1 waarbij 1 de hoogst mogelijke score is. 

Bij het berekenen van de uiteindelijke score wordt er een parameter gegeven die voortgaand is vastgesteld die bepaetald hoeveel invloed elk model heeft op het eindresultaat. Deze is berekend op basis van de resultaten tijdens het trainen. Uideindelijk wordt de parameter vermenigvuldigd met de scores van de twee modellen en bij elkaar opgeteld om een uiteindelijke top 5 te bereken voor de gebruiker.

Uiteindelijk worden de aanbevelingen terug gestuurd naar de sales agent, waarbij er samen met deze informatie een uiteindelijke response gemaakt kan worden.

