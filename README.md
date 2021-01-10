# Home Library

Home Library to domowa biblioteczka dzięki której możesz zapisywać swoje ulubione książki

Zainstaluj wszystkie niezbędne dodatki używając pip
```
pip install -r requirements.txt
```

## Uruchomienie

Uruchomienie serwera
```
python home_library.py
```
Otwórz w przeglądarce adres http://localhost:5000 , możesz przeglądać swoje książki, edytować je, sortować czy też usuwać. Kliknięcie na daną pozycję spowoduje wyświetlenie kilku podstawowych informaji o książce oraz krótki jej opis.

## REST Api

Biblioteka domowa jest wyposażona w REST Api do pobierania, tworzenia, edytowania i usuwania książek w
biblioteka korzystająca z żądań HTTP.


### GET

Użyj żądań GET, aby uzyskać wszystkie dane biblioteki lub informacje o określonej książce.

```python
import requests

# Getting the full library
requests.get("http://localhost:5000/api/v1/books")

# Specify url parameters to get a sorted copy of library
params = {
    "sort_key": "title", # or "author", "year", "pages"
    "sort_order": "asc" # or "desc"}
# Passing them to the call to requests.get
requests.get("http://localhost:5000/api/v1/books", params=params)

# Getting data from a specific book
book_id = 0
requests.get("http://localhost:5000/api/v1/books/%d" % book_id)
```

### POST

Użyj żądań POST, aby zapisać nowe książki w bibliotece i wysłać dane json.

```python
import json
import requests

# "genres" and "description" are optional and can be not specified
data = {
    "title": "Eragon",
    "author": "Christopher Paolini",
    "year": 2002, 
    "genres": [
        "fantasy", "dystopian", "" # specify up to three genres, leave empty strings
    ],
    "pages": 509,
    "description": """
        Eragon is the first book in The Inheritance Cycle
        by American fantasy writer Christopher Paolini.
    """}
# Making the request passing json data
requests.post("http://localhost:5000/api/v1/books", json=json.dumps(data))
```

### DELETE

Użyj żądań USUŃ, aby usunąć książki z biblioteki.

```python
import requests

book_id = 0
requests.delete("http://localhost:5000/api/v1/books/%d" % book_id)
```

### PUT

Użyj żądań PUT, aby zaktualizować określone książki w bibliotece.
```python
import json
import requests

book_id = 0
data = {
    "author": "Christopher Paolini",
    "year": 2002}
requests.put(
    "http://localhost:5000/api/v1/books/%d" % book_id,
    json=json.dumps(data))
```
