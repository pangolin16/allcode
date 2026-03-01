def remove_duplicate_lines(str_data):
    """
    Remove lines that appear more than once in the input string.
    Only keeps lines that appear exactly once.
    """
    # Split the string into lines
    lines = str_data.strip().split('\n')
    
    # Count occurrences of each line
    line_counts = {}
    for line in lines:
        line_counts[line] = line_counts.get(line, 0) + 1
    
    # Keep only lines that appear exactly once
    unique_lines = [line for line in lines if line_counts[line] == 1]
    
    # Join back into a string
    return '\n'.join(unique_lines)

# Example usage:
str_data = """1319
1519
1786
2345
2748
3014
3017
3088
3178
3217
3218
3587
3596
3653
3661
4129
4953
6143
6538
6643
6690
6758
6857
8426
1st Source Corporation
92 MNG Inc.
A&D Holon Holdings
A10 Networks, Inc.
A2M
AAK
AAON
Abbott Laboratories
Abercrombie & Fitch Co
Abercrombie & Fitch Co
Abu Dhabi Islamic Bank
ABU DHABI ISLAMIC BANK- EGYPT
ACCELLERON
Accton Technology
ACCTON TECHNOLOGY CORPD
ACER CYBER SECURITY INC
ACER E-ENABLING SERVICE BUSINESS IN
ACM Research, Inc.
ACTER GROUP CORPORATION LTD
Acuity Inc.
ADDTECH AB SER. B
Addus
ADF Foods
ADMIRAL GROUP PLC
ADNOC Drilling Company PJSC
ADNOC Logistics & Services plc
Adtalem Global Education Inc.
Adtalem Global Education Inc.
ADVANCED INFO SERVICE PUBLIC CO
ADVANCED POWER ELECTRONICSD
ADVANTEST CORPD
ADVTECH LTD
adyen
Aekyung Industrial
aena
AFYA
Agco
AGESA HAYAT EMEKLILIK
agi
Agilysys
AGNICO EAGLE MINES LTD
Agnico Eagle Mines Ltd
AIA GROUP LIMITEDD
AIRBUS SE
Airbus SE
AIRPORTS OF THAILAND PUBLIC CO
AIRTAC INTERNATIONAL GROUPD
AIXTRON
AJ BELL PLC ORD GBP
ako-b
AL MAWARID MANPOWER CO.D
Al Salam Bank B.S.C.
AL-BABTAIN POWER AND TELECOMMUNICATION CO.D
alamo
Alamos Gold
Alarm.com Holdings, Inc.
Alaska Air
alb
ALBARAKA TURK
alerion
ALFA FINANCIAL SOFTWARE HLDGS PLC ORD GBP
ALCHIP TECHNOLOGIES LIMITDD
ALK-ABELLO B A/S
Alkermes Plc
Alkermes Plc
ALKHORAYEF WATER AND POWER TECHNOLOGIES COD
Allegion
Allegro Microsystems
Allient
Allstate Corporation (The)
ALMASANE ALKOBRA MINING COD
Alphabet Inc.
AlphaPolis Co
ALS
Alten
Alten
Altium
ALTRI SGPS
ALZCHEM GROUP AG
Amada Co
amadeus it
AMADEUS IT GROUP, S.A.
Amalgamated Financial Corp.
Amano
amat
Amazon.com, Inc.
amdocs
American Coastal Insurance Corporation
AMETEK, Inc.
AMG ADVANCED
amgen
Amgen
Amphastar
Amvis Holdings
ANADOLU HAYAT EMEKL.
ANADOLU SIGORTA
Andritz
ANEKA TAMBANG
Anest Iwata
ANTIN INFRASTRUCTURE PARTNERS
ANYCOLOR INCD
ANYMIND GROUP INCD
APEX MINING COMPANY, INC.
APP INC
APP INC
AppFolio, Inc.
AppFolio, Inc.
Applied Industrial Technologies
Applovin Corporation
ARAB NATIONAL BANKD
ARABIAN INTERNET AND COMMUNICATIONS SERVICES CO.D
ARBITRAGED
ARC RESOURCES LTD
Arcadyan Technology
arco/nvt
Area Group Ltd
Argan, Inc.
Argan, Inc.
Arhaus
Aristocrat Leisure
Aritzia
ARIZON RFID TECH (CAYMAN) CO LTDD
Arm Holdings plc
Arm Holdings plc
Armstrong World Industries Inc
ARNK
ARTECHE LANTEGI ELKARTEA, S.A.
Artner Co
Asahi Intecc
Asahi Yukizai
ASEL
ASELSAN
ASIA VITAL COMPONENTS CO LTDD
ASMEDIA TECHNOLOGY INCD
ASROCK INCORPORATIOND
ASTER ENERGI
ASTOR ENERJI
ASTRA OTOPARTS TBK
ASTRAZENECA PLC ORD USD
ASUSTEK COMPUTER INCD
asx:cpu
ATHABASCA OIL CORP
ATI Inc.
Atlas Engineered Products
Atmus Filtration Technologies Inc.
ATOSS SOFTWARE SE
ATS
AUBAY
AURAS TECHNOLOGY CO
AURORA DESIGN PCL
Aussie Broadband
AUSTEVOLL SEAFOOD ASA
AUSTRALIAN ETHICAL INVESTMENT LIMITED
autoliv
AVANZA BANK HOLDING AB
Avery Dennison Corporation
AVI LTD
Avista Energy S.A.B. de C.V.
AVNW/nvt
Axcelis Technologies
Axis Capital Holdings Limited
axon
Axon Enterprise
axp
AYEN
AZBIL CORPD
AZZ
B3 ON NM
BABCOCK INTERNATIONAL GROUP ORD GBP
Badger Infrastructure
BADGER INFRASTRUCTURE SOLUTIONS LTD
Badger Meter, Inc.
BAE Systems
Baker Hughes Company
BANCA MEDIOLANUM
Banca Transilvania Cluj Napoca
BANCO HIPOTECAIRO SA
BANGKOK DUSIT MEDICAL SERVICES
BANK AL-HABIB LTD
BANK CENTRAL ASIA
BANK KENYA PLC
BANK OF THE PHILIPPINE ISLANDS
BANK SYARIAH INDONESIA TBK
Barco NV
Base Co
BASE CO LTDD
BASILEA
Baudroie
BAUDROIE INCD
BayCurrent Consulting
BAYCURRENT INCD
BBVA BANCO FRANCES
BDO UNIBANK, INC.
Beauty Garage
BEAZLEY PLC (UK) ORD GBP
Bechtle
BEIERSDORF AG
BEIERSDORF AG
BEIJER ALMA AB SER. B
Belc Co
Belimo Holding
Bellring Brands
Bengcon AB Ser. B
Bengo4.com
Betsson
better collective
BEXIMCO PHARMACEUTICALS LTD
BFF BANK
BHI CO., LTD.D
Biesse
BIM MAGAZALAR
BINASTRA CORPORATION BERHAD
BINGGRAED
Biosyent
Bird Construction
BIZLINK HOLDING INCD
BlackLine, Inc.
BlackLine, Inc.
Blackstone Inc.
BLAU ON NM
Block, Inc.
BLOOMSBURY PUBLISHING ORD GBP0.0125
Blue Bird Corporation
Blue Star
bme:fer
bme:vid
bmv:ac
Bodycote
BOLSA MEXICANA DE VALORES SAB DE CV
Booz Allen Hamilton Holding Corporation
BORA PHARMACEUTICALS CO LTD
Borouge PLC
BORREGAARD
BOURSA KUWAIT SECURITIES CO KPSC
Bowhead Specialty Holdings Inc.
Box, Inc.
Box, Inc.
Boyd Gaming
Boyd Services
Brambles
BRASILAGRO ON NM
Braysearch Laboratories AB Ser. B
Brederode
Breljers AB Ser. B
brembo
BREVILLE GROUP LIMITED
Brown & Brown, Inc.
BRP
BRP
BTS GROUP AB SER. B
BUA FOODS PLC
Bufab
Bucher Industries
BURCKHARDT
Burckhardt Compression Holding
BUREAU VERITAS
BUYSELL TECHNOLOGIES CO LTDD
buzzi
bvmf:wege3
BWX Technologies, Inc.
BYTES TECHNOLOGY GROUP PLC ORD GBP0.01
C Rad
C. UYEMURA & CO.LTDD
C&C International
Cadre Holdings
CAE
CAFE CORP.D
CAIRN HOMES PLC ORD EUR0.001 (CDI)
CAIXA SEGURION EDR NM
Calian
Calibre Mining
California Resources Corporation
Camtek Ltd.
Camurus
Canadian Pacific Kansas
Cantaloupe, Inc.
Capcom
Capital Bancorp, Inc.
Capital City Bank Group
CAPITEC BANK HLDGS LTD
CAPRICORN METALS LTD
Car
CARABAO GROUP PUBLIC COMPANY LTD
Cargotec
Cargotec
Carlo Gavazzi
Carpenter Technology Corporation
CASTLES TECH CO LTDD
Catalyst Pharmaceuticals, Inc.
CAVA Group, Inc.
CBIZ
ccep
ccj
CCL INDUSTRIES INC
CE Info Systems
CECO Environmental
Celestica
Celestica
CELLAVISION AB
CENERGY
Cenit
Central Automotive Products
Centrus Energy Corp.
Centurion
CENTURY PACIFIC FOOD, INC.
CERILLION PLC ORD GBP0.005
CICOR TECH
Cicor Technologies
Ciena
Cimpress plc
Cirrus Logic, Inc.
Cirrus Logic, Inc.
CISARUA MOUNTAIN DAIRY TBK
cl
Clarkson
CLAS OHLSON AB SER. B
CLASSYS INC.D
CLEANAWAY COMPANY LIMITEDD
Clear Secure, Inc.
Climb Global Solutions, Inc.
Clinuvel Pharmaceuticals
Clio Cosmetics
clmb
CMC MARKETS ORD GBP0.25
Coastal Financial Corporation
Coca Cola HBC
Coca-Cola Femsa S.A.B. de C.V.
CODAN LIMITED
Cohen & Steers Inc
Coinbase Global, Inc.
Coinbase Global, Inc.
COM7 PUBLIC CO LTD
Comer Industries
COMFORT SYSTEMS
Comfort Systems Usa
Comfort Systems USA, Inc.
COMM BK OF DUBAI
COMMERCIAL INTERNATIONAL BANK-EGYPT (CIB)
Community Trust Bancorp, Inc.
Compania de Distribucion Integral Logista Holdings, S.A.
COMPANIA DE MINAS BUENAVENTURA SA
CompuGroup
Computershare
Comture
Constellation Energy Corporation
Constellation Energy Corporation
CONSTELLATION SOFTWARE INC
Construction Partners
ContextVision
CONTINENTAL SAB DE CV
CONVERGE INFORMATION AND COMMUNICATIONS TECHNOLOGY SOLUTIONS, INC
copart
Corcept Therapeutics Incorporated
CORDIANT DIGITAL INFRASTRUCTURE LTD ORD NPV
Core & Main, Inc.
Corporate Travel Management
CORPORATIVA FRAGUA
Cosel Co
COSMAX, INC.D
Cosmecca Korea
COSMOS PHARMACEUTICAL CORPD
CoStar Group
COVER CORPORATIOND
CRA International, Inc.
Crane Company
Credicorp Ltd.
Credicorp Ltd.
Creek & River
CROWELL DEVELOPMENT CORPD
CSW Industrials
CTBC FINANCIAL HOLDINGS COMPANY LTDD
CTS Eventim AG & Co
CTS Eventim AG & Co. KGaA
Curtiss-Wright
cvco
CWCO
Cyber Security Cloud
CYBERFLKS
Cyberoo
DAEJOO ELECTRONIC MATERIALS CO., LTD.D
DAI NIPPON PRINTING COD
DAI-DAN CO LTDD
DAI-ICHI LIFE HOLDINGS INCD
DAIICHI SANKYO COMPANY LIMITEDD
DAIICHIKOSHO COD
DAIKOKUTENBUSSAN COD
Daiseki
Daiseki Eco Solution
DAIWABO HOLDINGS CO LTDD
Dalmia Bharat
dampskibsselskabet Norden A/S
Darktrace
Darktrace
DASSAULT AVIATION
Data#3
Dave & Buster's Entertainment
Dave & Buster's Entertainment
DAYANG ENTERPRISE HOLDINGS BHD
DB INSURANCED
DBS
Delfingen Industr
Dell Technologies Inc.
Dell Technologies Inc.
Delta Electronics
DEME GROUP
Dentsu Soken
Descartes Systems
DEUTSCHE BOERSE AG
Deutz
Deutz
DEXERIALS CORPORATIOND
Diamondback Energy, Inc.
Diamondback Energy, Inc.
Dick's Sporting Goods Inc
Dick's Sporting Goods Inc
Digi International
Digital Arts
Digital Value
DiRadimed Corporation
DIS-CHEM PHARMACIES LTD
DO & CO AG
DOCEBO INC
Dolby Laboratories
Dolby Laboratories
Dollarama
DOLLARAMA INC
Domino's Pizza Inc
DONGKOOK PHARMACEUTICAL CO.,LTD.D
DONGSUNG FINETEC CO., LTDD
Dongwon F & B
Doosan Bobcat
Dorman Products, Inc.
DoubleDown Interactive Co., Ltd. - American Depository Shares
DOUBLEUGAMESD
DoubleVerify Holdings
Douglas Dynamics, Inc.
Douglas Dynamics, Inc.
dover
Doximity, Inc.
DR. SULAIMAN AL HABIB MEDICAL SERVICES GROUPD
Drewloong Precision
DREWLOONG PRECISION INCD
DTS
DTS Share
DUK SAN NEOLUX CO.,LTDD
Dundee Precious Metals
Duolingo, Inc.
Duratec
DXP Enterprises
Dycom Industries
Dynatrace, Inc.
Dynavox Group AB
Ebara
EBOS
ebr:die
Ebro
Eckert & Ziegler SE
Eclerx Services
Ecolab Inc.
Ecolab Inc.
Edenred
EGUARANTEE INC.D
EIH Associated Hotels
Einhell Germany AG
el en spa
EL PUERTO DE LIVERPOOL
Elecnor
ELECOM COD
Elecon Engineering
Electrolux Professional
Electromed
ELF BEAUTY
Eli Lilly and Company
ELITE MATERIAL COD
Elixirr International
Elmos Semiconductor
Elopak ASA
Elswedy Electric
EM SYSTEMS CO LTDD
eme
EMEMORY TECHNOLOGY INC.
Emmi AG
Encompass Health Corporation
Enersys
Enersys
Ensign
Environmental
epa:dsy
ePlus
Equasens
Equity Group Holdings PLC
Erie Indemnity Company
Esautomotion
Esco Technologies
Esco Technologies
Espec
EssilorLuxottica SA
ETIHAD ETISALAT CO.D
etr:bc8
etr:fph
etr:g1a
etr:G24
etr:na9
etr:Sie
EUGENE TECHNOLOGY CO., LTD.D
eurofins
Euronet Worldwide, Inc.
Evercore Inc.
EVERLIGHT ELECTRONICS COD
Evs Broadcast Equipment
EVT
Exelixis, Inc.
exls
Exlservice Holdings
exor
Expedia Group, Inc.
Experian PLC Ord USD
Extendicare Inc. CDA
extr
Fabasoft
Fabrinet
Fair Isaac Corporation
FAR EASTONE TELECOMMUNICATIONSD
FAST
Fauji Cement Co. Ltd.
Fauji Fertilizer Co Ltd
FDC International Hotels
Federal Signal
Ferrari
Ferreycorp SA
Ferrovial SE
Fibergate
Fidelity Bank PLC
FINANCIAL PARTNERS GROUP CO LTDD
FinecoBank
Finning International
Finolex Cables
First Resources
First Solar, Inc.
First Solar, Inc.
Five Point Holdings
Fixstars
FlatexDegiro AG
FLEETCOR TECHNOLOGIES
Flotek Industries, Inc.
Flowserve
Flowserve
Fluor Corporation
Fonix PLC Ord GBP
Food Empire Holdings
Foraco International
Fortec
Fortinet, Inc.
Fortinet, Inc.
Fortnox
Fortnox
Fortune Electric
FORTUNE ELECTRIC CO LTDD
FORUM ENGINEERING INCD
Fourlis
FOXSEMICON INTEGRATED TECHNOLOGY IND
FPT Corporation
fra:bo4
fra:lto
Fractal Gaming AB
FreeBit Co
FreeBit Co
Freelance.com
Frequentis AG
Fresenius Medical Care AG
Fresenius SE & Co KGAA O.N.
Friedrich Vorwerk Group SE
Frontdoor, Inc.
Frontken Corporation BHD
Frp Advisory
ftdr
FTI Consulting
Fugro
fuchs
FUJI ELECTRIC CO. LTD.D
Fuji Kyuko Co
Fuji Oil Holdings
FUJIKURAD
FUJIMI INCD
FURUNO ELECTRIC COD
FURUYA METAL CO LTDD
Furyu
FUSHENG PRECISION CO LTDD
Futu Holdings Limited
FUTURE CORPORATIOND
G- HOLDINGS INCD
G8 Education
Gakujo Co
Galliford Try Holdings PLC Ord GBP
Gambling.com Group Limited
Games Workshop Group Ord GBP
Gamma Communications PLC Ord GBP
GAS ARABIAN SERVICES CO.D
Gatenationgate Holdings Berhad
GB Bank Financial Holdings Inc.
GBG ENERGY AGD
GCC SAB de CV
GE HealthCare Technologies Inc.
GEA AG
General Dynamics Corporation
Generation Development Group Limited
GENESYS LOGIC
GENIUS ELECTRONIC OPTICAL CO.LTDD
Genmab A/S
Genomma Lab Internacional SAB
GenOway S.A.
Gentera SAB de CV
Gentex
Genting Singapore
GenusPlus Group Ltd
Georg Fischer
Georg Fischer
Gerard Perrier Industrie
Gestamp Automocion
GETAC HOLDINGS CORPD
GIFT Holdings
Giftee
Giga Prize Co
GIGA-BYTE TECHNOLOGY COD
GigaCloud Technology Inc
Gilat Satellite Networks
Gilead Sciences, Inc.
Gilead Sciences, Inc.
Glanbia
Glenveagh Properties PLC
GLOBAL PMX CO LTDD
Global Security Experts
Global Ship Lease Inc New
GLOBAL UNICHIP CORP.D
Globant
Globus Medical
Gmm Pfaudler
GMO FINANCIAL GATE INCD
GMO PAYMENT GATEWAY INCD
Gold Fields Ltd
GOLDEN FRIENDS CO
goog
Goosehead Insurance, Inc.
Gorman-Rupp Co
GPO AEROPORTUARIO DEL SURESTE SAB
GQG Partners Inc.
Grand Canyon Education, Inc.
GRAND PHARMACEUTICAL GROUP LTDD
Greencore
Greggs Ord GBP
Grenevia
Greneviad
Group 1 Automotive
Gruma SAB de CV
Grupo Aeroportuario
Grupo Catalana Occidente, S.A.
Grupo Empresarial San Jose, S.A.
Grupo Financiero Galicia SAD
GRUPO HERDEZ
GRUPO HOTELERO SANTA
Grupo Inversiones Suramericana
Grupo Mateus ON NM
Grupo Mexico SAB de CV
Grupo SBF On NM
Grupo Supervielle S.A.
Grupracu JD
GS Yuasa
Guan Chong BHD
GUD Holdings
H Hotel Leasehold REIT
Haemonetics
Hai An Transport and Stevedoring Joint Stock Company
Halows Co
Halozyme Therapeutics, Inc.
Hammond Power Solutions
Hancock Whitney Corporation
Hannover Rueck SE
Hanover Insurance Group Inc
Happinet
Harmony Biosciences Holdings, Inc.
Hawkins, Inc.
HCI Group, Inc.
Headwater Exploration Inc.
Heineken Malaysia Berhad
Hellenic Exchanges (CR)
Hennge KK
Heritage Insurance Holdings, Inc.
Hess Corporation
Hexcel
Hibiya Engineering
HIKARI TSUSHIN INCD
Hikma Pharmaceuticals Ord GBP
Hill & Smith PLC Ord GBP
Hilton Worldwide Holdings Inc.
Himoshi Moshi Retail Corporation PCL
Hioki EE
Hitit Bilgisayar
HLKKRKA DD NPV
Ho Chi Minh City Securities Corporation
Hong Leong Industries BHD
Horiba
HOSHIZAKI CORP
Hosokawa Micron
HOTLAND HOLDINGS CO LTDD
Houlihan Lokey, Inc.
Housing & Development Bank
Howden Joinery
Howmet Aerospace
HOYA CORPORATION
HPSP Co
HUB24 Limited
Hubbell Inc
Huber+Suhner
Hugel
HUGEL, INC.D
HUMEDIX CO., LTD.D
Huntington Ingalls Industries, 
Huons
Huron Consulting Group Inc.
HXL
HY-Lok
Hyphens Pharma
Hyundai Autoever
HYUNDAI MERC MARD
Hyundai Mobis
Hyundai Mobis
HYUNDAI ROTEMD
CHAROEN POKPHAND INDONESIA
Chemed Corp
CHEMOMETEC A/S
CHEMRING GROUP ORD GBP0.01
CHENMING ELECTRONIC TECHNOLOGY CORPD
Chewy, Inc.
CHIEF TELECOM INC
Chipotle Mexican Grill, Inc.
CHROMA ATE INCD
CHUGAI PHARMACEUTICAL COD
CHUNG HSIN ELECTRIC & MACHINERYD
I Homes, Inc.
I-mobile Co Share
I-SHENG ELECTRIC WIRE & CABLE COD
I'LL
IAMGOLD Corp
IBJ
Ibotta, Inc.
ICF International
ICRA
Idacorp
idcc
IDOM INCD
Idp Education
IDT Corporation
IG Group Holdings Ord GBP
IGG INCD
Ichitan Group PCL
IMV
Indel
Infomedia
Infotel
Infusystem Holdings
Inghams
Inmode
Innodata Inc.
Inpost S.A.
Insperity
Insulet Corporation
Insurance Australia Group Limited
Int'l Container Terminals Inc.
Integer Holdings
Integral Diagnostics
Inter Action
Inter Cars SA
Interactive Brokers Group, Inc.
InterDigital, Inc.
InterDigital, Inc.
INTERNATIONAL GAMES SYSTEM CO
INTERNATIONAL GAMES SYSTEM CO
International Seaways
INTERNET INITIATIVE JAPAN INCD
Interparfums, Inc.
Interpump
Intertek Group Ord GBP
inTest
Intuit Inc.
INVEX Controladora SAB de CV
Ipsos
Iradimed
Irish Continental
Iriso Electronics
ISETAN MITSUKOSHI HOLDINGS LTDD
ISS A/S
ISUPETASYSD
ITAUSA ON NM
Itmax System Berhad
ITOKI CORPORATIOND
Itron, Inc.
ITT Inc.
IWAKI CO LTDD
J & J Snack Foods
James Hardie Industries
JAMJOOM PHARMACEUTICALS FACTORY CO.D
Janus International
Japan Elevator Service Holdings Co
JAPAN LIFELINE COD
JAPAN MATERIAL CO LTDD
Japfa Comfeed Indonesia
Japfa Comfeed Indonesia
Jayakerjaya Prospek Group Berhad
JBCC HOLDINGS INCD
JCU CORPORATIOND
Jenoptik AG
JENTECH PRECISION INDUSTRIAL
JEOL LTDD
JINS HOLDINGS INCD
JMDC
Johns Lyng
JOHNSON HEALTH TECHD
Joint
JP-HOLDINGS INCD
JPP HOLDING COMPANY LIMITEDD
JSE Ltd
JTEKT
JTEKT
Juhayna Food Industries
Jumbo Interactive Limited
Jungfraubahn Holding
JVCkenwood
JVM Co
Jyothy Labs
JYP Entertainment
K CARD
K-Bro Linen
KAKAKU.COM. INCD
KAKEN PHARMACEUTICALD
Kalbe Farma
Kale Kimyevi Maddeler
kambi
KANDENKO CO LTDD
Kangwon Land
Kansai Paint Co
Kaonavi
Kardex
Karooooo Ltd.
KASUMIGASEKI CAPITAL CO LTDD
KATITAS CO LTDD
Kaufman et Broad
KBC Ancora Ord
KCB Group Ltd
KeePer Technical Laboratory
KH NEOCHEM CO LTDD
Kid ASA
Kim Loong Resources BHD
Kimball Electronics
Kinaxis
KING SLIDE WORKS COD
Kingsgate Consolidated Ltd.
KINIK COD
Kinross Gold Corp
Kirby
Kirloskar Brothers
Kitron ASA
KLA Corporation
KNC Laboratories
KNORR-BREMSE
KOBE BUSSAN CO LTDD
Koei Tecmo Holdings
kof
KOHOKU KOGYO CO LTDD
KOKUSAI ELECTRIC CORPORATIOND
Komatsu Wall Industry
KONAMI GROUP CORPORATIOND
Konecranes
Kongsberg Gruppen
Kongsberg Gruppen
Koninklijke Heijmans N.V.
Kontron AG
koppers
Korea Electric Terminal
KOSAIDO HOLDINGS CO LTDD
Kotobuki Spirits
KOTOBUKI SPIRITSD
KP Resources BHD
KPIT Technologies
Kraken Robotics Inc
Krones AG
Krones AG
Krosaki Harima
Krystal Biotech, Inc.
KSB SE & Co
KUO TOONG INTERNATIONAL
KWS — KWS SAAT SE
L'Air Liquide
Laboratorios Farmaceuticos Rovi
LACOMER SAB DE CV
Lafarge Cement Wapco PLC
Lagercrantz Group AB Ser B
Laureate Education, Inc.
Laureate Education, Inc.
Leidos Holdings, Inc.
Lem Holding
LeMaitre Vascular, Inc.
Lifco AB Ser. B
Limbach Holdings, Inc.
Lime Technologies AB
Linamar
Link and Motivation
LION FINANCE GROUP PLC ORD GBP
Liquidity Services, Inc.
Litalico
Loma Negra Cia Ind Argentina SA
lon:cch
lon:HWDN
lon:npbe
lon:rel
lon:rto
lon:smt
Lorenzo
LOTUS PHARMACEUTICAL COD
Lovisa Holdings
LPI Capital BHD
LPL Financial Holdings Inc.
LSCC
Luckin Coffee
LUNGTEH SHIPBUILDING CO LTDD
M Energy Company
M UP HOLDINGS INCD
M-up Holdings
M&A CAPITAL PARTNERS CO LTDD
M&M Holdings PLC
Macbee Planet
MACQUARIE KOREA INFRASTRUCTURE FUNDDCEF
Macquarie Technology
Mader Group Limited
Madison Square Garden Entertainment Corp.
MAEDA KOSEN CO.LTDD
Magyar Telekom Shared
Maire
MAN Group PLC (New) Ord USD
MAN WAH HOLDINGS LTDD
Management Solutions
Mandalay Resources Corp
Manhattan Associates, Inc.
Mani
MannKind Corporation
Marco Polo Marine
Marcopolo On EJ N2
Marico Bangladesh Ltd
MarkLines Co
Marks and Spencer
Marks Electrical
Martinrea International
Masan Consumer Corporation
Matson, Inc.
Maurel et Prom
Max Healthcare Institute
Max Stock Ltd.
Mazda Motor
MCDONALD'S HOLDINGS COMPANY(JAPAN)D
McGrath RentCorp
MCJ CO LTDD
McMillan Shakespeare Limited
mdlz
Mears Group
Medacta Group
Medical Properties Trust
Medistim
Medley
Medpace Holdings
Medtronic
Medtronic
Mega First Corporation BHD
MEIDENSHA CORPD
Meier Tobler
MEIKO ELECTRONICS COD
Meko AB
Melexis NV
MercadoLibre, Inc.
MercadoLibre, Inc.
Merck & Company, Inc.
Mercury General Corporation
MERITZ FINANCIAL GROUPD
MERRY ELECTRONICS COD
Mersen
Metrodata Electronics TRK
Metropolitan Bank & Trust Co.
Micro Systemation
Microchip Technology
MICRONICS JAPAN COD
MIDAC HOLDINGS CO LTDD
Military Commercial Joint Stock Bank
Miller Industries, Inc.
Mimaki Engineering
Mineros S.A.
MIPS AB
MIROKU JYOHO SERVICE COD
MISUMI GROUP INCD
Mitek Systems
Mitie Group PLC
Mitra Keluarga Karyasehat TBK PT
MITSUI MINING & SMELTING COD
MITSUI O.S.K. LINES LTDD
MIURA CO LTDD
MLP Saglik
Mobile World Investment Corporation
MODEC INC(JAPAN)D
modine
Mold-Tek
Molina Healthcare Inc
Monash IVF
MONOGATARI CORPORATIOND
Monolithic Power Systems, Inc.
Mony Group PLC
Morgan Sindall Group PLC
MORINAGA & COD
MORIYA TPT ENG & MFG CO LTDD
Morningstar, Inc.
Mortgage Advice Bureau (Holdings) PLC
MPI CORPORATION
MPLX LP
MPS
MRC
MT Hojgaard Holding A/S
mtch
Mueller Industries, Inc.
Mueller Water Products
Multi Bintang Indonesia
Multiconsult ASA
Munters AB
Musashi Seimitsu Industry
My E.G. Services BHD
Mycronic AB
Myoung Shin Industrial
Myr
Mytilineos
N-Able
Nakanishi
NAN KANG RUBBER TIRED
NAN PAO RESINS CHEMICAL CO LTDD
Nanosonics
Napco Security Technologies
NATIONAL MEDICAL CARE CO.D
Navigator Global Investments Limited
NC AB Ser. A
Nedbank Group Ltd
Nederman Holding
nemak
Neogen
nesn
NetApp, Inc.
Netflix, Inc.
Neucad
Neuland
Neurocrine Biosciences
Neurones
New York Times Company (The)
Newlat Food
Nexteq
NEXTIN INC.D
NexTone
Nexus AG
NHK SPRING CO LTDD
NICE
NICE INFORMATION SERVICED
Nicolet Bankshares Inc.
NIEN MADE ENTERPRISE CO LTDD
NICHIAS CORPD
nintendo
Nippon Indosari Corpindo
NIPPON PARKING DEVELOPMENT CO.LTDD
Nishimoto Co
NISSAN CHEMICAL CORPORATIOND
NISSEI ASB MACHINE COD
Nisso Holdings
NITERRA CO LTDD
NKT a/s
NMDC Group PJSC
nmfc
NMI Holdings Inc
NOF CORPD
Nomura Micro Science
NOMURA RESEARCH INSTITUTE
Nongshim
Norbit ASA
Nordnet AB
Norion Bank AB
North American Construction
Northern Oil and Gas, Inc.
Northern Star Resources
Northrim BanCorp Inc
Nova Ltd.
Novo Nordisk B A/S
NRB Bearings
NRJ
NRW Holdings Limited
Nu Holdings Ltd.
Nu Holdings Ltd.
NVENT ELECTRIC
NVT
O'Reilly Automotive
OBIC CO
Objective Corporation Limited
OCBC Bank
Oceanagold Corporation
Oddity Tech Ltd.
Odfjell SE
OKAMURA CORPD
Okomu Oil Palm Co PLC
Okuma
Ollie's Bargain Outlet
One Career
OneSpaWorld Holdings Limited
Onto Innovation Inc.
OPAP (CR)
Open Up
OPTEX GROUP COMPANY LTDD
Optima Bank (CR)
Oracle Corporation
Oracle Corporation
Orascom Development Egypt
Orezone Gold Corp
ORGANO CORPD
Orica
ORIENTAL LAND
Orion
Orion Corporation
OSAKA TITANIUM TECHNOLOGIESD
Oshkosh
OSI Systems, Inc.
Ossur hf
Otsuka
ov
OVB Holding AG
Oxford Lane Capital Corp. CEF
Packaging Corporation of America
Palo Alto Networks
Palomar Holdings, Inc.
Pampa Energia S.A.
Pandora A/S
Panunited
PARK SYSTEMS CORP.D
Park24
Parsons Corporation
Partners Group
pax
Paylocity Holding Corporation
PayPoint Ord GBP
Paysign
Pearson
Pearson
Pegasystems Inc.
PEGAVISION CORPORATIOND
Pennant
PEOPLE & TECHNOLOGY, INC.D
pep
PeptiDream
Perenti
peri/nvt
Perseus Mining Limited
PERSOL HOLDINGS CO LTDD
Perusahaan Perkebunan London Sumtrad
Petershill Partners PLC
PETRINDO JAYA KREASI TBK
Petrorio On NM
Petrorio On NM
PETROVIETNAM CA MAU FERTILIZER JOINT STOCK COMPANY
PHA Co
Pharmanutra
PharmaResearch
Pharmasgp Holding SE
Phera Franchise Group
Philippine Seven Corporation
PHISON ELECTRONICS CORP
Phoenix
Phu Nhuan Jewelry Joint Stock Company
PI Industries
PILOT CORP(NEW).PORSCHE INN.LEASE OD
Pinnacle Investment Management Group Limited
PKOBP
Planet Fitness
Playway
Plejd AB
Plexus
Plus Alpha Consulting
Popular, Inc.
Porto Seguro On NM
Powell Industries, Inc.
Power Solutions International, Inc.
POYA INTERNATIONAL CO LTD
PRADA SPAD
Praram 9 Hospital PCL
PREMIUM GROUP CO LTDD
Presco PLC
Press Metal Aluminium Holdings Berhad
Prestige International
PriceSmart, Inc.
Primoris Services
PROG Holdings, Inc.
Progressive Corporation (The)
progyny
Promotora y Operadora de Infraestructura
Propel Holdings Inc
Protector Forsikring ASA
Proto
PSK
PSK HOLDINGS INC.D
PSK INC.D
PSO
pt jasa marga
pt mitra adiperkasa
pt sumber alfariya
PTC India
Publicis Groupe SAD
PulteGroup, Inc.
Pum Tech Korea
PUM-TECH KOREA CO., LTD.D
puody
Puuilo
Puuilo PLC
PWR Holdings
QB Net Holdings
QBE Insurance Group Limited
QinetiQ Group
QinetiQ Group Ord GBP
QT Group OYJ
QUANTA COMPUTERD
Qube Holdings
Quest Holdings (CR)
R. Sarantis (CR)
R&S Group
Raffles Medical
Raffles Medical
Rainbow
Rainbow Tours SA
Rakus
RAKUS CO LTDD
Ramelius Resources Limited
Raymond James Financial, Inc.
rbc
RBC Bearings
Recordati Ord
RECRUIT HOLDINGS
Red River Bancshares, Inc.
Regional SAB de CV
ReinetInvest
Rejlers
Reliance Worldwide
RELX PLC Ord GBP
Renta 4 Banco, S.A.
Reply
ReposiTrak, Inc.
Republic Services
ResMed Inc.
RESORTTRUST INCD
Revolve Group, Inc.
Rheinmetall
Richter Gedeon Share
Risura Group Ltd
RIVERSTONE
rl
Robertet
Robinhood Markets, Inc.
Rockwool A/S Ser. A
Rohto Pharmaceutical
Rollins, Inc.
rop
RORZE CORPD
Royal Caribbean Cruises Ltd.
Royal Gold, Inc.
Royal Unibrew A/S
RS TECHNOLOGIES CO LTDD
saab
SAAB AB Ser. B
Sabesp On EDJ NM
Sabre Insurance Group PLC Ord GBP
Saf-Holland Se
Saigon Securities Incorporation
SAKATA SEED CORPD
SALESFORCE
Samart Aviation Solutions PCL
Samsung Engineering
SAMSUNG FIRE & MARINE INSURANCED
Samwha Capacitor
SAMYANG FOODD
San Miguel Food and Beverage, Inc.
Sandhar
SandRidge Energy, Inc.
Sanken Electric
SANKI ENGINEERING COD
Sanlam Maroc
Sanlorenzo
Sanmina
Sanmina
Sanrio Co
Santam Limited
Santos BRP ON NM
Sanwa Holdings
SAP SE O.N.D
Sarawak Oil Palms BHD
SAUDI CEMENT CO.D
SAUDI GROUND SERVICES CO.D
Saunders International
Savaria
SBS PCL
Scanfil
Scout24 SE
SCREEN HOLDINGS CO LTDD
SCSK CORPD
SD Guthrie Berhad
Sdiptech
Sega Sammy Holdings
SEI Investments Company
Selcuk Ecza Deposu
SEM
Semler Scientific
SENSHU ELECTRIC COD
Seraku Co
Sercomm
Seven group
Sezzle Inc.
SFS AG
SharkNinja, Inc.
Shedir Pharm
Shibaura
Shibaura Machine
Shift
Shimadzu
Shin Maint Holdings Co
SHINY CHEMICAL INDUSTRIAL CO. LTD.D
SHIONOGI & COD
Shopper
Siam City Cement Public Company
Siegfried
Sigmaxyz Holdings
SIGMAXYZ HOLDINGS INCD
SIIX
Sika
SILICON  CO.,LTD.D
Silicon Motion Technology Corporation
Silvercorp Metals Inc
SilverCrest Metals
SIMPLEX HLDGS INCD
Simplex Holdings
Simulations Plus
Simulations Plus
Sinbon Electronics
SINFONIA TECHNOLOGY CO LTDD
SIS
SITC INTERNATIONAL HLDGS CO LTDD
SKAN
Skanska
Skanska
Skyward Specialty Insurance Group, Inc.
SL
SL CORPORATIOND
Smaregi
SMAREGI INCD
Smart Parking
SmartGroup Corporation Ltd
SmartPay Holdings
SMCI
Smith & Nephew PLC Common Stock
Smiths Group PLC
SMS CO
SNC-Lavalin
SNT MOTIV
Societe Ldc SA
Societe Pour l Informatique Industriell
Sol SpA
SOLID, INC.D
Solvi PLC
SOMPO HOLDINGS INCD
Sony Group Corporation
SONY GROUP CORPORATIOND
Southern Cross Electrical Engineering Ltd
Southern States Bancshares, Inc.
SP Group A/S
Sprott Inc.
Sprott Inc.
Sprouts Farmers Market, Inc.
SPS Commerce
spsc
SPX Technologies, Inc.
Square Pharmaceuticals PLC
SSR Mining
ST Engineering
ST HI-TECH ENT
Stanbic IBTC Holdings PLC
Standard Chartered Bank - Kenya
Stantec
Stantec
Stef SA
Sterling Infrastructure, Inc.
STO SE &
sto:camx
sto:evo
Stolt-Nielsen Limited
Straumann
Stride, Inc.
Strike Co
Stryker Corp
Stryker Corp
stz
Sues Microtec
SUGI HOLDINGS CO.LTD.D
Sulzer
Sulzer
SUMITOMO RIKO CO LTDD
Sun
Sun International Ltd
SUNDRUG CO LTDD
SUNONWEALTH ELECTRIC MACHINE IND COD
Sunway Construction Group Berhad
Super Group (SGHC) Limited
Supply Network
Surgical Science Sweden
SUZUKI MOTOR CORPD
svaw
SWCC CORPORATIOND
Swedish Orphan Biovitrum
Swissquote
swx:bchn
swx:gf
swx:lehn
swx:sfsn
swx:ypsn
Syarikat Takaful Malaysia Keluarga Berhad
Symrise AG
Symrise AG
SYNCMOLD ENTERPRISE CORPD
Synergie SE
Synnex (Thailand)
SYSMEX CORPD
System Support
Systemair
Systems Ltd
syy
T&D HOLDINGS INCD
T&L CO., LTD.D
TAISEI CORPD
TAIWAN HON CHUAN ENTERPRISED
TAIWAN SAKURAD
TAIWAN UNION TECHNOLOGY CORPORATION
Takeuchi Mfg
TAKUMA CO LTDD
TAMRON CO LTDD
Target Hospitality
Tased
Tasmea Limited
Taylor Morrison Home Corporation
TCP TD DABACO VIET NAM
TDC Soft
TeamViewer SE
Tecan AG
Tecnoglass
Tegma ON NM
TECHMATRIX CORPD
Technip Energies N.V.
Technogym
TECHNOLOGY CORPORATION
Teikoku Electric
Telecom Egypt
Tennant Co
Tentos ON NM
tep
teqnion
Teradyne, Inc.
terex
Terravest Industries Inc
TERUMO CORP
Tetra Tech
Tetragon Financial Group
Texas Roadhouse, Inc.
TF Bank AB
The Bancorp, Inc.
The Hartford Insurance Group, Inc.
The Lottery Corporation Limited
The Lottery Corporation Limited
The National Bank of Ras Al Khaimah
The Sage Group PLC
The Swatch Grp Ltd
The Trade Desk, Inc.
The Vita Coco Company, Inc.
THEEB RENT A CAR CO.D
Thermon group
Thor Explorations
Tidewater Inc.
Tidewater Inc.
Tim SA
TK
TKC
TOA (Hyogo
Tobii Dynavox AB
TOCALO CO LTDD
TOEI ANIMATIOND
Tokai Carbon Co
TOKIO MARINE HOLDINGS INCD
TOKYO OHKA KOGYO COD
TOKYO SEIMITSU COD
TomTomra Systems AS
TOMY COMPANY LTDD
TONGYANG LIFE INSURANCED
TOPCO SCIENTIFIC COD
Topicus Com Inc
Toro Company (The)
Toromont Industries
TOWA CORPD
Toyo Suisan Kaisha
Toyo Tanso Co
Toyoda Gosei
tpr
Tracsis
Tracsis
Trainline PLC
TRANSCOM INCD
TREASURE FACTORY CO LTDD
Trelleborg
TREND MICRO INCD
TRI CHEMICAL LABORATORIES INC.D
Trigano
Trimegah Bangun Persada TBK
Tripod Technology Corp
TRIPOD TECHNOLOGY CORPD
Triputra Agro Persada TBK
tRisura Group Ltd
Tryg A/S
tse:csu
tsm
Tsuburaya Fields Holdings
ttek
Turkiye Sigorta
TURN CLOUD TECHNOLOGY SERVICE INC
TXT e Solutions SpA
tyl
Tyro Payments Limited
U-NEXT HOLDINGS CO LTDD
Uber Technologies, Inc.
Uber Technologies, Inc.
UFP Technologies, Inc.
UL Solutions Inc.
Ulker Biskuvi
unh
Unipar ON
United Bank for Africa PLC - Nigeria
United Bank Ltd
UNITED INTERNATIONAL TRANSPORTATION CO.D
United States Lime & Minerals, Inc.
United Therapeutics Corporation
Unity Bancorp, Inc.
Universal Health Services, Inc.
UNIVERSAL MICROWAVE TECHNOLOGY INC
Universal Music Group N.V.
Universal Robina
Universal Technical Institute Inc
UNO Minda
Unum Group
Unum Group
Upwork Inc.
US Silica Holdings
USEN NEXT HOLDINGS
USS CO LTDD
VA Tepla AG
Vaisala Corporation
Vaisala Oyj
Valvoline Inc.
Van Elle Holdings
VAT Group
vbg
VC
vecima Networks
Veeva Systems
Ventia Services Group Limited
Ventia Services Group Limited
Veralto Corp
Vercom
Vertiv Holdings, LLC
Vibra ON NM
Victory Capital Holdings, Inc. Class A Common Stock
Vidrala, S.A.
vie:andr
Viemed Healthcare
Vinh Hoan Corporation
Viol Co
Viper Energy, Inc.
Virbac SA
Virtra
VISCO VISION INCD
Vision
Visional
visteon
Vistra Corp.
Vita Coco
Vital Farms, Inc.
Vitalhub
Vitrolife
Vivara S.A. ON NM
VIZIONFOCUS INCD
Vodafone Qatar PQSC
VOLTRONIC POWER TECHNOLOGY CORPD
Volue ASA
Volvo AB
vossloh
Voxel
VOYAGEURS DU MONDE
VSTECS HOLDINGS LTDD
VT Co
VTD
VTRU
VZ Holding
wab
WACI Worldwide, Inc.
Walmart Inc.
Walmart Inc.
Warpaint London PLC
WASION HOLDINGS LTDD
Waste Management
Wavestone SA
WD-40 Company
WDB coco Co
WEATHERNEWS INCD
WEG ON NM
Weir
Welspun
West African Resources Limited
West Pharmaceutical
West Pharmaceutical
Westports Holdings Berhad
Whitecap Resources Inc
Wilson Bayly Hlm-Ovc Ltd
WINGARCST INCD
Wingstop Inc.
WINMATE COMMUNICATION INCD
WINWAY TECHNOLOGY CO LTDD
Wise PLC CLS A Ord GBP
Wisetech Global
WISTRON
WIWYNN CORPORATIOND
Wix.com Ltd.
Wix.com Ltd.
WNS
Wolters Kluwer
Woodward, Inc.
Woolworths
Woolworths
WSP Global
WSP Global
Wyndham Hotels & Resorts, Inc.
Wyndham Hotels & Resorts, Inc.
XP Inc.
XPS Pensions Group PLC
XT e Solutions SpA
Yalla Group Limited
Yamami Co
YG Entertainment
YG Plus
Yokogawa Bridge Holdings
Yokogawa Electric
YONEX CO LTDD
York Water Co
YouGov plc
YOUNG FAST OPTOELECTRONICS CO. LTD.D
Ypsomed
ytl corp
Yubico AB
Zenith Bank PLC
Zenith Bank PLC
ZENKOKU HOSHO CO LTDD
ZERIA PHARMACEUTICALD
ZIGExN Co
Zoom Communications, Inc.
zts
Zurn Elkay Water Solutions"""

result = remove_duplicate_lines(str_data)
print("Original:")
print(repr(str_data))
print("\nAfter removing duplicates:")
print(repr(result))
print("\nFormatted output:")
print(result)

# Alternative one-liner approach using collections.Counter:
from collections import Counter

def remove_duplicates_oneliner(str_data):
    lines = str_data.strip().split('\n')
    counts = Counter(lines)
    return '\n'.join([line for line in lines if counts[line] == 1])

# Test the one-liner version
result2 = remove_duplicates_oneliner(str_data)
print("\nOne-liner result:")
print(result2)