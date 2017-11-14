import os
import sys
sys.path.insert(0,'C:/Users/Hala/Desktop/Projets/POOA_Project-master/POOA_Project-master/Calcul') 
os.chdir('C:/Users/Hala/Desktop/Projets/POOA_Project-master/POOA_Project-master')
from tkinter.ttk import *
import tkinter as tk
import googlemaps
from PIL import ImageTk, Image
import time
#import random
import requests 
from trajet import *
import urllib
import io
from PIL import ImageTk

gmaps = googlemaps.client.Client('AIzaSyAlYcXhPFn0N_3D9iwsFWBdN7cQNVpxCzc')

class Interface(Frame):

    def __init__(self,fenetre,**kwargs):
        Frame.__init__(self,fenetre,width=1000,height=900)
        self.depart = ''
        self.des = ''
        self.meteo = False
        self.charge = 0
        self.duree = ""
        self.connexion = True 
        self.p = tk.IntVar()
        self.t = tk.IntVar()
        self.a = tk.IntVar()
        self.v = tk.IntVar()
        self.p.set(1)
        self.t.set(1)
        self.a.set(1)
        self.v.set(1)
        self.mode = ""
        self.dico = {'transit':'en transports communs','walking':'à pied','velib':'en vélib', 'autolib':"en autolib"}
        self.poly= ""
        self.pack()
        background_image = tk.PhotoImage(file = "Images/co.gif")
        background = tk.Label(fenetre, image=background_image)
        background.place(x=0, y=0, relwidth=1, relheight=1)
        fenetre.wm_geometry("1000x900+20+40")
        background.image = background_image 
        ui_style = Style()
        ui_style.configure('My.TFrame', background='#FFC000') 
        ui_style.configure('My.TRadiobutton', background='#FFC000', foreground = 'white', width=25, padding = 5, font=('Helvetica', 14))
        ui_style.configure('My.TLabel', width=17, background='#FFC000', foreground = '#7F6000', font=('Helvetica', 14), anchor = 'Center', padding = 5)
        ui_style.configure('My.TButton', width=20, highlightbackground='#FFC000', background='#FFC000', foreground = '#7F6000', font=('Helvetica', 14), anchor = 'Center', padding = 5)
        ui_style.configure('My.TCheckbutton', background='#FFC000', foreground = 'white', width=25, padding = 5, font=('Helvetica', 14)) 
        ui_style.configure("green.Horizontal.TProgressbar",foreground='#FFC000', background='#FFC000')
        self.create_widgets()

    def create_widgets(self):
        self.check()
        if self.connexion :
            cadre_depart = Frame(fenetre,width=300,height=2,borderwidth=1, style='My.TFrame') #Création du container depart
            cadre_depart.place(x=620,y=250)
            cadre = Frame(fenetre, width=200, height=5,borderwidth=1,style='My.TFrame') #Création du container destination
            cadre.pack(side='top')
            cadre.place(x=620, y=327)
        
            depart_label = Label(fenetre,text="Départ", style='My.TLabel')
            depart_label.pack(side='top')
            depart_label.place(x=400,y=250)
            depart_fixe = Radiobutton(cadre_depart,text='Départ à définir',variable="Départ", value = 'Saisir adresse de départ',command=self.dep, style='My.TRadiobutton' )
            depart_geo = Radiobutton(cadre_depart,text='Localisation actuelle',variable="Départ",value="geo", command=self.geo, style='My.TRadiobutton')
            depart_geo.pack(side='left')
            depart_fixe.pack(side='left')
    
            
            destinationlabel = Label(fenetre, text='Destination', style='My.TLabel')
            destinationlabel.place(x=400,y=320)
    
            dest = Entry(cadre, text='Destination', width=100)
            dest.pack(side='right')
            self.listpre = tk.Listbox(fenetre, width=100, selectbackground='#FFC000', font=('Helvetica', 14), selectmode = 'SINGLE' )
            self.destination = tk.StringVar()
            # set it to some value
            self.destination.set("")
            dest["textvariable"] = self.destination
            dest.bind('<FocusOut>',self.get_destination)
            dest.bind('<Key>',self.predict)
            
    
            
            self.filtre = Button(fenetre, text='Plus de filtres', command=self.filtres,style='My.TButton' )
            self.filtre.place(x=750, y=400)
            
            self.chercher=Button(fenetre, text='Comment y aller ?', command=self.tra,style='My.TButton' )
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
            
    def get_destination(self,event):
        selct = self.listpre.get('anchor')
        self.destination.set(selct)
        self.listpre.place_forget()
        self.filtre.place(x=750, y=400)
        self.chercher.place(x=750, y=600)
        self.des = self.destination.get()
        self.i = 0
        
    def get_depart(self,event):
        selct = self.listpre.get('anchor')
        self.definir.set(selct)
        self.listpre.place_forget()
        self.filtre.place(x=750, y=400)
        self.chercher.place(x=750, y=600)
        self.depart = self.definir.get()
        self.j = 0
    i = 0
    j = 0
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
        self.j +=1
            
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
    
    def dep(self):
        cadep = Frame(fenetre, width=200, height=5,borderwidth=1,style='My.TFrame') #Création du container destination
        cadep.place(x=620, y=285)
        d = Entry(cadep, text='Départ',width = 100, background = '#FFC000')
        d.pack()
        self.definir = tk.StringVar()
        # set it to some value
        self.definir.set("")
        d["textvariable"] = self.definir
        d.bind('<FocusOut>',self.get_depart)
        d.bind('<Key>',self.predict_def)
        self.depart = self.definir
    
    def geo(self):
        geoloc = gmaps.geolocate()['location']
        c = 0 #random.randint(0,9)
        self.depart = gmaps.reverse_geocode(geoloc, result_type = "")[c]['formatted_address']
        
    
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
        #pi.select()
        tc = Checkbutton(cadre_tr,text='Transports Communs',variable=self.t, command = self.sel,width = 18, onvalue =True, offvalue =False,style='My.TCheckbutton')
        tc.pack(side='left')
        #tc.select()
        au = Checkbutton(cadre_tr,text='Autolib',variable=self.a, command = self.sel,width = 11, onvalue =True, offvalue =False, style='My.TCheckbutton')
        au.pack(side='left') 
        #au.select()
        ve = Checkbutton(cadre_tr,text='Vélib',variable=self.v, command = self.sel,width = 11, onvalue =True, offvalue =False, style='My.TCheckbutton')
        ve.pack(side='left')
        #ve.select()
       
        
    def sel(self):
        s = self.p.get()+ self.t.get()+ self.a.get()+ self.v.get() 
        if s == 0 :
            self.p.set(1)
            self.t.set(1)
            self.a.set(1)
            self.v.set(1)
        
        
    def ok(self):
        self.meteo = True 
        
    def tra(self): 
        if len(self.depart) == 0 or len(self.des) == 0 : 
            erreur = Label (fenetre, text = "Merci de saisir toutes les données", style = "My.TLabel", width = 30) 
            erreur.place(x=690, y=200)
        else :    
            fra = Frame(fenetre, width = 220, height = 150, style='My.TFrame')
            fra.place(x=750, y = 650)
            progress = Progressbar(fra, orient='horizontal', length =210, mode='indeterminate')
            progress.pack()
            progress.start()
            traj = Choix_Trajet()
            traj.entrer_donnees_utilisateur(self.depart, self.des, self.meteo,self.charge,True,True, True, True)
            traj.calculer()
            optimal = traj.choix()
            self.mode = optimal.transport
            self.poly = optimal.etapes[0].poly   
            self.duree = optimal.afficher_temps()
            for etape in optimal.etapes:
                transport = etape.transport
                if transport=='transit':
                    print(etape)
                    print(etape.nom_origine)
                    print(etape.nom_destination)
                    print(etape.type_transport)
                    print(etape.poly)
            
                        #optimal.etapes[1].origine #etapes [].origine optimal.transport
            progress.stop()
            ui = Affichage (fenetre, self.depart, self.des, self.meteo, self.duree, self.dico[self.mode], self.poly)
            ui.mainloop()         
       
