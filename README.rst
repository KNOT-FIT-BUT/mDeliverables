KNOT ÚPGM FIT VUT
Projekt: Deliverables2

Implementováno autory:
	- Jan Skácel <xskace08@stud.fit.vutbr.cz>
	- Pavel Novotný
	- Stanislav Heller
	- Lukáš Macko

Úvod:
*****
Tento dokument je určen pro uživatele skriptu či jeho částí, který je určen k
extrakci výstupy ze stránek různých projektů. Měl by poskytnout
dostatek informací osobám, kteří by snad chtěli tento skript upravit, opravit
či předělat.
Pro potřeby přímé přenositelnosti kódu jsou komentáře uvnitř kódu psány v
anglickém jazyce. Tento dokument je psán v češtině, kvůli zachování jazykové
sourodosti s KNOT wiki.

Požadavky:
**********
Python verze 2.x
Přítomnost nainstalované knihovny RRS

Použití jako balík skrz rozhraní:
*********************************

- Potřebujete mít balík deliverables ve Vaší python_path
- Nyní můžete importovat deliverables modul příkazem:

	from deliverables import *

- Nyní můžete utvořit objekt rozhraní (zde pro názornost inicializováno s 
počáteční url "http://siconos.inrialpes.fr/"):

deliv = deliverables.Deliverables_interface(url = "http://siconos.inrialpes.fr/")

- Nyní máte 2 možnosti, jak zahájit vyhledávání a stahování výstupů.

	1. Pokud chcete kořenový objekt RRSProject můžete použít:

		project = deliv.get_deliverables()

	2. Pokud chcete řetězec s výstupním RRS XML můžete použít:
		
		rss_xml = deliv.get_rrs_xml()

- První volání metod get_rrs_xml() nebo get_deliverables() spustí vyhledávání a
extrakci výstupů. Další volání již pouze vrátí dříve extrahovaná data. Metoda
get_rrs_xml() tak lze používat na mnoha místech bez výrazného zpomalení. Metoda
get_deliverables() v případě neúspěchu extrakce vrátí None. Metoda get_rrs_xml()
v takovém případě vrátí prázdný řetězec.



Adresářová struktura:
*********************
./ - Hlavní adresář projektu
./bin - Zde je uložen skript example.py, který by měl dát vodítko pro
	implementaci skriptů používajících modul deliverables. Dále je
	zde uložen doc.sh, což je skript v jazyce Bash, který automaticky
	vytvoří dokumentaci ve spolupráci s programem epydoc.
./bin/deliverables - Zde je uložen modul deliverables s
	hlavním programem
./data - Zde se nachází příklady výsledných xml dokumentů a soubor links, který
	obsahuje řádky oddělené url některých vybraných projektů.
./docs - Automaticky vygenerovaná dokumentace z programu epydoc


