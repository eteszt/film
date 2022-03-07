# 2022.02.21
import requests
from PIL import Image
import glob
import os
import yagmail
import PySimpleGUI as sg


def pillanat(s):
    print("\nPillanat...")
    print(s)
    return


def listToString(l):
    s = ""
    for a in l:
        s = s + a + ", "
    s = s[:-2]
    return s


def correct(cimke, szoveg):
    if cimke != "azonosito" and cimke != "poster" and cimke != "mdb":
        print(cimke + ":  " + szoveg)
        segedSzoveg = input()
        if segedSzoveg != "":
            szoveg = segedSzoveg
    return szoveg


def trailer(id):
    api_url = "https://imdb-api.com/en/API/YouTubeTrailer/k_esxzc7d2/" + id
    response = requests.get(api_url)
    videoUrl = response.json()["videoUrl"]
    return "https://www.youtube.com/embed/" + videoUrl[videoUrl.find("=") + 1 :]


# egy film adatait feltölti a wordpress bloghoz tartozo email cimre
def feltotes(f):
    youTube = ""
    if f["imdb"] != None:
        if trailer(f["imdb"]) != "https://www.youtube.com/embed/":
            youTube = f'<iframe width="560" height="315" src="{trailer(f["imdb"])}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    objektiv = (
        f["magyarTartalom"]
        + "\n\n"
        + youTube
        + "\n\n<i>"
        + f["angolTartalom"]
        + "\n\n<i>"
        + f["angolCim"]
    )
    objektiv += (
        " ("
        + f["premier"]
        + "), \n"
        + f["hossz"]
        + " perc/min </i> \n \n<h1>Értékelés: "
        + str(f["szavazat"])
        + "/10</h1>\n\n<b> Rendező/Director: </b>"
    )
    objektiv += f["rendezok"] + "\n <b>Szereplők/Cast: </b>" + f["szereplok"]
    objektiv += "\n <b>Gyártók/Production Companies: </b>" + f["gyarto"]
    objektiv += "\n <b>Magyar forgalmazó: </b>" + f["forgalmazo"]
    kepek = glob.glob(kepPath + "*.*")
    kepek.sort(reverse=True)
    tagok = (
        "\n \n tags: "
        + f["rendezok"]
        + ", "
        + f["szereplok"]
        + ", "
        + f["gyarto"]
        + ", "
        + f["forgalmazo"]
    )
    try:
        yag.send(
            to="szemlefilm@gmail.com",
            subject=f["magyarCim"],
            contents=objektiv + tagok,
            attachments=kepek,
        )
    except Exception as exception:
        print("Exception: {}".format(type(exception).__name__))
        print("Exception message: {}".format(exception))
    return


# kiirja a találati listát: sorszam, magyar cím, angol cím, premier, rendezo
# visszaadja a kivélasztott sorszámot
# ha -1, akkor kézi bevitel következik
def talalatiLista(filmCim):
    sorszam = 0
    talalatok = []
    api_url = (
        "https://api.themoviedb.org/3/search/movie?query="
        + filmCim
        + "&api_key=6e1d55445f8e73301f6f022dbdf48327&language=en-US"
    )
    response = requests.get(api_url)
    for r in response.json()["results"]:

        api_url2 = (
            "https://api.themoviedb.org/3/movie/"
            + str(r["id"])
            + "?api_key=6e1d55445f8e73301f6f022dbdf48327&language=hu-HU"
        )
        response2 = requests.get(api_url2)
        api_url3 = (
            "https://api.themoviedb.org/3/movie/"
            + str(r["id"])
            + "/credits?api_key=6e1d55445f8e73301f6f022dbdf48327&language=hu-HU"
        )
        response3 = requests.get(api_url3)
        szereplok = []
        for i in range(min(len(response3.json()["cast"]), 10)):
            szereplok.append(response3.json()["cast"][i]["name"])
        rendezok = []
        for i in range(len(response3.json()["crew"])):
            if response3.json()["crew"][i]["job"] == "Director":
                rendezok.append(response3.json()["crew"][i]["name"])
        gyartok = []
        for i in range(min(len(response2.json()["production_companies"]), 3)):
            gyartok.append(response2.json()["production_companies"][i]["name"])

        p = r["poster_path"]
        if p != None:
            talalatok.append(
                {
                    "azonosito": str(r["id"]),
                    "magyarCim": response2.json()["title"],
                    "angolCim": r["title"],
                    "hossz": str(response2.json()["runtime"]),
                    "premier": response2.json()["release_date"][:4],
                    "magyarTartalom": response2.json()["overview"],
                    "angolTartalom": r["overview"],
                    "imdb": response2.json()["imdb_id"],
                    "szavazat": str(response2.json()["vote_average"]),
                    "gyarto": listToString(gyartok),
                    "forgalmazo": "",
                    "szereplok": listToString(szereplok),
                    "rendezok": listToString(rendezok),
                    "poster": "https://www.themoviedb.org/t/p/original/"
                    + r["poster_path"],
                }
            )
            sorszam += 1
            if sorszam == 5:
                break
    return talalatok


def adatKorrekcio(filmTomb):
    print("\nAdatok módosítása (ha maradhat - Enter)\n")
    for t in filmTomb:
        filmTomb[t] = correct(str(t), filmTomb[t])
    return filmTomb


