Deze Proof of Concept (PoC) branch is opgezet om verschillende soorten AI te onderzoeken en uiteindelijk een Recommendation Model te trainen dat gebruikt kan worden binnen het Orisha‑platform.
De PoC bevat alle benodigde configuratiebestanden, voorbeeldcode en gegenereerde artifacts die bij een training zijn ontstaan en nodig zijn om offline een aanbeveling te maken. 

De PoC‑branch bestaat uit de volgende onderdelen:

environments.yaml
Dit bestand defineert de omgeving waarin gewerkt wordt om het project te laten functioneren. het bevat informatie waaronder: 
- De python versie dat gebruik is
- De afhankelijkheden (dependencies)

Voor dit project is conda gebruikt voor het beheren van omgevingen. Om de environment aan te maken, gebruik de volgende code: 
```
conda env create -f environments.yaml
conda activate recommendation-env
```

requirements.txt
dit bestand bevat alle python libraries die gebruikt zijn. Om deze te installeren gebruik je de volgende code:
```
pip install -r requirements.txt
```

Example-generated.ipynb
dit bestand is de omgeving waarin onderzocht is welke aanbevelingsmodellen geschikt waren voor Orisha Commerce en bevat de uiteindelijke code voor het trainingsproces van een aanbevelingsmodel.
Het bestand is eerst gebruikt om verschillende AI modellen uit te testen en te configureren, Wanneer er een definitieve keuze van AI modellen was gekozen is het bestand omgezet tot een reeks code verantwoordelijk voor het trainen van het model.
Om de code uit te voeren, controleer eerst je in de correcte omgeving zit en alle libraries geïnstalleerd is.
Druk vervolgens op de "Run All" knop om een nieuw model te trainen.
Er is een cel aanwezig waarin de resultaten van het getrainde model is weergegeven. deze cel bevindt zich onder de cel verantwoordelijk voor het trainen van het model.


Artifacts folder
Het recommendation model bestaat uit twee onderdelen: het getrainde AI model voor collaborative filtering en een matrix van data voor content based filtering. 
Om deze componenten toe te voegen aan het prototype wordt het AI model gexporteerd tot een onnx file en de matrix wordt omgezet tot een artifact. 

