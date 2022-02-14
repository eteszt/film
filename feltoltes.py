#film keresés TMDB-n, adatok kitoltése, korrekció, feltoltes wordpress-be
#kilistúzza a megadott cimnek megfelelő filmeket
#ebből lehet sorszam alapján választani
from tmdbv3api import TMDb
from tmdbv3api import Movie
import yagmail
from os.path import exists
import requests
from PIL import Image
import glob
import os

def correct(cimke,szoveg):
  print(cimke+":\n"+szoveg)
  segedSzoveg = input()
  if segedSzoveg != "":
    szoveg = segedSzoveg
  return(szoveg)

def meretezes(kep):
    # plakat atmeretezese
    image = Image.open(kep)
    image.thumbnail((400, 500))
    image.save(kep)
    return

def filmKeres(c,i):
  movie = Movie()
  talalat = movie.search(c)[i]
  return(talalat.id, talalat.title, talalat.original_title, talalat.release_date, talalat.overview)

def filmAdatok(azonosito):
  movie = Movie()
  talalat = movie.credits(azonosito)
  return(talalat.cast,talalat.crew)

def filmIdo(azonosito):
  #letölti a plakat kepet is és az anol leirast
  api_url = "https://api.themoviedb.org/3/movie/" + str(azonosito) + "?api_key=6e1d55445f8e73301f6f022dbdf48327&language=en-US"
  response = requests.get(api_url)
  r=response.json()

  plakat= "https://www.themoviedb.org/t/p/original/"+r["poster_path"]
  pKep = requests.get(plakat)
  pFile = open(kepPath+"plakat.jpg", "wb")
  pFile.write(pKep.content)
  pFile.close()
  meretezes(kepPath+"plakat.jpg")
  return(str(r["runtime"]), r["overview"])

def listToString(l):
  s=""
  for a in l:
    s=s+a+", "
  s=s [:-2]
  return(s)

def filmListazo(focim):
  movie = Movie()
  talalat = movie.search(focim)
  for filmIndex,f in enumerate(talalat):
    if "release_date" in f:
      print(f"{filmIndex}  {f.title} ({f.release_date})")
    else:
      print(f"{filmIndex}  {f.title} (0)")
  sorszam = 0
  ujSorszam = input("Melyik sorszámú film legyen? (Enter = 0) ")
  if ujSorszam != "":
    sorszam = int(ujSorszam)
  return(sorszam)


def sendFilm(cim,eredetiCim,ev,leiras,stab,szineszek,perc):

  magyarCim = cim
  angolCim = eredetiCim
  szereplok = listToString(szineszek)
  rendezok = listToString(stab)
  try:
    objektiv =leiras+ "\n\n<i>" + eredetiCim + " (" + ev+"), \n"+ str(perc)+" perc/min</i>\n<b> Rendező/Director: "+rendezok+ "\n Szereplők/Cast: "+szereplok+"</b>"
  except:
    objektiv =""

  kepek = glob.glob(kepPath + "*.*")
  kepek.sort(reverse=True)


  tagok = "\n \n tags: " + rendezok+", "+ szereplok
  #print(kepek)
  try:
    yag.send(to="szemlefilm@gmail.com", subject=magyarCim, contents=objektiv+tagok, attachments=kepek)
  except Exception as exception:
    print("Exception: {}".format(type(exception).__name__))
    print("Exception message: {}".format(exception))
  return

#itt kezdődik a program----------------------------------------------------------------------

yag = yagmail.SMTP(user='interfeszpress@gmail.com', password='jdxtlnjitfdsqqns')
tmdb = TMDb()
tmdb.api_key = '6e1d55445f8e73301f6f022dbdf48327'
tmdb.language = 'hu'
#kepPath = "/content/drive/MyDrive/Colab Notebooks/filmkepek/"
kepPath = "filmkepek/"
cim = input("A film címe: ")
filmIndex = filmListazo(cim)
azonosito, cim, eredetiCim,ev, leiras = filmKeres(cim,filmIndex)
ido, angolLeiras = filmIdo(azonosito)
ev = ev[:4]
print("Ezt találtam: ")
print(azonosito)
print(cim, ", ",eredetiCim, ", ",ev)
leiras =correct("Magyar lerás",leiras)
angolLeiras=correct("Angol tartalom",angolLeiras)
szineszek, alkotok = filmAdatok(azonosito)
szereplok = []
for i in range (min(len(szineszek), 10)):
  szereplok.append(szineszek[i].name)
#print (szereplok)
rendezok = []
for s in alkotok:
  if s.job == "Director":
    rendezok.append(s.name)

a = input("Minden rendben? (Y/N) ")

if a == "Y":

  sendFilm(cim,eredetiCim,ev,leiras+ "\n\n" + angolLeiras,rendezok,szereplok,ido)
  kepek = glob.glob(kepPath + "*.*")
  for kepnev in kepek:
    os.remove(kepnev)
  print("A film feltöltve!")
