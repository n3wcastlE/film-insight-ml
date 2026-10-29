"""Reproduce the exploratory analysis and classical NLP pilot. Run from any directory."""
from pathlib import Path
import hashlib, json, platform, re, tarfile, zipfile
import numpy as np
import pandas as pd
import scipy
from scipy.stats import mannwhitneyu, spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score, ConfusionMatrixDisplay

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.titleweight':'bold'})
COLORS=['#34495e','#009688']
def save(name):
    plt.tight_layout(); plt.savefig(OUT/f'{name}.png',dpi=160,bbox_inches='tight'); plt.close()
def main():
    rows=[]
    with tarfile.open(ROOT/'data/raw/review_polarity.tar.gz') as tar:
        for member in sorted(tar.getmembers(),key=lambda x:x.name):
            if member.isfile() and re.search(r'/(pos|neg)/.*\.txt$',member.name):
                rows.append({'file':member.name,'label':member.name.split('/')[-2], 'text':tar.extractfile(member).read().decode('utf-8',errors='replace')})
    reviews=pd.DataFrame(rows)
    assert len(reviews)==2000
    reviews['words']=reviews.text.str.findall(r"\b\w+\b").str.len()
    reviews['characters']=reviews.text.str.len()
    with zipfile.ZipFile(ROOT/'data/raw/ml-latest-small.zip') as z:
        ratings=pd.read_csv(z.open('ml-latest-small/ratings.csv'))
        movies=pd.read_csv(z.open('ml-latest-small/movies.csv'))
        license_text=z.read('ml-latest-small/README.txt').decode('utf-8')
    (ROOT/'data/MovieLens_README.txt').write_text(license_text,encoding='utf-8')
    movies['year']=pd.to_numeric(movies.title.str.extract(r'\((\d{4})\)\s*$')[0],errors='coerce')
    reviews[['file','label','words','characters']].to_csv(OUT/'review_features.csv',index=False)
    agg=ratings.groupby('movieId').rating.agg(['mean','count','std']).join(movies.set_index('movieId'))
    agg.to_csv(OUT/'movie_statistics.csv')
    genre=ratings.merge(movies[['movieId','genres']],on='movieId').assign(genre=lambda d:d.genres.str.split('|')).explode('genre')
    genres=genre.groupby('genre').rating.agg(['mean','count','std']).sort_values('mean')
    genres['se_naive']=genres['std']/np.sqrt(genres['count'])
    genres.to_csv(OUT/'genre_statistics.csv')
    pos=reviews.loc[reviews.label=='pos','words']; neg=reviews.loc[reviews.label=='neg','words']
    u,p=mannwhitneyu(pos,neg,alternative='two-sided')
    rho,rhop=spearmanr(agg['count'],agg['mean'])
    stats={'reviews':len(reviews),'ratings':len(ratings),'users':int(ratings.userId.nunique()),'movies_catalog':len(movies),'movies_rated':len(agg),'rating_mean':float(ratings.rating.mean()),'rating_median':float(ratings.rating.median()),'rating_std':float(ratings.rating.std()),'missing_ratings':ratings.isna().sum().to_dict(),'missing_movies':movies.isna().sum().to_dict(),'missing_year':int(movies.year.isna().sum()),'duplicate_rating_rows':int(ratings.duplicated().sum()),'duplicate_user_movie':int(ratings.duplicated(['userId','movieId']).sum()),'duplicate_texts':int(reviews.text.duplicated().sum()),'empty_texts':int(reviews.text.str.strip().eq('').sum()),'unknown_movie_ids':int((~ratings.movieId.isin(movies.movieId)).sum()),'text_by_label':reviews.groupby('label').words.agg(['count','mean','median','std','min','max']).to_dict('index'),'mann_whitney':{'U':float(u),'p':float(p),'rank_biserial_pos_minus_neg':float(2*u/(len(pos)*len(neg))-1)},'popularity_rating_spearman':{'rho':float(rho),'p':float(rhop)},'ratings_per_movie_median':float(agg['count'].median()),'rating_range':[float(ratings.rating.min()),float(ratings.rating.max())],'rating_dates_utc':[str(pd.to_datetime(ratings.timestamp,unit='s',utc=True).min()),str(pd.to_datetime(ratings.timestamp,unit='s',utc=True).max())]}
    fig,ax=plt.subplots(1,2,figsize=(10,3.4))
    for label,c in zip(['neg','pos'],COLORS):
        ax[0].hist(reviews.loc[reviews.label==label,'words'],bins=np.arange(0,2801,100),alpha=.55,label=label,color=c)
    ax[0].set(xlabel='Liczba słów (tokeny regex)',ylabel='Liczba recenzji',title='Długość recenzji'); ax[0].legend()
    ax[1].boxplot([neg,pos],tick_labels=['neg','pos'],showfliers=False)
    ax[1].set(xlabel='Klasa sentymentu',ylabel='Liczba słów',title='Mediana i rozrzut (bez punktów odstających)'); save('01_text_lengths')
    cv=CountVectorizer(stop_words='english',min_df=5,max_features=20000)
    x=cv.fit_transform(reviews.text); terms=cv.get_feature_names_out()
    fig,ax=plt.subplots(1,2,figsize=(10,3.6))
    for a,label,c in zip(ax,['neg','pos'],COLORS):
        counts=np.asarray(x[(reviews.label==label).to_numpy()].sum(axis=0)).ravel(); idx=counts.argsort()[-12:]
        a.barh(terms[idx],counts[idx],color=c); a.set(xlabel='Liczba wystąpień',title=f'Najczęstsze słowa: {label}')
    save('02_words')
    fig,ax=plt.subplots(1,2,figsize=(10,3.4)); ratings.rating.value_counts().sort_index().plot.bar(ax=ax[0],color=COLORS[1])
    ax[0].set(xlabel='Ocena [0,5-5]',ylabel='Liczba ocen',title='Rozkład ocen użytkowników'); ax[0].tick_params(axis='x',rotation=0)
    ax[1].hist(agg['count'],bins=np.logspace(0,np.log10(agg['count'].max()),25),color=COLORS[0]); ax[1].set_xscale('log'); ax[1].set(xlabel='Liczba ocen filmu (skala log)',ylabel='Liczba filmów',title='Nierówna popularność filmów'); save('03_ratings')
    fig,ax=plt.subplots(1,2,figsize=(10,4.2)); g=genres[genres['count']>=1000]
    ax[0].barh(g.index,g['mean'],color=COLORS[1]); ax[0].set(xlabel='Średnia ocena [0,5-5]',title='Gatunki z co najmniej 1000 ocen',xlim=(0,5))
    ax[1].scatter(agg['count'],agg['mean'],s=9,alpha=.25,color=COLORS[0]); ax[1].set_xscale('log'); ax[1].set(xlabel='Liczba ocen filmu (skala log)',ylabel='Średnia ocena [0,5-5]',title='Popularność a średnia ocena'); save('04_genres_popularity')
    # Exact duplicate groups must never cross evaluation partitions.
    unique=reviews.drop_duplicates('text')
    train,test=train_test_split(unique,test_size=.2,stratify=unique.label,random_state=42)
    results=[]; predictions=[]
    for name,est in [('LogisticRegression',LogisticRegression(max_iter=1500,random_state=42)),('LinearSVC',LinearSVC(random_state=42))]:
        pipe=make_pipeline(TfidfVectorizer(stop_words='english',ngram_range=(1,2),min_df=2,max_features=50000),est)
        pipe.fit(train.text,train.label); pred=pipe.predict(test.text)
        results.append({'model':name,'accuracy':float(accuracy_score(test.label,pred)),'f1_macro':float(f1_score(test.label,pred,average='macro'))})
        predictions.append((name,pred))
    stats['pilot']={'train_n':len(train),'test_n':len(test),'majority_baseline':float(test.label.value_counts(normalize=True).max()),'models':results,'seed':42,'selection':'fixed settings; no tuning or model selection on test'}
    fig,ax=plt.subplots(1,2,figsize=(8,3.5))
    for a,(name,pred) in zip(ax,predictions):
        ConfusionMatrixDisplay.from_predictions(test.label,pred,labels=['neg','pos'],ax=a,colorbar=False,cmap='Greens'); a.set(title=name,xlabel='Przewidywana klasa',ylabel='Rzeczywista klasa')
    save('05_pilot')
    pd.concat([train[['file','label']].assign(split='train'),test[['file','label']].assign(split='test')]).to_csv(OUT/'pilot_split.csv',index=False)
    for name,pred in predictions:
        pd.DataFrame({'file':test.file,'true':test.label,'predicted':pred}).to_csv(OUT/f'predictions_{name}.csv',index=False)
    stats['provenance']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((ROOT/'data/raw').iterdir())}
    stats['versions']={'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'matplotlib':matplotlib.__version__}
    (OUT/'summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=True,indent=2))
if __name__=='__main__': main()
