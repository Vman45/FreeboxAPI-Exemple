#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#Twitter: @xrths

#Importation des librairies.
import requests
import json
import os
import time
import hmac
import hashlib
import sys
import copy

API_URL = "http://mafreebox.freebox.fr/api" #URL de l'API Freebox 

def AskAuthorization(): #Fonction permettant de d'établir la première connexion.
	payload = {'app_id': 'fr.xrths.ota', 'app_name': 'Freebox - Monitoring', 'app_version': '1', 'device_name': 'Twitter: @xrths'} #Charge utile pour l'API.
	payload = json.dumps(payload) #Mise sous forme JSON de la charge utile pour l'envoie.

	directory = API_URL + "/v6/login/authorize/" #Création de l'URL pour appel de l'API.
	call_api = requests.post(url = directory, data = payload) #Appel de l'API avec la méthode POST.
	reponse = call_api.json() #Mise sous forme JSON de la réponse de l'API.

	file=open('app_token.txt','w') #Ouverture & création si n'existe pas du fichoer app_token.txt.
	file.write(reponse['result']['app_token']) #Écriture de l'app_token dans le fichier texte.
	file.close() #Fermeture du fichier texte.

	CheckAuthorization(reponse['result']['track_id']) #On change de fonction en appelant la fonction en dessous avec le 'track_id'.


def CheckAuthorization(track_id): #Fonction permettant de voir l'état de l'autorisation.
	track_id = str(track_id) #Mettre le 'track_id' sous forme de valeur string.

	def call(track_id): #Fonction permetant d'appeler l'API avec un 'track_id'.
		directory = API_URL + "/v6/login/authorize/" + str(track_id) #Création de l'URL pour appel de l'API.
		check_api = requests.get(url = directory) #Appel de l'API avec la méthode GET.
		reponse = check_api.json() #Mise sous forme JSON de la réponse de l'API.
		status = reponse['result']['status'] #On parse la réponse JSON pour récuperer le 'stauts'.
		return status #On renvoie le 'status'.

	status = call(track_id) #On définie le status pour la boucle si dessous. 
	while (status == 'pending'): #Cette boucle permet de gérer toutes les réponses possibles de l'API.
		call(track_id)
		status = call(track_id)

		if status == 'granted': #Accès autorisé.
			os.system('clear') #Nettoyage de la console (seulement Linux, OSX).
			print "Connexion réussi." #Message utilisateur.
			print "Veillez à bien donner les permissions 'Modification des réglages de la Freebox' (sinon le programme foctionnera très mal) dans:\n" + "'Paramètres de la Freebox' > 'Mode avancé' > 'Gestion des accès' > 'Éditer' > Donner les permissions" #Message utilisateur.
			raw_input("Appuyez sur une touche lorsque c'est fait...")
			MakeSession() #On continue en appelant la fonctoion 'MakeSession()'.

		elif status == 'pending': #En attente de connexion.
			os.system('clear') #Nettoyage de la console (seulement Linux, OSX).
			print "Veuillez vous rendre à votre Freebox Server et valider la connexion de l'application." #Message utilisateur.
			print "Vérification toute les 3 secondes." #Message utilisateur.
			time.sleep(3) #Pause de 3 secondes.

		elif status == 'denied': #Accès réfusé. 
			os.system('clear') #Nettoyage de la console (seulement Linux, OSX).
			os.remove('app_token.txt') #On supprime le fichier 'app_token.txt'.
			print "La connexion a été réfusée." #Message utilisateur.

		elif status == 'timeout': #Connexion time-out.  
			os.system('clear') #Nettoyage de la console (seulement Linux, OSX).
			print "Connexion timeout, veuillez contacter le créateur du programme." #Message utilisateur

		elif status == 'unknown': #Autre problème.
			os.system('clear') #Nettoyage de la console (seulement Linux, OSX).
			print "Erreur, redémarrez votre freebox ainsi que ce programme." #Message utilisateur.


