// geodata.js - Base de Datos Geográfica Completa (Países y Ciudades) para MED-INTELLIGENCE
// Creado automáticamente con todos los países del mundo y sus ciudades principales.

const COUNTRIES_AND_CITIES = {
  "República Dominicana": [
    "Santo Domingo",
    "Santiago de los Caballeros",
    "San Francisco de Macorís",
    "La Vega",
    "San Pedro de Macorís",
    "La Romana",
    "Puerto Plata",
    "Higüey",
    "San Cristóbal",
    "Baní",
    "Barahona",
    "San Juan de la Maguana",
    "Mao",
    "Bonao",
    "Cotuí",
    "Azua",
    "Monte Plata",
    "Moca",
    "Nagua",
    "Santa Cruz de Seibo",
    "Hato Mayor del Rey",
    "Pedernales",
    "Jimaní",
    "Neiba",
    "Sabaneta",
    "Monte Cristi",
    "Dajabón",
    "San Fernando de Monte Cristi",
    "Samaná",
    "Salcedo",
    "Comendador"
  ],
  "Colombia": [
    "Bogotá",
    "Medellín",
    "Cali",
    "Barranquilla",
    "Cartagena",
    "Cúcuta",
    "Bucaramanga",
    "Ibagué",
    "Soledad",
    "Pereira",
    "Santa Marta",
    "Soacha",
    "Bello",
    "Pasto",
    "Montería",
    "Valledupar",
    "Manizales",
    "Buenaventura",
    "Neiva",
    "Palmira",
    "Riohacha",
    "Sincelejo",
    "Popayán",
    "Itagüí",
    "Floridablanca",
    "Envigado",
    "Villavicencio",
    "Armenia",
    "Dosquebradas",
    "Yumbo",
    "Tunja",
    "Quibdó",
    "Florencia",
    "Mocoa",
    "San Andrés",
    "Arauca",
    "Yopal",
    "Mitú",
    "Puerto Carreño",
    "Inírida"
  ],
  "México": [
    "Ciudad de México",
    "Guadalajara",
    "Monterrey",
    "Puebla",
    "Tijuana",
    "León",
    "Juárez",
    "Zapopan",
    "Nezahualcóyotl",
    "Chihuahua",
    "Mérida",
    "Cancún",
    "San Luis Potosí",
    "Querétaro",
    "Aguascalientes",
    "Hermosillo",
    "Saltillo",
    "Culiacán",
    "Morelia",
    "Veracruz",
    "Acapulco",
    "Torreón",
    "Tlaquepaque",
    "Mexicali",
    "Chimalhuacán",
    "Reynosa",
    "Tuxtla Gutiérrez",
    "Cuernavaca",
    "Toluca",
    "Durango",
    "Veracruz",
    "Oaxaca de Juárez",
    "Pachuca",
    "Campeche",
    "Tepic",
    "Zacatecas",
    "Guanajuato",
    "Villahermosa",
    "La Paz",
    "Chetumal",
    "Colima",
    "Chilpancingo",
    "Tlaxcala"
  ],
  "Venezuela": [
    "Caracas",
    "Maracaibo",
    "Valencia",
    "Barquisimeto",
    "Maracay",
    "Ciudad Guayana",
    "San Cristóbal",
    "Barcelona",
    "Maturín",
    "Ciudad Bolívar",
    "Cumaná",
    "Barinas",
    "Mérida",
    "Coro",
    "Punto Fijo",
    "Cabimas",
    "Puerto La Cruz",
    "Guarenas",
    "Guatire",
    "Los Teques",
    "Valera",
    "Guanare",
    "San Felipe",
    "San Fernando de Apure",
    "San Carlos",
    "Tucupita",
    "La Asunción",
    "La Guaira",
    "Trujillo"
  ],
  "España": [
    "Madrid",
    "Barcelona",
    "Valencia",
    "Sevilla",
    "Zaragoza",
    "Málaga",
    "Murcia",
    "Palma de Mallorca",
    "Las Palmas de Gran Canaria",
    "Bilbao",
    "Alicante",
    "Córdoba",
    "Valladolid",
    "Vigo",
    "Gijón",
    "L'Hospitalet de Llobregat",
    "Vitoria-Gasteiz",
    "A Coruña",
    "Granada",
    "Elche",
    "Oviedo",
    "Badalona",
    "Terrassa",
    "Cartagena",
    "Jerez de la Frontera",
    "Sabadell",
    "Móstoles",
    "Santa Cruz de Tenerife",
    "Pamplona",
    "Almería",
    "Alcalá de Henares",
    "Fuenlabrada",
    "Leganés",
    "San Sebastián",
    "Getafe",
    "Burgos",
    "Santander",
    "Albacete",
    "Castellón de la Plana",
    "Cádiz",
    "Logroño",
    "Badajoz",
    "Salamanca",
    "Huelva",
    "Lleida",
    "Tarragona",
    "León"
  ],
  "Argentina": [
    "Buenos Aires",
    "Córdoba",
    "Rosario",
    "Mendoza",
    "La Plata",
    "San Miguel de Tucumán",
    "Mar del Plata",
    "Salta",
    "Santa Fe",
    "San Juan",
    "Resistencia",
    "Neuquén",
    "Santiago del Estero",
    "Corrientes",
    "Posadas",
    "Bahía Blanca",
    "San Salvador de Jujuy",
    "Paraná",
    "Formosa",
    "San Luis",
    "La Rioja",
    "Santa Rosa",
    "Catamarca",
    "Río Gallegos",
    "Ushuaia",
    "Viedma",
    "Rawson",
    "Bariloche"
  ],
  "Chile": [
    "Santiago",
    "Valparaíso",
    "Concepción",
    "La Serena",
    "Antofagasta",
    "Temuco",
    "Rancagua",
    "Talca",
    "Arica",
    "Chillán",
    "Iquique",
    "Puerto Montt",
    "Valdivia",
    "Copiapó",
    "Osorno",
    "Quillota",
    "San Antonio",
    "Melipilla",
    "Curicó",
    "Punta Arenas",
    "Coyhaique"
  ],
  "Perú": [
    "Lima",
    "Arequipa",
    "Trujillo",
    "Chiclayo",
    "Piura",
    "Iquitos",
    "Cusco",
    "Huancayo",
    "Chimbote",
    "Pucallpa",
    "Tacna",
    "Ica",
    "Juliaca",
    "Sullana",
    "Huánuco",
    "Ayacucho",
    "Cajamarca",
    "Tumbes",
    "Puerto Maldonado",
    "Puno",
    "Moyobamba",
    "Chachapoyas",
    "Huancavelica",
    "Abancay",
    "Cerro de Pasco"
  ],
  "Ecuador": [
    "Quito",
    "Guayaquil",
    "Cuenca",
    "Santo Domingo de los Colorados",
    "Machala",
    "Durán",
    "Manta",
    "Portoviejo",
    "Loja",
    "Ambato",
    "Esmeraldas",
    "Quevedo",
    "Riobamba",
    "Milagro",
    "Ibarra",
    "Babahoyo",
    "Sangolquí",
    "Latacunga",
    "Tulcán",
    "Tena",
    "Puyo",
    "Macas",
    "Nueva Loja",
    "Puerto Baquerizo Moreno"
  ],
  "Bolivia": [
    "La Paz",
    "Sucre",
    "Santa Cruz de la Sierra",
    "Cochabamba",
    "Oruro",
    "Potosí",
    "Tarija",
    "Trinidad",
    "Cobija",
    "El Alto",
    "Sacaba",
    "Quillacollo",
    "Montero"
  ],
  "Paraguay": [
    "Asunción",
    "Ciudad del Este",
    "Luque",
    "San Lorenzo",
    "Capiatá",
    "Lambaré",
    "Fernando de la Mora",
    "Limpio",
    "Encarnación",
    "Pedro Juan Caballero",
    "Villa Elisa"
  ],
  "Uruguay": [
    "Montevideo",
    "Salto",
    "Paysandú",
    "Las Piedras",
    "Maldonado",
    "Rivera",
    "Tacarembó",
    "Artigas",
    "Mercedes",
    "Colonia del Sacramento",
    "San José de Mayo"
  ],
  "Cuba": [
    "La Habana",
    "Santiago de Cuba",
    "Camagüey",
    "Holguín",
    "Guantánamo",
    "Santa Clara",
    "Las Tunas",
    "Bayamo",
    "Cienfuegos",
    "Pinar del Río",
    "Matanzas",
    "Sancti Spíritus"
  ],
  "Puerto Rico": [
    "San Juan",
    "Bayamón",
    "Carolina",
    "Ponce",
    "Caguas",
    "Guaynabo",
    "Mayagüez",
    "Arecibo",
    "Trujillo Alto",
    "Toa Baja"
  ],
  "Costa Rica": [
    "San José",
    "Alajuela",
    "Cartago",
    "Heredia",
    "Liberia",
    "Puntarenas",
    "Limón",
    "Pérez Zeledón",
    "Quesada"
  ],
  "Panamá": [
    "Ciudad de Panamá",
    "David",
    "Colón",
    "Chitré"
  ],
  "Guatemala": [
    "Ciudad de Guatemala",
    "Mixco",
    "Villa Nueva",
    "Quetzaltenango",
    "Escuintla",
    "Amatitlán",
    "Chinautla",
    "Cobán",
    "Puerto Barrios",
    "Mazatenango"
  ],
  "Honduras": [
    "Tegucigalpa",
    "San Pedro Sula",
    "Choloma",
    "La Ceiba",
    "El Progreso",
    "Choluteca",
    "Comayagua",
    "Puerto Cortés",
    "La Lima",
    "Danlí"
  ],
  "El Salvador": [
    "San Salvador",
    "Santa Ana",
    "San Miguel",
    "Mejicanos",
    "Santa Tecla",
    "Apopa",
    "Delgado",
    "Sonsonate",
    "Ilopango"
  ],
  "Nicaragua": [
    "Managua",
    "León",
    "Masaya",
    "Tipitapa",
    "Chinandega",
    "Matagalpa",
    "Estelí",
    "Granada",
    "Juigalpa",
    "Bluefields"
  ],
  "Estados Unidos": [
    "Nueva York",
    "Los Ángeles",
    "Chicago",
    "Houston",
    "Phoenix",
    "Philadelphia",
    "San Antonio",
    "San Diego",
    "Dallas",
    "San José",
    "Austin",
    "Jacksonville",
    "San Francisco",
    "Indianapolis",
    "Columbus",
    "Fort Worth",
    "Charlotte",
    "Seattle",
    "Denver",
    "Boston",
    "El Paso",
    "Detroit",
    "Nashville",
    "Portland",
    "Memphis",
    "Oklahoma City",
    "Las Vegas",
    "Louisville",
    "Baltimore",
    "Milwaukee",
    "Albuquerque",
    "Tucson",
    "Fresno",
    "Sacramento",
    "Atlanta",
    "Miami",
    "New Orleans",
    "Washington D.C."
  ],
  "Canadá": [
    "Toronto",
    "Montreal",
    "Vancouver",
    "Calgary",
    "Edmonton",
    "Ottawa",
    "Winnipeg",
    "Quebec City",
    "Hamilton",
    "Kitchener",
    "London",
    "Halifax",
    "Victoria"
  ],
  "Reino Unido": [
    "Londres",
    "Birmingham",
    "Leeds",
    "Glasgow",
    "Sheffield",
    "Manchester",
    "Liverpool",
    "Edinburgh",
    "Bristol",
    "Belfast",
    "Cardiff"
  ],
  "Francia": [
    "París",
    "Marsella",
    "Lyon",
    "Toulouse",
    "Niza",
    "Nantes",
    "Estrasburgo",
    "Montpellier",
    "Burdeos",
    "Lille",
    "Rennes"
  ],
  "Alemania": [
    "Berlín",
    "Hamburgo",
    "Múnich",
    "Colonia",
    "Fráncfort",
    "Stuttgart",
    "Düsseldorf",
    "Dortmund",
    "Essen",
    "Bremen",
    "Leipzig"
  ],
  "Italia": [
    "Roma",
    "Milán",
    "Nápoles",
    "Turín",
    "Palermo",
    "Génova",
    "Bolonia",
    "Florencia",
    "Bari",
    "Catania",
    "Venecia"
  ],
  "Portugal": [
    "Lisboa",
    "Oporto",
    "Amadora",
    "Braga",
    "Coímbra",
    "Funchal",
    "Setúbal"
  ],
  "Países Bajos": [
    "Ámsterdam",
    "Róterdam",
    "La Haya",
    "Utrecht",
    "Eindhoven",
    "Tilburgo"
  ],
  "Bélgica": [
    "Bruselas",
    "Amberes",
    "Gante",
    "Charleroi",
    "Lieja",
    "Brujas"
  ],
  "Suiza": [
    "Zúrich",
    "Ginebra",
    "Basilea",
    "Berna",
    "Lausana",
    "Lugano"
  ],
  "Austria": [
    "Viena",
    "Graz",
    "Linz",
    "Salzburgo",
    "Innsbruck",
    "Klagenfurt"
  ],
  "Grecia": [
    "Atenas",
    "Salónica",
    "Patras",
    "El Pireo",
    "Larissa",
    "Heraclión"
  ],
  "Irlanda": [
    "Dublín",
    "Cork",
    "Limerick",
    "Galway",
    "Waterford",
    "Drogheda"
  ],
  "Suecia": [
    "Estocolmo",
    "Gotemburgo",
    "Malmö",
    "Upsala",
    "Västerås",
    "Örebro"
  ],
  "Noruega": [
    "Oslo",
    "Bergen",
    "Trondheim",
    "Stavanger",
    "Bærum",
    "Kristiansand"
  ],
  "Dinamarca": [
    "Copenhague",
    "Aarhus",
    "Odense",
    "Aalborg",
    "Esbjerg",
    "Randers"
  ],
  "Finlandia": [
    "Helsinki",
    "Espoo",
    "Tampere",
    "Vantaa",
    "Oulu",
    "Turku"
  ],
  "Polonia": [
    "Varsovia",
    "Cracovia",
    "Lodz",
    "Breslavia",
    "Poznan",
    "Gdansk",
    "Szczecin"
  ],
  "República Checa": [
    "Praga",
    "Brno",
    "Ostrava",
    "Plzen",
    "Liberec",
    "Olomouc"
  ],
  "Hungría": [
    "Budapest",
    "Debrecen",
    "Szeged",
    "Miskolc",
    "Pécs",
    "Győr"
  ],
  "Rumanía": [
    "Bucarest",
    "Cluj-Napoca",
    "Timișoara",
    "Iași",
    "Constanța",
    "Craiova"
  ],
  "Bulgaria": [
    "Sofía",
    "Plovdiv",
    "Varna",
    "Burgas",
    "Ruse",
    "Stara Zagora"
  ],
  "Ucrania": [
    "Kiev",
    "Járkov",
    "Odesa",
    "Dnipró",
    "Donetsk",
    "Zaporiyia",
    "Leópolis"
  ],
  "Rusia": [
    "Moscú",
    "San Petersburgo",
    "Novosibirsk",
    "Ekaterimburgo",
    "Nizhni Nóvgorod",
    "Kazán",
    "Cheliábinsk",
    "Samara",
    "Omsk",
    "Rostov del Don"
  ],
  "China": [
    "Pekín",
    "Shanghái",
    "Cantón",
    "Shenzhen",
    "Tianjin",
    "Wuhan",
    "Dongguan",
    "Chongqing",
    "Chengdu",
    "Nankín",
    "Hangzhou",
    "Xi'an"
  ],
  "Japón": [
    "Tokio",
    "Yokohama",
    "Osaka",
    "Nagoya",
    "Sapporo",
    "Kobe",
    "Fukuoka",
    "Kioto",
    "Kawasaki",
    "Saitama",
    "Hiroshima"
  ],
  "India": [
    "Nueva Delhi",
    "Bombay",
    "Bangalore",
    "Calcuta",
    "Chennai",
    "Hyderabad",
    "Ahmedabad",
    "Pune",
    "Surat",
    "Jaipur",
    "Lucknow"
  ],
  "Corea del Sur": [
    "Seúl",
    "Busan",
    "Incheon",
    "Daegu",
    "Daejeon",
    "Gwangju",
    "Suwon",
    "Ulsan"
  ],
  "Corea del Norte": [
    "Pionyang",
    "Hamhung",
    "Chongjin",
    "Nampo",
    "Wonsan"
  ],
  "Taiwán": [
    "Taipéi",
    "Kaohsiung",
    "Taichung",
    "Tainan",
    "Hsinchu"
  ],
  "Singapur": [
    "Singapur"
  ],
  "Filipinas": [
    "Manila",
    "Quezon City",
    "Davao City",
    "Cebu City",
    "Zamboanga City"
  ],
  "Vietnam": [
    "Hanói",
    "Ciudad Ho Chi Minh",
    "Hai Phong",
    "Da Nang",
    "Can Tho"
  ],
  "Tailandia": [
    "Bangkok",
    "Nonthaburi",
    "Nakhon Ratchasima",
    "Chiang Mai",
    "Phuket"
  ],
  "Malasia": [
    "Kuala Lumpur",
    "George Town",
    "Ipoh",
    "Johor Bahru",
    "Melaka"
  ],
  "Indonesia": [
    "Yakarta",
    "Surabaya",
    "Bandung",
    "Medan",
    "Bekasi",
    "Tangerang",
    "Depok",
    "Semarang",
    "Palembang"
  ],
  "Turquía": [
    "Ankara",
    "Estambul",
    "Esmirna",
    "Bursa",
    "Adana",
    "Gaziantep",
    "Antalya"
  ],
  "Arabia Saudita": [
    "Riad",
    "Yeda",
    "La Meca",
    "Medina",
    "Dammam",
    "Taif",
    "Tabuk"
  ],
  "Emiratos Árabes Unidos": [
    "Abu Dabi",
    "Dubái",
    "Sharjah",
    "Al Ain",
    "Ajmán"
  ],
  "Catar": [
    "Doha",
    "Al Wakrah",
    "Al Rayyan"
  ],
  "Israel": [
    "Jerusalén",
    "Tel Aviv",
    "Haifa",
    "Rishon LeZion",
    "Petaj Tikva"
  ],
  "Irán": [
    "Teherán",
    "Mashhad",
    "Isfahán",
    "Karaj",
    "Tabriz",
    "Shiraz"
  ],
  "Irak": [
    "Bagdad",
    "Mosul",
    "Basora",
    "Erbil",
    "Solimania"
  ],
  "Pakistán": [
    "Islamabad",
    "Karachi",
    "Lahore",
    "Faisalabad",
    "Rawalpindi",
    "Multan"
  ],
  "Kazajistán": [
    "Astaná",
    "Almaty",
    "Shymkent",
    "Karagandá",
    "Aktobé"
  ],
  "Bangladés": [
    "Daca",
    "Chittagong",
    "Khulna",
    "Rajshahi",
    "Sylhet"
  ],
  "Brasil": [
    "Brasilia",
    "São Paulo",
    "Río de Janeiro",
    "Salvador",
    "Fortaleza",
    "Belo Horizonte",
    "Manaos",
    "Curitiba",
    "Recife",
    "Porto Alegre",
    "Belém",
    "Goiânia"
  ],
  "Guyana": [
    "Georgetown",
    "Linden",
    "New Amsterdam"
  ],
  "Surinam": [
    "Paramaribo",
    "Nieuw Nickerie",
    "Moengo"
  ],
  "Guayana Francesa": [
    "Cayena",
    "Kourou",
    "Saint-Laurent-du-Maroni"
  ],
  "Egipto": [
    "El Cairo",
    "Alejandría",
    "Giza",
    "Shubra El-Kheima",
    "Puerto Said",
    "Suez"
  ],
  "Sudáfrica": [
    "Pretoria",
    "Ciudad del Cabo",
    "Johannesburgo",
    "Durban",
    "Soweto",
    "Bloemfontein",
    "Port Elizabeth"
  ],
  "Nigeria": [
    "Abuya",
    "Lagos",
    "Kano",
    "Ibadán",
    "Kaduna",
    "Port Harcourt",
    "Benin City"
  ],
  "Kenia": [
    "Nairobi",
    "Mombasa",
    "Kisumu",
    "Nakuru",
    "Eldoret"
  ],
  "Marruecos": [
    "Rabat",
    "Casablanca",
    "Fez",
    "Tánger",
    "Marrakech",
    "Salé",
    "Meknes"
  ],
  "Argelia": [
    "Argel",
    "Orán",
    "Constantina",
    "Annaba",
    "Blida"
  ],
  "Túnez": [
    "Túnez",
    "Sfax",
    "Susa",
    "Bizerta",
    "Gabes"
  ],
  "Etiopía": [
    "Adís Abeba",
    "Dire Dawa",
    "Mekele",
    "Gondar",
    "Adama"
  ],
  "Ghana": [
    "Acra",
    "Kumasi",
    "Tamale",
    "Takoradi",
    "Achimota"
  ],
  "Costa de Marfil": [
    "Yamusukro",
    "Abiyán",
    "Bouaké",
    "Daloa",
    "San Pedro"
  ],
  "Camerún": [
    "Yaundé",
    "Duala",
    "Bamenda",
    "Garua",
    "Marua"
  ],
  "Senegal": [
    "Dakar",
    "Touba",
    "Thiès",
    "Rufisque",
    "Saint-Louis"
  ],
  "Angola": [
    "Luanda",
    "Huambo",
    "Lobito",
    "Benguela",
    "Lubango"
  ],
  "Zimbabue": [
    "Harare",
    "Bulawayo",
    "Chitungwiza",
    "Mutare"
  ],
  "Australia": [
    "Canberra",
    "Sídney",
    "Melbourne",
    "Brisbane",
    "Perth",
    "Adelaida",
    "Gold Coast",
    "Newcastle",
    "Hobart"
  ],
  "Nueva Zelanda": [
    "Wellington",
    "Auckland",
    "Christchurch",
    "Hamilton",
    "Tauranga",
    "Dunedin"
  ],
  "Fiyi": [
    "Suva",
    "Lautoka",
    "Nadi"
  ],
  "Papúa Nueva Guinea": [
    "Puerto Moresby",
    "Lae",
    "Mendi"
  ],
  "Afganistán": [
    "Kabul",
    "Herat",
    "Mazar-i-Sharif",
    "Kandahar"
  ],
  "Albania": [
    "Tirana",
    "Durrës",
    "Vlorë",
    "Elbasan"
  ],
  "Andorra": [
    "Andorra la Vella",
    "Escaldes-Engordany",
    "Encamp"
  ],
  "Antigua y Barbuda": [
    "Saint John's",
    "All Saints",
    "Liberta"
  ],
  "Armenia": [
    "Ereván",
    "Gyumri",
    "Vanadzor"
  ],
  "Azerbaiyán": [
    "Bakú",
    "Ganja",
    "Sumqayit"
  ],
  "Bahamas": [
    "Nasáu",
    "Freeport",
    "West End"
  ],
  "Baréin": [
    "Manama",
    "Riffa",
    "Muharraq"
  ],
  "Barbados": [
    "Bridgetown",
    "Speightstown",
    "Oistins"
  ],
  "Bielorrusia": [
    "Minsk",
    "Gomel",
    "Mogilev",
    "Vitebsk"
  ],
  "Belice": [
    "Belmopán",
    "Ciudad de Belice",
    "San Ignacio"
  ],
  "Benín": [
    "Porto Novo",
    "Cotonú",
    "Parakou"
  ],
  "Bután": [
    "Timbu",
    "Phuntsholing",
    "Punakha"
  ],
  "Bosnia y Herzegovina": [
    "Sarajevo",
    "Bania Luka",
    "Tuzla"
  ],
  "Botsuana": [
    "Gaborone",
    "Francistown",
    "Molepolole"
  ],
  "Brunéi": [
    "Bandar Seri Begawan",
    "Kuala Belait",
    "Seria"
  ],
  "Burkina Faso": [
    "Uagadugú",
    "Bobo-Dioulasso",
    "Koudougou"
  ],
  "Burundi": [
    "Gitega",
    "Buyumbura",
    "Muyinga"
  ],
  "Cabo Verde": [
    "Praia",
    "Mindelo",
    "Santa Maria"
  ],
  "Camboya": [
    "Nom Pen",
    "Battambang",
    "Siem Riep"
  ],
  "República Centroafricana": [
    "Bangui",
    "Bimbo",
    "Mbaïki"
  ],
  "Chad": [
    "Yamena",
    "Moundou",
    "Sarh"
  ],
  "Comoras": [
    "Moroni",
    "Mutsamudu",
    "Fomboni"
  ],
  "República del Congo": [
    "Brazzaville",
    "Pointe-Noire",
    "Dolisie"
  ],
  "República Democrática del Congo": [
    "Kinsasa",
    "Lubumbashi",
    "Mbuji-Mayi",
    "Goma"
  ],
  "Croacia": [
    "Zagreb",
    "Split",
    "Rijeka",
    "Osijek"
  ],
  "Chipre": [
    "Nicosia",
    "Limassol",
    "Lárnaca",
    "Pafos"
  ],
  "Yibuti": [
    "Yibuti",
    "Ali Sabieh",
    "Tadjoura"
  ],
  "Dominica": [
    "Roseau",
    "Portsmouth",
    "Marigot"
  ],
  "Guinea Ecuatorial": [
    "Malabo",
    "Bata",
    "Oyala"
  ],
  "Eritrea": [
    "Asmara",
    "Keren",
    "Massawa"
  ],
  "Estonia": [
    "Tallin",
    "Tartu",
    "Narva"
  ],
  "Eswatini": [
    "Mbabane",
    "Manzini",
    "Lobamba"
  ],
  "Gabón": [
    "Libreville",
    "Port-Gentil",
    "Franceville"
  ],
  "Gambia": [
    "Banjul",
    "Serekunda",
    "Brikama"
  ],
  "Georgia": [
    "Tiflis",
    "Kutaisi",
    "Batumi"
  ],
  "Granada": [
    "Saint George's",
    "Gouyave",
    "Grenville"
  ],
  "Guinea": [
    "Conakry",
    "Nzérékoré",
    "Kankan"
  ],
  "Guinea-Bisáu": [
    "Bisáu",
    "Bafatá",
    "Gabú"
  ],
  "Haití": [
    "Puerto Príncipe",
    "Cabo Haitiano",
    "Gonaïves",
    "Les Cayes"
  ],
  "Islandia": [
    "Reikiavik",
    "Kópavogur",
    "Hafnarfjörður"
  ],
  "Jamaica": [
    "Kingston",
    "Montego Bay",
    "Spanish Town"
  ],
  "Jordania": [
    "Amán",
    "Zarqa",
    "Irbid",
    "Aqaba"
  ],
  "Kirguistán": [
    "Biskek",
    "Osh",
    "Jalal-Abad"
  ],
  "Kiribati": [
    "Tarawa",
    "Betio",
    "Bikenibeu"
  ],
  "Kuwait": [
    "Kuwait City",
    "Jahra",
    "Salmiya"
  ],
  "Laos": [
    "Vientián",
    "Pakse",
    "Luang Prabang"
  ],
  "Letonia": [
    "Riga",
    "Daugavpils",
    "Liepāja"
  ],
  "Líbano": [
    "Beirut",
    "Trípoli",
    "Sidón",
    "Tiro"
  ],
  "Lesoto": [
    "Maseru",
    "Teyateyaneng",
    "Mafeteng"
  ],
  "Liberia": [
    "Monrovia",
    "Gbarnga",
    "Kakata"
  ],
  "Libia": [
    "Trípoli",
    "Bengasi",
    "Misrata",
    "Tobruk"
  ],
  "Liechtenstein": [
    "Vaduz",
    "Schaan",
    "Triesen"
  ],
  "Lituania": [
    "Vilna",
    "Kaunas",
    "Klaipėda"
  ],
  "Luxemburgo": [
    "Luxemburgo",
    "Esch-sur-Alzette",
    "Differdange"
  ],
  "Madagascar": [
    "Antananarivo",
    "Toamasina",
    "Antsirabe"
  ],
  "Malaui": [
    "Lilongüe",
    "Blantyre",
    "Mzuzu"
  ],
  "Maldivas": [
    "Malé",
    "Addu City",
    "Fuvahmulah"
  ],
  "Malí": [
    "Bamako",
    "Sikasso",
    "Mopti",
    "Tombuctú"
  ],
  "Malta": [
    "La Valeta",
    "Birkirkara",
    "Mosta"
  ],
  "Islas Marshall": [
    "Majuro",
    "Ebeye",
    "Jaluit"
  ],
  "Mauritania": [
    "Nuakchot",
    "Nuadibú",
    "Néma"
  ],
  "Mauricio": [
    "Port Louis",
    "Beau Bassin-Rose Hill",
    "Vacoas-Phoenix"
  ],
  "Micronesia": [
    "Palikir",
    "Weno",
    "Kolonia"
  ],
  "Moldavia": [
    "Chisináu",
    "Tiraspol",
    "Bălți"
  ],
  "Mónaco": [
    "Mónaco",
    "Montecarlo",
    "La Condamine"
  ],
  "Mongolia": [
    "Ulán Bator",
    "Erdenet",
    "Darjan"
  ],
  "Montenegro": [
    "Podgorica",
    "Nikšić",
    "Pljevlja"
  ],
  "Myanmar": [
    "Naipyidó",
    "Rangún",
    "Mandalay"
  ],
  "Namibia": [
    "Windhoek",
    "Walvis Bay",
    "Rundu"
  ],
  "Nauru": [
    "Yaren",
    "Denigomodu",
    "Meneng"
  ],
  "Nepal": [
    "Katmandú",
    "Pokhara",
    "Lalitpur"
  ],
  "Níger": [
    "Niamey",
    "Zinder",
    "Maradi"
  ],
  "Macedonia del Norte": [
    "Skopie",
    "Bitola",
    "Kumanovo"
  ],
  "Omán": [
    "Mascate",
    "Salalah",
    "Sohar"
  ],
  "Palaos": [
    "Ngerulmud",
    "Koror",
    "Airai"
  ],
  "Palestina": [
    "Gaza",
    "Cisjordania",
    "Ramala",
    "Nablus",
    "Hebrón",
    "Jericó"
  ],
  "Ruanda": [
    "Kigali",
    "Gisenyi",
    "Butare"
  ],
  "San Cristóbal y Nieves": [
    "Basseterre",
    "Sandy Point Town",
    "Charlestown"
  ],
  "Santa Lucía": [
    "Castries",
    "Gros Islet",
    "Vieux Fort"
  ],
  "San Vicente y las Granadinas": [
    "Kingstown",
    "Georgetown",
    "Barrouallie"
  ],
  "Samoa": [
    "Apia",
    "Vaitele",
    "Faleasiu"
  ],
  "San Marino": [
    "San Marino",
    "Dogana",
    "Borgo Maggiore"
  ],
  "Santo Tomé y Príncipe": [
    "Santo Tomé",
    "Trindade",
    "Neves"
  ],
  "Seychelles": [
    "Victoria",
    "Anse Royale",
    "Bel Ombre"
  ],
  "Sierra Leona": [
    "Freetown",
    "Bo",
    "Kenema"
  ],
  "Eslovaquia": [
    "Bratislava",
    "Košice",
    "Prešov"
  ],
  "Eslovenia": [
    "Liubliana",
    "Maribor",
    "Celje"
  ],
  "Islas Salomón": [
    "Honiara",
    "Gizo",
    "Auki"
  ],
  "Somalia": [
    "Mogadiscio",
    "Hargeisa",
    "Bosaso"
  ],
  "Sudán": [
    "Jartum",
    "Omdurmán",
    "Puerto Sudán"
  ],
  "Sudán del Sur": [
    "Yuba",
    "Malakal",
    "Wau"
  ],
  "Sri Lanka": [
    "Colombo",
    "Kaduwela",
    "Galle"
  ],
  "Siria": [
    "Damasco",
    "Alepo",
    "Homs",
    "Latakia"
  ],
  "Tayikistán": [
    "Dusambé",
    "Jujand",
    "Kulob"
  ],
  "Tanzania": [
    "Dodoma",
    "Dar es Salaam",
    "Mwanza"
  ],
  "Togo": [
    "Lomé",
    "Sokodé",
    "Kara"
  ],
  "Tonga": [
    "Nukualofa",
    "Neiafu",
    "Mu'a"
  ],
  "Trinidad y Tobago": [
    "Puerto España",
    "Chaguanas",
    "San Fernando"
  ],
  "Turkmenistán": [
    "Asjabad",
    "Turkmenabat",
    "Daşoguz"
  ],
  "Tuvalu": [
    "Funafuti",
    "Asau",
    "Nanumea"
  ],
  "Uganda": [
    "Kampala",
    "Nansana",
    "Kira"
  ],
  "Uzbekistán": [
    "Taskent",
    "Samarcanda",
    "Namangán"
  ],
  "Vanuatu": [
    "Port Vila",
    "Luganville",
    "Port Olry"
  ],
  "Ciudad del Vaticano": [
    "Ciudad del Vaticano"
  ],
  "Yemen": [
    "Saná",
    "Adén",
    "Taiz",
    "Al Hudaydah"
  ],
  "Zambia": [
    "Lusaka",
    "Kitwe",
    "Ndola"
  ]
};
