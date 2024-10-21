#!/bin/bash

#Sprawdzamy, czy serwer blockchaina jest uruchomiony

docker-compose down
docker-compose up --build -d

sleep 7

echo "Sprawdzanie, czy usługa jest uruchomiona"
if curl -s http://localhost:1234/blocks > /dev/null; then
    echo "Usługa działa."
else
    echo "Usługa nie działa." 
fi

#Inicjalizacja 3 wezłow
echo "Inicjowanie 3 węzłów w sieci blockchain..."
curl -X POST http://localhost:1234/init/app1:5000
curl -X POST http://localhost:1234/init/app2:5000
curl -X POST http://localhost:1234/init/app3:5000
echo -e "\n"

#Wyświetlenie aktywnych węzłów
echo "Wyświetlanie aktywnych węzłów w sieci..."
curl -X GET http://localhost:1234/nodes
echo -e "\n"


#Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node1:"
curl -X GET http://localhost:1234/blocks
echo -e "\n"

#Wykopanie nowego bloku przez node 1
echo "Kopanie nowego bloku z danymi przez node1:"
curl -X POST http://localhost:1234/mine -H "Content-Type: application/json" -d '{"data": "Pierwszy wykopany blok - node1"}'

#Wykopanie nowego bloku przez node 1
echo "Kopanie nowego bloku z danymi przez node1:"
curl -X POST http://localhost:1234/mine -H "Content-Type: application/json" -d '{"data": "Drugi wykopany blok - node1"}'
echo -e "\n"


sleep 3

#Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node1:"
curl -X GET http://localhost:1234/blocks

#Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node2:"
curl -X GET http://localhost:1235/blocks

#Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node3:"
curl -X GET http://localhost:1236/blocks
echo -e "\n"


#Wykopanie nowego bloku przez node 2
echo "Kopanie nowego bloku z danymi przez node2:"
curl -X POST http://localhost:1235/mine -H "Content-Type: application/json" -d '{"data": "Trzeci wykopany blok - node2"}'
echo -e "\n"

sleep 5

#Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node1:"
curl -X GET http://localhost:1234/blocks

#Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node2:"
curl -X GET http://localhost:1235/blocks

#Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node3:"
curl -X GET http://localhost:1236/blocks



docker-compose down
