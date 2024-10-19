# Potężny blockchain
Propozycja jak to zrobić:
1. Komunikacja jako zwykłe HTTP (szkic endpointów w main.py),
2. Propozycja implementacji bloków i liczenia hashów itd. w block.py (tam też jest przykład użycia na dole).

W zasadzie cała komunikacja to byłoby użycie *requests*, wywoływanie
- requests.get()
- requests.post()

z argumentami odpowiednimi. Jakieś opisy tego co endpointy powinny robić są w kodzie.