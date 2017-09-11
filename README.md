# Komponent ping-store (aw-ping-store)

## TO-DO
* swagger: przenieść do definicji wspólne parametry
* dodać endpoint pings/{id} - zgodnie z tym, co na swaggerze
* dodać kody błędów
* dodać 200 do poprawnych wyników
* zmienić wyniki z text/html na json
* dodać warunki do targets/origins
* podzielić dodawanie warunków na dwie części (?)
* zmienić start/end na prefix (?, w niektórych kontekstach?)
* robić dobrego POST pings, GET pings-post może pozostać do testów
* sortowanie do sensownego działania limit i offset, opisać?
* czy DELETE ma działać dokłanie tak samo jak GET (nie będzie wtedy idempotentne)
* użycie poprawnych metod HTTP
* zapisywanie jednego pinga
* napisać ping-probe
* odczytywanie agregatów z pingów surowych
* automatyczna agregacja
* pamięć sond na wypadek przerwy w połączeniu
* testy jednostkowe ???czy to ma sens
* doczytać i potestować  (dziwne: udały się konkurencyjne zmiany)
zachowanie bazy sqlite przy jednoczesnych zapisach i odczytach tych samych rekordów, przeanalizować sytuacje równoległości w przypadkach użycia komponentu ping-store  

## Opis komponentu

Przechowuje informacje o wynikach wykonanych pingów.
Każdy wynik składa się z:
* **id** (unikalne, nadawane przez magazyn, nie podawać przy wstawianiu)
* **time** (czas wykonania testu w formacie tekstowym YYYYMMDDHHMMSS - porządek leksykograficzny pozwala porównywać tekstowo z prefiksami oznaczającymi grubsze jednostki czasu)
* **origin** (określenie miejsca, z którego ping był wykonany)
* **target** (bo można badać wiele różnych hostów)
* **success** (0/1 w zależności od tego czy ping doszedł do skutku, w zadanym czasie granicznym)
* **rtt** (liczba milisekund RTT, None jeśli ping nie był skuteczy)


## Pojedyncze pingi

### Wstawianie wyników ping

```
POST ping-store/pings
>>> {timestamp:"20170903175923", origin:"A8", target:"onet.pl", success:1, rtt:32}
<<< id
```
? czy takie cudzysłowy w JSON?

Wyniki można wstawiać z opóźnieniem i nie w kolejności.
Jeśli opóźnienie jest duże, próbka może być odrzucona (komunikat błędu czy ciche odrzucenie?).
Nie ma wstawiania wielu próbek na raz.

### Pobieranie wyników ping

```
GET ping-store/pings			
>>> [{id:456, time:"20170903175923", ...}, {}, {}, ...]						
```

!!! inne podejście do zapytania po id
```
GET ping-store/pings/{id}
```
```
GET ping-store/pings?limit=N     # N kolejnych ostatnich wg czasu zapisów (domyślnie 10)
GET ping-store/pings?offset=M     #z pominięciem M pierwszych (domyślnie 0)
GET ping-store/pings?origin=A8
GET ping-store/pings?target=192.168.2.1
GET ping-store/pings?start=20180801     # od tego momentu tak
GET ping-store/pings?end=20180715     # od tego momentu nie
GET ping-store/pings?origin=A8&start=20180801&end=20180915
```

### Zapisane pingi tworzą automatyczne słowniki

```
GET ping-store/origins
>>> [ "A8", "RaspPi" ]

GET ping-store/targets			
GET ping-store/targets?origin=A8
GET ping-store/targets?origin=A8&end=20180903
```

### Usuwanie wyników ping

```
DELETE ping-store/pings/{id}
DELETE ping-store/pings?limit=N
DELETE ping-store/pings?offset=M
DELETE ping-store/pings?id=367
DELETE ping-store/pings?origin=A8
DELETE ping-store/pings?target=192.168.2.1
DELETE ping-store/pings?start=20180801
DELETE ping-store/pings?end=20180715
DELETE ping-store/pings?origin=A8&start=20180801&end=20180915
```

## Wyniki agregowane

### Tworzenie agregatów

Można mieć wiele agregatów za ten sam okres?
Można agregować agregaty?
A może agreagowanie nie powinno być zlecane tylko dziać się automatycznie?
Agregaty można robić też z dancyh surowych na bieżąco np. za pomocą widoków - zajmują więcej miejsca.
A może widoki połączą dane surowe i zagregowane (może wymagać transakcyjnej agregacji).

Możliwe agregaty: minuta, godzina, doba

ping-store/days&date=		-> JSON { start:, end:, expected:(liczba próbek), actual:(liczba próbek), avg... }
ping-store/days			- lista dni -> { 2017-08-20, 2018-08-21, ... }   "20170820"
ping-store/days?date=20170824 albo start=20170824&end=20170825 (wymaga tworów typu +1 różnych poziomach}


### Pobieranie agregatów

```
ping-store/days
<<< [ "20170801", "20170802", "20170803", ...]

ping-store/days/20170801
<<< { start:"20170801000000", end:"20170802000000", expected:86400, actual:84354, avg_succes:0.98, avg_time:23.54 }
```

```
ping-store/hours
ping-store/hours/2017080119
ping-store/minutes
ping-store/minutes/201708011934
```

?Czy agregaty mogą dostać dokładniejszy czas? Chyba tak, będzie zwyczajne porównanie?

> Niezależne agregaty mogą być niezależnie tworzone (automatycznie wg konfiguracji), pobierane i kasowane (automatycznie wg konfiguracji).
> Zakończone minuty są agregowane do minut. ALE KIEDY? A JEŚLI DOJDZIE SPÓŹNIONA DANA? AUMOTYCZNA AKTUALIZACJA?
> Zakończone godziny - do godzin.
> Zakończone doby - do dni.
> Można też agregować z opóźnieniem, a agregaty robić z danych surowych.
> Albo: agregować dane po X dniach. Bardziej spóźnione próbki odrzucać przy próbe wstawienia.
> A może agregować tylko dni (po X dniach), a reszta tylko w postaci danych surowych (wtedy minuty i godziny zawsze z surowych danych, a dni z agregatów i surowych)


### Usuwanie agregatów

Automatyczne czy ręczne?

> kombinacja (wymagane jednoczesne spłenienie) poniższych warunków
> wg czasu - starsze niż (start ts<=s), młodsze niż (end ts<e)
> wg źródła - równość (origin)
> wg celu - równość (target)
> DELETE ping-store/aggregates?start=20170823&target=10.0.2.3
