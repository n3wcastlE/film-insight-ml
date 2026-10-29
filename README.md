# Film Insight

Analiza opinii tekstowych i ocen liczbowych filmów. Projekt z uczenia maszynowego, etap I, 29.10.2026.

## Szybki start

Sprawdzono na Pythonie 3.12.14. W katalogu projektu:

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python src/download_data.py
python src/analyze.py
python src/build_report.py
python src/serve.py
```

Panel: http://localhost:8765/dashboard.html. Serwer działa tylko lokalnie, bez kont i kluczy API. Zakończenie: Ctrl+C. Sam dashboard.html można otworzyć również bez serwera.

## Wykonane analizy

- Cornell: 2000 recenzji, po 1000 neg/pos, bez pustych tekstów i dokładnych duplikatów.
- Mediana długości: neg 595,5; pos 659 słów. Mann-Whitney p=4,57e-7; niewielki efekt rangowy 0,1303.
- MovieLens: 100 836 ocen od 610 użytkowników, 9742 filmy w katalogu, 9724 z oceną. Średnia 3,5016/5; mediana liczby ocen na film: 3.
- Popularność a ocena: Spearman rho=0,0396, bardzo słaba zależność pomimo p<0,001.
- TF-IDF + LogisticRegression: accuracy 81%, macro-F1 0,8098. TF-IDF + LinearSVC: 82,75%, macro-F1 0,8273. Baseline: 50% accuracy.

## Dane i odtwarzalność

1. Cornell polarity v2.0, Pang i Lee (2004): https://www.cs.cornell.edu/people/pabo/movie-review-data/
   Archiwum: https://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz
2. MovieLens latest-small, GroupLens: https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html
   Archiwum: https://files.grouplens.org/datasets/movielens/ml-latest-small.zip

Użyto całych zbiorów, bez podpróbkowania. Pobrano 29.10.2026. Rozmiary, SHA-256 i wersje bibliotek zapisano w results/summary.json. Skrypt download_data.py sprawdza sumy kontrolne i przerywa, jeżeli źródło zmieni archiwum. MovieLens small jest zbiorem rozwojowym, nie stałym benchmarkiem.

Warunki MovieLens dołączono w data/MovieLens_README.txt; wymagane cytowanie i zachowanie warunków niekomercyjnego użycia. Cornell pobiera się bezpośrednio od autorów; źródłowy pakiet do publikacji nie zawiera jego tekstów. Nie deklarujemy własnej licencji na cudze teksty. Oryginalne README Cornell znajduje się w archiwum.

## Metodologia i ograniczenia

Liczba słów: regex `\b\w+\b`. Najczęstsze słowa: CountVectorizer, angielskie stopwords, min_df=5. Pilotaż: usunięcie dokładnych duplikatów, stratyfikacja 80/20, seed=42. Pipeline dopasowuje TF-IDF wyłącznie na treningu (1-2-gramy, min_df=2, max_features=50000). LR max_iter=1500; LinearSVC; pozostałe parametry domyślne zapisanej wersji sklearn. Nie strojono modeli i nie wybierano parametrów na teście. Podział i przewidywania zapisano w CSV.

Zbiory nie są połączone rekord po rekordzie. Nie wnioskujemy o przyczynowości. Gatunki nakładają się; oceny tych samych użytkowników i recenzje tych samych autorów/filmów mogą być zależne. Testy są eksploracyjne, bez korekty wielokrotnych porównań. Pilotaż nie jest grupowany po autorach/filmach, co może zawyżać generalizację. Cornell ma sztucznie zrównoważone klasy.

## Zawartość

- src/: pobieranie, obliczenia, generowanie PDF i lokalny serwer.
- data/raw/: oryginalne archiwa; Cornell pobierany przy reprodukcji.
- results/: summary.json, CSV, podział, predykcje i pięć wykresów.
- reports/raport_etap_1.pdf: raport po polsku.
- dashboard.html: panel przeglądania wyników.
- project.json: dane organizacyjne do uzupełnienia.

## Zespół i podział odpowiedzialności

- Mykola Kostiuk (72256), lider: koordynacja i metodologia, integracja kodu i wyników, redakcja końcowa raportu, zarządzanie repozytorium.
- Ivan Vlasenko (71732): dane Cornell, kontrola jakości tekstów, analiza długości i słownictwa, wykresy i opis wyników tekstowych.
- Yehor Lysenko (71886): dane MovieLens, kontrola jakości ocen, analiza gatunków i popularności, wykresy i opis wyników liczbowych.
- Ivan Saltykov (71657): pilotaż LR/SVM, podział trening-test, metryki i analiza błędów, panel wyników i weryfikacja odtwarzalności.

Repozytorium: https://github.com/n3wcastlE/film-insight-ml

Dane organizacyjne są zapisane w project.json. Po ich zmianie ponownie uruchom `python src/build_report.py`. Podział określa odpowiedzialność członków zespołu za poszczególne części projektu.

## Oddanie

Termin etapu I: 30.10.2026, 23:59; Platon: jeden PDF z reports/raport_etap_1.pdf. Do utworzonego repozytorium prześlij zawartość projektu; .gitignore wyklucza archiwum Cornell, które odtwarza skrypt, a cechy i wyniki są dołączone. Pliki z tego pakietu nie zostały wysłane automatycznie na GitHub.

## Kolejne etapy (plan)

Walidacja krzyżowa na treningu i analiza błędów LR/SVM; KMeans dla preferencji użytkowników; NMF dla tematów recenzji; porównanie z DistilBERT; predykcje w interfejsie. Metody należy dostosować do materiału zajęć. Pakiet realizuje etap I z pilotażem klasyfikacji, nie wszystkie późniejsze etapy.

## Bibliografia

Pang, B., Lee, L. (2004). A Sentimental Education: Sentiment Analysis Using Subjectivity Summarization Based on Minimum Cuts. ACL.

Harper, F. M., Konstan, J. A. (2015). The MovieLens Datasets: History and Context. ACM TiiS 5(4), 19. https://doi.org/10.1145/2827872
