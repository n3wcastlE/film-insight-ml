"""Build the Polish stage-one report from measured results and project.json."""
from pathlib import Path
import json, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'results/summary.json').read_text(encoding='utf-8'))
c=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
font_dir=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'
if (font_dir/'arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('Body',str(font_dir/'arial.ttf'))); pdfmetrics.registerFont(TTFont('BodyBold',str(font_dir/'arialbd.ttf')))
else:
    import matplotlib.font_manager as fm
    pdfmetrics.registerFont(TTFont('Body',fm.findfont('DejaVu Sans'))); pdfmetrics.registerFont(TTFont('BodyBold',fm.findfont(fm.FontProperties(family='DejaVu Sans',weight='bold'))))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TextPL',fontName='Body',fontSize=10,leading=15,spaceAfter=9,textColor=colors.HexColor('#243746')))
styles.add(ParagraphStyle(name='TitlePL',fontName='BodyBold',fontSize=30,leading=36,spaceAfter=20,textColor=colors.HexColor('#102c3c')))
styles.add(ParagraphStyle(name='HeadPL',fontName='BodyBold',fontSize=18,leading=23,spaceAfter=14,textColor=colors.HexColor('#102c3c')))
styles.add(ParagraphStyle(name='SubPL',fontName='BodyBold',fontSize=11,leading=15,spaceBefore=7,spaceAfter=8,textColor=colors.HexColor('#008577')))
styles.add(ParagraphStyle(name='SmallPL',fontName='Body',fontSize=8,leading=11,spaceAfter=7,textColor=colors.HexColor('#52636f')))
story=[]
def p(t,style='TextPL'): story.append(Paragraph(t,styles[style]))
def h(t): p(t,'HeadPL')
def sub(t): p(t,'SubPL')
def page(): story.append(PageBreak())
def image(name,w=480):
    from PIL import Image as PILImage
    path=ROOT/'results'/name
    with PILImage.open(path) as im: height=w*im.height/im.width
    story.append(Image(str(path),width=w,height=height)); story.append(Spacer(1,8))
def table(headers,rows,widths):
    data=[[Paragraph(str(x),styles['SmallPL']) for x in row] for row in [headers]+rows]
    t=Table(data,colWidths=widths,hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6f1ef')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor('#008577')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d6dfe2'))])); story.append(t); story.append(Spacer(1,10))
def fmt(x): return f'{x:.2f}'.replace('.',',')
p('UCZENIE MASZYNOWE / PROJEKT 1 / ETAP I','SubPL'); story.append(Spacer(1,32))
p('Film Insight','TitlePL')
p('Analiza opinii tekstowych i ocen liczbowych filmów','HeadPL')
p('Od języka recenzji do wzorców oceniania','SubPL')
p('Raport eksploracyjny • 29 października 2026','SmallPL')
story.append(Spacer(1,24))
table(['RECENZJE','OCENY','UŻYTKOWNICY'],[[s['reviews'],f"{s['ratings']:,}".replace(',',' '),s['users']]],[160,160,160])
sub('Cel projektu')
p('Zbadać, jakie cechy odróżniają pozytywne i negatywne recenzje filmów oraz jakie wzorce ujawniają oceny użytkowników. Projekt łączy analizę tekstu z analizą liczbową w ramach wspólnej tematyki kina.')
sub('Zakres tego raportu')
p('Źródła i jakość dwóch rzeczywistych zbiorów, analiza eksploracyjna, statystyka opisowa, pytania badawcze oraz pilotaż klasyfikacji sentymentu. Klasteryzacja, transformery i pełna ewaluacja są zaplanowane na dalsze etapy.')
team=c.get('team',[])
if team:
    p('Zespół i podział odpowiedzialności','SubPL')
    table(['Imię i nazwisko','ID','Zakres prac'],[[x['name'],x['id'],x['role']] for x in team],[160,70,250])
else:
    p('Informacje organizacyjne wymagają uzupełnienia przed oddaniem: imiona i nazwiska 4-5 członków zespołu, numery ID oraz rzeczywisty podział pracy.','SmallPL')
p('Repozytorium GitHub: '+(c.get('github_url') or 'adres wymaga uzupełnienia przed oddaniem.'),'SmallPL')
page(); h('01 / Pytania i projekt badania')
questions=[('P1. Język recenzji','Czy długość i słownictwo recenzji różnią się pomiędzy klasą pozytywną i negatywną? Hipoteza robocza: rozkłady długości nie są identyczne. Sprawdzenie: mediany, histogramy, test Manna-Whitneya i wielkość efektu.'),('P2. Struktura ocen','Jak wyglądają rozkład ocen oraz zależność średniej oceny filmu od liczby ocen? Sprawdzenie: statystyki opisowe, wykres rozrzutu i korelacja rang Spearmana.'),('P3. Gatunki','Jak różnią się średnie oceny między gatunkami? Analiza opisowa obejmuje gatunki z co najmniej 1000 ocen; uwzględnia wielogatunkowość filmów i zależność obserwacji.'),('P4. Predykcja','Czy TF-IDF z regresją logistyczną i liniowym SVM przewyższa klasyfikator większościowy? Miary: accuracy i macro-F1 na wydzielonym zbiorze testowym.'),('P5. Dalszy etap','Czy metody nienadzorowane wyodrębnią stabilne grupy preferencji, a transformer poprawi klasyfikację sentymentu? Odpowiedź wymaga kolejnych eksperymentów.')]
for title,body in questions: sub(title); p(body)
sub('Dwie perspektywy, dwa zbiory')
p('Jednostką obserwacji w Cornell jest recenzja, a w MovieLens - pojedyncza ocena użytkownika dla filmu. Zbiory nie są połączone rekord po rekordzie. Nie można na ich podstawie wyliczyć bezpośredniej zgodności tekstu recenzji z oceną MovieLens ani porównywać proporcji sentymentu jak populacyjnych ocen widowni.')
page(); h('02 / Dane i kontrola jakości')
table(['Cecha','Cornell polarity v2.0','MovieLens latest-small'],[['Pochodzenie','Bo Pang i Lillian Lee; rzeczywiste recenzje filmowe [1]','GroupLens, University of Minnesota; rzeczywiste oceny użytkowników [2]'],['Rozmiar',f"{s['reviews']} recenzji; po 1000 neg i pos",f"{s['ratings']} ocen; {s['users']} użytkowników; {s['movies_catalog']} filmów w katalogu"],['Zmienne','tekst, klasa neg/pos, identyfikator pliku','userId, movieId, rating, timestamp; tytuł i gatunki'],['Zakres','Cały korpus v2.0; bez podpróbkowania','Wszystkie rekordy archiwum small; bez podpróbkowania'],['Przetwarzanie','Tekst już wstępnie przetworzony przez autorów; tokenizacja regex do długości','Połączenie ocen z filmami po movieId; rozdzielenie list gatunków; rok z tytułu']],[75,200,205])
p(f"Cornell: {s['empty_texts']} pustych tekstów i {s['duplicate_texts']} dokładnych duplikatów. MovieLens: {sum(s['missing_ratings'].values())} braków w ratings.csv, {s['duplicate_rating_rows']} identycznych wierszy, {s['duplicate_user_movie']} powtórzeń par użytkownik-film i {s['unknown_movie_ids']} ocen bez filmu w katalogu. Roku wydania nie udało się odczytać dla {s['missing_year']} tytułów; nie uzupełniano go sztucznie.")
p(f"Okres ocen MovieLens (UTC): {s['rating_dates_utc'][0][:10]} - {s['rating_dates_utc'][1][:10]}. W analizie ocen występuje {s['movies_rated']} filmów; sam katalog zawiera również pozycje bez oceny.")
sub('Pochodzenie, licencje i odtwarzalność')
p('Archiwa pobrano z oryginalnych serwisów 29.10.2026. Ich rozmiary i SHA-256 zapisano w results/summary.json. Dołączono oryginalne README. MovieLens pozwala na niekomercyjną redystrybucję na warunkach swojego README. Cornell wymaga wskazania wersji i cytowania źródła; prawa do oryginalnych tekstów pozostają przy ich właścicielach. Skrypt download_data.py pobiera Cornell bezpośrednio od autorów.')
p('MovieLens latest-small to zbiór rozwojowy, a nie stabilny benchmark badawczy. W projekcie edukacyjnym zamrażamy konkretny pobrany plik za pomocą jego sumy kontrolnej.','SmallPL')
page(); h('03 / Tekst: długość i słownictwo')
image('01_text_lengths.png')
a=s['text_by_label']; table(['Klasa','N','Średnia słów','Mediana','Odch. stand.'],[[k,int(a[k]['count']),fmt(a[k]['mean']),fmt(a[k]['median']),fmt(a[k]['std'])] for k in ['neg','pos']],[80,55,115,100,130])
u=s['mann_whitney']; p(f"Test Manna-Whitneya: U = {u['U']:.0f}, p = {u['p']:.3g}; rangowa wielkość efektu (pos względem neg) = {fmt(u['rank_biserial_pos_minus_neg'])}. Efekt jest niewielki mimo małej wartości p. Test porównuje rozkłady/rangi; interpretacja jako różnicy median wymaga założeń o ich kształcie. Wynik jest eksploracyjny; zależność recenzji tego samego autora lub filmu może wpływać na wnioskowanie.")
image('02_words.png',440)
p('Źródło wykresów: pełny Cornell polarity v2.0. Liczba słów: tokeny regex \\b\\w+\\b. Słownictwo: CountVectorizer, angielskie stopwords, min_df=5, maks. 20 000 cech. Częstość słowa nie dowodzi jego przyczynowego wpływu na sentyment.','SmallPL')
page(); h('04 / Oceny: rozkład i popularność')
image('03_ratings.png')
p(f"Średnia ocena wynosi {fmt(s['rating_mean'])}, mediana {fmt(s['rating_median'])}, a odchylenie standardowe {fmt(s['rating_std'])} na skali 0,5-5. Mediana liczby ocen przypadających na film to {fmt(s['ratings_per_movie_median'])}. Rozkład popularności jest nierówny, dlatego średnia oparta na kilku ocenach jest znacznie mniej stabilna niż średnia oparta na setkach ocen.")
image('04_genres_popularity.png')
r=s['popularity_rating_spearman']; p(f"Korelacja Spearmana pomiędzy liczbą ocen a średnią oceną filmu: rho = {fmt(r['rho'])}, p = {r['p']:.3g}. Zależność jest bardzo słaba mimo małej wartości p; nie wnioskujemy o przyczynowości. Każdy film jest tu jedną obserwacją; małe liczby ocen zwiększają szum średnich.")
p('Źródło: MovieLens latest-small, wszystkie oceny z okresu 1996-2018. Gatunki: średnia ważona liczbą ocen; film wielogatunkowy występuje w kilku grupach. Grupy nie są niezależne, podobnie jak oceny jednego użytkownika. Różnice średnich mogą wynikać ze składu użytkowników, filmów i okresu; nie interpretujemy ich jako efektu gatunku.','SmallPL')
page(); h('05 / Pilotaż uczenia nadzorowanego')
p(f"Wstępnie porównano dwa modele: regresję logistyczną i liniowy SVM. Po usunięciu dokładnych duplikatów tekstu zastosowano jeden podział stratyfikowany 80/20: {s['pilot']['train_n']} recenzji treningowych i {s['pilot']['test_n']} testowych, random_state=42. TF-IDF jest dopasowywany wyłącznie na treningu wewnątrz Pipeline: unigramy i bigramy, min_df=2, do 50 000 cech, angielskie stopwords.")
table(['Model','Accuracy','Macro-F1'],[['Klasa większościowa','50,00%','nie oceniano']]+[[m['model'],f"{100*m['accuracy']:.2f}%",f"{m['f1_macro']:.4f}"] for m in s['pilot']['models']],[240,120,120])
image('05_pilot.png',440)
sub('Interpretacja i granice pilotażu')
p('Macierze pomyłek pokazują osobno poprawne i błędne rozpoznania obu klas. Oba modele mają ustalone parametry; nie prowadzono strojenia ani wyboru parametrów na teście. Jest to punkt odniesienia dla dalszych prac, a nie ostateczny ranking metod. Różnic na pojedynczym podziale nie traktujemy jako dowodu przewagi statystycznej.')
p('Dokładne duplikaty nie przekraczają granicy trening-test. Podział nie jest jednak grupowany po autorze lub filmie; współdzielone źródła i podobne recenzje mogą zawyżać wynik. W kolejnym etapie należy wykorzystać identyfikatory źródeł, jeśli da się je wiarygodnie odtworzyć, oraz walidację krzyżową na części treningowej. Cornell ma sztucznie zrównoważone klasy: nie odzwierciedla częstości opinii w całej widowni.')
page(); h('06 / Wnioski i dalsze eksperymenty')
pos_long=a['pos']['median']>a['neg']['median']
p(f"W badanym korpusie mediana długości recenzji {'pozytywnych' if pos_long else 'negatywnych'} jest wyższa. Wielkość efektu i wykresy są potrzebne do oceny znaczenia tej różnicy; sama mała wartość p nie wystarcza. Tekstowe modele bazowe zostały rzeczywiście uruchomione i ocenione na odłożonych danych.")
p('W MovieLens oceny i popularność filmów są nierównomierne. Interpretując rankingi gatunków, trzeba uwzględnić liczbę ocen i powtarzających się użytkowników. Oba zbiory umożliwiają analizę opinii o kinie, lecz nie stanowią wspólnej reprezentatywnej próby.')
table(['Następny eksperyment','Uzasadnienie i ewaluacja'],[['Nadzorowane: LR i liniowy SVM','Rozszerzyć wykonany pilotaż o walidację krzyżową na treningu i analizę błędów; test zachować do oceny końcowej.'],['Nienadzorowane: KMeans i NMF','KMeans: segmentacja użytkowników na podstawie profili preferencji po redukcji wymiaru. NMF: nieujemne tematy recenzji TF-IDF. Ocena: stabilność klastrów, silhouette i interpretowalność tematów; parametry dobierane bez etykiet testowych.'],['Transformer: DistilBERT','Porównać z klasycznymi modelami na tym samym podziale; dokumentować źródło modelu i możliwość kontaktu z benchmarkiem podczas pretreningu.'],['Interfejs','Dołączony lokalny panel pozwala przeglądać wyniki. Kolejny etap: predykcja sentymentu nowych tekstów i analiza segmentów.']],[170,310])
sub('Odtworzenie wyników')
p('Python 3.11 lub nowszy. Polecenia: pip install -r requirements.txt; python src/download_data.py; python src/analyze.py; python src/build_report.py. Panel: python src/serve.py, następnie http://localhost:8765. Szczegóły oraz sprawdzone wersje bibliotek znajdują się w README.md i requirements-lock.txt.')
sub('Źródła')
p('[1] Pang, B., Lee, L. (2004). A Sentimental Education: Sentiment Analysis Using Subjectivity Summarization Based on Minimum Cuts. ACL. Cornell polarity dataset v2.0. https://www.cs.cornell.edu/people/pabo/movie-review-data/','SmallPL')
p('[2] Harper, F. M., Konstan, J. A. (2015). The MovieLens Datasets: History and Context. ACM TiiS 5(4), 19. https://doi.org/10.1145/2827872. Dane i warunki: https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html','SmallPL')
def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#d6dfe2')); canvas.line(56,48,539,48)
    canvas.setFont('Body',8); canvas.setFillColor(colors.HexColor('#52636f')); canvas.drawString(56,34,'FILM INSIGHT  /  UCZENIE MASZYNOWE  /  ETAP I'); canvas.drawRightString(539,34,str(doc.page))
dest=ROOT/'reports/raport_etap_1.pdf'
SimpleDocTemplate(str(dest),pagesize=(595.28,841.89),rightMargin=56,leftMargin=56,topMargin=48,bottomMargin=64,title='Film Insight - raport etapu I',author='Zespół projektowy').build(story,onFirstPage=footer,onLaterPages=footer)
print(dest)
