# Recommendation model
(Lucas Hoek - 220216) - 23/04/2026 
In deze branch bevindt zich de uiteindelijke prototype van het Recommendation model. Dit model is ontwikkeld 
In totaal bestaat uit meerdere onderdelen: 
### 1: de Mastra applicatie (Orisha-sales-agent)
deze folder beheert de TypeScript code om te zorgen dat de Mastra Agent functioneert. Bevat ook een brug naar de code om de tool te laten functioneren.
### 2: het recommendation tool (Recommender.py)
Hierin bevindt zich de tool waarmee de LLM-chatbot mee communiceert. Het maakt gebruik van de aritfacts files en AI-model om een top 5 lijst te creëren van een gegeven klanten-id.

### 3: artifacts & ncf_model.onnx
Deze twee bestanden zijn nodig om te functioneren. Het bevat de getrainde twee modellen om een aanbeveling aan te maken. Mocht deze bestanden niet aanwezig zijn kan er een nieuwe set aan bestanden door het bestand `example-generated.ipynb` te runnen. 

## Installation guide: 
Er zijn een aantal processen die uitgevoerd moet worden om te zorgen dat de code werkt.

### 1: Conda
Voor het ontwikkelen is anaconda gebruikt. De keuze voor deze applicatie is 

### 2: environments.yaml
Dit bestand defineert de omgeving waarin gewerkt wordt om het project te laten functioneren. het bevat informatie waaronder: 
- De python versie dat gebruik is
- De afhankelijkheden (dependencies)

Voor dit project is conda gebruikt voor het beheren van omgevingen. Om de environment aan te maken en te gebruiken, gebruik de volgende code: 
```
conda env create -f environments.yaml
conda activate orisha-recommendation-model
```
### 3: requirements.txt
dit bestand bevat alle python libraries die gebruikt zijn. Om deze te installeren gebruik je de volgende code:
```
pip install -r requirements.txt
```
### 4: Mastra
Mastra is het Typescript framework dat gebruikt is voor de sales agent. Dit moet apart geïnstalleerd worden. Om mastra te installeren, voer de volgende code uit in de nieuwe environment: 
```
cd Orisha-Sales-Agent
```
en voer daarna uit: 
```
npm install mastra
```
navigeer daarna uit de folder met 
```
cd..
```

### 5: Environment variables en Google Key
Er is een Google API key gebruikt voor de chatbot. Om te zorgen dat de code kan functioneren moet er een .env bestand aangemaakt worden als deze nog niet aanwezig is.  Mocht deze key nog niet aanwezig zijn, volgt hieronder hoe de .env bestand eruit moet zien.
```
# add API key after the =
GOOGLE_API_KEY = 
#mastra internally needs to check GOOGLE_GENERATIVE_AI_API_KEY for the API key, so we set it to the same value as GOOGLE_API_KEY
GOOGLE_GENERATIVE_AI_API_KEY = ${GOOGLE_API_KEY}
```

### 6: Code
om de code uit te voeren is een .bat bestand aangemaakt. om de code te starten gebruik je de volgende code:
```
run.bat
```
vervolgens kan de sales agent getest worden op de volgende pagina: `http://localhost:4111/agents/sales-agent `
op deze pagina kan ook de tool getest worden.
Om een visuele front end te zien hoe het concept functioneel werkt, bekijk de volgende pagin: `http://localhost:5000/` 


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

## 
