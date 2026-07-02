import time
import math
import copy

# METADATOS CLÍNICOS DE LAS 23 ENFERMEDADES (Atención Primaria y Urgencias)
CLINICAL_METADATA = {
    "Gripe Común / Influenza": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Familiar",
        "summary": "Infección viral de las vías respiratorias superiores. Autolimitada en pacientes sanos pero altamente contagiosa.",
        "clinical_tests": [
            "**Panel Viral Respiratorio (PCR)**: Positivo para virus de Influenza A o B.",
            "**Hemograma Completo**: Leucocitos dentro de rango normal o leve linfocitosis reactiva."
        ],
        "habits": [
            "Reposo absoluto en cama por al menos 48 a 72 horas.",
            "Hidratación agresiva con 2.5 a 3 litros de agua al día.",
            "Dieta blanda rica en frutas cítricas (vitamina C).",
            "Ventilar adecuadamente la habitación."
        ],
        "medications": [
            "Paracetamol 500mg a 1g vía oral cada 8 horas en caso de fiebre.",
            "Lavados nasales frecuentes con solución salina estéril.",
            "Antihistamínicos orales (ej. Loratadina 10mg una vez al día).",
            "**ADVERTENCIA**: Está prohibido el uso de antibióticos en gripe viral."
        ],
        "red_flags": [
            "Fiebre persistente que no cede con antipiréticos después de 3 días.",
            "Aparición súbita de dificultad para respirar o dolor torácico.",
            "Somnolencia inusual o confusión."
        ]
    },
    "Neumonía": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Neumología / Medicina Interna",
        "summary": "Infección pulmonar aguda que inflama los alvéolos, llenándolos de secreciones purulentas.",
        "clinical_tests": [
            "**Radiografía de Tórax (AP y Lateral)**: Consolidación lobar alveolar densa.",
            "**Hemograma Completo**: Leucocitosis marcada con neutrofilia severa.",
            "**Proteína C Reactiva (PCR)**: Elevada, indica inflamación activa."
        ],
        "habits": [
            "Reposo en cama con el torso semielevado a 30-45 grados.",
            "Uso de oxímetro de pulso para monitorizar saturación 3 veces al día.",
            "Ejercicios de espiración lenta para movilizar secreciones.",
            "Hidratación abundante para fluidificar el moco."
        ],
        "medications": [
            "**Antibióticos**: Amoxicilina con Ácido Clavulánico 875/125mg cada 12 horas por 7-10 días.",
            "Paracetamol 500mg cada 6 horas solo si hay fiebre.",
            "Evitar jarabes antitusivos; se necesita expectorar.",
            "**ADVERTENCIA**: El retraso en el antibiótico aumenta el riesgo de sepsis."
        ],
        "red_flags": [
            "Saturación de oxígeno por debajo de 92%.",
            "Frecuencia respiratoria superior a 24 rpm en reposo.",
            "Alteración de la conciencia o desorientación."
        ]
    },
    "Bronquitis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Neumología",
        "summary": "Inflamación aguda de los conductos bronquiales, usualmente secundaria a un cuadro viral previo.",
        "clinical_tests": [
            "**Radiografía de Tórax**: Campos limpios, sin infiltrados (descarta neumonía).",
            "**Auscultación Pulmonar**: Roncus y sibilancias bilaterales dispersas."
        ],
        "habits": [
            "Evitar la exposición al humo de tabaco y vapores químicos.",
            "Vaporizaciones con agua tibia o humidificador ultrasónico.",
            "Consumir abundantes líquidos tibios (té con miel).",
            "Evitar cambios bruscos de temperatura."
        ],
        "medications": [
            "Mucolíticos (N-Acetilcisteína 600mg una vez al día).",
            "Broncodilatadores inhalados (Salbutamol) solo si hay sibilancias.",
            "Ibuprofeno 400mg cada 8 horas para el malestar.",
            "**ADVERTENCIA**: >90% de bronquitis son virales. No usar antibióticos sin indicación."
        ],
        "red_flags": [
            "Tos persistente por más de 3 semanas o con sangre.",
            "Silbidos en el pecho con asfixia al caminar.",
            "Fiebre de más de 38.5°C persistente."
        ]
    },
    "Crisis Asmática Aguda": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Alergología / Neumología / Urgencias",
        "summary": "Estrechamiento agudo de las vías respiratorias por espasmo muscular e inflamación bronquial.",
        "clinical_tests": [
            "**Flujometría (Peak Flow)**: PEF <60% del valor teórico habitual.",
            "**Auscultación**: Sibilancias espiratorias agudas bilaterales.",
            "**Saturación O2**: Hipoxia si crisis severa."
        ],
        "habits": [
            "Sentarse con el torso recto apoyando los brazos sobre una mesa.",
            "Mantener la calma; la ansiedad agrava el broncoespasmo.",
            "Alejarse del alérgeno sospechoso inmediatamente.",
            "Respirar con los labios fruncidos de manera pausada."
        ],
        "medications": [
            "**Rescate**: Salbutamol 2-4 puff cada 20 minutos durante la primera hora.",
            "Corticoide oral (Prednisona 40mg) para frenar la inflamación.",
            "Uso estricto del inhalador de control habitual.",
            "**ADVERTENCIA**: Sin mejoría tras 3 rondas de Salbutamol → urgencias inmediatas."
        ],
        "red_flags": [
            "Tiraje intercostal visible (piel se hunde entre costillas).",
            "Imposibilidad de completar una frase por falta de aire.",
            "Coloración azulada alrededor de los labios (cianosis)."
        ]
    },
    "Exacerbación Aguda de EPOC": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neumología / Sala de Urgencias",
        "summary": "Empeoramiento agudo y potencialmente letal de los síntomas pulmonares obstructivos crónicos.",
        "clinical_tests": [
            "**Gasometría Arterial**: Hipoxia (pO2 <60 mmHg), hipercapnia y acidosis respiratoria.",
            "**Radiografía de Tórax**: Atrapamiento aéreo severo.",
            "**Espirometría (FEV1)**: Marcadamente reducida."
        ],
        "habits": [
            "Posición erguida con codos apoyados sobre muslos.",
            "Oxígeno domiciliario a flujos bajos (1-2 lpm) si disponible.",
            "Evitar cualquier esfuerzo físico innecesario.",
            "Ambiente con temperatura regulada, sin corrientes de aire."
        ],
        "medications": [
            "Combivent (Bromuro de Ipratropio + Salbutamol) cada 4-6 horas.",
            "Corticosteroides sistémicos (Metilprednisolona 40mg) por 5 días.",
            "Antibióticos si hay esputo purulento y fiebre.",
            "**ADVERTENCIA**: Sedantes y ansiolíticos CONTRAINDICADOS — deprimen el centro respiratorio."
        ],
        "red_flags": [
            "Somnolencia extrema, confusión o incoherencia.",
            "Saturación <88% en EPOC previo.",
            "Uso marcado de músculos accesorios del cuello para respirar."
        ]
    },
    "Infarto Agudo de Miocardio (IAM)": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Cardiología / Unidad de Cuidados Coronarios",
        "summary": "Necrosis aguda de músculo cardíaco por obstrucción de arteria coronaria. Emergencia tiempo-dependiente.",
        "clinical_tests": [
            "**ECG de 12 Derivaciones**: Elevación convexa del ST >2mm (V1-V4 o DII/DIII/aVF).",
            "**Troponina I ultra-sensible**: Patológicamente elevada (>14 ng/L).",
            "**CK-MB**: Elevada confirma necrosis miocárdica."
        ],
        "habits": [
            "**REPOSO FÍSICO ABSOLUTO**: Ningún esfuerzo, incluso hablar es riesgo.",
            "Ambiente ventilado, ropa aflojada alrededor de cuello y pecho.",
            "No ingerir alimentos líquidos ni sólidos.",
            "**Llamar ambulancia medicalizada de inmediato.**"
        ],
        "medications": [
            "**Emergencia**: Aspirina 325mg masticada de inmediato.",
            "Clopidogrel 300mg (dosis carga, criterio médico).",
            "Nitroglicerina 0.4mg sublingual cada 5 min (máx 3 dosis, solo si PAS >90 mmHg).",
            "**ADVERTENCIA**: No dar Nitroglicerina si se usó Sildenafil (Viagra) en 24-48h."
        ],
        "red_flags": [
            "Dolor opresivo retroesternal irradiado a mandíbula, cuello o brazo izquierdo.",
            "Sudoración fría profusa con náuseas y sensación de muerte.",
            "Pérdida del conocimiento o desmayo súbito."
        ]
    },
    "Insuficiencia Cardíaca Congestiva (ICC)": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Cardiología / Medicina Interna",
        "summary": "Incapacidad del corazón para bombear suficiente sangre, acumulando líquidos en pulmones y extremidades.",
        "clinical_tests": [
            "**NT-proBNP**: Elevación marcada (>400 pg/mL), confirma sobrecarga hemodinámica.",
            "**Ecocardiograma**: Fracción de eyección reducida (<40%).",
            "**Radiografía de Tórax**: Cardiomegalia y líneas B de Kerley."
        ],
        "habits": [
            "**Restricción de líquidos**: Máximo 1.5 litros totales al día.",
            "**Dieta hiposódica**: <2g de sal al día, eliminar procesados.",
            "Dormir con 2-3 almohadas para evitar congestión nocturna.",
            "Pesar diariamente en ayunas; +1.5kg en 2 días = alerta."
        ],
        "medications": [
            "Furosemida 40mg oral por la mañana para eliminar líquidos.",
            "IECA (Enalapril) o Sacubitrilo/Valsartán para remodelación.",
            "Beta-bloqueadores (Carvedilol) bajo control estricto.",
            "**ADVERTENCIA**: Ibuprofeno y Diclofenaco CONTRAINDICADOS — retienen sodio y descompensan."
        ],
        "red_flags": [
            "Ahogo severo al estar acostado que obliga a sentarse.",
            "Aumento rápido de peso con hinchazón en piernas y tobillos.",
            "Tos con esputo espumoso rosado."
        ]
    },
    "Miocarditis": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Cardiología / Medicina Interna",
        "summary": "Inflamación aguda del miocardio secundaria a infecciones virales o respuestas autoinmunes.",
        "clinical_tests": [
            "**Resonancia Magnética Cardíaca**: Edema miocárdico con realce de gadolinio.",
            "**ECG y Troponinas**: Alteraciones del ST y Troponina I elevada.",
            "**Ecocardiograma**: Función sistólica reducida."
        ],
        "habits": [
            "Evitar ejercicio físico vigoroso durante 3-6 meses.",
            "Reposo absoluto en fase inflamatoria aguda.",
            "Alimentación balanceada, libre de estimulantes.",
            "Monitoreo diario de temperatura y frecuencia cardíaca."
        ],
        "medications": [
            "AINEs o Colquicina bajo criterio cardiológico.",
            "IECA/ARA-II si hay compromiso de la fracción de eyección.",
            "Antivirales o antibióticos si etiología confirmada.",
            "**ADVERTENCIA**: Ejercicio intenso en miocarditis activa puede causar muerte súbita."
        ],
        "red_flags": [
            "Palpitaciones severas con mareo.",
            "Dolor punzante en el pecho que mejora al inclinarse.",
            "Falta de aire al realizar mínimos esfuerzos."
        ]
    },
    "Encefalitis": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neurología / Infectología / UCI",
        "summary": "Inflamación difusa del parénquima cerebral, usualmente viral (Herpes Simple). Emergencia neurológica crítica.",
        "clinical_tests": [
            "**Punción Lumbar (LCR)**: Pleocitosis linfocitaria e hiperproteinorraquia.",
            "**PCR del LCR**: Positiva para VHS-1.",
            "**Resonancia Magnética Cerebral**: Hiperseñal T2/FLAIR en lóbulos temporales."
        ],
        "habits": [
            "**TRASLADO INMEDIATO a UCI.**",
            "Posición lateral de seguridad si hay alteración de conciencia.",
            "Entorno silencioso y oscuro, sin estímulos.",
            "Ayuno estricto por riesgo de broncoaspiración."
        ],
        "medications": [
            "Aciclovir IV 10mg/kg cada 8 horas de urgencia.",
            "Anticonvulsivantes profilácticos (Levetiracetam o Fenitoína IV).",
            "Dexametasona IV para reducir edema cerebral.",
            "**ADVERTENCIA**: Retraso en Aciclovir IV → 70% mortalidad o secuelas permanentes."
        ],
        "red_flags": [
            "Crisis epilépticas (convulsiones) súbitas.",
            "Confusión marcada, alucinaciones o agresividad.",
            "Rigidez de nuca intolerable con cefalea severa."
        ]
    },
    "Accidente Cerebrovascular (ACV)": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neurología / Unidad de Ictus / Urgencias",
        "summary": "Interrupción del flujo sanguíneo cerebral o ruptura vascular. Pérdida neuronal acelerada.",
        "clinical_tests": [
            "**TC de Cráneo simple**: Descarta sangrado agudo, permite trombolisis.",
            "**Angio-TC**: Identifica oclusión trombótica en arteria cerebral.",
            "**Glucemia**: Descarta hipoglucemia como causa mimética."
        ],
        "habits": [
            "**TIEMPO ES CEREBRO**: Anotar hora exacta de inicio de síntomas.",
            "No dar comida, líquidos ni aspirina (puede empeorar hemorrágico).",
            "Recostar al paciente con cabeza elevada 30 grados.",
            "Llamar emergencias con código ACV/Ictus."
        ],
        "medications": [
            "**Alteplasa IV** en hospital, dentro de las primeras 4.5 horas del ACV isquémico.",
            "Trombectomía mecánica para oclusiones de grandes arterias.",
            "Control de PA sistólica <180 mmHg con Labetalol IV.",
            "**ADVERTENCIA**: NO bajar la PA bruscamente a valores normales en ACV agudo."
        ],
        "red_flags": [
            "Desviación de la comisura bucal (parálisis facial unilateral).",
            "Debilidad súbita en un brazo o pierna (hemiparesia).",
            "Dificultad repentina para hablar o comprender."
        ]
    },
    "Migraña Severa": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Neurología",
        "summary": "Trastorno neurológico crónico con cefaleas pulsátiles de intensidad severa, típicamente unilaterales.",
        "clinical_tests": [
            "**TC de Cráneo**: Normal, sin hemorragias o tumores.",
            "**Fondo de Ojo**: Sin papiledema (descarta HTE).",
            "**EEG**: Normal entre episodios."
        ],
        "habits": [
            "Aislarse en habitación oscura, fresca y silenciosa.",
            "Compresas frías sobre frente y sienes.",
            "Evitar desencadenantes: chocolate, quesos, alcohol, cafeína.",
            "Mantener horarios de sueño regulares."
        ],
        "medications": [
            "**Abortivo**: Triptanos (Eletriptán 40mg o Sumatriptán 50mg) al inicio.",
            "Ibuprofeno 400mg + Cafeína si cuadro leve-moderado.",
            "Metoclopramida 10mg si hay náuseas.",
            "**ADVERTENCIA**: Analgésicos >10-15 días/mes causan cefalea por rebote."
        ],
        "red_flags": [
            "Dolor de cabeza súbito de intensidad máxima instantánea.",
            "Cefalea con fiebre alta y rigidez de nuca.",
            "Dolor que empeora con esfuerzos físicos progresivamente."
        ]
    },
    "Dengue": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Infectología / Medicina Interna",
        "summary": "Infección viral por Aedes aegypti. Puede evolucionar a dengue grave con sangrado y shock.",
        "clinical_tests": [
            "**Antígeno NS1**: Positivo en sangre durante fase febril.",
            "**Hemograma**: Leucopenia, trombocitopenia progresiva y hemoconcentración.",
            "**Transaminasas (ALT/AST)**: Elevadas en dengue grave."
        ],
        "habits": [
            "**HIDRATACIÓN EXTREMA**: 3-4 litros de suero oral al día.",
            "Reposo bajo mosquitero para evitar transmisión.",
            "Control diario de color y volumen urinario.",
            "Evitar cualquier trauma mecánico (plaquetas bajas)."
        ],
        "medications": [
            "**ÚNICO analgésico**: Paracetamol 500-750mg cada 6-8 horas.",
            "Lavados cutáneos con agua tibia para controlar fiebre.",
            "**PROHIBICIÓN ABSOLUTA**: Aspirina, Ibuprofeno, Diclofenaco — aumentan riesgo de hemorragia.",
            "Prohibidas las inyecciones intramusculares."
        ],
        "red_flags": [
            "Dolor abdominal intenso con vómitos persistentes.",
            "Sangrado de encías, nariz, orina o petequias en piel.",
            "Mareo intenso al pararse o letargia."
        ]
    },
    "Otitis Media": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Otorrinolaringología / Pediatría",
        "summary": "Infección bacteriana o viral en el oído medio, frecuente tras un resfriado.",
        "clinical_tests": [
            "**Otoscopia Neumática**: Membrana timpánica abombada, eritematosa y opaca.",
            "**Timpanometría**: Curva tipo B con efusión en caja timpánica.",
            "**Cultivo de secreción** (si hay perforación)."
        ],
        "habits": [
            "Calor seco local sobre el oído (paño tibio).",
            "Evitar agua en el canal auditivo (tapones con vaselina).",
            "No realizar lavados de oído caseros.",
            "Dormir ligeramente elevado."
        ],
        "medications": [
            "Ibuprofeno 400mg cada 8 horas para el dolor.",
            "**Amoxicilina 500mg-1g** cada 8 horas por 7 días si infección bacteriana.",
            "Gotas analgésicas SOLO si el tímpano no está perforado.",
            "**ADVERTENCIA**: Nunca introducir hisopos ni aceites en el oído."
        ],
        "red_flags": [
            "Parálisis facial unilateral.",
            "Hinchazón y dolor en el hueso detrás de la oreja (mastoiditis).",
            "Salida de secreción purulenta con sangre del oído."
        ]
    },
    "Sinusitis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Otorrinolaringología",
        "summary": "Inflamación e infección de los senos paranasales por retención de moco.",
        "clinical_tests": [
            "**TC de Senos Paranasales**: Engrosamiento mucoso con niveles hidroaéreos.",
            "**Rinoscopia**: Drenaje mucopurulento en meato medio.",
            "**Cultivo de secreción nasal** si falla el tratamiento inicial."
        ],
        "habits": [
            "Lavados nasales con solución salina 3-4 veces al día.",
            "Duchas calientes e inhalación de vapor por 10 minutos.",
            "3 litros de agua al día para diluir el moco.",
            "Paño tibio sobre frente y pómulos para aliviar presión."
        ],
        "medications": [
            "Fluticasona o Mometasona nasal (2 aplicaciones/fosa nasal/día).",
            "Oximetazolina: máximo 3 días consecutivos.",
            "Amoxicilina + Ácido Clavulánico si síntomas >10 días.",
            "**ADVERTENCIA**: Descongestionantes >5 días causan rinitis medicamentosa."
        ],
        "red_flags": [
            "Hinchazón o dolor en ojos con visión doble.",
            "Dolor frontal que no responde a analgésicos fuertes.",
            "Fiebre muy alta con confusión."
        ]
    },
    "COVID-19": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Infectología / Medicina Interna",
        "summary": "Infección viral por SARS-CoV-2 con riesgo de progresión a enfermedad pulmonar severa.",
        "clinical_tests": [
            "**PCR de SARS-CoV-2**: Positiva en casos activos.",
            "**Radiografía de Tórax**: Opacidades en vidrio deslustrado bilaterales.",
            "**Hemograma y ferritina**: Inflamación sistémica en casos moderados."
        ],
        "habits": [
            "Reposo absoluto y aislamiento respiratorio.",
            "Hidratación abundante y control de temperatura cada 4 horas.",
            "Monitoreo de saturación 3 veces al día con oxímetro.",
            "Evitar humo, polvo and aire acondicionado directo."
        ],
        "medications": [
            "Paracetamol 500mg cada 6-8 horas para fiebre y malestar.",
            "Anticoagulación profiláctica solo bajo criterio médico.",
            "No administrar corticoides sin indicación de especialista.",
            "**ADVERTENCIA**: Consultar por telemedicina ante cualquier deterioro."
        ],
        "red_flags": [
            "Saturación <94% en reposo.",
            "Aumento rápido de disnea o esfuerzo respiratorio.",
            "Dolor torácico persistente o confusión súbita."
        ]
    },
    "COVID-19 Grave": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neumología / Infectología / UCI",
        "summary": "Presentación severa de COVID-19 con compromiso respiratorio y riesgo de SDRA.",
        "clinical_tests": [
            "**Gasometría arterial**: Hipoxemia severa (PaO2 <60 mmHg).",
            "**TC de Tórax**: Consolidación bilateral y patrón en vidrio deslustrado.",
            "**IL-6 y Dímero D**: Elevados indican tormenta inflamatoria."
        ],
        "habits": [
            "Posición semisentado para optimizar la oxigenación.",
            "Oxígeno suplementario con mascarilla o cánula nasal.",
            "Evitar deambulación y esfuerzo respiratorio.",
            "Monitoreo continuo de constantes vitales."
        ],
        "medications": [
            "Oxígeno para mantener SpO2 >92%.",
            "Dexametasona 6mg/día (si requiere O2 suplementario).",
            "Anticoagulantes profilácticos.",
            "**ADVERTENCIA**: Hospitalización inmediata es mandatoria."
        ],
        "red_flags": [
            "Uso de músculos accesorios, tiraje o cianosis.",
            "SpO2 <90% a pesar de oxigenoterapia.",
            "Estado mental alterado o somnolencia profunda."
        ]
    },
    "Faringoamigdalitis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Otorrinolaringología",
        "summary": "Inflamación aguda de faringe y amígdalas con odinofagia marcada.",
        "clinical_tests": [
            "**Examen de garganta**: Amígdalas eritematosas con exudado purulento.",
            "**Prueba rápida de estreptococo**: Distingue etiología bacteriana.",
            "**Cultivo faríngeo** si la prueba rápida es negativa con alta sospecha."
        ],
        "habits": [
            "Hidratación frecuente con líquidos fríos o tibios.",
            "Gárgaras suaves con solución salina varias veces al día.",
            "Reposo de la voz, evitar el humo de tabaco.",
            "Habitación ventilada y libre de polvo."
        ],
        "medications": [
            "Paracetamol o Ibuprofeno para el dolor de garganta.",
            "Antibióticos solo si la prueba confirma infección estreptocócica.",
            "Sprays o pastillas anestésicas locales para la odinofagia.",
            "**ADVERTENCIA**: No automedicarse con antibióticos sin confirmación bacteriana."
        ],
        "red_flags": [
            "Dificultad para tragar saliva o abrir bien la boca.",
            "Fiebre alta persistente >72 horas.",
            "Aumento rápido de dolor con voz apagada (absceso periamigdalino)."
        ]
    },
    "Tromboembolismo Pulmonar": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Cardiología / Neumología / Urgencias",
        "summary": "Oclusión aguda de arterias pulmonares por coágulos con repercusión hemodinámica potencialmente letal.",
        "clinical_tests": [
            "**Angio-TC Pulmonar**: Defecto de llenado en arterias pulmonares (gold standard).",
            "**Dímero D**: Elevado (>500 ng/mL) en contexto clínico.",
            "**ECG**: Patrón S1Q3T3 o taquicardia sinusal.",
            "**Ecocardiograma**: Disfunción ventricular derecha."
        ],
        "habits": [
            "Reposo absoluto hasta valoración hospitalaria.",
            "Evitar cualquier esfuerzo o cambio posicional brusco.",
            "No automedicarse con anticoagulantes.",
            "Notificar cualquier sangre en esputo o dolor torácico."
        ],
        "medications": [
            "Anticoagulantes iniciales bajo supervisión hospitalaria (Heparina o HBPM).",
            "Terapia trombolítica en compromiso hemodinámico grave.",
            "Oxígeno suplementario durante la evaluación.",
            "**ADVERTENCIA**: Hospitalización urgente obligatoria."
        ],
        "red_flags": [
            "Dolor torácico pleurítico súbito y severo.",
            "Disnea intensa de aparición brusca sin explicación.",
            "Hemoptisis o mareo con presión arterial baja."
        ]
    },
    "Diabetes Mellitus Tipo 2": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Endocrinología / Medicina Interna",
        "summary": "Enfermedad metabólica crónica por resistencia a la insulina con hiperglucemia crónica.",
        "clinical_tests": [
            "**Glucosa en Ayunas**: ≥126 mg/dL en dos ocasiones confirma diagnóstico.",
            "**Hemoglobina Glicosilada (HbA1c)**: ≥6.5% indica mal control crónico.",
            "**Perfil Lipídico**: Evalúa riesgo cardiovascular asociado.",
            "**Función Renal y Microalbuminuria**: Detección temprana de nefropatía."
        ],
        "habits": [
            "Dieta estricta baja en carbohidratos simples y azúcares refinados.",
            "Ejercicio cardiovascular regular moderado (30 min diarios).",
            "Cuidado minucioso de los pies para prevenir úlceras.",
            "Automonitoreo de glucemia capilar según pauta médica."
        ],
        "medications": [
            "Metformina 500-850mg con las comidas principales.",
            "Inhibidores de SGLT2 (Empagliflozina) si hay riesgo cardiovascular.",
            "Insulina según requerimiento y control glucémico.",
            "**ADVERTENCIA**: Hipoglucemia (<70 mg/dL) es emergencia: consumir azúcar inmediatamente."
        ],
        "red_flags": [
            "Alteración grave de la conciencia o aliento afrutado (cetoacidosis).",
            "Glucosa persistente >300 mg/dL.",
            "Pérdida de visión súbita o dolor en el pie con cambio de color."
        ]
    },
    "Gastroenteritis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Gastroenterología / Medicina General",
        "summary": "Inflamación del tracto gastrointestinal (estómago e intestinos) de etiología viral, bacteriana o parasitaria.",
        "clinical_tests": [
            "**Coprocultivo**: Identificación de patógenos bacterianos.",
            "**Examen Parasitológico de Heces**: Identificación de parásitos.",
            "**Electrólitos Séricos**: Evaluar estado de deshidratación si vómitos de gran volumen."
        ],
        "habits": [
            "Hidratación oral constante con suero oral (evitar bebidas azucaradas).",
            "Dieta blanda astringente (arroz, plátano, manzana, pollo hervido).",
            "Lavado de manos estricto antes de comer y después de ir al baño.",
            "Reposo relativo según tolerancia física."
        ],
        "medications": [
            "Probióticos para restauración de la flora intestinal.",
            "Paracetamol 500mg para la fiebre o dolor abdominal (máx 3g/día).",
            "Suero de rehidratación oral (SRO).",
            "**ADVERTENCIA**: Evitar el uso de Loperamida (antidiarreico) si hay sospecha de diarrea bacteriana/invasiva."
        ],
        "red_flags": [
            "Signos de deshidratación severa (boca seca, llanto sin lágrimas, ausencia de orina).",
            "Presencia de sangre, moco o pus en las heces (disentería).",
            "Vómitos incoercibles que impiden la tolerancia oral."
        ]
    },
    "Resfriado Común (Rinofaringitis)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Familiar",
        "summary": "Infección viral autolimitada y benigna de las vías respiratorias superiores, caracterizada por congestión, estornudos y malestar leve.",
        "clinical_tests": [
            "**Examen Clínico Nasofaríngeo**: Mucosa nasal eritematosa y congestionada.",
            "**Radiografía de Tórax**: Normal, campos pulmonares limpios."
        ],
        "habits": [
            "Abundante reposo e hidratación (mínimo 2 litros de agua/líquidos templados al día).",
            "Evitar ambientes fríos o con corrientes de aire.",
            "Lavarse las manos frecuentemente para evitar contagio familiar."
        ],
        "medications": [
            "Paracetamol 500mg vía oral cada 8 horas si hay febrícula o dolor de cabeza.",
            "Lavados nasales frecuentes con solución salina estéril.",
            "Antihistamínicos si la rinorrea o estornudos son muy molestos."
        ],
        "red_flags": [
            "Dificultad respiratoria o silbidos en el pecho.",
            "Fiebre alta (>38.5 °C) que no responde a antipiréticos.",
            "Dolor de oído intenso."
        ]
    },
    "Infección de Vías Urinarias (IVU)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Urología / Medicina General / Ginecología",
        "summary": "Colonización e infección bacteriana de la vejiga urinaria (cistitis), común en mujeres y tratable con antibióticos estándar.",
        "clinical_tests": [
            "**Examen General de Orina (EGO)**: Leucocituria marcada, bacterias y nitritos positivos.",
            "**Urocultivo con Antibiograma**: Confirma agente bacteriano (usualmente E. coli) y sensibilidad antibiótica."
        ],
        "habits": [
            "Hidratación oral agresiva con 3 litros de agua al día para lavado vesical.",
            "Orinar inmediatamente después del coito y no retener la micción.",
            "Higiene íntima de adelante hacia atrás."
        ],
        "medications": [
            "**Antibiótico**: Nitrofurantoína 100mg cada 12 horas por 5 días (o ciprofloxacino bajo criterio médico).",
            "Fenazopiridina 100mg cada 8 horas por 2 días para el ardor.",
            "**ADVERTENCIA**: Completar el esquema antibiótico completo para evitar resistencia."
        ],
        "red_flags": [
            "Fiebre alta con escalofríos y dolor lumbar fuerte (sospecha de pielonefritis).",
            "Vómitos que impiden la toma del antibiótico.",
            "Sangre abundante en la orina."
        ]
    },
    "Reflujo Gastroesofágico (ERGE)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Gastroenterología / Medicina Interna",
        "summary": "Retorno del contenido ácido del estómago hacia el esófago debido a disfunción del esfínter esofágico inferior, produciendo acidez.",
        "clinical_tests": [
            "**Endoscopia Digestiva Alta (EDA)**: Descarta esofagitis, hernia hiatal o esófago de Barrett.",
            "**Manometría esofágica / pH-metría** de 24 horas (casos resistentes)."
        ],
        "habits": [
            "Evitar acostarse antes de 2 a 3 horas después de comer.",
            "Elevar la cabecera de la cama unos 15 cm.",
            "Evitar alimentos desencadenantes: grasas, picantes, chocolate, café, menta y alcohol.",
            "Comer porciones pequeñas y frecuentes."
        ],
        "medications": [
            "**Inhibidor de Bomba de Protones**: Omeprazol 20mg vía oral en ayunas 30 min antes del desayuno.",
            "Antiácidos de barrera (alginato de sodio + bicarbonato) tras las comidas.",
            "Procinéticos si hay vaciamiento gástrico lento."
        ],
        "red_flags": [
            "Dificultad o dolor al tragar comida (disfagia/odinofagia).",
            "Pérdida de peso involuntaria.",
            "Vómitos oscuros (con sangre digerida o melenas)."
        ]
    }
}

