#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This code should serve as an example of how to use deliverables2
as a module using its threading api. Added monitor support.
"""

# Import deliverables
from deliverables.thread import *
# Import URL monitor
#from rrslib.web.changemonitor import Monitor
from rrs_page_change_monitoring import Monitor

# Example of threading deamon

# Load iterator and establish connection to database (if no db connection is given, it is expected to run on localhost:)
daemon = Deliverables_daemon(8,
[
	"http://2wear.ics.forth.gr/"
	,"http://adapt.ls.fi.upm.es/adapt.htm"
	,"http://agentacademy.iti.gr/"
	,"http://ametist.cs.utwente.nl/"
	,"http://aris-ist.intranet.gr/"
	,"http://benogo.dk/"
	,"http://bind.upatras.gr/"
	,"http://cic.vtt.fi/projects/elegal/"
	,"http://cmp.felk.cvut.cz/projects/omniviews/"
	,"http://context.upc.es"
	,"http://cortex.di.fc.ul.pt/"
	,"http://danae.rd.francetelecom.com/"
	,"http://dip.semanticweb.org/"
	,"http://muchmore.dfki.de/"
	,"http://qviz.eu/"
	,"http://recherche.ircam.fr/projects/SemanticHIFI/wg/"
	,"http://research.ac.upc.edu/catnet/"
].__iter__(),
monitor = Monitor(user_id="rrs_university"))

""","http://www.argonaproject.eu/"
,"http://www.artist-embedded.org/"
,"http://www.asisknown.org/"
,"http://www.awissenet.eu/"
,"http://www.bootstrep.eu/"
,"http://www.consensus-online.org/"
,"http://www.cvisproject.org/"
,"http://www.diadem-firewall.org/"
,"http://www.elu-project.com/"
,"http://www.epros.ed.ac.uk/mission/"
,"http://www.equimar.org/"
,"http://www.euro-cscl.org/site/itcole/"
,"http://www.fusionweb.org/fusion/"
,"http://www-g.eng.cam.ac.uk/robuspic/"
,"http://www.imec.be/impact/ "
,"http://www-interval.imag.fr/"
,"http://www.ist-gollum.org/"
,"http://www.ist-opium.org/"
,"http://www.ltg.ed.ac.uk/magicster/"
,"http://www.mescal.org/"
,"http://www.mpower-project.eu/"
,"http://www.mtitproject.com"
,"http://www.nlr.nl/public/hosted-sites/hybridge/"
,"http://www.ofai.at/rascalli/"
,"http://www.s-ten.eu/"
,"http://www.umsic.org/"
,"http://io.intec.ugent.be/"
,"http://siconos.inrialpes.fr/"
,"http://context.upc.es/"
,"http://www.ist-mascot.org"
,"http://www.6net.org/"
,"http://www.cwi.nl/projects/mascot/"
,"http://www.ana-project.org/"
,"http://www.multimatch.eu/"
,"http://www.ist-iphobac.org/"
,"http://www.bacs.ethz.ch/"
,"http://metokis.salzburgresearch.at/index.html"
,"http://dip.semanticweb.org/"
,"http://mexpress.intranet.gr/"
,"http://www.stork.eu.org/"
,"http://www.mg-bl.com/"
,"http://www.irt.de/mhp-confidence/"
,"http://www.ist-sims.org"
,"http://www.ist-discreet.org"
,"http://www.safespot-eu.org"
,"http://www.safespot-eu.org"
,"http://www.mhp-knowledgebase.org/"
"""
# Parsing and writing to database
daemon.parse()

# Checking for fatal error (most errors are recoverable, some like unhandeled
# exception in thread or no db connection are not)
if daemon.isErr():
	print daemon.isErr()
