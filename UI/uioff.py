import sys
sys.path.insert(0,'../Calcul') 
import io
import urllib
import polyline
import requests
import googlemaps
import tkinter as tk
from trajet import *
from PIL import ImageTk
from tkinter.ttk import *

gmaps = googlemaps.client.Client('AIzaSyAlYcXhPFn0N_3D9iwsFWBdN7cQNVpxCzc')

class Interface(Frame): #Création de la page d'affichage où l'utilisateur entre les données
    def __init__(self,fenetre,**kwargs):
        Frame.__init__(self,fenetre,width=1900,height=900)
        fenetre.iconbitmap("../Image/marker.ico") #Changement de l'icone d'affichage
        self.depart = ''            #initiation des paramètres départ, destination, durée du trajet, mode de transport, itinéraire
        self.des = ''
        self.duree = ""
        self.mode = ""
        self.dico = {'transit':'en transports communs','walking':'à pied','velib':'en vélib', 'autolib':"en autolib"}
        self.itineraire = ""
        self.details = []           #détails de l'itinéraire
        self.connexion = True       #état de la connexion de l'utilisateur
        self.gap = 150
        self.pack()
        #Attributs liés aux préférences de choix de l'utilisateur (météo, charge à déplacer, les transports à prendre en compte)
        self.charge = 0
        self.meteo = False
        #indicateurs de modes de transports choisis par l'utilisateur
        self.p = tk.IntVar()
        self.t = tk.IntVar()
        self.a = tk.IntVar()
        self.v = tk.IntVar()
        self.p.set(1)           #indicateurs mis à 1 par défaut, le calcul du trajet optimal prend en charge l'usage de tous les transports
        self.t.set(1)
        self.a.set(1)
        self.v.set(1)
        #Création du fond d'écran
        background_image = tk.PhotoImage(file = "../Image/paris.gif")
        background = tk.Label(fenetre, image=background_image)
        background.place(x = 0, y = 0, relwidth=1, relheight=1)
        fenetre.wm_geometry("1366x768+0+0")
        background.image = background_image 
        #Initiation des styles utilisés pour les différents widgets
        ui_style = Style()
        ui_style.configure('My.TFrame', background='#FFC000') 
        ui_style.configure('My.TRadiobutton', background='#FFC000', foreground = 'white', width=25, padding = 5, font=('Helvetica', 14))
        ui_style.configure('My.TLabel', width=17, background='#FFC000', foreground = '#7F6000', font=('Helvetica', 14), anchor = 'Center', padding = 5)
        ui_style.configure('My.TButton', width=20, highlightbackground='#FFC000', background='#FFC000', foreground = '#7F6000', font=('Helvetica', 14), anchor = 'Center', padding = 5)
        ui_style.configure('My.TCheckbutton', background='#FFC000', foreground = 'white', width=25, padding = 5, font=('Helvetica', 14)) 
        ui_style.configure("green.Horizontal.TProgressbar",foreground='#FFC000', background='#FFC000')
        self.create_widgets()

    def create_widgets(self):
        self.check()   #On commence par vérifier la connexion de l'utilisateur
        if self.connexion :
            cadre_depart = Frame(fenetre, width=300, height=2, borderwidth=1, style='My.TFrame') #Création du container depart
            cadre_depart.place(x=620, y=250) 
            depart_label = Label(fenetre, text="Départ", style='My.TLabel')
            depart_label.pack(side='top')
            depart_label.place(x=400, y=250)
            depart_fixe = Radiobutton(cadre_depart, text='Départ à définir', variable="Départ", value = 'Saisir adresse de départ', command=self.dep, style='My.TRadiobutton')
            depart_geo = Radiobutton(cadre_depart, text='Localisation actuelle', variable="Départ", value="geo", command=self.geo, style='My.TRadiobutton')
            depart_geo.pack(side='left')
            depart_fixe.pack(side='left')
            
            
            cadre = Frame(fenetre, width=200, height=5,borderwidth=1,style='My.TFrame') #Création du container destination
            cadre.pack(side='top')
            cadre.place(x=620, y=327)
            destinationlabel = Label(fenetre, text='Destination', style='My.TLabel')
            destinationlabel.place(x=400,y=320)
            dest = Entry(cadre, text='Destination', width=100)
            dest.pack(side='right')
            self.listpre = tk.Listbox(fenetre, width=100, selectbackground='#FFC000', font=('Helvetica', 14), selectmode = 'SINGLE' )
            self.destination = tk.StringVar()
            self.destination.set("")
            dest["textvariable"] = self.destination
            dest.bind('<FocusOut>',self.get_destination)
            dest.bind('<Key>',self.predict)
            self.filtre = Button(fenetre, text='Plus de filtres', command=self.filtres,style='My.TButton' )
            self.filtre.place(x=750, y=400)
            self.chercher = Button(fenetre, text='Comment y aller ?', command=self.tra,style='My.TButton' )
            self.chercher.place(x=750, y=600)
        
        else :
            Label(fenetre, text="Merci de vérifier votre connexion Internet", style = "My.TLabel", width =50, padding = 10).place(x=420,y=400)
            
        
    def check(self):
        try :
            reponse = requests.get("https://opendata.paris.fr/api/records/1.0/search/?dataset=autolib-disponibilite-temps-reel&lang=fr&rows=-1")
            code = reponse.status_code
            assert code == 200
        except AssertionError:
            self.connexion = False
        except requests.exceptions.ConnectionError:
            self.connexion = False 
    #Initiation de compteurs utilisés pour la prédiction lors de la saisie des données
    i = 0 
    j = 0        
    
    #Fonctions qui lancent la fonctionnalité de prédiction lors de la saisie et enregistre la destination et le départ de l'utilisateur
    def get_depart(self,event):
        selct = self.listpre.get('anchor')
        self.definir.set(selct)
        self.listpre.place_forget()
        self.filtre.place(x=750, y=400)
        self.chercher.place(x=750, y=600)
        self.depart = self.definir.get()
        self.j = 0
        
    def get_destination(self,event): 
        selct = self.listpre.get('anchor')
        self.destination.set(selct)
        self.listpre.place_forget()
        self.filtre.place(x=750, y=400)
        self.chercher.place(x=750, y=600)
        self.des = self.destination.get()
        self.i = 0
    
    def predict(self,event):
        if self.i>1 :
            self.filtre.place_forget()
            self.chercher.place_forget()
            self.listpre.place(x=620, y=345)
            list_auto = self.liste_prediction()
            for item in list_auto:
                self.listpre.insert(0, item)
        self.i += 1
            
    def predict_def(self,event):
        if self.j>1 :
            self.filtre.place_forget()
            self.chercher.place_forget()
            self.listpre.place(x=620, y=305)
            list_auto = self.liste_def()
            for item in list_auto:
                self.listpre.insert(0, item)
        self.j += 1
            
    def liste_prediction(self):
        texte = self.destination.get()
        if len(texte)>1 :
            liste = gmaps.places_autocomplete(texte, offset=None, location=gmaps.geocode('Paris, France')[0]['geometry']['location'], radius=5000, language = "fr") 
            list_auto = []
            for dico in liste :
                list_auto.append(dico['description'])
            return list_auto
        elif len(texte) == 0 : 
            self.i = 0
        
    def liste_def(self):
        texte = self.definir.get()
        if len(texte)>1 :
            liste = gmaps.places_autocomplete(texte, offset=None, location=gmaps.geocode('Paris, France')[0]['geometry']['location'], radius=5000, language = "fr") 
            list_auto = []
            for dico in liste :
                list_auto.append(dico['description'])
            return list_auto
        elif len(texte) == 0 :
            self.j = 0
    
    def dep(self): #Fonction lancée si l'utilisateur choisit de saisir une adresse de départ au lieu d'être géolocalisé
        cadep = Frame(fenetre, width=200, height=5,borderwidth=1,style='My.TFrame') #Création du container destination
        cadep.place(x=620, y=285)
        d = Entry(cadep, text='Départ',width = 100, background = '#FFC000')
        d.pack()
        self.definir = tk.StringVar()
        self.definir.set("")
        d["textvariable"] = self.definir
        d.bind('<FocusOut>',self.get_depart)
        d.bind('<Key>',self.predict_def)
        self.depart = self.definir
    
    def geo(self): #Fonction lancée pour la géolocalisation de l'utilisateur
        geoloc = gmaps.geolocate()['location']
        c = 0 
        self.depart = gmaps.reverse_geocode(geoloc, result_type = "")[c]['formatted_address']
        
        
    #Fonction d'affichage des préférences de choix
    def filtres(self):
        #Météo
        meteolabel = Label(fenetre, text='Météo', style='My.TLabel')
        meteolabel.place(x=400,y=450)
        cadre_meteo = Frame(fenetre,width=302,height=2,borderwidth=2, style='My.TFrame') #Création du container depart
        cadre_meteo.place(x=620,y=450)
        ok = Radiobutton(cadre_meteo,text='Oui',variable="Météo",value="ok",command=self.ok, style='My.TRadiobutton', width=26 )
        ko = Radiobutton(cadre_meteo,text='Non',variable="Météo",value="ko", style='My.TRadiobutton')
        ok.pack(side='left')
        ko.pack(side='left')
        #Charge
        charge = Label(fenetre, text='Charge', style='My.TLabel')
        charge.place(x=400,y=500)
        cadre_charge = Frame(fenetre,width=300,height=2,borderwidth=2, style='My.TFrame') #Création du container depart
        cadre_charge.place(x=620,y=500)
        Radiobutton(cadre_charge,text='Rien',variable=self.charge,value=0, style='My.TRadiobutton', width = 5).pack(side='left')
        Radiobutton(cadre_charge,text='Sac à dos',variable=self.charge,value=1, style='My.TRadiobutton', width = 18).pack(side='left')
        Radiobutton(cadre_charge,text='Valise',variable=self.charge,value=2, style='My.TRadiobutton', width = 11).pack(side='left')
        Radiobutton(cadre_charge,text='Meuble',variable=self.charge,value=3, style='My.TRadiobutton', width = 11).pack(side='left')
        #Choix de transports 
        tr = Label(fenetre, text='Mode(s) de tranport', style='My.TLabel')
        tr.place(x=400,y=550)
        cadre_tr = Frame(fenetre,width=300,height=2,borderwidth=2, style='My.TFrame') #Création du container depart
        cadre_tr.place(x=620,y=550)
        pi = Checkbutton(cadre_tr,text='A pied',variable=self.p, command = self.sel, width = 5, onvalue =True, offvalue =False, style='My.TCheckbutton')
        pi.pack(side='left')
        tc = Checkbutton(cadre_tr,text='Transports Communs',variable=self.t, command = self.sel,width = 18, onvalue =True, offvalue =False,style='My.TCheckbutton')
        tc.pack(side='left')
        au = Checkbutton(cadre_tr,text='Autolib',variable=self.a, command = self.sel,width = 11, onvalue =True, offvalue =False, style='My.TCheckbutton')
        au.pack(side='left') 
        ve = Checkbutton(cadre_tr,text='Vélib',variable=self.v, command = self.sel,width = 11, onvalue =True, offvalue =False, style='My.TCheckbutton')
        ve.pack(side='left')
        
    def sel(self): #Prend en charge tous les modes de transport au cas où l'utilisateur décoche toutes les cases
        s = self.p.get()+ self.t.get()+ self.a.get()+ self.v.get() 
        if s == 0 :
            self.p.set(1)
            self.t.set(1)
            self.a.set(1)
            self.v.set(1)
        
    def ok(self):
        self.meteo = True 

    def get_itineraire(self, optimal):
        L=[]
        for etape in optimal[:-1]:
            L += polyline.decode(etape.poly)[:-1]
        L += polyline.decode(optimal[-1].poly)
        return polyline.encode(L)

    def get_markers(self):
        marker_list = []
        marker_list.append("markers=size:mid|color:red|label:Depart|" + str(gmaps.geocode(self.depart)[0]['geometry']['location']['lat']) + "," + str(gmaps.geocode(self.depart)[0]['geometry']['location']['lng']))
        marker_list.append("markers=size:mid|color:red|label:Arrivee|" + str(gmaps.geocode(self.des)[0]['geometry']['location']['lat']) + "," + str(gmaps.geocode(self.des)[0]['geometry']['location']['lng']))
        return marker_list

    def get_static_google_map(self, filename_wo_extension, center=None, zoom=None, imgsize="400x400", imgformat="gif", maptype="roadmap", markers=None, path=None):
        # permet la récupération d'une carte statique à partir de l'api Google Maps

        # construire URL
        request = "http://maps.google.com/maps/api/staticmap?"  # URL de base
        request += "size=%ix%i&" % (imgsize)  # taille de l'image
        request += "format=%s&" % imgformat
        request += "maptype=%s&" % maptype  # roadmap, satellite, hybrid, terrain
    

        # Ajouter les marqueurs au départ et à l'arrivée
        if markers != None:
            for marker in markers:
                request += "%s&" % marker

        # Ajouter l'itinéraire
        request += "path=color:blue|weight:2"
        request += "|enc:%s" % (path)

        # Récupération de la carte et son enregistrement dans le dossier Imaages
        web_sock = urllib.request.urlopen(request)
        imgdata = io.BytesIO(web_sock.read())  # constructs a StringIO holding the image
        try:
            PIL_img = ImageTk.Image.open(imgdata)

        # Si l'image ne peut être lue
        except IOError:
            print("IOError:", imgdata.read())  # retourne une image d'erreur
        else:
            PIL_img.save("../Image/Roadmap" + ".gif", "GIF")

    def tra(self): #Fonction qui lance le calcul du trajet optimal et affiche les résultats 
        if len(self.depart) == 0 or len(self.des) == 0 : 
            erreur = Label (fenetre, text = "Merci de saisir toutes les données", style = "My.TLabel", width = 30) 
            erreur.place(x=690, y=200)
        else :    
            fra = Frame(fenetre, width = 220, height = 150, style='My.TFrame')
            fra.place(x=750, y = 650)
            traj = Choix_Trajet()
            traj.entrer_donnees_utilisateur(self.depart, self.des, self.meteo,self.charge, bool(self.p.get()), bool(self.t.get()), bool(self.v.get()), bool(self.a.get()))
            traj.calculer()
            optimal = traj.choix()  #Récupération du trajet optimal et de toutes les données à afficher 
            self.mode = optimal.transport
            self.itineraire = self.get_itineraire(optimal.etapes)
            self.duree = optimal.afficher_temps()
            for etape in optimal.etapes:
                self.details.append(etape.transport)
                self.details.append(etape.afficher_temps())
                if etape.transport=='transit':
                    self.details.append(etape.nom_origine)
                    self.details.append(etape.nom_destination)
                    self.details.append(etape.type_transport)
                    self.details.append(etape.nom_transport)

            #Création de la fenetre d'affichage
            self.markers = self.get_markers()
            self.get_static_google_map("Roadmap", zoom =17, imgsize=(440, 440), imgformat="gif", markers=self.markers, path=self.itineraire)
            ui = Affichage (fenetre, self.depart, self.des, self.meteo, self.duree, self.dico[self.mode], self.itineraire, self.details)
            ui.mainloop()
            os.remove("../Image/Roadmap.gif")