# MOTOR DE DIAGNÓSTICO BAYESIANO v2.1 — CON LOG-SPACE Y LAPLACE SMOOTHING
class BayesianDiagnosticSystem:
    LAPLACE_ALPHA = 0.01  # Suavizado de Laplace para evitar P=0

    def __init__(self):
        self.enfermedades = list(CLINICAL_METADATA.keys())

        # ── PROBABILIDADES PREVIAS BASE (Epidemiológicas)
        self.P_enfermedad_base = {
            "Gripe Común / Influenza":                 0.09,
            "Neumonía":                                0.06,
            "Bronquitis Aguda":                        0.06,
            "Crisis Asmática Aguda":                   0.04,
            "Exacerbación Aguda de EPOC":              0.03,
            "Infarto Agudo de Miocardio (IAM)":        0.04,
            "Insuficiencia Cardíaca Congestiva (ICC)": 0.04,
            "Miocarditis":                             0.02,
            "Encefalitis":                             0.01,
            "Accidente Cerebrovascular (ACV)":         0.04,
            "Migraña Severa":                          0.05,
            "Dengue":                                  0.05,
            "Otitis Media":                            0.05,
            "Sinusitis Aguda":                         0.05,
            "COVID-19":                                0.07,
            "COVID-19 Grave":                          0.02,
            "Faringoamigdalitis Aguda":                0.05,
            "Tromboembolismo Pulmonar":                0.02,
            "Diabetes Mellitus Tipo 2":                0.05,
            "Gastroenteritis Aguda":                   0.06,
            "Resfriado Común (Rinofaringitis)":        0.08,
            "Infección de Vías Urinarias (IVU)":       0.07,
            "Reflujo Gastroesofágico (ERGE)":          0.06,
        }

        # ── PROBABILIDADES CONDICIONALES: P(Síntoma | Enfermedad)
        self.P_sintoma = {
            "Tos Persistente": {
                "Gripe Común / Influenza": 0.72, "Neumonía": 0.85, "Bronquitis Aguda": 0.92, "Crisis Asmática Aguda": 0.75,
                "Exacerbación Aguda de EPOC": 0.88, "Infarto Agudo de Miocardio (IAM)": 0.10, "Insuficiencia Cardíaca Congestiva (ICC)": 0.60,
                "Miocarditis": 0.18, "Encefalitis": 0.05, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.03,
                "Dengue": 0.15, "Otitis Media": 0.10, "Sinusitis Aguda": 0.38, "COVID-19": 0.82, "COVID-19 Grave": 0.90,
                "Faringoamigdalitis Aguda": 0.28, "Tromboembolismo Pulmonar": 0.35, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.65, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.15
            },
            "Dificultad Respiratoria (Disnea)": {
                "Gripe Común / Influenza": 0.15, "Neumonía": 0.88, "Bronquitis Aguda": 0.45, "Crisis Asmática Aguda": 0.97,
                "Exacerbación Aguda de EPOC": 0.98, "Infarto Agudo de Miocardio (IAM)": 0.62, "Insuficiencia Cardíaca Congestiva (ICC)": 0.95,
                "Miocarditis": 0.65, "Encefalitis": 0.15, "Accidente Cerebrovascular (ACV)": 0.20, "Migraña Severa": 0.03,
                "Dengue": 0.22, "Otitis Media": 0.03, "Sinusitis Aguda": 0.05, "COVID-19": 0.68, "COVID-19 Grave": 0.98,
                "Faringoamigdalitis Aguda": 0.10, "Tromboembolismo Pulmonar": 0.95, "Diabetes Mellitus Tipo 2": 0.08,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.05, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.02
            },
            "Tos con Sangre (Hemoptisis)": {
                "Gripe Común / Influenza": 0.02, "Neumonía": 0.18, "Bronquitis Aguda": 0.05, "Crisis Asmática Aguda": 0.03,
                "Exacerbación Aguda de EPOC": 0.10, "Infarto Agudo de Miocardio (IAM)": 0.02, "Insuficiencia Cardíaca Congestiva (ICC)": 0.08,
                "Miocarditis": 0.02, "Encefalitis": 0.01, "Accidente Cerebrovascular (ACV)": 0.01, "Migraña Severa": 0.01,
                "Dengue": 0.20, "Otitis Media": 0.01, "Sinusitis Aguda": 0.02, "COVID-19": 0.05, "COVID-19 Grave": 0.12,
                "Faringoamigdalitis Aguda": 0.02, "Tromboembolismo Pulmonar": 0.25, "Diabetes Mellitus Tipo 2": 0.02,
                "Gastroenteritis Aguda": 0.01, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Dolor en el Pecho": {
                "Gripe Común / Influenza": 0.10, "Neumonía": 0.65, "Bronquitis Aguda": 0.35, "Crisis Asmática Aguda": 0.30,
                "Exacerbación Aguda de EPOC": 0.40, "Infarto Agudo de Miocardio (IAM)": 0.98, "Insuficiencia Cardíaca Congestiva (ICC)": 0.38,
                "Miocarditis": 0.90, "Encefalitis": 0.02, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.02,
                "Dengue": 0.12, "Otitis Media": 0.02, "Sinusitis Aguda": 0.05, "COVID-19": 0.28, "COVID-19 Grave": 0.60,
                "Faringoamigdalitis Aguda": 0.05, "Tromboembolismo Pulmonar": 0.90, "Diabetes Mellitus Tipo 2": 0.12,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.05, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.45
            },
            "Palpitaciones": {
                "Gripe Común / Influenza": 0.10, "Neumonía": 0.15, "Bronquitis Aguda": 0.08, "Crisis Asmática Aguda": 0.15,
                "Exacerbación Aguda de EPOC": 0.20, "Infarto Agudo de Miocardio (IAM)": 0.50, "Insuficiencia Cardíaca Congestiva (ICC)": 0.65,
                "Miocarditis": 0.80, "Encefalitis": 0.10, "Accidente Cerebrovascular (ACV)": 0.10, "Migraña Severa": 0.05,
                "Dengue": 0.20, "Otitis Media": 0.02, "Sinusitis Aguda": 0.02, "COVID-19": 0.18, "COVID-19 Grave": 0.30,
                "Faringoamigdalitis Aguda": 0.05, "Tromboembolismo Pulmonar": 0.55, "Diabetes Mellitus Tipo 2": 0.10,
                "Gastroenteritis Aguda": 0.05, "Resfriado Común (Rinofaringitis)": 0.05, "Infección de Vías Urinarias (IVU)": 0.05,
                "Reflujo Gastroesofágico (ERGE)": 0.05
            },
            "Edema (Hinchazón)": {
                "Gripe Común / Influenza": 0.03, "Neumonía": 0.08, "Bronquitis Aguda": 0.03, "Crisis Asmática Aguda": 0.03,
                "Exacerbación Aguda de EPOC": 0.35, "Infarto Agudo de Miocardio (IAM)": 0.20, "Insuficiencia Cardíaca Congestiva (ICC)": 0.92,
                "Miocarditis": 0.40, "Encefalitis": 0.05, "Accidente Cerebrovascular (ACV)": 0.10, "Migraña Severa": 0.02,
                "Dengue": 0.30, "Otitis Media": 0.02, "Sinusitis Aguda": 0.03, "COVID-19": 0.10, "COVID-19 Grave": 0.20,
                "Faringoamigdalitis Aguda": 0.02, "Tromboembolismo Pulmonar": 0.25, "Diabetes Mellitus Tipo 2": 0.30,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.02,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Dolor de Cabeza Severo": {
                "Gripe Común / Influenza": 0.62, "Neumonía": 0.22, "Bronquitis Aguda": 0.15, "Crisis Asmática Aguda": 0.10,
                "Exacerbación Aguda de EPOC": 0.22, "Infarto Agudo de Miocardio (IAM)": 0.05, "Insuficiencia Cardíaca Congestiva (ICC)": 0.10,
                "Miocarditis": 0.15, "Encefalitis": 0.88, "Accidente Cerebrovascular (ACV)": 0.62, "Migraña Severa": 0.99,
                "Dengue": 0.88, "Otitis Media": 0.42, "Sinusitis Aguda": 0.68, "COVID-19": 0.48, "COVID-19 Grave": 0.42,
                "Faringoamigdalitis Aguda": 0.32, "Tromboembolismo Pulmonar": 0.15, "Diabetes Mellitus Tipo 2": 0.18,
                "Gastroenteritis Aguda": 0.10, "Resfriado Común (Rinofaringitis)": 0.35, "Infección de Vías Urinarias (IVU)": 0.05,
                "Reflujo Gastroesofágico (ERGE)": 0.05
            },
            "Confusión / Convulsiones": {
                "Gripe Común / Influenza": 0.03, "Neumonía": 0.18, "Bronquitis Aguda": 0.02, "Crisis Asmática Aguda": 0.05,
                "Exacerbación Aguda de EPOC": 0.28, "Infarto Agudo de Miocardio (IAM)": 0.22, "Insuficiencia Cardíaca Congestiva (ICC)": 0.15,
                "Miocarditis": 0.15, "Encefalitis": 0.95, "Accidente Cerebrovascular (ACV)": 0.52, "Migraña Severa": 0.03,
                "Dengue": 0.18, "Otitis Media": 0.05, "Sinusitis Aguda": 0.03, "COVID-19": 0.12, "COVID-19 Grave": 0.28,
                "Faringoamigdalitis Aguda": 0.02, "Tromboembolismo Pulmonar": 0.15, "Diabetes Mellitus Tipo 2": 0.15,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.02,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Pérdida de Fuerza/Sensibilidad Unilateral": {
                "Gripe Común / Influenza": 0.01, "Neumonía": 0.01, "Bronquitis Aguda": 0.01, "Crisis Asmática Aguda": 0.01,
                "Exacerbación Aguda de EPOC": 0.01, "Infarto Agudo de Miocardio (IAM)": 0.05, "Insuficiencia Cardíaca Congestiva (ICC)": 0.02,
                "Miocarditis": 0.02, "Encefalitis": 0.32, "Accidente Cerebrovascular (ACV)": 0.98, "Migraña Severa": 0.06,
                "Dengue": 0.02, "Otitis Media": 0.01, "Sinusitis Aguda": 0.01, "COVID-19": 0.05, "COVID-19 Grave": 0.08,
                "Faringoamigdalitis Aguda": 0.01, "Tromboembolismo Pulmonar": 0.03, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.01, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Dificultad para Hablar/Entender": {
                "Gripe Común / Influenza": 0.01, "Neumonía": 0.02, "Bronquitis Aguda": 0.01, "Crisis Asmática Aguda": 0.01,
                "Exacerbación Aguda de EPOC": 0.05, "Infarto Agudo de Miocardio (IAM)": 0.05, "Insuficiencia Cardíaca Congestiva (ICC)": 0.05,
                "Miocarditis": 0.02, "Encefalitis": 0.42, "Accidente Cerebrovascular (ACV)": 0.95, "Migraña Severa": 0.03,
                "Dengue": 0.02, "Otitis Media": 0.01, "Sinusitis Aguda": 0.01, "COVID-19": 0.05, "COVID-19 Grave": 0.10,
                "Faringoamigdalitis Aguda": 0.02, "Tromboembolismo Pulmonar": 0.03, "Diabetes Mellitus Tipo 2": 0.03,
                "Gastroenteritis Aguda": 0.01, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Mareos / Vértigo": {
                "Gripe Común / Influenza": 0.35, "Neumonía": 0.18, "Bronquitis Aguda": 0.12, "Crisis Asmática Aguda": 0.10,
                "Exacerbación Aguda de EPOC": 0.22, "Infarto Agudo de Miocardio (IAM)": 0.30, "Insuficiencia Cardíaca Congestiva (ICC)": 0.35,
                "Miocarditis": 0.28, "Encefalitis": 0.45, "Accidente Cerebrovascular (ACV)": 0.60, "Migraña Severa": 0.72,
                "Dengue": 0.55, "Otitis Media": 0.50, "Sinusitis Aguda": 0.30, "COVID-19": 0.35, "COVID-19 Grave": 0.40,
                "Faringoamigdalitis Aguda": 0.12, "Tromboembolismo Pulmonar": 0.35, "Diabetes Mellitus Tipo 2": 0.20,
                "Gastroenteritis Aguda": 0.20, "Resfriado Común (Rinofaringitis)": 0.15, "Infección de Vías Urinarias (IVU)": 0.05,
                "Reflujo Gastroesofágico (ERGE)": 0.05
            },
            "Fiebre Alta": {
                "Gripe Común / Influenza": 0.88, "Neumonía": 0.85, "Bronquitis Aguda": 0.40, "Crisis Asmática Aguda": 0.25,
                "Exacerbación Aguda de EPOC": 0.38, "Infarto Agudo de Miocardio (IAM)": 0.08, "Insuficiencia Cardíaca Congestiva (ICC)": 0.10,
                "Miocarditis": 0.75, "Encefalitis": 0.90, "Accidente Cerebrovascular (ACV)": 0.08, "Migraña Severa": 0.05,
                "Dengue": 0.98, "Otitis Media": 0.70, "Sinusitis Aguda": 0.62, "COVID-19": 0.85, "COVID-19 Grave": 0.90,
                "Faringoamigdalitis Aguda": 0.82, "Tromboembolismo Pulmonar": 0.15, "Diabetes Mellitus Tipo 2": 0.10,
                "Gastroenteritis Aguda": 0.40, "Resfriado Común (Rinofaringitis)": 0.10, "Infección de Vías Urinarias (IVU)": 0.35,
                "Reflujo Gastroesofágico (ERGE)": 0.02
            },
            "Fatiga / Cansancio Extremo": {
                "Gripe Común / Influenza": 0.82, "Neumonía": 0.78, "Bronquitis Aguda": 0.55, "Crisis Asmática Aguda": 0.45,
                "Exacerbación Aguda de EPOC": 0.72, "Infarto Agudo de Miocardio (IAM)": 0.45, "Insuficiencia Cardíaca Congestiva (ICC)": 0.85,
                "Miocarditis": 0.80, "Encefalitis": 0.70, "Accidente Cerebrovascular (ACV)": 0.35, "Migraña Severa": 0.55,
                "Dengue": 0.92, "Otitis Media": 0.38, "Sinusitis Aguda": 0.48, "COVID-19": 0.88, "COVID-19 Grave": 0.95,
                "Faringoamigdalitis Aguda": 0.52, "Tromboembolismo Pulmonar": 0.55, "Diabetes Mellitus Tipo 2": 0.62,
                "Gastroenteritis Aguda": 0.60, "Resfriado Común (Rinofaringitis)": 0.40, "Infección de Vías Urinarias (IVU)": 0.30,
                "Reflujo Gastroesofágico (ERGE)": 0.15
            },
            "Dolor de Cuerpo Generalizado": {
                "Gripe Común / Influenza": 0.78, "Neumonía": 0.38, "Bronquitis Aguda": 0.30, "Crisis Asmática Aguda": 0.12,
                "Exacerbación Aguda de EPOC": 0.22, "Infarto Agudo de Miocardio (IAM)": 0.18, "Insuficiencia Cardíaca Congestiva (ICC)": 0.28,
                "Miocarditis": 0.38, "Encefalitis": 0.42, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.12,
                "Dengue": 0.98, "Otitis Media": 0.22, "Sinusitis Aguda": 0.32, "COVID-19": 0.75, "COVID-19 Grave": 0.82,
                "Faringoamigdalitis Aguda": 0.42, "Tromboembolismo Pulmonar": 0.22, "Diabetes Mellitus Tipo 2": 0.18,
                "Gastroenteritis Aguda": 0.30, "Resfriado Común (Rinofaringitis)": 0.30, "Infección de Vías Urinarias (IVU)": 0.10,
                "Reflujo Gastroesofágico (ERGE)": 0.02
            },
            "Pérdida del Olfato o Gusto": {
                "Gripe Común / Influenza": 0.20, "Neumonía": 0.10, "Bronquitis Aguda": 0.08, "Crisis Asmática Aguda": 0.05,
                "Exacerbación Aguda de EPOC": 0.08, "Infarto Agudo de Miocardio (IAM)": 0.02, "Insuficiencia Cardíaca Congestiva (ICC)": 0.02,
                "Miocarditis": 0.02, "Encefalitis": 0.08, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.02,
                "Dengue": 0.05, "Otitis Media": 0.05, "Sinusitis Aguda": 0.42, "COVID-19": 0.78, "COVID-19 Grave": 0.62,
                "Faringoamigdalitis Aguda": 0.12, "Tromboembolismo Pulmonar": 0.02, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.01, "Resfriado Común (Rinofaringitis)": 0.08, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Erupciones Cutáneas (Rash)": {
                "Gripe Común / Influenza": 0.05, "Neumonía": 0.05, "Bronquitis Aguda": 0.02, "Crisis Asmática Aguda": 0.05,
                "Exacerbación Aguda de EPOC": 0.02, "Infarto Agudo de Miocardio (IAM)": 0.02, "Insuficiencia Cardíaca Congestiva (ICC)": 0.02,
                "Miocarditis": 0.05, "Encefalitis": 0.10, "Accidente Cerebrovascular (ACV)": 0.02, "Migraña Severa": 0.02,
                "Dengue": 0.72, "Otitis Media": 0.02, "Sinusitis Aguda": 0.02, "COVID-19": 0.18, "COVID-19 Grave": 0.12,
                "Faringoamigdalitis Aguda": 0.10, "Tromboembolismo Pulmonar": 0.02, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.05, "Resfriado Común (Rinofaringitis)": 0.02, "Infección de Vías Urinarias (IVU)": 0.02,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Náuseas / Vómitos": {
                "Gripe Común / Influenza": 0.25, "Neumonía": 0.25, "Bronquitis Aguda": 0.12, "Crisis Asmática Aguda": 0.10,
                "Exacerbación Aguda de EPOC": 0.20, "Infarto Agudo de Miocardio (IAM)": 0.48, "Insuficiencia Cardíaca Congestiva (ICC)": 0.22,
                "Miocarditis": 0.25, "Encefalitis": 0.55, "Accidente Cerebrovascular (ACV)": 0.35, "Migraña Severa": 0.75,
                "Dengue": 0.75, "Otitis Media": 0.25, "Sinusitis Aguda": 0.20, "COVID-19": 0.38, "COVID-19 Grave": 0.42,
                "Faringoamigdalitis Aguda": 0.28, "Tromboembolismo Pulmonar": 0.18, "Diabetes Mellitus Tipo 2": 0.28,
                "Gastroenteritis Aguda": 0.85, "Resfriado Común (Rinofaringitis)": 0.05, "Infección de Vías Urinarias (IVU)": 0.20,
                "Reflujo Gastroesofágico (ERGE)": 0.45
            },
            "Diarrea": {
                "Gripe Común / Influenza": 0.15, "Neumonía": 0.12, "Bronquitis Aguda": 0.05, "Crisis Asmática Aguda": 0.03,
                "Exacerbación Aguda de EPOC": 0.05, "Infarto Agudo de Miocardio (IAM)": 0.05, "Insuficiencia Cardíaca Congestiva (ICC)": 0.05,
                "Miocarditis": 0.08, "Encefalitis": 0.12, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.05,
                "Dengue": 0.40, "Otitis Media": 0.05, "Sinusitis Aguda": 0.05, "COVID-19": 0.32, "COVID-19 Grave": 0.28,
                "Faringoamigdalitis Aguda": 0.08, "Tromboembolismo Pulmonar": 0.05, "Diabetes Mellitus Tipo 2": 0.15,
                "Gastroenteritis Aguda": 0.95, "Resfriado Común (Rinofaringitis)": 0.02, "Infección de Vías Urinarias (IVU)": 0.02,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Dolor Abdominal Agudo": {
                "Gripe Común / Influenza": 0.10, "Neumonía": 0.12, "Bronquitis Aguda": 0.05, "Crisis Asmática Aguda": 0.05,
                "Exacerbación Aguda de EPOC": 0.08, "Infarto Agudo de Miocardio (IAM)": 0.15, "Insuficiencia Cardíaca Congestiva (ICC)": 0.15,
                "Miocarditis": 0.12, "Encefalitis": 0.15, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.08,
                "Dengue": 0.75, "Otitis Media": 0.05, "Sinusitis Aguda": 0.08, "COVID-19": 0.25, "COVID-19 Grave": 0.30,
                "Faringoamigdalitis Aguda": 0.05, "Tromboembolismo Pulmonar": 0.10, "Diabetes Mellitus Tipo 2": 0.35,
                "Gastroenteritis Aguda": 0.88, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.18,
                "Reflujo Gastroesofágico (ERGE)": 0.30
            },
            "Dolor de Garganta": {
                "Gripe Común / Influenza": 0.82, "Neumonía": 0.18, "Bronquitis Aguda": 0.42, "Crisis Asmática Aguda": 0.10,
                "Exacerbación Aguda de EPOC": 0.15, "Infarto Agudo de Miocardio (IAM)": 0.02, "Insuficiencia Cardíaca Congestiva (ICC)": 0.05,
                "Miocarditis": 0.05, "Encefalitis": 0.10, "Accidente Cerebrovascular (ACV)": 0.02, "Migraña Severa": 0.02,
                "Dengue": 0.48, "Otitis Media": 0.32, "Sinusitis Aguda": 0.48, "COVID-19": 0.52, "COVID-19 Grave": 0.32,
                "Faringoamigdalitis Aguda": 0.99, "Tromboembolismo Pulmonar": 0.05, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.70, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.15
            },
            "Dolor de Oído / Cara": {
                "Gripe Común / Influenza": 0.22, "Neumonía": 0.05, "Bronquitis Aguda": 0.05, "Crisis Asmática Aguda": 0.02,
                "Exacerbación Aguda de EPOC": 0.05, "Infarto Agudo de Miocardio (IAM)": 0.05, "Insuficiencia Cardíaca Congestiva (ICC)": 0.02,
                "Miocarditis": 0.05, "Encefalitis": 0.12, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.18,
                "Dengue": 0.28, "Otitis Media": 0.97, "Sinusitis Aguda": 0.88, "COVID-19": 0.28, "COVID-19 Grave": 0.15,
                "Faringoamigdalitis Aguda": 0.45, "Tromboembolismo Pulmonar": 0.02, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.20, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Disuria (Ardor al orinar)": {
                "Gripe Común / Influenza": 0.01, "Neumonía": 0.01, "Bronquitis Aguda": 0.01, "Crisis Asmática Aguda": 0.01,
                "Exacerbación Aguda de EPOC": 0.01, "Infarto Agudo de Miocardio (IAM)": 0.01, "Insuficiencia Cardíaca Congestiva (ICC)": 0.01,
                "Miocarditis": 0.01, "Encefalitis": 0.01, "Accidente Cerebrovascular (ACV)": 0.01, "Migraña Severa": 0.01,
                "Dengue": 0.05, "Otitis Media": 0.01, "Sinusitis Aguda": 0.01, "COVID-19": 0.01, "COVID-19 Grave": 0.01,
                "Faringoamigdalitis Aguda": 0.01, "Tromboembolismo Pulmonar": 0.01, "Diabetes Mellitus Tipo 2": 0.25,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.98,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Polaquiuria (Orinar muy seguido)": {
                "Gripe Común / Influenza": 0.01, "Neumonía": 0.01, "Bronquitis Aguda": 0.01, "Crisis Asmática Aguda": 0.01,
                "Exacerbación Aguda de EPOC": 0.01, "Infarto Agudo de Miocardio (IAM)": 0.01, "Insuficiencia Cardíaca Congestiva (ICC)": 0.01,
                "Miocarditis": 0.01, "Encefalitis": 0.01, "Accidente Cerebrovascular (ACV)": 0.01, "Migraña Severa": 0.01,
                "Dengue": 0.05, "Otitis Media": 0.01, "Sinusitis Aguda": 0.01, "COVID-19": 0.01, "COVID-19 Grave": 0.01,
                "Faringoamigdalitis Aguda": 0.01, "Tromboembolismo Pulmonar": 0.01, "Diabetes Mellitus Tipo 2": 0.40,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.92,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Dolor Lumbar / Suprapúbico": {
                "Gripe Común / Influenza": 0.15, "Neumonía": 0.05, "Bronquitis Aguda": 0.02, "Crisis Asmática Aguda": 0.01,
                "Exacerbación Aguda de EPOC": 0.01, "Infarto Agudo de Miocardio (IAM)": 0.02, "Insuficiencia Cardíaca Congestiva (ICC)": 0.10,
                "Miocarditis": 0.05, "Encefalitis": 0.05, "Accidente Cerebrovascular (ACV)": 0.02, "Migraña Severa": 0.05,
                "Dengue": 0.35, "Otitis Media": 0.01, "Sinusitis Aguda": 0.02, "COVID-19": 0.05, "COVID-19 Grave": 0.05,
                "Faringoamigdalitis Aguda": 0.01, "Tromboembolismo Pulmonar": 0.05, "Diabetes Mellitus Tipo 2": 0.12,
                "Gastroenteritis Aguda": 0.15, "Resfriado Común (Rinofaringitis)": 0.02, "Infección de Vías Urinarias (IVU)": 0.85,
                "Reflujo Gastroesofágico (ERGE)": 0.05
            },
            "Pirosis (Acidez estomacal)": {
                "Gripe Común / Influenza": 0.02, "Neumonía": 0.02, "Bronquitis Aguda": 0.02, "Crisis Asmática Aguda": 0.02,
                "Exacerbación Aguda de EPOC": 0.05, "Infarto Agudo de Miocardio (IAM)": 0.20, "Insuficiencia Cardíaca Congestiva (ICC)": 0.05,
                "Miocarditis": 0.02, "Encefalitis": 0.01, "Accidente Cerebrovascular (ACV)": 0.01, "Migraña Severa": 0.01,
                "Dengue": 0.05, "Otitis Media": 0.01, "Sinusitis Aguda": 0.01, "COVID-19": 0.05, "COVID-19 Grave": 0.05,
                "Faringoamigdalitis Aguda": 0.02, "Tromboembolismo Pulmonar": 0.02, "Diabetes Mellitus Tipo 2": 0.15,
                "Gastroenteritis Aguda": 0.22, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.98
            },
            "Regurgitación Ácida": {
                "Gripe Común / Influenza": 0.01, "Neumonía": 0.01, "Bronquitis Aguda": 0.01, "Crisis Asmática Aguda": 0.01,
                "Exacerbación Aguda de EPOC": 0.02, "Infarto Agudo de Miocardio (IAM)": 0.10, "Insuficiencia Cardíaca Congestiva (ICC)": 0.02,
                "Miocarditis": 0.01, "Encefalitis": 0.01, "Accidente Cerebrovascular (ACV)": 0.01, "Migraña Severa": 0.01,
                "Dengue": 0.02, "Otitis Media": 0.01, "Sinusitis Aguda": 0.01, "COVID-19": 0.02, "COVID-19 Grave": 0.02,
                "Faringoamigdalitis Aguda": 0.01, "Tromboembolismo Pulmonar": 0.01, "Diabetes Mellitus Tipo 2": 0.08,
                "Gastroenteritis Aguda": 0.10, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.95
            },
            "Congestión Nasal / Estornudos": {
                "Gripe Común / Influenza": 0.85, "Neumonía": 0.08, "Bronquitis Aguda": 0.22, "Crisis Asmática Aguda": 0.15,
                "Exacerbación Aguda de EPOC": 0.05, "Infarto Agudo de Miocardio (IAM)": 0.01, "Insuficiencia Cardíaca Congestiva (ICC)": 0.02,
                "Miocarditis": 0.02, "Encefalitis": 0.02, "Accidente Cerebrovascular (ACV)": 0.01, "Migraña Severa": 0.05,
                "Dengue": 0.25, "Otitis Media": 0.28, "Sinusitis Aguda": 0.82, "COVID-19": 0.72, "COVID-19 Grave": 0.35,
                "Faringoamigdalitis Aguda": 0.55, "Tromboembolismo Pulmonar": 0.01, "Diabetes Mellitus Tipo 2": 0.02,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.95, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Rinorrea (Moqueo)": {
                "Gripe Común / Influenza": 0.82, "Neumonía": 0.05, "Bronquitis Aguda": 0.18, "Crisis Asmática Aguda": 0.12,
                "Exacerbación Aguda de EPOC": 0.03, "Infarto Agudo de Miocardio (IAM)": 0.01, "Insuficiencia Cardíaca Congestiva (ICC)": 0.01,
                "Miocarditis": 0.01, "Encefalitis": 0.01, "Accidente Cerebrovascular (ACV)": 0.01, "Migraña Severa": 0.02,
                "Dengue": 0.20, "Otitis Media": 0.25, "Sinusitis Aguda": 0.75, "COVID-19": 0.68, "COVID-19 Grave": 0.30,
                "Faringoamigdalitis Aguda": 0.48, "Tromboembolismo Pulmonar": 0.01, "Diabetes Mellitus Tipo 2": 0.02,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.92, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Fiebre": {
                "Gripe Común / Influenza": 0.88, "Neumonía": 0.85, "Bronquitis Aguda": 0.38, "Crisis Asmática Aguda": 0.22,
                "Exacerbación Aguda de EPOC": 0.35, "Infarto Agudo de Miocardio (IAM)": 0.08, "Insuficiencia Cardíaca Congestiva (ICC)": 0.08,
                "Miocarditis": 0.75, "Encefalitis": 0.92, "Accidente Cerebrovascular (ACV)": 0.08, "Migraña Severa": 0.05,
                "Dengue": 0.98, "Otitis Media": 0.72, "Sinusitis Aguda": 0.60, "COVID-19": 0.85, "COVID-19 Grave": 0.90,
                "Faringoamigdalitis Aguda": 0.80, "Tromboembolismo Pulmonar": 0.15, "Diabetes Mellitus Tipo 2": 0.10,
                "Gastroenteritis Aguda": 0.45, "Resfriado Común (Rinofaringitis)": 0.10, "Infección de Vías Urinarias (IVU)": 0.35,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Febrícula": {
                "Gripe Común / Influenza": 0.55, "Neumonía": 0.45, "Bronquitis Aguda": 0.40, "Crisis Asmática Aguda": 0.18,
                "Exacerbación Aguda de EPOC": 0.28, "Infarto Agudo de Miocardio (IAM)": 0.10, "Insuficiencia Cardíaca Congestiva (ICC)": 0.12,
                "Miocarditis": 0.50, "Encefalitis": 0.60, "Accidente Cerebrovascular (ACV)": 0.10, "Migraña Severa": 0.05,
                "Dengue": 0.70, "Otitis Media": 0.55, "Sinusitis Aguda": 0.45, "COVID-19": 0.60, "COVID-19 Grave": 0.65,
                "Faringoamigdalitis Aguda": 0.65, "Tromboembolismo Pulmonar": 0.10, "Diabetes Mellitus Tipo 2": 0.08,
                "Gastroenteritis Aguda": 0.35, "Resfriado Común (Rinofaringitis)": 0.28, "Infección de Vías Urinarias (IVU)": 0.25,
                "Reflujo Gastroesofágico (ERGE)": 0.05
            },
            "Hipoxia Leve": {
                "Gripe Común / Influenza": 0.08, "Neumonía": 0.65, "Bronquitis Aguda": 0.22, "Crisis Asmática Aguda": 0.60,
                "Exacerbación Aguda de EPOC": 0.75, "Infarto Agudo de Miocardio (IAM)": 0.35, "Insuficiencia Cardíaca Congestiva (ICC)": 0.70,
                "Miocarditis": 0.40, "Encefalitis": 0.10, "Accidente Cerebrovascular (ACV)": 0.12, "Migraña Severa": 0.02,
                "Dengue": 0.12, "Otitis Media": 0.02, "Sinusitis Aguda": 0.03, "COVID-19": 0.55, "COVID-19 Grave": 0.88,
                "Faringoamigdalitis Aguda": 0.05, "Tromboembolismo Pulmonar": 0.75, "Diabetes Mellitus Tipo 2": 0.08,
                "Gastroenteritis Aguda": 0.05, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Hipoxia Severa": {
                "Gripe Común / Influenza": 0.02, "Neumonía": 0.35, "Bronquitis Aguda": 0.08, "Crisis Asmática Aguda": 0.40,
                "Exacerbación Aguda de EPOC": 0.55, "Infarto Agudo de Miocardio (IAM)": 0.22, "Insuficiencia Cardíaca Congestiva (ICC)": 0.45,
                "Miocarditis": 0.25, "Encefalitis": 0.08, "Accidente Cerebrovascular (ACV)": 0.08, "Migraña Severa": 0.01,
                "Dengue": 0.05, "Otitis Media": 0.01, "Sinusitis Aguda": 0.01, "COVID-19": 0.28, "COVID-19 Grave": 0.75,
                "Faringoamigdalitis Aguda": 0.02, "Tromboembolismo Pulmonar": 0.65, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.01, "Resfriado Común (Rinofaringitis)": 0.01, "Infección de Vías Urinarias (IVU)": 0.01,
                "Reflujo Gastroesofágico (ERGE)": 0.01
            },
            "Hipertensión": {
                "Gripe Común / Influenza": 0.10, "Neumonía": 0.18, "Bronquitis Aguda": 0.08, "Crisis Asmática Aguda": 0.10,
                "Exacerbación Aguda de EPOC": 0.22, "Infarto Agudo de Miocardio (IAM)": 0.60, "Insuficiencia Cardíaca Congestiva (ICC)": 0.55,
                "Miocarditis": 0.30, "Encefalitis": 0.25, "Accidente Cerebrovascular (ACV)": 0.72, "Migraña Severa": 0.18,
                "Dengue": 0.08, "Otitis Media": 0.05, "Sinusitis Aguda": 0.05, "COVID-19": 0.12, "COVID-19 Grave": 0.22,
                "Faringoamigdalitis Aguda": 0.05, "Tromboembolismo Pulmonar": 0.12, "Diabetes Mellitus Tipo 2": 0.55,
                "Gastroenteritis Aguda": 0.08, "Resfriado Común (Rinofaringitis)": 0.05, "Infección de Vías Urinarias (IVU)": 0.15,
                "Reflujo Gastroesofágico (ERGE)": 0.10
            },
            "Hipotensión": {
                "Gripe Común / Influenza": 0.05, "Neumonía": 0.25, "Bronquitis Aguda": 0.03, "Crisis Asmática Aguda": 0.10,
                "Exacerbación Aguda de EPOC": 0.15, "Infarto Agudo de Miocardio (IAM)": 0.52, "Insuficiencia Cardíaca Congestiva (ICC)": 0.40,
                "Miocarditis": 0.45, "Encefalitis": 0.12, "Accidente Cerebrovascular (ACV)": 0.10, "Migraña Severa": 0.05,
                "Dengue": 0.65, "Otitis Media": 0.02, "Sinusitis Aguda": 0.02, "COVID-19": 0.08, "COVID-19 Grave": 0.35,
                "Faringoamigdalitis Aguda": 0.03, "Tromboembolismo Pulmonar": 0.55, "Diabetes Mellitus Tipo 2": 0.15,
                "Gastroenteritis Aguda": 0.35, "Resfriado Común (Rinofaringitis)": 0.02, "Infección de Vías Urinarias (IVU)": 0.12,
                "Reflujo Gastroesofágico (ERGE)": 0.02
            },
            "Taquicardia": {
                "Gripe Común / Influenza": 0.35, "Neumonía": 0.65, "Bronquitis Aguda": 0.25, "Crisis Asmática Aguda": 0.55,
                "Exacerbación Aguda de EPOC": 0.60, "Infarto Agudo de Miocardio (IAM)": 0.75, "Insuficiencia Cardíaca Congestiva (ICC)": 0.65,
                "Miocarditis": 0.80, "Encefalitis": 0.45, "Accidente Cerebrovascular (ACV)": 0.25, "Migraña Severa": 0.15,
                "Dengue": 0.72, "Otitis Media": 0.18, "Sinusitis Aguda": 0.12, "COVID-19": 0.50, "COVID-19 Grave": 0.72,
                "Faringoamigdalitis Aguda": 0.22, "Tromboembolismo Pulmonar": 0.80, "Diabetes Mellitus Tipo 2": 0.18,
                "Gastroenteritis Aguda": 0.45, "Resfriado Común (Rinofaringitis)": 0.10, "Infección de Vías Urinarias (IVU)": 0.30,
                "Reflujo Gastroesofágico (ERGE)": 0.10
            },
            "Bradicardia": {
                "Gripe Común / Influenza": 0.05, "Neumonía": 0.05, "Bronquitis Aguda": 0.03, "Crisis Asmática Aguda": 0.03,
                "Exacerbación Aguda de EPOC": 0.05, "Infarto Agudo de Miocardio (IAM)": 0.25, "Insuficiencia Cardíaca Congestiva (ICC)": 0.15,
                "Miocarditis": 0.30, "Encefalitis": 0.12, "Accidente Cerebrovascular (ACV)": 0.15, "Migraña Severa": 0.05,
                "Dengue": 0.08, "Otitis Media": 0.02, "Sinusitis Aguda": 0.02, "COVID-19": 0.05, "COVID-19 Grave": 0.08,
                "Faringoamigdalitis Aguda": 0.02, "Tromboembolismo Pulmonar": 0.05, "Diabetes Mellitus Tipo 2": 0.05,
                "Gastroenteritis Aguda": 0.02, "Resfriado Común (Rinofaringitis)": 0.02, "Infección de Vías Urinarias (IVU)": 0.05,
                "Reflujo Gastroesofágico (ERGE)": 0.02
            },
            "Taquipnea": {
                "Gripe Común / Influenza": 0.15, "Neumonía": 0.78, "Bronquitis Aguda": 0.38, "Crisis Asmática Aguda": 0.88,
                "Exacerbación Aguda de EPOC": 0.90, "Infarto Agudo de Miocardio (IAM)": 0.55, "Insuficiencia Cardíaca Congestiva (ICC)": 0.82,
                "Miocarditis": 0.55, "Encefalitis": 0.22, "Accidente Cerebrovascular (ACV)": 0.18, "Migraña Severa": 0.05,
                "Dengue": 0.22, "Otitis Media": 0.05, "Sinusitis Aguda": 0.05, "COVID-19": 0.60, "COVID-19 Grave": 0.92,
                "Faringoamigdalitis Aguda": 0.10, "Tromboembolismo Pulmonar": 0.88, "Diabetes Mellitus Tipo 2": 0.10,
                "Gastroenteritis Aguda": 0.20, "Resfriado Común (Rinofaringitis)": 0.15, "Infección de Vías Urinarias (IVU)": 0.15,
                "Reflujo Gastroesofágico (ERGE)": 0.05
            },
            "Edad Avanzada": {
                "Gripe Común / Influenza": 0.25, "Neumonía": 0.45, "Bronquitis Aguda": 0.25, "Crisis Asmática Aguda": 0.15,
                "Exacerbación Aguda de EPOC": 0.60, "Infarto Agudo de Miocardio (IAM)": 0.60, "Insuficiencia Cardíaca Congestiva (ICC)": 0.70,
                "Miocarditis": 0.20, "Encefalitis": 0.20, "Accidente Cerebrovascular (ACV)": 0.65, "Migraña Severa": 0.15,
                "Dengue": 0.20, "Otitis Media": 0.15, "Sinusitis Aguda": 0.15, "COVID-19": 0.30, "COVID-19 Grave": 0.55,
                "Faringoamigdalitis Aguda": 0.10, "Tromboembolismo Pulmonar": 0.50, "Diabetes Mellitus Tipo 2": 0.55,
                "Gastroenteritis Aguda": 0.20, "Resfriado Común (Rinofaringitis)": 0.25, "Infección de Vías Urinarias (IVU)": 0.45,
                "Reflujo Gastroesofágico (ERGE)": 0.30
            },
        }

        # ── LIKELIHOODS DE PRUEBAS DIAGNÓSTICAS ─────────────────────────────
        self.P_test_result = {
            "Panel Viral Respiratorio (PCR)": {
                "Positivo": {"Gripe Común / Influenza": 0.95, "COVID-19": 0.95, "COVID-19 Grave": 0.95, "Resfriado Común (Rinofaringitis)": 0.60},
                "Negativo": {"Gripe Común / Influenza": 0.02, "COVID-19": 0.02, "COVID-19 Grave": 0.02, "Resfriado Común (Rinofaringitis)": 0.40}
            },
            "Hemograma Completo": {
                "Leucocitosis": {"Neumonía": 0.88, "Bronquitis Aguda": 0.65, "Faringoamigdalitis Aguda": 0.70, "Infección de Vías Urinarias (IVU)": 0.75},
                "Leucopenia": {"Dengue": 0.90, "COVID-19": 0.55, "Gripe Común / Influenza": 0.45},
                "Normal": {"Gripe Común / Influenza": 0.75, "Migraña Severa": 0.80, "Bronquitis Aguda": 0.35, "Resfriado Común (Rinofaringitis)": 0.85, "Reflujo Gastroesofágico (ERGE)": 0.90}
            },
            "Glucosa en Ayunas": {
                "Alto (>=126 mg/dL)": {"Diabetes Mellitus Tipo 2": 0.98},
                "Normal": {"Diabetes Mellitus Tipo 2": 0.02}
            },
            "Hemoglobina Glicosilada (HbA1c)": {
                "Alto (>=6.5%)": {"Diabetes Mellitus Tipo 2": 0.97},
                "Normal": {"Diabetes Mellitus Tipo 2": 0.03}
            },
            "Radiografía de Tórax": {
                "Consolidación": {"Neumonía": 0.92, "COVID-19 Grave": 0.85},
                "Vidrio deslustrado": {"COVID-19": 0.80, "COVID-19 Grave": 0.90, "Neumonía": 0.60},
                "Normal": {"Bronquitis Aguda": 0.75, "Gripe Común / Influenza": 0.70, "Crisis Asmática Aguda": 0.70, "Resfriado Común (Rinofaringitis)": 0.95, "Reflujo Gastroesofágico (ERGE)": 0.98}
            },
            "Antígeno NS1 (Dengue)": {
                "Positivo": {"Dengue": 0.97},
                "Negativo": {"Dengue": 0.05}
            },
            "Troponina I": {
                "Elevada": {"Infarto Agudo de Miocardio (IAM)": 0.95, "Miocarditis": 0.75},
                "Normal": {"Infarto Agudo de Miocardio (IAM)": 0.05, "Miocarditis": 0.15}
            },
            "ECG de 12 Derivaciones": {
                "Elevación ST": {"Infarto Agudo de Miocardio (IAM)": 0.92},
                "Normal": {"Infarto Agudo de Miocardio (IAM)": 0.05, "Migraña Severa": 0.90}
            },
            "Dímero D": {
                "Elevado": {"Tromboembolismo Pulmonar": 0.88, "COVID-19 Grave": 0.70},
                "Normal": {"Tromboembolismo Pulmonar": 0.10}
            },
            "Punción Lumbar (LCR)": {
                "Pleocitosis linfocitaria": {"Encefalitis": 0.92, "Accidente Cerebrovascular (ACV)": 0.08},
                "Normal": {"Encefalitis": 0.05, "Migraña Severa": 0.85}
            },
            "TC de Cráneo": {
                "Anormal (sangrado/isquemia)": {"Accidente Cerebrovascular (ACV)": 0.90, "Encefalitis": 0.40},
                "Normal": {"Migraña Severa": 0.90, "Accidente Cerebrovascular (ACV)": 0.15}
            },
            "Flujometría (Peak Flow)": {
                "PEF <60%": {"Crisis Asmática Aguda": 0.90, "Exacerbación Aguda de EPOC": 0.75},
                "Normal": {"Crisis Asmática Aguda": 0.10, "Exacerbación Aguda de EPOC": 0.20}
            },
            "Otoscopia": {
                "Patológica": {"Otitis Media": 0.95},
                "Normal": {"Otitis Media": 0.05}
            },
            "TC de Senos Paranasales": {
                "Niveles hidroaéreos": {"Sinusitis Aguda": 0.95},
                "Normal": {"Sinusitis Aguda": 0.05}
            },
            "Gasometría Arterial": {
                "Hipoxia severa (PaO2 <60)": {"COVID-19 Grave": 0.88, "Exacerbación Aguda de EPOC": 0.85, "Tromboembolismo Pulmonar": 0.80},
                "Normal": {"Gripe Común / Influenza": 0.80, "Migraña Severa": 0.85}
            },
            "NT-proBNP": {
                "Elevado": {"Insuficiencia Cardíaca Congestiva (ICC)": 0.92, "Miocarditis": 0.55},
                "Normal": {"Insuficiencia Cardíaca Congestiva (ICC)": 0.05}
            },
            "Prueba rápida de estreptococo": {
                "Positiva": {"Faringoamigdalitis Aguda": 0.92},
                "Negativa": {"Faringoamigdalitis Aguda": 0.30}
            },
            "Angio-TC Pulmonar": {
                "Defecto de llenado": {"Tromboembolismo Pulmonar": 0.97},
                "Normal": {"Tromboembolismo Pulmonar": 0.03}
            },
            "Examen General de Orina (EGO)": {
                "Patológico": {"Infección de Vías Urinarias (IVU)": 0.95},
                "Normal": {"Infección de Vías Urinarias (IVU)": 0.05}
            },
            "Endoscopia Digestiva Alta": {
                "Esofagitis / Hernia hiatal": {"Reflujo Gastroesofágico (ERGE)": 0.85},
                "Normal": {"Reflujo Gastroesofágico (ERGE)": 0.15}
            },
            "Urocultivo": {
                "Positivo (>100,000 UFC)": {"Infección de Vías Urinarias (IVU)": 0.96},
                "Negativo": {"Infección de Vías Urinarias (IVU)": 0.04}
            }
        }

        # Asegurar condicionales para Gastroenteritis Aguda
        gi_symptoms = {
            "Diarrea": 0.95,
            "Dolor Abdominal Agudo": 0.85,
            "Náuseas / Vómitos": 0.70,
            "Fiebre": 0.40,
            "Febrícula": 0.30,
            "Dolor de Cuerpo Generalizado": 0.30,
            "Fatiga / Cansancio Extremo": 0.50,
            "Hipotensión": 0.15,
            "Taquicardia": 0.20
        }
        for sintoma in self.P_sintoma.keys():
            self.P_sintoma[sintoma]["Gastroenteritis Aguda"] = gi_symptoms.get(sintoma, 0.01)

        # Agregar a P_test_result para Hemograma Completo
        if "Hemograma Completo" in self.P_test_result:
            if "Leucocitosis" in self.P_test_result["Hemograma Completo"]:
                self.P_test_result["Hemograma Completo"]["Leucocitosis"]["Gastroenteritis Aguda"] = 0.45
            if "Normal" in self.P_test_result["Hemograma Completo"]:
                self.P_test_result["Hemograma Completo"]["Normal"]["Gastroenteritis Aguda"] = 0.55

        self._default_priors = copy.deepcopy(self.P_enfermedad_base)
        self._default_conditionals = copy.deepcopy(self.P_sintoma)

        # Cargar parámetros desde base de datos si existen
        try:
            from database import get_parameters
            db_params = get_parameters()
            if db_params:
                if "priors" in db_params and db_params["priors"]:
                    self.P_enfermedad_base.update(db_params["priors"])
                if "conditionals" in db_params and db_params["conditionals"]:
                    self.P_sintoma.update(db_params["conditionals"])
        except Exception as e:
            print(f"Error al cargar parámetros desde la base de datos: {e}")

    @property
    def priors(self):
        return self.P_enfermedad_base

    def guardar_configuracion(self):
        from database import save_parameters
        save_parameters(self.P_enfermedad_base, self.P_sintoma)

    def cargar_configuracion_por_defecto(self):
        self.restaurar_por_defecto()
        from database import reset_parameters
        reset_parameters(self.P_enfermedad_base, self.P_sintoma)

    # ── RESTAURAR VALORES POR DEFECTO
    def restaurar_por_defecto(self):
        self.P_enfermedad_base = copy.deepcopy(self._default_priors)
        self.P_sintoma = copy.deepcopy(self._default_conditionals)

    # ── NORMALIZACIÓN
    def normalizar(self, prob: dict) -> dict:
        total = sum(prob.values())
        if total <= 0:
            n = len(prob)
            return {k: 1.0 / n for k in prob}
        return {k: v / total for k, v in prob.items()}

    # ── MAPEO DE SIGNOS VITALES A ESTADOS LÓGICOS
    def mapear_signos_vitales(self, constantes: dict) -> dict:
        edad = float(constantes.get("edad", 30))
        temp = float(constantes.get("temperatura", 37.0))
        spo2 = float(constantes.get("spo2", 98))
        pas  = float(constantes.get("pas", 120))
        pad  = float(constantes.get("pad", 80))
        fc   = float(constantes.get("fc", 80))
        fr   = float(constantes.get("fr", 16))

        return {
            "Fiebre":        temp >= 37.8,
            "Febrícula":     37.3 <= temp < 37.8,
            "Hipoxia Leve":  92 <= spo2 < 95,
            "Hipoxia Severa": spo2 < 92,
            "Hipertensión":  pas >= 140 or pad >= 90,
            "Hipotensión":   pas < 90,
            "Taquicardia":   fc > 100,
            "Bradicardia":   fc < 60,
            "Taquipnea":     fr > 20,
            "Edad Avanzada": edad >= 65,
        }

    # ── MODIFICADORES DE RIESGO POR ANTECEDENTES
    def aplicar_antecedentes(self, prob_base: dict, antecedentes: dict) -> dict:
        prob = {k: math.log(max(v, self.LAPLACE_ALPHA)) for k, v in prob_base.items()}

        # Asma
        if antecedentes.get("Asma"):
            prob["Crisis Asmática Aguda"] = prob.get("Crisis Asmática Aguda", 0) + math.log(3.0)
            prob["Bronquitis Aguda"]      = prob.get("Bronquitis Aguda", 0)      + math.log(1.5)
            prob["Exacerbación Aguda de EPOC"] = prob.get("Exacerbación Aguda de EPOC", 0) + math.log(1.3)

        # EPOC
        if antecedentes.get("EPOC"):
            prob["Exacerbación Aguda de EPOC"] = prob.get("Exacerbación Aguda de EPOC", 0) + math.log(4.0)
            prob["Neumonía"]                   = prob.get("Neumonía", 0)                   + math.log(1.8)

        # Cardiopatía
        if antecedentes.get("Cardiopatía"):
            prob["Infarto Agudo de Miocardio (IAM)"]        = prob.get("Infarto Agudo de Miocardio (IAM)", 0)        + math.log(2.5)
            prob["Insuficiencia Cardíaca Congestiva (ICC)"] = prob.get("Insuficiencia Cardíaca Congestiva (ICC)", 0) + math.log(3.0)
            prob["Miocarditis"]                              = prob.get("Miocarditis", 0)                              + math.log(1.8)
            prob["Tromboembolismo Pulmonar"]                 = prob.get("Tromboembolismo Pulmonar", 0)                 + math.log(1.5)

        # Hipertensión
        if antecedentes.get("Hipertensión Arterial (HTA)"):
            prob["Accidente Cerebrovascular (ACV)"]         = prob.get("Accidente Cerebrovascular (ACV)", 0)         + math.log(2.5)
            prob["Infarto Agudo de Miocardio (IAM)"]        = prob.get("Infarto Agudo de Miocardio (IAM)", 0)        + math.log(2.0)
            prob["Insuficiencia Cardíaca Congestiva (ICC)"] = prob.get("Insuficiencia Cardíaca Congestiva (ICC)", 0) + math.log(2.0)

        # Diabetes
        if antecedentes.get("Diabetes") or antecedentes.get("Diabetes Mellitus"):
            prob["Accidente Cerebrovascular (ACV)"]  = prob.get("Accidente Cerebrovascular (ACV)", 0)  + math.log(1.8)
            prob["Infarto Agudo de Miocardio (IAM)"] = prob.get("Infarto Agudo de Miocardio (IAM)", 0) + math.log(1.8)
            prob["Neumonía"]                          = prob.get("Neumonía", 0)                          + math.log(1.7)
            prob["Diabetes Mellitus Tipo 2"]          = prob.get("Diabetes Mellitus Tipo 2", 0)          + math.log(2.5)

        # Inmunosupresión
        if antecedentes.get("Inmunosupresión"):
            prob["Neumonía"]      = prob.get("Neumonía", 0)      + math.log(2.2)
            prob["Encefalitis"]   = prob.get("Encefalitis", 0)   + math.log(3.0)
            prob["COVID-19 Grave"] = prob.get("COVID-19 Grave", 0) + math.log(2.0)
            prob["Infección de Vías Urinarias (IVU)"] = prob.get("Infección de Vías Urinarias (IVU)", 0) + math.log(2.0)

        # Tabaquismo
        if antecedentes.get("Tabaquismo"):
            prob["Exacerbación Aguda de EPOC"] = prob.get("Exacerbación Aguda de EPOC", 0) + math.log(2.2)
            prob["Infarto Agudo de Miocardio (IAM)"] = prob.get("Infarto Agudo de Miocardio (IAM)", 0) + math.log(1.7)
            prob["Bronquitis Aguda"]   = prob.get("Bronquitis Aguda", 0)   + math.log(1.5)

        # Meningitis previa
        if antecedentes.get("Meningitis"):
            prob["Encefalitis"] = prob.get("Encefalitis", 0) + math.log(3.5)

        # Cáncer
        if antecedentes.get("Cáncer"):
            prob["Accidente Cerebrovascular (ACV)"] = prob.get("Accidente Cerebrovascular (ACV)", 0) + math.log(1.8)
            prob["Neumonía"]             = prob.get("Neumonía", 0)             + math.log(1.8)
            prob["Tromboembolismo Pulmonar"] = prob.get("Tromboembolismo Pulmonar", 0) + math.log(2.0)

        # HIV / SIDA
        if antecedentes.get("HIV / SIDA"):
            prob["Neumonía"]      = prob.get("Neumonía", 0)      + math.log(2.5)
            prob["Encefalitis"]   = prob.get("Encefalitis", 0)   + math.log(2.5)
            prob["COVID-19 Grave"] = prob.get("COVID-19 Grave", 0) + math.log(1.8)

        # Obesidad
        if antecedentes.get("Obesidad"):
            prob["Insuficiencia Cardíaca Congestiva (ICC)"] = prob.get("Insuficiencia Cardíaca Congestiva (ICC)", 0) + math.log(1.5)
            prob["Diabetes Mellitus Tipo 2"]                = prob.get("Diabetes Mellitus Tipo 2", 0)                + math.log(2.0)
            prob["COVID-19 Grave"]                          = prob.get("COVID-19 Grave", 0)                          + math.log(1.7)
            prob["Tromboembolismo Pulmonar"]                = prob.get("Tromboembolismo Pulmonar", 0)                + math.log(1.5)

        # Fibrilación Auricular
        if antecedentes.get("Fibrilación Auricular"):
            prob["Accidente Cerebrovascular (ACV)"] = prob.get("Accidente Cerebrovascular (ACV)", 0) + math.log(3.0)
            prob["Tromboembolismo Pulmonar"]        = prob.get("Tromboembolismo Pulmonar", 0)        + math.log(1.8)

        # ACV previo
        if antecedentes.get("ACV / Derrame Previo"):
            prob["Accidente Cerebrovascular (ACV)"] = prob.get("Accidente Cerebrovascular (ACV)", 0) + math.log(3.0)

        # Insuficiencia Renal Crónica
        if antecedentes.get("Insuficiencia Renal Crónica"):
            prob["Insuficiencia Cardíaca Congestiva (ICC)"] = prob.get("Insuficiencia Cardíaca Congestiva (ICC)", 0) + math.log(1.5)
            prob["Diabetes Mellitus Tipo 2"]                = prob.get("Diabetes Mellitus Tipo 2", 0)                + math.log(1.5)

        # Convertir de log-space a probabilidades y normalizar
        max_log = max(prob.values())
        exp_prob = {k: math.exp(v - max_log) for k, v in prob.items()}
        return self.normalizar(exp_prob)

    def cargar_aprendizaje_clinico(self):
        """
        Carga el historial de casos confirmados y síntomas reales de la base de datos
        para ajustar dinámicamente las probabilidades previas (priors) y condicionales (conditionals).
        """
        try:
            from database import get_connection
            import json
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # 1. Obtener total de diagnósticos finales guardados
            cursor.execute("""
                SELECT COUNT(*) FROM dbo.diagnoses 
                WHERE phase = 'final'
            """)
            total_casos_global = cursor.fetchone()[0] or 0
            
            if total_casos_global == 0:
                cursor.close()
                conn.close()
                return
                
            # 2. Contar casos confirmados por enfermedad
            cursor.execute("""
                SELECT 
                    COALESCE(doctor_override_diagnosis, diagnosis_primary) as disease,
                    COUNT(*) as total_cases
                FROM dbo.diagnoses
                WHERE phase = 'final'
                GROUP BY COALESCE(doctor_override_diagnosis, diagnosis_primary)
            """)
            counts_enfermedad = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 3. Contar síntomas observados en diagnósticos confirmados
            cursor.execute("""
                SELECT 
                    COALESCE(d.doctor_override_diagnosis, d.diagnosis_primary) as disease,
                    vs.symptom_name,
                    SUM(CAST(vs.is_present AS INT)) as present_count
                FROM dbo.diagnoses d
                JOIN dbo.visit_symptoms vs ON d.visit_id = vs.visit_id
                WHERE d.phase = 'final'
                GROUP BY COALESCE(d.doctor_override_diagnosis, d.diagnosis_primary), vs.symptom_name
            """)
            rows_sintomas = cursor.fetchall()
            
            # Estructurar conteos de síntomas
            counts_sintomas = {}
            for r in rows_sintomas:
                enf, sint, cant = r[0], r[1], r[2]
                if enf not in counts_sintomas:
                    counts_sintomas[enf] = {}
                counts_sintomas[enf][sint] = cant
                
            cursor.close()
            conn.close()
            
            # --- CALCULAR AJUSTES DE APRENDIZAJE ---
            # Peso de aprendizaje general para priors (N0 = 50 casos de muestra virtual)
            N0_priors = 50.0
            w_prior = total_casos_global / (total_casos_global + N0_priors)
            
            # Ajustar priors (P_enfermedad_base)
            K = len(self.enfermedades)
            alpha_laplace = 1.0
            priors_actualizados = {}
            for enf in self.enfermedades:
                p_base = self.P_enfermedad_base.get(enf, 1.0 / K)
                cant_enf = counts_enfermedad.get(enf, 0)
                p_obs = (cant_enf + alpha_laplace) / (total_casos_global + alpha_laplace * K)
                priors_actualizados[enf] = (1.0 - w_prior) * p_base + w_prior * p_obs
                
            self.P_enfermedad_base = priors_actualizados
            
            # Ajustar condicionales de síntomas (N0_sint = 10 casos por enfermedad)
            N0_sint = 10.0
            beta_laplace = 0.5
            for sint, dict_enf in self.P_sintoma.items():
                for enf in self.enfermedades:
                    cant_enf = counts_enfermedad.get(enf, 0)
                    if cant_enf > 0:
                        w_sint = cant_enf / (cant_enf + N0_sint)
                        p_s_base = dict_enf.get(enf, self.LAPLACE_ALPHA)
                        
                        # Frecuencia observada del síntoma en casos reales de esta enfermedad
                        cant_sint_presente = counts_sintomas.get(enf, {}).get(sint, 0)
                        p_s_obs = (cant_sint_presente + beta_laplace) / (cant_enf + beta_laplace * 2)
                        
                        dict_enf[enf] = (1.0 - w_sint) * p_s_base + w_sint * p_s_obs
                        
            print(f"[Aprendizaje Bayesiano] Modelo actualizado con éxito a partir de {total_casos_global} casos confirmados.")
            
        except Exception as e:
            print(f"[Aprendizaje Bayesiano] Error al cargar aprendizaje clínico: {e}")

    # ── DIAGNÓSTICO PRELIMINAR (FASE 1)
    def calcular_diagnostico_preliminar(
        self, constantes: dict, antecedentes: dict, sintomas: dict,
        priors_custom=None, conditionals_custom=None
    ):
        self.cargar_aprendizaje_clinico()
        priors      = priors_custom      if priors_custom      else self.P_enfermedad_base
        conditionals = conditionals_custom if conditionals_custom else self.P_sintoma

        # Paso 1: Priors modificados por antecedentes
        prob_post_antecedentes = self.aplicar_antecedentes(priors, antecedentes)

        # Paso 2: Iniciar acumulador en log-space
        log_prob = {e: math.log(max(p, self.LAPLACE_ALPHA))
                    for e, p in prob_post_antecedentes.items()}

        # Paso 3: Combinar síntomas clínicos + signos vitales mapeados
        signos_mapeados = self.mapear_signos_vitales(constantes)
        todos_sintomas  = {**sintomas, **signos_mapeados}

        pasos = 0
        BETA = 0.5
        for sintoma, presente in todos_sintomas.items():
            if sintoma not in conditionals:
                continue
            for enf in self.enfermedades:
                p_s = conditionals[sintoma].get(enf, self.LAPLACE_ALPHA)
                p_s = max(min(p_s, 1.0 - self.LAPLACE_ALPHA), self.LAPLACE_ALPHA)
                contrib = math.log(p_s) if presente else math.log(1.0 - p_s)
                log_prob[enf] = log_prob.get(enf, 0) + (contrib * BETA)
            pasos += 1

        # Interacción cardiovascular especial
        if sintomas.get("Dolor en el Pecho") and (
            antecedentes.get("Cardiopatía") or antecedentes.get("Hipertensión Arterial (HTA)")
        ):
            log_prob["Infarto Agudo de Miocardio (IAM)"] += math.log(1.5)
            log_prob["Miocarditis"]                       += math.log(1.2)

        # Convertir de log-space a probabilidades
        max_log = max(log_prob.values())
        prob_final = {k: math.exp(v - max_log) for k, v in log_prob.items()}
        return self.normalizar(prob_final), pasos

    # ── DIAGNÓSTICO FINAL (FASE 2)
    def calcular_diagnostico_final(self, prob_preliminar: dict, resultados_pruebas: list):
        log_prob = {e: math.log(max(p, self.LAPLACE_ALPHA))
                    for e, p in prob_preliminar.items()}
        pasos = 0

        for prueba in resultados_pruebas:
            if not prueba.get("done") or not prueba.get("result"):
                continue
            test_name = prueba["test_name"]
            resultado  = prueba["result"]

            if test_name not in self.P_test_result:
                continue
            if resultado not in self.P_test_result[test_name]:
                continue

            likelihoods = self.P_test_result[test_name][resultado]
            for enf in self.enfermedades:
                p_r = likelihoods.get(enf, self.LAPLACE_ALPHA)
                p_r = max(min(p_r, 1.0 - self.LAPLACE_ALPHA), self.LAPLACE_ALPHA)
                log_prob[enf] = log_prob.get(enf, 0) + math.log(p_r)
            pasos += 1

        max_log = max(log_prob.values())
        prob_final = {k: math.exp(v - max_log) for k, v in log_prob.items()}
        return self.normalizar(prob_final), pasos


