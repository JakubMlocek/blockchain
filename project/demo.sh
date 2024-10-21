#!/bin/bash

# Sprawdzamy, czy serwer blockchaina jest uruchomiony
echo "Sprawdzanie, czy usługa jest uruchomiona"
if curl -s http://localhost:1234/blocks > /dev/null; then
    echo "Usługa działa."
else
    echo "Usługa nie działa." 
fi

# Krok 1: Inicjowanie węzła
echo "Inicjowanie węzłów w sieci blockchain..."
curl -X POST http://localhost:1234/init/app1:5000
curl -X POST http://localhost:1234/init/app2:5000

# Krok 2: Wyświetlenie aktywnych węzłów
echo "Wyświetlanie aktywnych węzłów w sieci..."
curl -X GET http://localhost:1234/nodes
echo -e "\nLista aktywnych węzłów została wyświetlona.\n"
echo -e "\nWęzeły zostały zainicjowane.\n"

# Krok 3: Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node1:"
curl -X GET http://localhost:1234/blocks
echo -e "\nLista bloków w blockchainie została wyświetlona.\n"

# Krok 4: Wykopanie nowego bloku
echo "Kopanie nowego bloku z danymi przez node1:"
curl -X POST http://localhost:1234/mine -H "Content-Type: application/json" -d '{"data": "Tutaj dane dla blocku"}'
echo -e "\nNowy blok został wykopany i dodany do blockchaina.\n"

# Krok 5: Przeglądanie blockchaina
echo "Bloki w łańcuchu widziane przez node2 po wykopaniu bloku:"
curl -X GET http://localhost:1234/blocks
echo -e "\nLista bloków w blockchainie została wyświetlona.\n"

# Krok 6: Dodanie bloku z innego węzła (symulacja)
echo "Symulacja dodania bloku z innego węzła..."

curl -X POST http://localhost:1234/store_data -H "Content-Type: application/json" -d '{
    "data": "Dane z innego węzła",
    "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
    "hash": "b5d4045c49a1e50ef6b2f83c8e07a3b9932cc705f3e7d46abf738effa1c4d1d1",
    "nonce": 283
}'
echo -e "\nBlok z innego węzła został dodany do lokalnego blockchaina.\n"

echo "Demonstracja zakończona."