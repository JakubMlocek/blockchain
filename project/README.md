# Implementacja wlasnego blockchain

## Komunikacja jako HTTP (szkic endpointów w main.py),
    Cała komunikacja poprzez użycie
    - requests.get()
    - requests.post()

## Implementacja bloków itd. w block.py (przykład wykorzystania na dole.).

## Dostepne funkcjonalnosci:

Inicjalizacja nodów:
        
    curl -X POST http://localhost:1234/init/app1:5000

Wykopanie bloku:

    curl -X POST http://localhost:1234/mine -H "Content-Type: application/json" -d '{"data": "Tutaj dane dla blocku"}'

Przejrzenie bloków:

    curl -X GET http://127.0.0.1:1234/blocks

Przejrzenie konkretnego bloku

    curl -X GET http://127.0.0.1:1234/blocks/<id>

Dodawanie bloku otrzymanego od innego node:

    curl -X POST http://127.0.0.1:5000/store_data -H "Content-Type: application/json" -d '{
        "data": "Tutaj dane dla blocku",
        "prev_hash": "<prev_hash from mined block>",
        "hash": "<hash from mined block>",
        "nonce": <nonce>
}'


## Uruchomienie środowiska:

Aby uruchomic dwa przykladowe wezly nalezy w katalogu projektu skorzystac z narzedzia docker-compose:

    docker-compose up --build -d  

Następnie mozemy korzystac z zapewnianych funkcjonalnosci lub podejrzec ich demo za pomoca:

    ./demo.sh

Na koniec wylaczamy srodowisko:

    docker-compose down