# MOTOR CLÍNICO DE IA OFFLINE (INTERNISTA VIRTUAL)
class OfflineAIEngine:

    @staticmethod
    def generar_explicacion(
        paciente_nombre, constantes, diagnostico, probabilidad,
        sintomas_activos, antecedentes_activos, diagnosticos_diferenciales,
        motivo_consulta="No especificado", tipo_visita="consulta",
        seccion_gemini_override=None
    ):
        meta = CLINICAL_METADATA.get(diagnostico, {})
        alert_text = meta.get("alert_level", "Verde").upper()
        emoji = "🟢" if alert_text == "VERDE" else ("🟡" if alert_text == "AMARILLO" else "🔴")

        edad  = constantes.get("edad", 30)
        temp  = constantes.get("temperatura", 37.0)
        spo2  = constantes.get("spo2", 98)
        pas   = constantes.get("pas", 120)
        pad   = constantes.get("pad", 80)
        fc    = constantes.get("fc", 80)
        fr    = constantes.get("fr", 16)

        banderas = []
        if float(temp) >= 37.8:  banderas.append("⚠️ FIEBRE")
        elif float(temp) >= 37.3: banderas.append("⚠️ FEBRÍCULA")
        if float(spo2) < 92:     banderas.append("🚨 HIPOXIA SEVERA")
        elif float(spo2) < 95:   banderas.append("⚠️ HIPOXIA LEVE")
        if float(pas) >= 140 or float(pad) >= 90: banderas.append("🚨 HTA")
        elif float(pas) < 90:    banderas.append("🚨 HIPOTENSIÓN / SHOCK")
        if float(fc) > 100:      banderas.append("⚠️ TAQUICARDIA")
        if float(fr) > 20:       banderas.append("⚠️ TAQUIPNEA")

        banderas_str = " | ".join(banderas) if banderas else "Ninguna (Signos Estables)"

        # Top 3 diagnósticos diferenciales
        sorted_diag = sorted(diagnosticos_diferenciales.items(), key=lambda x: x[1], reverse=True)
        diferenciales_str = ""
        count = 0
        for d, p in sorted_diag:
            if d != diagnostico and count < 3:
                diferenciales_str += f"*   **{d}**: {p*100:.2f}%\n"
                count += 1

        habitos_html = ""
        for h in meta.get("habits", []):
            habitos_html += f"1.  {h}\n"

        farmacos_html = ""
        for f in meta.get("medications", []):
            farmacos_html += f"*   {f}\n"

        red_flags_html = ""
        for flag in meta.get("red_flags", []):
            red_flags_html += f"*   **{flag}**\n"

        estudios_html = ""
        for t in meta.get("clinical_tests", []):
            estudios_html += f"*   {t}\n"
        if not estudios_html:
            estudios_html = "*   No se requieren análisis complejos adicionales de manera mandatoria.\n"

        tipo_label = "🚨 EMERGENCIA" if tipo_visita == "emergencia" else "📋 CONSULTA"

        reporte_markdown = f'''
### {emoji} INFORME CLÍNICO — MED-INTELLIGENCE PRO

**PACIENTE:** {paciente_nombre} | **EDAD:** {edad} años  
**FECHA Y HORA:** {time.strftime('%d/%m/%Y %I:%M %p')}  
**TIPO DE VISITA:** {tipo_label}  
**MOTIVO DE CONSULTA:** {motivo_consulta}  

---

#### 🩺 1. Constantes Vitales y Triaje Fisiológico

| Parámetro | Valor | Referencia |
|---|---|---|
| Temperatura | {temp} °C | 36.5 – 37.2 °C |
| Saturación O2 (SpO2) | {spo2} % | ≥ 95% |
| Presión Arterial | {pas}/{pad} mmHg | <120/80 mmHg |
| Frecuencia Cardíaca | {fc} bpm | 60 – 100 bpm |
| Frecuencia Respiratoria | {fr} rpm | 12 – 20 rpm |

**Alertas Fisiológicas:** `{banderas_str}`

---

#### 🧠 2. Juicio Diagnóstico (Análisis Bayesiano)

*   **Diagnóstico Principal:** **{diagnostico}**
*   **Confianza de Inferencia:** `{probabilidad*100:.2f}%`
*   **Nivel de Triage:** **{alert_text}** {emoji}
*   **Especialista Sugerido:** {meta.get("specialist", "Medicina Interna")}

##### Diagnósticos Diferenciales:
{diferenciales_str}

---

#### 🔬 3. Análisis Fisiopatológico{' ✨ *(Generado por Gemini AI)*' if seccion_gemini_override else ''}

{seccion_gemini_override if seccion_gemini_override else f'El cuadro de **{diagnostico}** es el más compatible clínicamente por:\n*   **Correlación de Constantes Vitales:** {"Alteraciones detectadas en los parámetros fisiológicos sustentan la sospecha." if banderas else "El paciente se mantiene hemodinámicamente estable con manifestaciones sintomáticas locales."}\n*   **Antecedentes de Riesgo:** {", ".join(antecedentes_activos) if antecedentes_activos else "Ninguno reportado"}\n*   **Síntomas Presentes:** {", ".join(sintomas_activos) if sintomas_activos else "Ver evaluación de síntomas"}'}

---

#### 🧪 4. Estudios y Análisis Clínicos Sugeridos

{estudios_html}

---

#### 🍎 5. Recomendaciones de Hábitos y Estilo de Vida

{habitos_html}

---

#### 💊 6. Orientación Farmacológica

{farmacos_html}

---

#### 🚨 7. Señales de Alarma — Acudir Inmediatamente a Emergencias si:

{red_flags_html}

---
*Nota Legal: Este informe es un soporte de apoyo a la decisión clínica basado en el Teorema de Bayes {'complementado con análisis de lenguaje natural por Gemini AI' if seccion_gemini_override else ''}. No reemplaza el examen físico y el juicio médico profesional. UTESA — Informática Médica © 2026.*
'''
        return reporte_markdown

    @staticmethod
    def chatear(diagnostico, sintomas_activos, mensaje_usuario, historial_conversacion):
        meta = CLINICAL_METADATA.get(diagnostico, {})
        msg  = mensaje_usuario.lower().strip()

        if any(w in msg for w in ["hola", "buenos dias", "buenas", "saludos", "doctor"]):
            return f"Hola. Soy tu Médico Internista de apoyo. He analizado tu diagnóstico presuntivo de **{diagnostico}** y tus signos vitales. ¿Qué dudas tienes respecto a los medicamentos, hábitos recomendados o señales de peligro?"

        elif any(w in msg for w in ["habito", "comer", "dieta", "ejercicio", "agua", "reposo", "dormir"]):
            habits_str = "\\n".join([f"*   {h}" for h in meta.get("habits", [])])
            return f"Para la recuperación de **{diagnostico}**, sigue estas indicaciones:\\n\\n{habits_str}\\n\\n¿Estás en condiciones de cumplir con estas pautas?"

        elif any(w in msg for w in ["medicamento", "tomar", "pastilla", "jarabe", "receta", "antibiotico", "paracetamol"]):
            meds_str = "\\n".join([f"*   {f}" for f in meta.get("medications", [])])
            return f"Respecto al soporte farmacológico para **{diagnostico}**:\\n\\n{meds_str}\\n\\n**IMPORTANTE**: Ante señales de alarma, la automedicación puede enmascarar síntomas críticos."

        elif any(w in msg for w in ["peligro", "grave", "emergencia", "alerta", "bandera", "roja"]):
            flags_str = "\\n".join([f"*   **{flag}**" for flag in meta.get("red_flags", [])])
            return f"Para **{diagnostico}** (Triage: **{meta.get('alert_level', 'Verde').upper()}**), las señales de alarma que requieren traslado inmediato son:\\n\\n{flags_str}\\n\\n¿Experimentas alguno de estos signos ahora?"

        elif any(w in msg for w in ["bayes", "probabilidad", "calculo", "matematica", "como funciona"]):
            return f"El motor aplica el Teorema de Bayes secuencial: partimos de la prevalencia base de **{diagnostico}** en la población. Cada síntoma, signo vital y antecedente actúa como evidencia condicional P(S|E). Calculamos en espacio logarítmico para evitar errores numéricos. La patología con mayor probabilidad posterior P(E|S1..Sn) es el diagnóstico sugerido."

        elif any(w in msg for w in ["prueba", "analisis", "examen", "laboratorio", "estudio"]):
            tests_str = "\\n".join([f"*   {t}" for t in meta.get("clinical_tests", [])])
            return f"Para confirmar o descartar **{diagnostico}**, los estudios sugeridos son:\\n\\n{tests_str}\\n\\n¿Ya realizaste alguno de estos análisis?"

        else:
            return f"Como tu médico internista, ante un diagnóstico de **{diagnostico}**, la prioridad es seguir las pautas de medicación sintomática, respetar las recomendaciones de hábitos y vigilar las señales de alarma. ¿Hay algún síntoma específico sobre el que te gustaría profundizar?"
