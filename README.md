# trOPP Installation

Install paver
```
pip install paver
pip install -r requirements.txt
```

Install neo4j 
```
apt-get install neo4j
```

Go to http://localhost:7474 update the default password. 
Populate database with cypher script provided in cypher-scripts/script
Update trOPP/settings.py file - change neo4j database password to the one you set
```
NEO4J_PASSWORD = 
```
Setup Django database:
```
python trOPP/manage.py makemigrations
python trOPP/manage.py migrate
python trOPP/manage.py bootstrap
python trOPP/manage.py runserver
```

Go to http://localhost:8000 to see the app


