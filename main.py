#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2014 Cédric BERTRAND
#
import codecs
import sys
import re,base64,os
import xml.etree.ElementTree as ET
from datetime import datetime
from StringIO import StringIO
import shutil
import glob,os,string,subprocess,ConfigParser,os.path,getopt 
import libxml2
from xml.dom.minidom import parse
import getopt
import fonctions 	#importation du fichier contenant le fonctions utilisées dans le script
#import nessus		#importation du fichier contenant le parsing des rapports nessus
import argparse

version="1"

def analyse(domaine,ctraces):
	if not (os.path.isdir(ctraces+"/"+domaine)):os.mkdir(ctraces+"/"+domaine)
	tmp_domain=ctraces+domaine+"/"
	fonctions.Recup_emails(domaine,tmp_domain)
	fonctions.Recup_users(domaine,tmp_domain)
	fonctions.Generer_users(tmp_domain,"users_linkedin.txt","user_gen.txt")
	fonctions.Extract_users(domaine,tmp_domain,telechargements)
	fonctions.Generer_users(tmp_domain,domaine+".html_users","user_gen_meta.txt")
	fonctions.Merge_files(tmp_domain+"email.txt",tmp_domain+domaine+".html_emails",tmp_domain+"emails.txt")
	fonctions.Merge_files(tmp_domain+"user_gen.txt",tmp_domain+"user_gen_meta.txt",tmp_domain+"users.txt")
	#fonctions.Merge_emails(ctraces+"email.txt",ctraces+"probtp.com.html_emails",ctraces+"email.txt")
	print "--------------------------------"
	print "--------------------------------"
	print "\nGénération terminée\n"
	print "--------------------------------"
	print "--------------------------------"
	print "\nFichier des noms utilisateurs:" + str(tmp_domain+"users.txt") +"\n"
	users=fonctions.Lancer_commande("cat " + tmp_domain+"users.txt")
	print users
	print "\nFichier des adresses emails:" + str(tmp_domain+"emails.txt") +"\n"
	emails=fonctions.Lancer_commande("cat " + tmp_domain+"emails.txt")
	print emails
	if os.path.exists(tmp_domain+domaine+".html"):os.remove(tmp_domain+domaine+".html")

def usage():
	print "\nEnum_users version: " + str(version) + " bypar Cédric BERTRAND\n"
	print "Recherche des adresses emails, génération de noms utilisateurs liés à un domaine"
	print "Recherche des emails sur google, recherche noms utilisateurs sur linkedin, extraction des meta-données des documents accessibles publiquement sur un site"
	print "\nUsage\n"
	print "./main.py --domaine=<nom_domaine> --telechargements=<nb_de_fichier> --output=<repertoire de sortie>"
	print "\nOptions:\n"
	print "--domaine=<domaine> : Domaine à analyer"
	print "--liste=<fichier> : Liste de domaine à analyser (fichier)"
	print "--output=repertoire : Répertoire où les données seront enregistrées. Par défaut répertoire crée dans le répertoire result de l'outil"
	print "--telechargements=<nb_de_fichiers> : Nombre de fichiers à télécharger pour l'extraction des métas-données (par défaut 30)"
	print "\nExemple : ./main.py --domaine=probtp.com --telechargements=50 --output=/home/result/"

	sys.exit(1)


# Parse Arguments##################################################
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--domaine", help="Domaine à analyer", nargs='*')
parser.add_argument("-o", "--output", help="Répertoire où les données seront enregistrées. Par défaut répertoire crée dans le répertoire result de l'outil", nargs='*')
parser.add_argument("-t", "--telechargements", help="Nombre de fichiers à télécharger pour l'extraction des métas-données (par défaut 20)", nargs='*')
parser.add_argument("-l", "--liste", help="Liste de domaines à analyser (fichier)", nargs='*')
parser.add_argument("-a", "--aide", help="Aide", nargs='*')
args = parser.parse_args()
###################################################################

################################        
if __name__ == "__main__":
  if(len(sys.argv) < 2):
    usage()
    sys.exit(1)
print args
print ""


fonctions.Appliquer_droits() #Vérifier que les droits d'exécution sont bien mis dans le répertoire tools
print "\n Début du script \n"

if args.aide:
	usage()
	sys.exit(1)

if not args.domaine and not args.liste:
	print "\nVous devez indiquer un domaine à analyser ou un fichier contenant les domaines à analyser\n"
	usage()

if args.domaine and args.liste:
	print "\nVous devez indiquer un domaine à analyser ou un fichier contenant les domaines à analyser (pas les 2)\n"
	usage()

if args.telechargements:telechargements=' '.join(args.telechargements)
else: telechargements=20


if args.output:	
	ctraces = ' '.join(args.output)
	if not (ctraces[-1:])== "/":ctraces=ctraces+"/"
	if not (os.path.isdir(ctraces)):os.mkdir(ctraces)
else:
	if not (os.path.isdir("result")):os.mkdir("result")
	#if not (os.path.isdir("result/"+domaine)):os.mkdir("result/"+domaine)
	#ctraces="result/"+domaine+"/"
	ctraces="result/"
	#global ctraces
	#chemin = os.path.split (' '.join(args.nessus))
	print "\nRépertoire d'enregistrement "+ ctraces + "\n"

if args.domaine:
	domaine = ' '.join(args.domaine)
	if re.search("http",domaine) or re.search("www",domaine):
		print ("Vous devez indiquer un domaine, pas un site web")
		usage()
	else:
		print "--------------------------------------------------"
		print "\nDomaine analysé: ", ' '.join(args.domaine)+"\n"
		print "--------------------------------------------------"
		analyse(domaine,ctraces)

if args.liste:
	liste = ' '.join(args.liste)
	if not os.path.exists(liste):
		print "Le fichier " + str(liste) + " n'existe pas"
		sys.exit(1)
	else:
		#try:
		fichier_domaines = open(liste,"r")
		domaines_all = fichier_domaines.readlines()
		fichier_domaines.close
		nbdomaines_total = len(domaines_all)
		print "\n Il y a " + str(nbdomaines_total)+" domaines à analyser\n"
		nbdomaine=0
		for ligne in domaines_all:
			domaine = ligne.lower()
			domaine=domaine.replace("http://","")
			domaine=domaine.replace("https://","")
			domaine=domaine.replace('\n', '')
			#if not (domaine[-1:])== "/":domaine=domaine
			nbdomaine=nbdomaine+1
			print "\nAnalyse du domaine " + str(nbdomaine) + " \ " + str(nbdomaines_total)
			print "--------------------------------------------------"
			print "Domaine analysé: "+str(domaine)
			print "--------------------------------------------------"
			analyse(domaine,ctraces)
		print "\n Analyse terminée"
		#except:
   		#	print "Erreur:", sys.exc_info()[0]

fonctions.Suppression_temp()#suppression des fichiers temporaires