class Affichage(Interface):
    def __init__(self,fenetre, depart, dest, meteo, duree, mode, itineraire, details):
        Interface.__init__(self,fenetre)
        self.depart = depart
        self.des = dest
        self.meteo = meteo
        self.duree =  duree
        self.mode = mode
        self.details = details
        #Paramètres liés à l'affichage de la carte
        self.itineraire = itineraire
        self.create_widgets()

    def create_widgets(self):
        cadre = tk.Frame (fenetre, width = 1220, height = 500, background = '#FFC000')
        cadre.place(x=70, y=210)
        resultat = Label(cadre, text = "Nous vous conseillons de vous y rendre %s"%(self.mode), font=('Helvetica', 14), background = '#FFC000')
        resultat.place(x = 550, y = 30)
        #Affichage de  l'itinéraire
        if 'transit' in self.details :
            k = self.get_k()
            y = self.gap
            for i in range(0, len(self.details)):
                if self.details[i] == 'walking' :
                    y += k
                    Label(cadre, text="%s à pied"%(self.details[i+1]), font=('Helvetica', 14), background='#FFC000').place(x=700, y=y)
                elif self.details[i] == 'transit' :
                    y += k
                    Label(cadre, text = self.details[i+2], font = ('Helvetica', 14), background = '#FFC000').place(x = 700, y = y)
                    if self.details[i+4] == 'SUBWAY':
                        Label(cadre, text = "BUS %s -- %s"%(self.details[i+5],self.details[i+1]) , font=('Helvetica', 14), background='#FFC000').place(x= 760, y=y+30)
                    else :
                        Label(cadre, text="%s -- %s" % (self.details[i + 5], self.details[i + 1]), font=('Helvetica', 14), background='#FFC000').place(x=760, y=y + 30)
                    Label(cadre, text=self.details[i+3], font=('Helvetica', 14), background='#FFC000').place(x= 700, y=y+60)
                    y += 60
            arrivee = Label(cadre, text = 'Destination : %s'%(self.des), font = ('Helvetica', 14), background = '#FFC000')
            arrivee.place(x=550, y = y+k)
        else :
            arrivee = Label(cadre, text='Destination : %s' % (self.des), font=('Helvetica', 14), background='#FFC000')
            arrivee.place(x=550, y=200)
        Label(cadre, text="Départ : %s" % (self.depart), font=('Helvetica', 14), background='#FFC000').place(x=550,y=self.gap)
        # Afficher la durée du trajet
        Label(cadre, text='Durée du trajet : %s' % (self.duree), font=('Helvetica', 14), background='#FFC000').place(x=550, y=self.gap - 30)

        #Affichage de la carte
        self.map = ImageTk.PhotoImage(file = "../Image/Roadmap.gif")
        map_label = tk.Label(fenetre, image = self.map, borderwidth = 0)
        map_label.place(x = 120, y = 240)
        map_label.image = self.map

        #Calcul d'une nouveau trajet
        Button(fenetre, text='Choisir un autre trajet', command=self.nouveau, style='My.TButton').place(x=700, y=170)

    def get_k(self):
        L = self.details.copy()
        k = 70
        while 'transit' in L:
            k -= 15
            L.remove('transit')
            if k <= 40 :
                self.gap = 90
        return k

    def nouveau(self):
        os.remove("../Image/Roadmap.gif")
        nouveau = Interface(fenetre)
        nouveau.mainloop()


fenetre = tk.Tk()
fenetre.wm_state(newstate="zoomed") #met la fenetre en agrandi
interface = Interface(fenetre)
interface.master.title('Comment y aller ?')
interface.mainloop()