def simpleAdatKorrekcio(filmTomb):
    fontSize = 16
    layout = [
        [sg.Text('Magyar cím', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["magyarCim"],key='magyarCim',size=(70,1),font=("Verdana",fontSize))],
        [sg.Text('Angol cím', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["angolCim"],key='angolCim',size=(70,1),font=("Verdana",fontSize))],
        [sg.Text('Hossz', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["hossz"],key='hossz',font=("Verdana",fontSize))],
        [sg.Text('Bemutató', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["premier"],key='premier',font=("Verdana",fontSize))],
        [sg.Text('Magyar tartalom', size=(16,1),font=("Verdana",fontSize)), sg.Multiline(filmTomb ["magyarTartalom"],key="magyarTartalom",size=(64,3),font=("Verdana",fontSize))],
        [sg.Text('Angol tartalom', size=(16,1),font=("Verdana",fontSize)), sg.Multiline(filmTomb ["angolTartalom"],key='angolTartalom',size=(64,3),font=("Verdana",fontSize))],
        [sg.Text('Szereplők', size=(10,1),font=("Verdana",fontSize)), sg.Multiline(filmTomb ["szereplok"],key='szereplok',size=(70,1),font=("Verdana",fontSize))],
        [sg.Text('Rendezők', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["rendezok"],key='rendezok',size=(70,1),font=("Verdana",fontSize))],
        [sg.Text('Gyártók', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["gyarto"],key='gyarto',size=(70,1),font=("Verdana",fontSize))],
        [sg.Text('Forgalmazó', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["forgalmazo"],key='forgalmazo',font=("Verdana",fontSize))],
        [sg.Text('Szavazat', size=(10,1),font=("Verdana",fontSize)), sg.InputText(filmTomb ["szavazat"],key='szavazat',font=("Verdana",fontSize))],

        [sg.Submit(), sg.Button('Töröl'), sg.Exit()]
    ]

    window = sg.Window('Új film adatainak feltöltése', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            break
        if event == 'Töröl':
            for key in values:
                window[key]('')
        if event == 'Submit':
            window.close()
            for kulcs in values:
                filmTomb [kulcs]=values [kulcs].strip()
    return filmTomb


def posterFeltoltes(film):
    plakat = "https://www.themoviedb.org/t/p/original/" + film["poster"]
    pKep = requests.get(plakat)
    pFile = open(kepPath + "x_plakat.jpg", "wb")
    pFile.write(pKep.content)
    pFile.close()
    image = Image.open(kepPath + "x_plakat.jpg")
    image.thumbnail((700, 1200))
    image.save(kepPath + "x_plakat.jpg")
    return


def imdbKepek(id):
    api_url = "https://imdb-api.com/en/API/Images/k_esxzc7d2/" + id + "/Short"
    response = requests.get(api_url)
    x = response.json()
    for i in range(min(20, len(x["items"]))):
        plakat = x["items"][i]["image"]
        pKep = requests.get(plakat)
        pFile = open(kepPath + "kep" + str(i) + ".jpg", "wb")
        pFile.write(pKep.content)
        pFile.close()
        try:
            image = Image.open(kepPath + "kep" + str(i) + ".jpg")
            width, height = image.size
            print(i, width, height)
            if width > height:
                image.thumbnail((1600, 1200))
                image.save(kepPath + "kep" + str(i) + ".jpg")
            else:
                os.remove(kepPath + "kep" + str(i) + ".jpg")
        except:
            os.remove(kepPath + "kep" + str(i) + ".jpg")
    return


def kepekTorlese():
    kepek = glob.glob(kepPath + "*.*")
    for kepnev in kepek:
        os.remove(kepnev)
    return

#itt kezdődik a program
print("Film keresés és feltöltés v3.0")
yag = yagmail.SMTP(user="interfeszpress@gmail.com", password="jdxtlnjitfdsqqns")
kepPath = "filmkepek/"
try:
    os.mkdir(kepPath)
except:
    None
uresFilmAdat = {
    "azonosito": "",
    "magyarCim": "",
    "angolCim": "",
    "hossz": "",
    "premier": "",
    "magyarTartalom": "",
    "angolTartalom": "",
    "szereplok": "",
    "rendezok": "",
    "poster": "",
    "imdb": "",
    "gyarto": "",
    "forgalmazo": "",
    "szavazat": "",
}
bemutato = input("Melyik filmcímet keressem? ")
print("\nEzeket találtam:\n")
filmLista = talalatiLista(bemutato)
for i, talalat in enumerate(filmLista):
    print(
        f'{i}. {talalat["magyarCim"]}/{talalat["angolCim"]} ({talalat["premier"]}) Rendező: {talalat["rendezok"]}'
    )
azon = input("\nMelyiket szeretnéd feltölteni? (Enter = 0, egyiket sem = -1) ")
azon = 0 if azon == "" else int(azon)
if azon == -1:
    filmTeljesAdat = uresFilmAdat
else:
    filmTeljesAdat = filmLista[azon]
if filmTeljesAdat["szavazat"]=="0.0":
    filmTeljesAdat["szavazat"]="-/0"
filmTeljesAdat = simpleAdatKorrekcio(filmTeljesAdat)

sajatKep = ""
sajatKep = input("Szeretnél saját képeket használni (Y/N)? ")
if sajatKep == "Y":
    print("Töltsd fel a kepeket a 'filmkepek/' könyvtárba! Legyen közte plakátkép, ennek neve legyen plakat.jpg, a többi kép neve tetszőleges.")
    fel = input("Feltöltötted (Y/N)? ")
    if fel == "Y":
        None
else:
    pillanat("Keresem a képeket")
    posterFeltoltes(filmTeljesAdat)
    if filmTeljesAdat ['imdb'] != None:
        imdbKepek(filmTeljesAdat["imdb"])
ok = "Y"
#ok = input("\nMinden rendben (Y/N)? ")
if ok == "Y":
    feltotes(filmTeljesAdat)
    print("\nA film fel van töltve.")
else:
    print("\nNem sikerült a feltöltés.")
kepekTorlese()