class Affichage(Interface):
    def __init__(self,fenetre, depart, dest, meteo, duree, mode, poly):
        Interface.__init__(self,fenetre)
        self.depart = depart
        self.des = dest
        self.meteo = meteo
        self.duree =  duree
        self.mode = mode 
        self.markers = self.get_markers()
        self.poly = poly
        self.get_static_google_map("Roadmap", imgsize=(440,440), imgformat="gif", markers = self.markers, path = self.path)
        self.create_widgets() 
        
    def create_widgets(self):
        cadre = tk.Frame (fenetre, width = 1220, height = 500, background='#FFC000')
        cadre.place(x=70, y=210)
        resultat = Label(cadre, text = "Nous vous conseillons de vous y rendre %s"%(self.mode), font=('Helvetica', 14), background = '#FFC000')
        resultat.place(x = 500, y = 30)
        depart = Label(cadre, text = "Départ : %s"%(self.depart), font=('Helvetica', 14), background = '#FFC000')
        depart.place(x=550, y = 150)
        arrivee = Label(cadre, text='Destination : %s'%(self.des), font=('Helvetica', 14), background = '#FFC000')
        arrivee.place(x=550, y = 200)
        duree  = Label(cadre, text='Durée du trajet : %s'%(self.duree), font=('Helvetica', 14), background = '#FFC000')
        duree.place(x=550, y = 100)
        #self.depart_coor = (
        #Map
        #im = Image.open("C:\\Users\Hala\Roadmap.gif")
        map = ImageTk.PhotoImage(file = "C:\\Users\Hala\Roadmap.gif") # <--- results of PhotoImage() must be stored
        map_label = tk.Label(fenetre, image=map, borderwidth = 0) 
        map_label.place(x=100, y=250)
        map_label.image = map
        
    def get_markers(self):
        marker_list = []
        '''marker_list.append("markers=color:blue|label:S|11211|11206|11222") # blue S at several zip code's centers
        marker_list.append("markers=size:tiny|label:B|color:0xFFFF00|40.702147,-74.015794|") # tiny yellow B at lat/long'''
        marker_list.append("markers=size:mid|color:red|label:Depart|" + str(gmaps.geocode(self.depart)[0]['geometry']['location']['lat']) + "," + str(gmaps.geocode(self.depart)[0]['geometry']['location']['lng']))
        marker_list.append("markers=size:mid|color:red|label:Arrivee|" + str(gmaps.geocode(self.des)[0]['geometry']['location']['lat']) + "," + str(gmaps.geocode(self.des)[0]['geometry']['location']['lng']))
        return marker_list
    
    def get_path(self):
        path_list = []
        path_list.append(str(gmaps.geocode(self.depart)[0]['geometry']['location']['lat']) + "," + str(gmaps.geocode(self.depart)[0]['geometry']['location']['lng']))
        path_list.append(str(gmaps.geocode(self.des)[0]['geometry']['location']['lat']) + "," + str(gmaps.geocode(self.des)[0]['geometry']['location']['lng']))
        return path_list
        
    def get_static_google_map(self,filename_wo_extension, center=None, zoom=None, imgsize="400x400", imgformat="gif",
                            maptype="roadmap", markers=None, path=None):  
        """retrieve a map (image) from the static google maps server 
        
        See: http://code.google.com/apis/maps/documentation/staticmaps/
            
            Creates a request string with a URL like this:
            http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512&maptype=roadmap
    &markers=color:blue|label:S|40.702147,-74.015794&sensor=false"""
    
        #https://maps.googleapis.com/maps/api/staticmap?size=400x400&path=weight:3%7Ccolor:orange%7Cenc:polyline_data&key=YOUR_API_KEY
        # assemble the URL
        request =  "http://maps.google.com/maps/api/staticmap?" # base URL, append query params, separated by &
    
        # if center and zoom  are not given, the map will show all marker locations
        if center != None:
            request += "center=%s&" % center
            #request += "center=%s&" % "40.714728, -73.998672"   # latitude and longitude (up to 6-digits)
            #request += "center=%s&" % "50011" # could also be a zipcode,
            #request += "center=%s&" % "Brooklyn+Bridge,New+York,NY"  # or a search term 
        if zoom != None:
            request += "zoom=%i&" % zoom  # zoom 0 (all of the world scale ) to 22 (single buildings scale)
    
    
        request += "size=%ix%i&" % (imgsize)  # tuple of ints, up to 640 by 640
        request += "format=%s&" % imgformat
        request += "maptype=%s&" % maptype  # roadmap, satellite, hybrid, terrain
        #request += "path=weight:3%7Ccolor:orange%7Cenc:polyline_data&" 
        #request += "key=%s"%(api_key)
    
        # add markers (location and style)
        if markers != None:
            for marker in markers:
                request += "%s&" % marker
                    
        
        request += "path=color:blue|weight:2"
        #request += "|enc:%s"%(self.poly)
    
    
        #request += "mobile=false&"  # optional: mobile=true will assume the image is shown on a small screen (mobile device)
        #request += "&sensor=false&"   # must be given, deals with getting loction from mobile device 
        print (request)
        
        urllib.request.urlretrieve(request, filename_wo_extension+"."+imgformat) # Option 1: save image directly to disk
        
        # Option 2: read into PIL 
        web_sock = urllib.request.urlopen(request) 
        imgdata = io.BytesIO(web_sock.read()) # constructs a StringIO holding the image
        try:
            PIL_img = ImageTk.Image.open(imgdata)
        
        # if this cannot be read as image that, it's probably an error from the server,
        except IOError:
            print ("IOError:", imgdata.read()) # print error (or it may return a image showing the error"
        
        # show image 
        else:
            #PIL_img.show()
            PIL_img.save("Roadmap"+".gif", "GIF") # save as jpeg


fenetre = tk.Tk()
interface = Interface(fenetre)

interface.master.title('Comment y aller ?')

interface.mainloop()