def GetPassword(): #Fonction permettant de créer le 'password'. 
	challenge = requests.get(url = API_URL + '/v6/login/') #Création de l'URL et appel de l'API avec la méthode GET.
	challenge = challenge.json() #Mise sous forme JSON de la réponse de l'API.
	challenge = challenge['result']['challenge'] #On parse la réponse pour récuper la valeur 'challenge'.

	file = open('app_token.txt', 'r') #On ouvre le fichier 'app_token.txt'.
	app_token = file.read() #On lit son contenu.

	password = hmac.new(app_token,challenge,hashlib.sha1).hexdigest() #On calcule le hmac-sha1 avec l'APP_TOKEN et le CHALLENGE.
	return password #On retourne le mot de passe.


def MakeSession(): #Fonction permettant d'avoir un token pour faire des appels d'API.

	def CheckAppToken(): #Fonction permettant de vérifier que le fichier 'app_token.txt'.
		directory = 'app_token.txt' #On défini le fichier à checker.
		if not os.path.exists(directory): #On check et si il n'existe pas: 
			AskAuthorization() #On appelle la fonction de départ.

	CheckAppToken() #Appel de fonction 'CheckAppToken()'

	directory = API_URL + "/v6/login/session/" #Création de l'URL et appel de l'API.

	payload = {"app_id": "fr.xrths.ota", "password": GetPassword()} #Charge utile pour l'API.
	payload = json.dumps(payload) #Mise sous forme JSON de la charge utile pour l'envoie.

	call_api = requests.post(url = directory, data = payload) #Création de l'URL et appel de l'API avec la méthode JSON. 
	reponse = call_api.json() #Mise sous forme JSON de la réponse de l'API.

	if reponse['success'] == False: #On parse la réponse pour vérifier si 'success' est égal à False.
		os.remove('app_token.txt') #On supprime 'app_token.txt'.
		os.system('clear') #Nettoyage de la console (seulement Linux, OSX).
		print ("Une erreur de connexion est survenue, veuillez vous rendre dans le panel 'mafreebox.freebox.fr':\n" + "'Paramètres de la Freebox' > 'Mode avancé' > 'Gestion des accès' > 'Applications' et révoquer l'accès à 'Freebox Monitoring'.\n" + "Puis relancez le programme.") #Message utilisateur.
		sys.exit() #On ferme le programme.
	elif reponse['success'] == True: #On parse la réponse pour vérifier si 'success' est égal à True.
		return reponse['result']['session_token'] #On retourne la valeur 'session_token'.


def CloseSession(session): #Fonction permettant de terminer la session après utilisation.
	directory = API_URL + "/v6/login/logout/" #Création de l'URL et appel de l'API.
	headers = {'X-Fbx-App-Auth': session} #Création du HEADER.
	reponse = requests.post(directory, headers=headers) #Envoie de la requête en POST.


###EXEMPLE D'UTILISATION###

def GetApiVersion(configuration):
	session = copy.deepcopy(MakeSession()) #On copie le token pour pouvoir l'utilser deux fois.
	directory = 'http://mafreebox.freebox.fr' + "/api_version" #Création de l'URL et appel de l'API.
	headers = {'X-Fbx-App-Auth': session} #Création du HEADER.
	reponse = requests.get(directory, headers=headers) #Envoie de la requête en GET.
	reponse = reponse.json() #Mise sous forme JSON de la réponse de l'API.
	CloseSession(session) #Toujours fermer la session, sinon le programme risque de planter à cause d'un refus de l'API.
	
	configuration = str(configuration)

	if configuration == 'https_port': 
		return reponse['https_port']
	elif configuration == 'box_model':
		return reponse['box_model']
	elif configuration == 'device_name':
		return reponse['device_name']
	elif configuration == 'https_available':
		return reponse['https_available']
	elif configuration == 'api_version':
		return reponse['api_version']
	elif configuration == 'device_type':
		return reponse['device_type']
	elif configuration == 'uid':
		return reponse['uid']
	elif configuration == 'api_domain':
		return reponse['api_domain']
	elif configuration == ['api_base_url']:
		return reponse['api_base_url']
	elif configuration == ['box_model_name']:
		return reponse['box_model_name']
	else:
		print("Erreur, la configuration spécifiée ne fonctionne pas.")

print GetApiVersion('device_name') #Print de la fonction d'exemple.