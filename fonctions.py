#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2013 Cedric Bertrand - Orange Consulting
#
#version 4.G
import codecs
import sys
import re,base64
import xml.etree.ElementTree as ET
from datetime import datetime
from StringIO import StringIO
import shutil
import glob,os,string,subprocess,ConfigParser,os.path,getopt 
import libxml2
from xml.dom.minidom import parse

#import ConfigParser
import ConfigParser

def Config_Section_Map(section):
  dict1 = {}
  options = Config.options(section)
  for option in options:
      try:
	  dict1[option] = Config.get(section, option)
	  if dict1[option] == -1:DebugPrint("skip: %s" % option)
      except:
	  print("exception on %s!" % option)
	  dict1[option] = None
  return dict1

Config = ConfigParser.ConfigParser()
Config.read("enum.conf")
Config.sections()
######################################################
##### Définitions Outils #############################
######################################################

def Appliquer_droits(): #appliquer les droits d'exécution sur le répertoire tools
	commande = "chmod -R +x tools"
	Lancer_commande(commande)

def Suppression_temp(): #suppression des fichiers temporaires
	commande = "rm *.xml"
	Lancer_commande(commande)

def Calcul_nblignes_fichier(fichier):
	Fichier_ligne = open(fichier,"r")
	Lignes=Fichier_ligne.readlines()
	Fichier_ligne.close
	Nblignes=len(Lignes)
	return Nblignes

#Lancer une commande et enregistrer le résultat
def Lancer_commande(commande):
  #print "Lancement de la commande " + commande
  p = subprocess.Popen(commande, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  result=""
  line=""
  for line in p.stdout.readlines():
    result=result + line
  retval = p.wait()
  return result

#Récupération d'infos pour le SE
def Recup_emails(domaine,ctraces):
	#try:
	theharvester = Config_Section_Map("TOOLS")['theharvester']
      	print('Recherche emails\n')
	resultat = Lancer_commande ("python " + theharvester + " -d " + domaine + " -l 200 -b google | grep \"@" + domaine + "\" | sort -u")
	#print resultat
	Fichier_email = open(ctraces + "email.txt","w")
	Fichier_email.write(resultat)
	Fichier_email.close
	#except e:
    		#print "Erreur:", sys.exc_info()[0]
    	#	print "Erreur:", e

#Récupération noms users pour le SE
def Recup_users(domaine,ctraces):
	#try:
	theharvester = Config_Section_Map("TOOLS")['theharvester']
      	print('Recherche users\n')
	resultat = Lancer_commande ("python " + theharvester + " -d " + domaine + " -l 200 -b linkedin | grep -A 200 \'Users from Linkedin:\' | sort -u")
	Fichier_users = open(ctraces + "users_linkedin.txt","w")
	Fichier_users.write(resultat)
	Fichier_users.close
	#except e:
    	#	#print "Erreur:", sys.exc_info()[0]
    	#	print "Erreur:", e

def Extract_users(domaine,ctraces,telechargements):
	#try:
	metagoofil = Config_Section_Map("TOOLS")['metagoofil']
      	print('Extraction metadata - Attention ça peut être long selon la taille des fichiers\n')
	resultat = Lancer_commande ("python " + metagoofil + " -d " + domaine + " -t doc,docx,xls,xlsx,pdf -l 200 -n " + str(telechargements) + " -o " +ctraces + "tmp -f " +ctraces + domaine + ".html | grep -A 1000 \'processing\'")
	if not os.path.exists(ctraces + domaine + ".html"):
		print "Il y a eu un problème lors de l'extraction des méta-données"
	Lancer_commande("rm -R " + ctraces + "tmp") #nettoyage des fichiers téléchargés
	#except:
    	#	print "Erreur:", sys.exc_info()[0]

def Merge_files(file1,file2,filefinal):
	#try:
	if os.path.exists(file1) and os.path.exists(file2):
		result1 = Lancer_commande("cat " + file1 + " | sort -u")
		result2 = Lancer_commande("cat " + file2 + " | sort -u")
		Fichier_users = open(filefinal,"w")
		Fichier_users.write(result1)
		Fichier_users.write(result2)
		Fichier_users.close
		Lancer_commande("cat " + filefinal + " | sort -u > " + filefinal)
		os.remove(file1)
		os.remove(file2)
	#except:
    	#	print "Erreur:", sys.exc_info()[0]

def Generer_users(ctraces,fichier,fichier_result):
	#try:
	if not os.path.exists(ctraces+fichier):
		print ("Erreur: le fichier " + str(fichier) + " n'existe pas")		
		return
	Fichier_users = open(ctraces+fichier,"r")
	Users_all = Fichier_users.readlines()
	Fichier_users.close
	Resultat = ""
	for ligne in Users_all:
		User = ligne.lower()
		if Filtrer_mot(User)=="filtre":	User= ""
		else:
			User = User.replace(" ",".")
			User = User.replace("ç","c")
			Resultat = Resultat + User
	Resultat_tri=""
	for ligne in Resultat:
		if not Filtrer_mot(ligne)=="filtre" and (len(ligne) < 5):Resultat_tri=Resultat_tri+ligne
		ligne = ligne.replace("..",".")
	Fichier_users = open(ctraces + fichier_result,"w")
	Fichier_users.write(Resultat_tri)
	Fichier_users.close
	Lancer_commande("cat " + ctraces + fichier_result + " | sort -u > " + ctraces + fichier_result)
	if os.path.exists(ctraces+fichier):os.remove(ctraces+fichier)
	#except:
    	#	print "Erreur:", sys.exc_info()[0]

def Filtrer_mot(mot):
	liste=['executive','actuel','voir','view','poste','account','expert','specialist','manager','adjoint',':','engineer','quality','linkedin','technical', 'assistant','project','=','community','_','from','senior','professeur','users','community','expert','_','consultant','secretaire',
'expert','organizer','director','directeur','vente','marketing','descriptif','professionnel','profil','learning','account','poste','linkedin',
'users','quality','engineer','employer','digital','science','intern']
	for chaine in liste:
		if re.search(chaine,mot):return("filtre")
	return ("good")
