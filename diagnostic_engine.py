import time
import math
import copy

# METADATOS CLÍNICOS DE LAS 34 ENFERMEDADES (Atención Primaria y Urgencias)
CLINICAL_METADATA = {
    "Gripe Común / Influenza": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Familiar",
        "summary": "Infección viral aguda de las vías respiratorias. Altamente contagiosa, generalmente autolimitada en pacientes sanos.",
        "clinical_tests": [
            "**Panel Viral Respiratorio (PCR)**: Positivo para virus de Influenza A o B.",
            "**Hemograma Completo**: Leucocitos en rango normal o leve linfocitosis reactiva."
        ],
        "habits": [
            "Reposo absoluto en cama por al menos 48 a 72 horas.",
            "Hidratación abundante con 2.5 a 3 litros de agua al día.",
            "Evitar cambios bruscos de temperatura."
        ],
        "medications": [
            "Paracetamol 500mg a 1g vía oral cada 8 horas en caso de fiebre.",
            "Lavados nasales frecuentes con solución salina estéril.",
            "**ADVERTENCIA**: Está prohibido el uso de antibióticos en gripe viral."
        ],
        "red_flags": [
            "Fiebre persistente que no cede después de 3 días.",
            "Aparición súbita de dificultad para respirar o dolor torácico.",
            "Confusión o somnolencia extrema."
        ]
    },
    "Neumonía": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Neumología / Medicina Interna",
        "summary": "Infección pulmonar aguda que inflama los alvéolos, los cuales pueden llenarse de secreciones purulentas.",
        "clinical_tests": [
            "**Radiografía de Tórax (AP y Lateral)**: Consolidación lobar o alveolar densa.",
            "**Hemograma Completo**: Leucocitosis marcada con neutrofilia severa.",
            "**Proteína C Reactiva (PCR)**: Elevada, indica inflamación activa."
        ],
        "habits": [
            "Reposo en cama con el torso semielevado a 30-45 grados.",
            "Monitorizar saturación de oxígeno 3 veces al día.",
            "Ejercicios de espiración lenta para movilizar secreciones."
        ],
        "medications": [
            "**Antibióticos**: Amoxicilina con Ácido Clavulánico 875/125mg cada 12 horas por 7-10 días (bajo criterio médico).",
            "Paracetamol 500mg cada 6 horas solo si hay fiebre.",
            "**ADVERTENCIA**: Evitar antitusivos que bloqueen la expectoración necesaria."
        ],
        "red_flags": [
            "Saturación de oxígeno por debajo de 92%.",
            "Frecuencia respiratoria superior a 24 respiraciones por minuto en reposo.",
            "Alteración del estado mental o confusión."
        ]
    },
    "Bronquitis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Neumología",
        "summary": "Inflamación aguda de los conductos bronquiales, frecuentemente de etiología viral secundaria a un cuadro respiratorio superior previo.",
        "clinical_tests": [
            "**Radiografía de Tórax**: Campos pulmonares limpios, descarta consolidación neumónica.",
            "**Auscultación**: Roncus y sibilancias bilaterales dispersas."
        ],
        "habits": [
            "Evitar exposición al humo del tabaco y vapores químicos.",
            "Hidratación abundante para disolver y expulsar la mucosidad.",
            "Uso de humidificador ultrasónico en la habitación."
        ],
        "medications": [
            "N-Acetilcisteína 600mg una vez al día para fluidificar el moco.",
            "Ibuprofeno 400mg cada 8 horas si hay dolor torácico por tos constante.",
            "**ADVERTENCIA**: Más del 90% de los casos son virales; no automedicarse antibióticos."
        ],
        "red_flags": [
            "Tos con sangre (hemoptisis) o de más de 3 semanas de duración.",
            "Dificultad respiratoria al caminar en llano.",
            "Fiebre persistente superior a 38.5 °C."
        ]
    },
    "Crisis Asmática Aguda": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Alergología / Neumología / Urgencias",
        "summary": "Estrechamiento agudo de las vías respiratorias bajas por espasmo muscular, edema e inflamación bronquial.",
        "clinical_tests": [
            "**Flujometría (Peak Flow)**: PEF <60% del valor teórico habitual.",
            "**Auscultación**: Sibilancias espiratorias agudas bilaterales difusas."
        ],
        "habits": [
            "Sentarse en posición erguida apoyando los brazos.",
            "Alejarse inmediatamente de alérgenos conocidos (polvo, humo, mascotas).",
            "Mantener la calma para evitar la hiperventilación."
        ],
        "medications": [
            "**Broncodilatadores**: Salbutamol inhalado 2-4 puffs cada 20 minutos durante la primera hora.",
            "Prednisona oral según indicación y gravedad de la crisis.",
            "**ADVERTENCIA**: El uso excesivo de Salbutamol sin mejoría clínica amerita auxilio inmediato."
        ],
        "red_flags": [
            "Silencio auscultatorio (ausencia de sibilancias con asfixia severa).",
            "Dificultad para formular frases completas debido a la falta de aire.",
            "Uso de músculos accesorios (tiraje intercostal)."
        ]
    },
    "Exacerbación Aguda de EPOC": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neumología / Medicina Interna / Urgencias",
        "summary": "Empeoramiento agudo de los síntomas respiratorios en un paciente con Enfermedad Pulmonar Obstructiva Crónica.",
        "clinical_tests": [
            "**Gasometría Arterial**: Revela hipoxia con o sin hipercapnia.",
            "**Radiografía de Tórax**: Hiperinsuflación pulmonar, descarta neumotórax o neumonía."
        ],
        "habits": [
            "Sentarse con el torso recto y aplicar respiración con labios fruncidos.",
            "Utilizar oxígeno suplementario al flujo indicado (usualmente bajo, 1-2 lpm) para evitar la retención de CO2.",
            "Reposo físico absoluto."
        ],
        "medications": [
            "Salbutamol y Bromuro de Ipratropio combinados por nebulización o inhalador.",
            "Corticoides sistémicos (Metilprednisolona o Prednisona).",
            "**ADVERTENCIA**: Hospitalización inmediata ante somnolencia o cianosis."
        ],
        "red_flags": [
            "Cianosis distal o perioral (uñas/labios morados).",
            "Confusión, letargia o somnolencia inusual.",
            "Saturación de oxígeno persistente <88%."
        ]
    },
    "Infarto Agudo de Miocardio (IAM)": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Cardiología / Urgencias",
        "summary": "Necrosis de una parte del músculo cardíaco debida a la obstrucción aguda de una arteria coronaria. Emergencia de vida.",
        "clinical_tests": [
            "**Electrocardiograma (ECG)**: Elevación o descenso del segmento ST o bloqueo de rama izquierda nuevo.",
            "**Troponinas Cardíacas (I o T)**: Elevación significativa en muestras seriadas."
        ],
        "habits": [
            "Reposo absoluto acostado con el torso semielevado.",
            "Mantener la calma, aflojar ropa ajustada y esperar a la ambulancia.",
            "Evitar cualquier tipo de esfuerzo físico."
        ],
        "medications": [
            "Ácido Acetilsalicílico (Aspirina) 160-325mg masticados inmediatamente.",
            "Nitroglicerina sublingual si la presión sistólica es >90 mmHg.",
            "**ADVERTENCIA**: No retrasar el traslado al hospital por esperar resultados de laboratorio."
        ],
        "red_flags": [
            "Dolor opresivo retroesternal que se irradia a mandíbula, cuello o brazo izquierdo.",
            "Sudoración fría profusa, náuseas, disnea o sensación de muerte inminente.",
            "Pérdida súbita del conocimiento o arritmias severas."
        ]
    },
    "Insuficiencia Cardíaca Congestiva (ICC)": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Cardiología / Medicina Interna",
        "summary": "Incapacidad estructural del corazón para bombear suficiente sangre, acumulando fluidos en pulmones y extremidades.",
        "clinical_tests": [
            "**Ecocardiograma**: Determina la fracción de eyección del ventrículo izquierdo (FEVI).",
            "**Péptido Natriurético (NT-proBNP)**: Elevado significativamente.",
            "**Radiografía de Tórax**: Cardiomegalia y signos de congestión venosa pulmonar."
        ],
        "habits": [
            "Restricción estricta de sodio (sal) en la dieta.",
            "Monitoreo diario del peso corporal (un aumento de >1.5 kg en 2 días indica retención de líquidos).",
            "Dormir con 2 o 3 almohadas (posición semi-Fowler)."
        ],
        "medications": [
            "Diuréticos de asa (Furosemida) según balance hídrico.",
            "Inhibidores de la ECA (Enalapril) o ARNI (Sacubitrilo/Valsartán) para remodelado.",
            "**ADVERTENCIA**: La disnea de aparición brusca al acostarse (ortopnea) es señal de descompensación."
        ],
        "red_flags": [
            "Dificultad respiratoria severa incluso en reposo.",
            "Aparición de tos con esputo asalmonado o espumoso.",
            "Aumento abrupto y masivo del edema en ambas piernas."
        ]
    },
    "Miocarditis": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Cardiología / Medicina Interna",
        "summary": "Inflamación del músculo cardíaco, comúnmente secundaria a infecciones virales. Puede simular un infarto.",
        "clinical_tests": [
            "**Resonancia Magnética Cardíaca**: Criterios de Lake Louise positivos.",
            "**Troponinas**: Moderadamente elevadas.",
            "**ECG**: Cambios inespecíficos del segmento ST u ondas T."
        ],
        "habits": [
            "Reposo físico estricto, prohibido realizar deportes por al menos 3 a 6 meses.",
            "Evitar el consumo de alcohol y estimulantes (cafeína).",
            "Control regular con ecocardiograma."
        ],
        "medications": [
            "Antiinflamatorios o medicamentos de soporte cardíaco según la gravedad.",
            "Evitar AINEs en la fase aguda inicial a menos que lo autorice el cardiólogo.",
            "**ADVERTENCIA**: La presencia de fatiga extrema con palpitaciones requiere evaluación."
        ],
        "red_flags": [
            "Síncope (desmayo) o palpitaciones rápidas asociadas a dolor de pecho.",
            "Dificultad respiratoria que empeora rápidamente en reposo.",
            "Signos de choque (extremidades frías y sudorosas, hipotensión)."
        ]
    },
    "Encefalitis": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neurología / Infectología / Urgencias",
        "summary": "Inflamación aguda del parénquima cerebral, frecuentemente causada por virus, que causa alteración neurológica.",
        "clinical_tests": [
            "**Punción Lumbar**: Pleocitosis linfocitaria en líquido cefalorraquídeo.",
            "**Resonancia Magnética de Cerebro**: Señales hiperintensas en lóbulos temporales.",
            "**Electroencefalograma (EEG)**: Actividad lenta o descargas periódicas."
        ],
        "habits": [
            "Hospitalización inmediata en sala de cuidados intermedios o intensivos.",
            "Aislamiento sensorial (habitación con luz tenue y bajo ruido).",
            "Monitoreo neurológico continuo de la escala de Glasgow."
        ],
        "medications": [
            "Antivirales endovenosos (Aciclovir) iniciados empíricamente ante sospecha.",
            "Anticonvulsivantes profilácticos si hay crisis convulsivas.",
            "**ADVERTENCIA**: Requiere terapia endovenosa urgente para evitar secuelas permanentes."
        ],
        "red_flags": [
            "Convulsiones de inicio reciente o focalidad neurológica.",
            "Alteración progresiva y grave del estado de conciencia o coma.",
            "Fiebre muy alta asociada a rigidez de nuca."
        ]
    },
    "Accidente Cerebrovascular (ACV)": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neurología / Urgencias",
        "summary": "Pérdida de flujo sanguíneo a una parte del cerebro (isquémico) o ruptura de un vaso sanguíneo cerebral (hemorrágico). Tiempo-dependiente.",
        "clinical_tests": [
            "**Tomografía Computada de Cráneo (TC Simple)**: Permite diferenciar isquemia de hemorragia.",
            "**Resonancia Magnética**: Altamente sensible en las primeras horas."
        ],
        "habits": [
            "Mantener al paciente acostado con la cabeza a 30 grados.",
            "No administrar alimentos, líquidos ni medicamentos por boca (riesgo de aspiración).",
            "Anotar con precisión la hora exacta del inicio de los síntomas."
        ],
        "medications": [
            "Terapia trombolítica (rtPA) endovenosa si es ACV isquémico y se encuentra dentro de la ventana de 4.5 horas.",
            "Antiagregantes plaquetarios solo tras descartar hemorragia por TC.",
            "**ADVERTENCIA**: No administrar aspirina en casa antes de la tomografía cerebral."
        ],
        "red_flags": [
            "Pérdida súbita de fuerza o sensibilidad en la mitad de la cara, brazo o pierna.",
            "Dificultad repentina para hablar, articular palabras o comprender el lenguaje.",
            "Desviación de la comisura bucal o pérdida del equilibrio súbito."
        ]
    },
    "Migraña Severa": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Neurología / Medicina General",
        "summary": "Cefalea primaria recurrente, intensa, de carácter pulsátil, usualmente unilateral, que se acompaña de náuseas o fotofobia.",
        "clinical_tests": [
            "**Examen Neurológico**: Completamente normal durante e inter crisis.",
            "**TC de Cráneo**: Normal, indicada solo ante signos de alarma."
        ],
        "habits": [
            "Reposo en habitación oscura, fresca y sin ruidos.",
            "Colocar compresas frías sobre la frente o sienes.",
            "Evitar factores desencadenantes (quesos maduros, chocolate, vino tinto, estrés)."
        ],
        "medications": [
            "Triptanos (Sumatriptán 50-100mg) al inicio de la cefalea.",
            "Analgésicos y antieméticos (Metoclopramida) para las náuseas asociadas.",
            "**ADVERTENCIA**: Limitar el uso de analgésicos a un máximo de 2-3 días por semana para evitar cefalea por rebote."
        ],
        "red_flags": [
            "Cefalea de inicio súbito, de intensidad máxima en segundos (cefalea en trueno).",
            "Presencia de fiebre, rigidez de nuca o confusión.",
            "Aparición del dolor tras un traumatismo de cráneo."
        ]
    },
    "Dengue No Grave (Clásico)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Infectología",
        "summary": "Infección viral transmitida por el mosquito Aedes aegypti. Caracterizada por fiebre alta repentina y dolores corporales intensos.",
        "clinical_tests": [
            "**Prueba Rápida de Dengue (Antígeno NS1 / IgM-IgG)**: Positiva.",
            "**Hemograma Completo**: Trombocitopenia (plaquetas bajas) y leucopenia."
        ],
        "habits": [
            "Reposo absoluto en cama bajo mosquitero para evitar propagación.",
            "Hidratación oral agresiva con suero oral (2 a 3 litros al día).",
            "Uso de paños húmedos de agua templada para controlar la temperatura."
        ],
        "medications": [
            "Paracetamol 500mg a 1g cada 6 horas vía oral si hay fiebre (máximo 3g al día).",
            "**ADVERTENCIA**: Está terminantemente prohibido el uso de Aspirina, Ibuprofeno o AINEs por riesgo de sangrado."
        ],
        "red_flags": [
            "Dolor abdominal intenso y continuo.",
            "Vómitos persistentes (más de 3 en 1 hora).",
            "Sangrado de encías, nariz o presencia de petequias."
        ]
    },
    "Dengue Grave": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Infectología / Medicina Interna / Urgencias",
        "summary": "Forma severa del dengue caracterizada por choque por fuga de plasma, hemorragias graves o falla orgánica múltiple.",
        "clinical_tests": [
            "**Hemograma**: Hemoconcentración marcada (aumento rápido del hematocrito) y plaquetas <100,000/mm³.",
            "**Ecografía Abdominal**: Presencia de ascitis o derrame pleural."
        ],
        "habits": [
            "Hospitalización obligatoria e inmediata en unidad de cuidados intensivos o intermedios.",
            "Reposo absoluto en cama.",
            "Monitoreo continuo de signos vitales y diuresis horaria."
        ],
        "medications": [
            "Reposición vigorosa de líquidos endovenosos con cristaloides (Suero fisiológico o Ringer lactato).",
            "**ADVERTENCIA**: No administrar ningún medicamento por vía intramuscular por riesgo de hematomas gigantes."
        ],
        "red_flags": [
            "Signos de choque (frialdad distal, pulso rápido y débil, hipotensión).",
            "Sangrado activo digestivo o hematuria.",
            "Acumulación de líquidos con dificultad para respirar."
        ]
    },
    "Fiebre Zika": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Ginecología (embarazadas)",
        "summary": "Enfermedad viral transmitida por mosquitos, a menudo muy leve, pero con alta importancia por riesgo de malformaciones fetales (microcefalia).",
        "clinical_tests": [
            "**Prueba de PCR en Sangre u Orina (Zika)**: Positiva en la fase aguda.",
            "**Hemograma**: Generalmente normal o con alteraciones muy leves."
        ],
        "habits": [
            "Abundante hidratación y reposo relativo.",
            "Uso de repelentes de insectos y ropa de manga larga para evitar picaduras secundarias.",
            "**Embarazo**: Control ecográfico fetal estricto si la paciente está gestando."
        ],
        "medications": [
            "Paracetamol 500mg cada 8 horas para controlar la fiebre y el malestar general.",
            "Antihistamínicos si el sarpullido (rash) produce mucha comezón.",
            "**ADVERTENCIA**: Evitar relaciones sexuales sin protección durante al menos 3 meses tras la infección."
        ],
        "red_flags": [
            "Debilidad muscular ascendente rápida o parálisis (Sospecha de Guillain-Barré).",
            "Fiebre persistente con alteración del estado de alerta.",
            "Dolor de articulaciones severo que impida la movilidad."
        ]
    },
    "Fiebre Chikungunya": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Reumatología / Medicina General",
        "summary": "Infección viral caracterizada por la aparición súbita de fiebre alta y dolores articulares bilaterales severos y debilitantes.",
        "clinical_tests": [
            "**Serología (Chikungunya IgM)**: Positiva.",
            "**PCR específico**: Detectable en los primeros 5 días."
        ],
        "habits": [
            "Reposo absoluto por la severidad del dolor articular.",
            "Uso de compresas frías en las articulaciones inflamadas.",
            "Hidratación continua."
        ],
        "medications": [
            "Paracetamol en fase aguda (primeros 5 días).",
            "AINEs (Ibuprofeno o Naproxeno) solo después de descartar dengue y pasar la fase aguda febril.",
            "**ADVERTENCIA**: Los dolores articulares pueden persistir durante meses en forma crónica."
        ],
        "red_flags": [
            "Fiebre de más de 39 °C que no responde a antipiréticos.",
            "Dolor articular intratable con analgésicos estándar.",
            "Alteración de la marcha o incapacidad para sostenerse en pie."
        ]
    },
    "Otitis Media Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Otorrinolaringología / Pediatría",
        "summary": "Infección bacteriana o viral del oído medio, común tras resfriados. Se caracteriza por dolor de oído intenso y sordera temporal.",
        "clinical_tests": [
            "**Otoscopia**: Membrana timpánica abombada, eritematosa (roja) y con movilidad disminuida.",
            "**Examen Clínico**: Dolor a la palpación de la mastoides o tracción leve."
        ],
        "habits": [
            "Evitar la entrada de agua en el oído afectado al bañarse.",
            "Mantener al paciente en posición semisentada para reducir la presión en el oído.",
            "No utilizar hisopos o introducir objetos extraños."
        ],
        "medications": [
            "Amoxicilina 500mg cada 8 horas por 7 días (bajo indicación médica).",
            "Ibuprofeno 400mg cada 8 horas para reducir la inflamación y el dolor.",
            "**ADVERTENCIA**: No aplicar gotas óticas si se sospecha o confirma perforación timpánica."
        ],
        "red_flags": [
            "Salida de pus o sangre por el oído (otorrea).",
            "Hinchazón y enrojecimiento detrás de la oreja con desviación de la misma (mastoiditis).",
            "Vértigo rotatorio severo o parálisis facial."
        ]
    },
    "Otitis Externa Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Otorrinolaringología / Medicina General",
        "summary": "Infección del conducto auditivo externo, comúnmente llamada 'oído de nadador', debido a retención de humedad.",
        "clinical_tests": [
            "**Otoscopia**: Conducto auditivo externo eritematoso, edematoso, con detritos celulares.",
            "**Signo del Trago**: Dolor intenso al presionar el trago de la oreja."
        ],
        "habits": [
            "Mantener el oído completamente seco (usar tapones o algodón con vaselina al ducharse).",
            "Suspender la natación durante al menos 10 a 14 días.",
            "Evitar el rascado del conducto."
        ],
        "medications": [
            "Gotas óticas de Ciprofloxacino con Dexametasona (3-4 gotas cada 8 horas por 7 días).",
            "Analgésicos orales para el control del dolor.",
            "**ADVERTENCIA**: Las otitis externas agudas suelen ser muy dolorosas a la palpación."
        ],
        "red_flags": [
            "Dolor severo persistente que se irradia a la mitad de la cara en pacientes diabéticos (Otitis externa maligna).",
            "Fiebre alta con escalofríos.",
            "Incapacidad para abrir completamente la boca (trismo)."
        ]
    },
    "Sinusitis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Otorrinolaringología / Medicina General",
        "summary": "Inflamación de la mucosa de los senos paranasales, caracterizada por congestión nasal, secreción purulenta y dolor facial.",
        "clinical_tests": [
            "**Examen Clínico**: Dolor a la presión sobre los senos maxilares o frontales.",
            "**TC de Senos Paranasales**: Oclusión y niveles hidroaéreos (indicado solo en casos recurrentes)."
        ],
        "habits": [
            "Realizar vaporizaciones con agua templada o uso de humidificadores.",
            "Abundante hidratación oral para diluir las secreciones.",
            "Lavados nasales frecuentes con solución salina."
        ],
        "medications": [
            "Analgésicos (Ibuprofeno o Paracetamol).",
            "Descongestionantes nasales por no más de 3 a 5 días (evitar congestión de rebote).",
            "Antibióticos (ej. Amoxicilina) solo si los síntomas duran >10 días o empeoran drásticamente."
        ],
        "red_flags": [
            "Hinchazón, enrojecimiento o dolor alrededor de uno o ambos ojos (celulitis periorbitaria).",
            "Visión doble o disminución de la agudeza visual.",
            "Dolor de cabeza frontal severo que no cede con analgésicos."
        ]
    },
    "COVID-19": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Infectología",
        "summary": "Infección respiratoria viral por SARS-CoV-2. Cursa con síntomas gripales y malestar general en casos leves o moderados.",
        "clinical_tests": [
            "**Prueba rápida de Antígeno SARS-CoV-2**: Positiva.",
            "**PCR Nasofaríngeo**: Detecta ARN viral."
        ],
        "habits": [
            "Aislamiento preventivo en habitación ventilada durante el periodo activo.",
            "Uso de mascarilla al salir de la habitación.",
            "Monitorear la saturación de oxígeno en reposo dos veces al día."
        ],
        "medications": [
            "Tratamiento puramente sintomático: Paracetamol 500mg cada 8 horas.",
            "Lavados nasales.",
            "**ADVERTENCIA**: Está desaconsejado el uso de antibióticos, esteroides u otros fármacos no aprobados en casos leves."
        ],
        "red_flags": [
            "Dificultad respiratoria al hablar o al hacer mínimos esfuerzos.",
            "Saturación de oxígeno por debajo de 94% sostenida.",
            "Dolor opresivo persistente en el pecho."
        ]
    },
    "COVID-19 Grave": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neumología / Medicina Crítica",
        "summary": "Infección sistémica por SARS-CoV-2 que progresa a neumonía bilateral grave, insuficiencia respiratoria y SDRA.",
        "clinical_tests": [
            "**Radiografía/TC de Tórax**: Infiltrados bilaterales en vidrio deslustrado extensos.",
            "**Gasometría Arterial**: Hipoxia severa con índice de Kirby (PaO2/FiO2) disminuido.",
            "**Dímero D / PCR / Ferritina**: Elevados significativamente."
        ],
        "habits": [
            "Hospitalización inmediata en sala de aislamiento COVID de alta complejidad.",
            "Uso de ventilación mecánica o soporte de oxígeno de alto flujo.",
            "Posición de prono vigil (acostado boca abajo) para mejorar la ventilación."
        ],
        "medications": [
            "Oxigenoterapia agresiva.",
            "Corticoides (Dexametasona 6mg/día) indicados únicamente por requerimiento de oxígeno.",
            "Anticoagulación profiláctica con Heparina de bajo peso molecular por alto riesgo trombótico."
        ],
        "red_flags": [
            "Dificultad respiratoria extrema con cianosis.",
            "Saturación de oxígeno inferior al 90% a pesar de oxígeno suplementario nasal.",
            "Trastornos de la coagulación o choque séptico."
        ]
    },
    "Faringoamigdalitis Viral": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Familiar",
        "summary": "Inflamación de la faringe y amígdalas de causa viral, cursa usualmente con congestión, tos y ausencia de exudado purulento.",
        "clinical_tests": [
            "**Criterios de Centor**: 0-2 puntos (sugiere causa viral).",
            "**Prueba rápida de estreptococo**: Negativa."
        ],
        "habits": [
            "Hacer gárgaras con agua tibia con sal para aliviar el dolor local.",
            "Consumo de líquidos a temperatura ambiente o templados.",
            "Reposo relativo."
        ],
        "medications": [
            "Analgésicos (Paracetamol o Ibuprofeno) para el dolor de garganta.",
            "Anestésicos locales en spray o pastillas para chupar.",
            "**ADVERTENCIA**: Está contraindicado el uso de antibióticos."
        ],
        "red_flags": [
            "Dificultad para tragar incluso saliva (sialorrea).",
            "Incapacidad para abrir la boca (trismo).",
            "Dificultad para respirar o estridor laríngeo."
        ]
    },
    "Faringoamigdalitis Estreptocócica": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Pediatría",
        "summary": "Infección bacteriana aguda de la faringe por Streptococcus pyogenes, caracterizada por placas purulentas y adenopatías dolorosas.",
        "clinical_tests": [
            "**Criterios de Centor**: >=3 puntos (alta sospecha bacteriana).",
            "**Prueba rápida de estreptococo / Cultivo faríngeo**: Positivo."
        ],
        "habits": [
            "Evitar compartir vasos o utensilios de comida para prevenir el contagio.",
            "Hidratación abundante.",
            "Lavado de manos frecuente."
        ],
        "medications": [
            "**Antibiótico**: Penicilina benzatínica intramuscular (dosis única) o Amoxicilina oral por 10 días.",
            "Antiinflamatorios orales (Ibuprofeno) para el dolor facial/garganta.",
            "**ADVERTENCIA**: Es crítico completar los 10 días de antibiótico oral para prevenir la fiebre reumática."
        ],
        "red_flags": [
            "Desviación de la úvula hacia un lado con dolor faríngeo extremo (Absceso periamigdalino).",
            "Dificultad severa para tragar o respirar.",
            "Aparición de sarpullido rojo áspero en el cuerpo (escarlatina)."
        ]
    },
    "Tromboembolismo Pulmonar": {
        "alert_level": "Rojo",
        "color": "#ef4444",
        "specialist": "Neumología / Medicina Interna / Urgencias",
        "summary": "Obstrucción de una arteria pulmonar por un coágulo desprendido (usualmente de las piernas). Cuadro agudo potencialmente mortal.",
        "clinical_tests": [
            "**Angio-TC Pulmonar**: Defecto de llenado arterial en el árbol pulmonar.",
            "**Dímero D**: Elevado (alta sensibilidad, baja especificidad).",
            "**Ecocardiograma**: Signos de sobrecarga del ventrículo derecho."
        ],
        "habits": [
            "Reposo absoluto en cama sin realizar ningún movimiento de extremidades.",
            "Hospitalización inmediata.",
            "Evitar masajes o manipulación de las piernas ante sospecha de trombosis venosa profunda."
        ],
        "medications": [
            "Anticoagulación parenteral inmediata con Heparina no fraccionada o de bajo peso molecular.",
            "Fibrinolíticos (Alteplasa) en casos de compromiso hemodinámico grave (choque).",
            "**ADVERTENCIA**: El diagnóstico rápido y la anticoagulación salvan vidas."
        ],
        "red_flags": [
            "Aparición brusca de falta de aire intensa sin causa respiratoria previa.",
            "Dolor de pecho de tipo pleurítico (empeora al respirar hondo).",
            "Pérdida brusca del conocimiento o tos con sangre (hemoptisis)."
        ]
    },
    "Diabetes Mellitus Tipo 2": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Endocrinología / Medicina Interna",
        "summary": "Trastorno metabólico crónico caracterizado por resistencia a la insulina e hiperglucemia. Requiere control estricto a largo plazo.",
        "clinical_tests": [
            "**Glucemia en Ayunas**: >=126 mg/dL en dos ocasiones.",
            "**Hemoglobina Glicosilada (HbA1c)**: >=6.5% confirma diagnóstico.",
            "**Examen de Orina**: Evalúa glucosuria o microalbuminuria."
        ],
        "habits": [
            "Dieta baja en azúcares refinados y carbohidratos simples.",
            "Realizar actividad física aeróbica moderada al menos 150 minutos por semana.",
            "Revisión diaria del estado de la piel de los pies."
        ],
        "medications": [
            "Metformina 500mg-850mg administrada con las comidas principales.",
            "Otros antidiabéticos orales o insulina según la indicación del especialista.",
            "**ADVERTENCIA**: En caso de temblor, sudoración fría o confusión (hipoglucemia), consumir azúcar inmediatamente."
        ],
        "red_flags": [
            "Aliento con olor a frutas dulces, deshidratación extrema y confusión (Cetoacidosis).",
            "Nivel de glucosa capilar persistente >300 mg/dL.",
            "Presencia de heridas o úlceras en los pies con signos de infección."
        ]
    },
    "Gastroenteritis Aguda Viral": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Gastroenterología",
        "summary": "Inflamación gastrointestinal viral (ej. Rotavirus, Norovirus) que causa diarrea líquida explosiva y vómitos. Muy contagiosa.",
        "clinical_tests": [
            "**Coprocultivo**: Negativo para bacterias patógenas.",
            "**Electrólitos Séricos**: Evalúa grado de alteración por pérdidas líquidas."
        ],
        "habits": [
            "Rehidratación oral constante con soluciones de rehidratación oral (suero oral), no usar bebidas energéticas.",
            "Dieta astringente blanda (arroz, manzana rallada, plátano, pollo cocido).",
            "Lavado riguroso de manos tras ir al baño y antes de comer."
        ],
        "medications": [
            "Probióticos para restauración de la flora bacteriana.",
            "Paracetamol para dolores musculares o fiebre.",
            "**ADVERTENCIA**: Está contraindicado el uso de antibióticos y loperamida."
        ],
        "red_flags": [
            "Signos de deshidratación severa (ausencia de orina, boca completamente seca, mareo al ponerse de pie).",
            "Vómitos repetidos que impiden tolerar los líquidos por boca.",
            "Fiebre persistente >38.5 °C."
        ]
    },
    "Gastroenteritis Aguda Bacteriana": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Gastroenterología / Infectología",
        "summary": "Infección intestinal bacteriana (ej. Salmonella, Shigella, Campylobacter) adquirida por alimentos contaminados. Frecuentemente causa diarrea con moco o sangre.",
        "clinical_tests": [
            "**Coprocultivo / Reacción Inflamatoria en Heces**: Positivo para bacterias o presencia de leucocitos abundantes.",
            "**Hemograma Completo**: Leucocitosis con neutrofilia."
        ],
        "habits": [
            "Hidratación agresiva con suero oral.",
            "Evitar alimentos grasos, lácteos y condimentos.",
            "Extremar medidas de higiene personal."
        ],
        "medications": [
            "Antibióticos (ej. Azitromicina o Ciprofloxacino) bajo estricto criterio médico.",
            "Probióticos y suero oral.",
            "**ADVERTENCIA**: Está prohibido el uso de Loperamida, ya que retiene las toxinas bacterianas en el intestino."
        ],
        "red_flags": [
            "Diarrea con sangre franca, moco o pus (disentería).",
            "Dolor abdominal insoportable continuo.",
            "Fiebre alta con escalofríos."
        ]
    },
    "Gastroenteritis Aguda Parasitaria": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Pediatría / Gastroenterología / Infectología",
        "summary": "Infección intestinal por protozoos o helmintos (ej. Giardia, Entamoeba). Cursa con diarrea prolongada, cólicos y meteorismo.",
        "clinical_tests": [
            "**Examen Coproparasitológico Seriados**: Presencia de quistes, trofozoítos o huevos.",
            "**Prueba de Antígeno en heces**: Positiva para Giardia o amebas."
        ],
        "habits": [
            "Hervir el agua de consumo o beber agua embotellada.",
            "Lavar minuciosamente frutas y verduras antes de consumirlas.",
            "Evitar el consumo de alimentos crudos en puestos callejeros."
        ],
        "medications": [
            "Antiparasitarios específicos (Metronidazol, Secnidazol o Nitazoxanida) según el parásito identificado.",
            "Suero oral de soporte.",
            "**ADVERTENCIA**: Completar el tratamiento antiparasitario aun si los síntomas desaparecen antes."
        ],
        "red_flags": [
            "Pérdida de peso significativa involuntaria.",
            "Diarrea que se prolonga por más de 14 días.",
            "Deposiciones con sangre oscura y dolor abdominal severo."
        ]
    },
    "Resfriado Común (Rinofaringitis)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Familiar",
        "summary": "Infección viral benigna de las vías aéreas superiores. Produce congestión nasal, estornudos y malestar general leve.",
        "clinical_tests": [
            "**Examen Clínico Nasofaríngeo**: Mucosa nasal eritematosa, rinorrea clara.",
            "**Radiografía de Tórax**: Normal, campos pulmonares limpios."
        ],
        "habits": [
            "Reposo e hidratación adecuada (mínimo 2 litros de agua al día).",
            "Lavados nasales con agua salina para desobstruir las fosas nasales.",
            "Evitar fumar o la exposición al humo de tabaco."
        ],
        "medications": [
            "Paracetamol o Ibuprofeno oral a demanda para la congestión o dolor de cabeza.",
            "Antihistamínicos si hay rinorrea abundante.",
            "**ADVERTENCIA**: Los jarabes para la tos no tienen alta evidencia; priorice la hidratación."
        ],
        "red_flags": [
            "Fiebre persistente por más de 3 días que no cede con analgésicos.",
            "Aparición de dolor de oído intenso.",
            "Dificultad para respirar o ruidos al exhalar (sibilancias)."
        ]
    },
    "Cistitis Aguda (IVU Baja)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Ginecología / Urología / Medicina General",
        "summary": "Infección bacteriana localizada en la vejiga urinaria. Es muy común en mujeres y produce dolor al orinar y micción frecuente.",
        "clinical_tests": [
            "**Examen General de Orina (EGO)**: Leucocituria, nitritos positivos y presencia de bacterias.",
            "**Urocultivo**: Confirma agente bacteriano (usualmente E. coli) con antibiograma."
        ],
        "habits": [
            "Aumentar el consumo de agua a 3 litros diarios para favorecer la eliminación de bacterias.",
            "Orinar inmediatamente después de las relaciones sexuales.",
            "Higiene íntima de adelante hacia atrás."
        ],
        "medications": [
            "**Antibióticos**: Nitrofurantoína 100mg cada 12 horas por 5 días o Fosfomicina 3g (dosis única) según indicación médica.",
            "Fenazopiridina 100mg cada 8 horas por 2 días para aliviar el ardor.",
            "**ADVERTENCIA**: No suspender el antibiótico al desaparecer los síntomas."
        ],
        "red_flags": [
            "Aparición de dolor lumbar intenso con fiebre alta y escalofríos (sugiere pielonefritis).",
            "Hematuria masiva (sangre abundante en la orina).",
            "Imposibilidad para realizar la micción."
        ]
    },
    "Pielonefritis Aguda (IVU Alta)": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Nefrología / Urología / Infectología",
        "summary": "Infección bacteriana grave que asciende al riñón. Se manifiesta con fiebre, escalofríos intensos y dolor en la fosa renal.",
        "clinical_tests": [
            "**Examen de Orina y Urocultivo**: Altamente patológico, bacterias y leucocitos.",
            "**Hemograma**: Leucocitosis con desviación a la izquierda.",
            "**Ecografía Renal**: Descarte de obstrucción o absceso renal."
        ],
        "habits": [
            "Reposo absoluto en cama.",
            "Control diario de la temperatura corporal.",
            "Hidratación oral si se tolera, de lo contrario requiere vía endovenosa."
        ],
        "medications": [
            "**Antibióticos**: Ciprofloxacino 500mg cada 12 horas o Ceftriaxona endovenosa según gravedad.",
            "Antipiréticos (Paracetamol) para la fiebre.",
            "**ADVERTENCIA**: Requiere estrecho seguimiento por riesgo de sepsis urinaria."
        ],
        "red_flags": [
            "Hipotensión o confusión mental (signos de choque séptico).",
            "Vómitos persistentes que impiden tomar los antibióticos orales.",
            "Disminución drástica del volumen de orina (oligurioa)."
        ]
    },
    "Reflujo Gastroesofágico (ERGE)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Gastroenterología / Medicina Interna",
        "summary": "Retorno anormal del contenido ácido del estómago hacia el esófago debido a disfunción del esfínter esofágico inferior.",
        "clinical_tests": [
            "**Endoscopia Digestiva Alta (EDA)**: Descarta esofagitis, hernia hiatal o esófago de Barrett.",
            "**pH-metría de 24 horas**: Gold standard para confirmar reflujo ácido."
        ],
        "habits": [
            "Evitar acostarse antes de 2 a 3 horas después de ingerir alimentos.",
            "Elevar la cabecera de la cama 15 cm.",
            "Evitar alimentos grasos, picantes, menta, café, chocolate y alcohol."
        ],
        "medications": [
            "**Inhibidores de la Bomba de Protones**: Omeprazol 20mg en ayunas 30 minutos antes del desayuno.",
            "Antiácidos de barrera (Alginato de sodio) tras las comidas principales.",
            "**ADVERTENCIA**: La automedicación prolongada con antiácidos puede enmascarar patologías graves."
        ],
        "red_flags": [
            "Dificultad o dolor al tragar alimentos (disfagia u odinofagia).",
            "Pérdida de peso involuntaria y anemia.",
            "Vómitos con sangre o deposiciones negras (melenas)."
        ]
    },
    "Gastritis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Gastroenterología / Medicina General",
        "summary": "Inflamación aguda de la mucosa gástrica, frecuentemente secundaria a consumo de AINEs, alcohol o estrés severo.",
        "clinical_tests": [
            "**Endoscopia Digestiva Alta**: Visualiza mucosa eritematosa o erosiones superficiales.",
            "**Prueba de aliento para H. pylori**: Descarta infección asociada."
        ],
        "habits": [
            "Dieta blanda fraccionada, libre de irritantes (grasas, condimentos, cítricos, picantes).",
            "Evitar de forma absoluta el tabaco y el alcohol.",
            "No consumir medicamentos antiinflamatorios (AINEs) sin protección gástrica."
        ],
        "medications": [
            "Omeprazol 20mg o Esomeprazol 40mg diario en ayunas.",
            "Sucralfato o antiácidos orales como protector de la mucosa.",
            "**ADVERTENCIA**: No suspender el tratamiento antes del tiempo indicado por riesgo de recidiva."
        ],
        "red_flags": [
            "Vómito persistente en 'poso de café' o con sangre fresca.",
            "Dolor epigástrico severo y repentino que no cede.",
            "Melenas (heces negras y fétidas)."
        ]
    },
    "Úlcera Péptica No Complicada": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Gastroenterología / Medicina Interna",
        "summary": "Lesión profunda en la mucosa del estómago o duodeno. Caracterizada por dolor epigástrico quemante que se alivia o empeora con la comida.",
        "clinical_tests": [
            "**Endoscopia Digestiva Alta con biopsia**: Descarta malignidad y confirma presencia de la úlcera.",
            "**Detección de H. pylori**: Confirmatorio mediante biopsia o prueba de antígenos."
        ],
        "habits": [
            "Evitar el ayuno prolongado; realizar comidas frecuentes de menor volumen.",
            "Evitar medicamentos lesivos para la mucosa (Aspirina, Ibuprofeno, Ketorolaco).",
            "Evitar bebidas carbonatadas y café."
        ],
        "medications": [
            "**Bloqueadores ácidos**: Omeprazol 40mg diario por 4-8 semanas.",
            "Tratamiento erradicador para H. pylori (Claritiromicina + Amoxicilina + Omeprazol) si resulta positivo.",
            "**ADVERTENCIA**: El tabaco retrasa significativamente la curación de las úlceras."
        ],
        "red_flags": [
            "Dolor de aparición brusca en abdomen superior, que se vuelve rígido (sospecha de perforación).",
            "Signos de sangrado gastrointestinal activo.",
            "Dificultad persistente para tragar o vómitos recurrentes."
        ]
    },
    "Varicela (Leve/Moderada)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Pediatría / Medicina General",
        "summary": "Infección viral altamente contagiosa por el virus varicela-zóster. Produce sarpullido pruriginoso característico con vesículas.",
        "clinical_tests": [
            "**Examen Clínico Visual**: Lesiones en diferentes estadios (máculas, pápulas, vesículas y costras).",
            "**PCR del líquido de la vesícula**: Confirma en casos de duda diagnóstica."
        ],
        "habits": [
            "Mantener las uñas cortas y limpias para evitar sobreinfecciones bacterianas por rascado.",
            "Baños diarios con agua templada y avena coloidal para aliviar el picor.",
            "Aislamiento escolar o laboral hasta que todas las lesiones estén en fase de costra."
        ],
        "medications": [
            "Antihistamínicos orales (Loratadina) para el control del prurito.",
            "Loción de calamina tópica en las lesiones costrosas.",
            "Paracetamol para la fiebre.",
            "**ADVERTENCIA**: Está prohibido el uso de Aspirina en niños por riesgo de Síndrome de Reye."
        ],
        "red_flags": [
            "Lesiones de la piel que se vuelven calientes, rojas, con pus o muy dolorosas (infección bacteriana secundaria).",
            "Tos persistente o dificultad para respirar.",
            "Inestabilidad al caminar, confusión o convulsiones."
        ]
    }
}


# MOTOR DE DIAGNÓSTICO BAYESIANO v3.2
class BayesianDiagnosticSystem:
    LAPLACE_ALPHA = 0.01

    def __init__(self):
        self.enfermedades = list(CLINICAL_METADATA.keys())

        # ── PROBABILIDADES PREVIAS BASE (Epidemiológicas actualizadas)
        self.P_enfermedad_base = {
            "Gripe Común / Influenza":                 0.06,
            "Neumonía":                                0.04,
            "Bronquitis Aguda":                        0.04,
            "Crisis Asmática Aguda":                   0.03,
            "Exacerbación Aguda de EPOC":              0.02,
            "Infarto Agudo de Miocardio (IAM)":        0.03,
            "Insuficiencia Cardíaca Congestiva (ICC)": 0.03,
            "Miocarditis":                             0.015,
            "Encefalitis":                             0.005,
            "Accidente Cerebrovascular (ACV)":         0.03,
            "Migraña Severa":                          0.04,
            "Dengue No Grave (Clásico)":               0.04,
            "Dengue Grave":                            0.01,
            "Fiebre Zika":                             0.03,
            "Fiebre Chikungunya":                      0.02,
            "Otitis Media Aguda":                      0.03,
            "Otitis Externa Aguda":                    0.03,
            "Sinusitis Aguda":                         0.04,
            "COVID-19":                                0.05,
            "COVID-19 Grave":                          0.01,
            "Faringoamigdalitis Viral":                0.04,
            "Faringoamigdalitis Estreptocócica":       0.03,
            "Tromboembolismo Pulmonar":                0.015,
            "Diabetes Mellitus Tipo 2":                0.04,
            "Gastroenteritis Aguda Viral":             0.04,
            "Gastroenteritis Aguda Bacteriana":        0.03,
            "Gastroenteritis Aguda Parasitaria":       0.03,
            "Resfriado Común (Rinofaringitis)":        0.06,
            "Cistitis Aguda (IVU Baja)":               0.04,
            "Pielonefritis Aguda (IVU Alta)":          0.02,
            "Reflujo Gastroesofágico (ERGE)":          0.04,
            "Gastritis Aguda":                         0.04,
            "Úlcera Péptica No Complicada":            0.025,
            "Varicela (Leve/Moderada)":                0.015,
        }

        # ── PROBABILIDADES CONDICIONALES: P(Síntoma | Enfermedad)
        self.P_sintoma = {
            "Tos Seca Irritativa": {
                "Gripe Común / Influenza": 0.65, "Neumonía": 0.30, "Bronquitis Aguda": 0.50, "Crisis Asmática Aguda": 0.60,
                "Exacerbación Aguda de EPOC": 0.30, "COVID-19": 0.70, "COVID-19 Grave": 0.50, "Faringoamigdalitis Viral": 0.35,
                "Resfriado Común (Rinofaringitis)": 0.40, "Reflujo Gastroesofágico (ERGE)": 0.30
            },
            "Tos Productiva / con Flema": {
                "Gripe Común / Influenza": 0.20, "Neumonía": 0.85, "Bronquitis Aguda": 0.88, "Crisis Asmática Aguda": 0.40,
                "Exacerbación Aguda de EPOC": 0.85, "COVID-19": 0.25, "COVID-19 Grave": 0.45, "Sinusitis Aguda": 0.30
            },
            "Tos Ferina / Accesos": {
                "Gripe Común / Influenza": 0.05, "Bronquitis Aguda": 0.15, "Crisis Asmática Aguda": 0.20
            },
            "Dificultad Respiratoria (Disnea)": {
                "Gripe Común / Influenza": 0.15, "Neumonía": 0.88, "Bronquitis Aguda": 0.45, "Crisis Asmática Aguda": 0.97,
                "Exacerbación Aguda de EPOC": 0.98, "Infarto Agudo de Miocardio (IAM)": 0.62, "Insuficiencia Cardíaca Congestiva (ICC)": 0.95,
                "Miocarditis": 0.65, "Encefalitis": 0.15, "Accidente Cerebrovascular (ACV)": 0.20, "COVID-19": 0.45, "COVID-19 Grave": 0.98,
                "Tromboembolismo Pulmonar": 0.95, "Pielonefritis Aguda (IVU Alta)": 0.10
            },
            "Tos con Sangre (Hemoptisis)": {
                "Neumonía": 0.18, "Bronquitis Aguda": 0.05, "Exacerbación Aguda de EPOC": 0.10, "COVID-19 Grave": 0.12,
                "Tromboembolismo Pulmonar": 0.25
            },
            "Dolor en el Pecho": {
                "Gripe Común / Influenza": 0.10, "Neumonía": 0.65, "Bronquitis Aguda": 0.35, "Crisis Asmática Aguda": 0.30,
                "Exacerbación Aguda de EPOC": 0.40, "Infarto Agudo de Miocardio (IAM)": 0.98, "Insuficiencia Cardíaca Congestiva (ICC)": 0.38,
                "Miocarditis": 0.90, "COVID-19 Grave": 0.60, "Tromboembolismo Pulmonar": 0.90, "Reflujo Gastroesofágico (ERGE)": 0.45,
                "Gastritis Aguda": 0.25, "Úlcera Péptica No Complicada": 0.30
            },
            "Palpitaciones": {
                "Gripe Común / Influenza": 0.10, "Infarto Agudo de Miocardio (IAM)": 0.50, "Insuficiencia Cardíaca Congestiva (ICC)": 0.65,
                "Miocarditis": 0.80, "Tromboembolismo Pulmonar": 0.55, "Diabetes Mellitus Tipo 2": 0.15
            },
            "Edema (Hinchazón)": {
                "Insuficiencia Cardíaca Congestiva (ICC)": 0.92, "Miocarditis": 0.40, "Diabetes Mellitus Tipo 2": 0.30,
                "Tromboembolismo Pulmonar": 0.25
            },
            "Dolor de Cabeza Severo": {
                "Gripe Común / Influenza": 0.60, "Encefalitis": 0.88, "Accidente Cerebrovascular (ACV)": 0.60, "Migraña Severa": 0.99,
                "Dengue No Grave (Clásico)": 0.85, "Dengue Grave": 0.85, "Fiebre Zika": 0.65, "Fiebre Chikungunya": 0.70,
                "Sinusitis Aguda": 0.68, "COVID-19": 0.48
            },
            "Confusión / Convulsiones": {
                "Encefalitis": 0.95, "Accidente Cerebrovascular (ACV)": 0.52, "Diabetes Mellitus Tipo 2": 0.15,
                "Pielonefritis Aguda (IVU Alta)": 0.20
            },
            "Pérdida de Fuerza/Sensibilidad Unilateral": {
                "Accidente Cerebrovascular (ACV)": 0.98, "Encefalitis": 0.25
            },
            "Dificultad para Hablar/Entender": {
                "Accidente Cerebrovascular (ACV)": 0.95, "Encefalitis": 0.30
            },
            "Mareos / Vértigo": {
                "Gripe Común / Influenza": 0.25, "Infarto Agudo de Miocardio (IAM)": 0.30, "Insuficiencia Cardíaca Congestiva (ICC)": 0.35,
                "Accidente Cerebrovascular (ACV)": 0.60, "Migraña Severa": 0.65, "Dengue Grave": 0.50, "Otitis Media Aguda": 0.40,
                "Otitis Externa Aguda": 0.15, "Pielonefritis Aguda (IVU Alta)": 0.25
            },
            "Fiebre Alta": {
                "Gripe Común / Influenza": 0.85, "Neumonía": 0.80, "Encefalitis": 0.90, "Dengue No Grave (Clásico)": 0.98,
                "Dengue Grave": 0.98, "Fiebre Zika": 0.35, "Fiebre Chikungunya": 0.95, "Otitis Media Aguda": 0.65,
                "Sinusitis Aguda": 0.55, "COVID-19": 0.80, "COVID-19 Grave": 0.90, "Faringoamigdalitis Estreptocócica": 0.85,
                "Gastroenteritis Aguda Bacteriana": 0.75, "Pielonefritis Aguda (IVU Alta)": 0.90, "Varicela (Leve/Moderada)": 0.80
            },
            "Febrícula": {
                "Gripe Común / Influenza": 0.12, "Bronquitis Aguda": 0.35, "Miocarditis": 0.50, "Fiebre Zika": 0.60,
                "Otitis Media Aguda": 0.30, "Otitis Externa Aguda": 0.25, "Sinusitis Aguda": 0.35, "COVID-19": 0.15,
                "Faringoamigdalitis Viral": 0.60, "Gastroenteritis Aguda Viral": 0.55, "Cistitis Aguda (IVU Baja)": 0.20,
                "Resfriado Común (Rinofaringitis)": 0.30
            },
            "Fatiga / Cansancio Extremo": {
                "Gripe Común / Influenza": 0.82, "Neumonía": 0.78, "Bronquitis Aguda": 0.55, "Insuficiencia Cardíaca Congestiva (ICC)": 0.85,
                "Miocarditis": 0.80, "Encefalitis": 0.70, "Dengue No Grave (Clásico)": 0.90, "Dengue Grave": 0.95,
                "Fiebre Zika": 0.60, "Fiebre Chikungunya": 0.85, "COVID-19": 0.85, "COVID-19 Grave": 0.95,
                "Diabetes Mellitus Tipo 2": 0.62, "Gastroenteritis Aguda Bacteriana": 0.70, "Pielonefritis Aguda (IVU Alta)": 0.80
            },
            "Dolor de Cuerpo Generalizado": {
                "Gripe Común / Influenza": 0.78, "Dengue No Grave (Clásico)": 0.95, "Fiebre Zika": 0.75,
                "Fiebre Chikungunya": 0.90, "COVID-19": 0.75, "Varicela (Leve/Moderada)": 0.50
            },
            "Pérdida del Olfato o Gusto": {
                "COVID-19": 0.65, "COVID-19 Grave": 0.55, "Resfriado Común (Rinofaringitis)": 0.15
            },
            "Erupciones Cutáneas (Rash)": {
                "Dengue No Grave (Clásico)": 0.45, "Fiebre Zika": 0.90, "Fiebre Chikungunya": 0.55,
                "Varicela (Leve/Moderada)": 0.99
            },
            "Náuseas / Vómitos": {
                "Gripe Común / Influenza": 0.15, "Neumonía": 0.20, "Infarto Agudo de Miocardio (IAM)": 0.25,
                "Encefalitis": 0.65, "Migraña Severa": 0.75, "Dengue No Grave (Clásico)": 0.40, "Dengue Grave": 0.85,
                "COVID-19": 0.20, "Gastroenteritis Aguda Viral": 0.85, "Gastroenteritis Aguda Bacteriana": 0.80,
                "Gastroenteritis Aguda Parasitaria": 0.40, "Pielonefritis Aguda (IVU Alta)": 0.65, "Gastritis Aguda": 0.75,
                "Úlcera Péptica No Complicada": 0.45
            },
            "Diarrea Acuosa Profusa": {
                "Gastroenteritis Aguda Viral": 0.92, "Gastroenteritis Aguda Parasitaria": 0.45
            },
            "Diarrea Disentérica (con Sangre/Moco)": {
                "Gastroenteritis Aguda Bacteriana": 0.78, "Gastroenteritis Aguda Parasitaria": 0.35
            },
            "Dolor Abdominal Cólico": {
                "Gastroenteritis Aguda Viral": 0.65, "Gastroenteritis Aguda Bacteriana": 0.85, "Gastroenteritis Aguda Parasitaria": 0.75,
                "Úlcera Péptica No Complicada": 0.20
            },
            "Dolor Abdominal Sordo / Difuso": {
                "Cistitis Aguda (IVU Baja)": 0.35, "Pielonefritis Aguda (IVU Alta)": 0.40, "Gastritis Aguda": 0.50,
                "Úlcera Péptica No Complicada": 0.55
            },
            "Dispepsia / Ardor Epigástrico": {
                "Reflujo Gastroesofágico (ERGE)": 0.70, "Gastritis Aguda": 0.90, "Úlcera Péptica No Complicada": 0.95
            },
            "Dolor de Garganta": {
                "Gripe Común / Influenza": 0.55, "COVID-19": 0.60, "Faringoamigdalitis Viral": 0.95,
                "Faringoamigdalitis Estreptocócica": 0.98, "Resfriado Común (Rinofaringitis)": 0.60
            },
            "Dolor de Oído / Cara": {
                "Otitis Media Aguda": 0.95, "Otitis Externa Aguda": 0.90, "Sinusitis Aguda": 0.85
            },
            "Otalgia (Dolor de oído)": {
                "Otitis Media Aguda": 0.98, "Otitis Externa Aguda": 0.95
            },
            "Odor Fétido / Secreción Ótica": {
                "Otitis Externa Aguda": 0.75, "Otitis Media Aguda": 0.35
            },
            "Disuria (Ardor al orinar)": {
                "Cistitis Aguda (IVU Baja)": 0.98, "Pielonefritis Aguda (IVU Alta)": 0.75
            },
            "Polaquiuria (Orinar muy seguido)": {
                "Cistitis Aguda (IVU Baja)": 0.95, "Pielonefritis Aguda (IVU Alta)": 0.60, "Diabetes Mellitus Tipo 2": 0.65
            },
            "Dolor Lumbar / Suprapúbico": {
                "Cistitis Aguda (IVU Baja)": 0.60, "Pielonefritis Aguda (IVU Alta)": 0.98
            },
            "Pirosis (Acidez estomacal)": {
                "Reflujo Gastroesofágico (ERGE)": 0.95, "Gastritis Aguda": 0.60, "Úlcera Péptica No Complicada": 0.55
            },
            "Regurgitación Ácida": {
                "Reflujo Gastroesofágico (ERGE)": 0.90
            },
            "Congestión Nasal / Estornudos": {
                "Gripe Común / Influenza": 0.60, "Sinusitis Aguda": 0.70, "COVID-19": 0.40,
                "Resfriado Común (Rinofaringitis)": 0.90
            },
            "Rinorrea (Moqueo)": {
                "Gripe Común / Influenza": 0.58, "Sinusitis Aguda": 0.65, "Resfriado Común (Rinofaringitis)": 0.92
            },
            "Artralgias Severas": {
                "Dengue No Grave (Clásico)": 0.40, "Fiebre Zika": 0.60, "Fiebre Chikungunya": 0.98
            },
            "Mialgias Intensas": {
                "Gripe Común / Influenza": 0.70, "Dengue No Grave (Clásico)": 0.90, "Fiebre Zika": 0.50,
                "Fiebre Chikungunya": 0.80, "COVID-19": 0.60
            },
            "Dolor Retroocular": {
                "Dengue No Grave (Clásico)": 0.85, "Dengue Grave": 0.80, "Fiebre Zika": 0.40, "Fiebre Chikungunya": 0.30
            },
            "Lesiones Vesiculares Cutáneas": {
                "Varicela (Leve/Moderada)": 0.99
            },
            "Prurito Generalizado": {
                "Fiebre Zika": 0.65, "Varicela (Leve/Moderada)": 0.85
            }
        }

        # ── LIKELIHOODS DE PRUEBAS DIAGNÓSTICAS (Ampliado)
        self.P_test_result = {
            "Panel Viral Respiratorio (PCR)": {
                "Positivo": {"Gripe Común / Influenza": 0.95, "COVID-19": 0.95, "COVID-19 Grave": 0.95, "Resfriado Común (Rinofaringitis)": 0.60},
                "Negativo": {"Gripe Común / Influenza": 0.02, "COVID-19": 0.02, "COVID-19 Grave": 0.02, "Resfriado Común (Rinofaringitis)": 0.40}
            },
            "Hemograma Completo": {
                "Leucocitosis": {"Neumonía": 0.88, "Bronquitis Aguda": 0.65, "Faringoamigdalitis Estreptocócica": 0.82, "Pielonefritis Aguda (IVU Alta)": 0.85, "Gastroenteritis Aguda Bacteriana": 0.70},
                "Leucopenia": {"Dengue No Grave (Clásico)": 0.90, "Dengue Grave": 0.92, "COVID-19": 0.55, "Gripe Común / Influenza": 0.45},
                "Normal": {"Gripe Común / Influenza": 0.75, "Migraña Severa": 0.80, "Resfriado Común (Rinofaringitis)": 0.85, "Reflujo Gastroesofágico (ERGE)": 0.90, "Cistitis Aguda (IVU Baja)": 0.80}
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
                "Positivo": {"Dengue No Grave (Clásico)": 0.97, "Dengue Grave": 0.97},
                "Negativo": {"Dengue No Grave (Clásico)": 0.05, "Dengue Grave": 0.05}
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
                "Elevado": {"Tromboembolismo Pulmonar": 0.88, "COVID-19 Grave": 0.70, "Dengue Grave": 0.60},
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
                "Patológica": {"Otitis Media Aguda": 0.95, "Otitis Externa Aguda": 0.92},
                "Normal": {"Otitis Media Aguda": 0.05, "Otitis Externa Aguda": 0.08}
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
                "Positiva": {"Faringoamigdalitis Estreptocócica": 0.95, "Faringoamigdalitis Viral": 0.02},
                "Negativa": {"Faringoamigdalitis Estreptocócica": 0.05, "Faringoamigdalitis Viral": 0.98}
            },
            "Angio-TC Pulmonar": {
                "Defecto de llenado": {"Tromboembolismo Pulmonar": 0.97},
                "Normal": {"Tromboembolismo Pulmonar": 0.03}
            },
            "Examen General de Orina (EGO)": {
                "Patológico": {"Cistitis Aguda (IVU Baja)": 0.95, "Pielonefritis Aguda (IVU Alta)": 0.96},
                "Normal": {"Cistitis Aguda (IVU Baja)": 0.05, "Pielonefritis Aguda (IVU Alta)": 0.04}
            },
            "Endoscopia Digestiva Alta": {
                "Esofagitis / Hernia hiatal": {"Reflujo Gastroesofágico (ERGE)": 0.85},
                "Erosiones gástricas": {"Gastritis Aguda": 0.90},
                "Úlcera visualizada": {"Úlcera Péptica No Complicada": 0.95},
                "Normal": {"Reflujo Gastroesofágico (ERGE)": 0.15, "Gastritis Aguda": 0.10, "Úlcera Péptica No Complicada": 0.05}
            },
            "Urocultivo": {
                "Positivo (>100,000 UFC)": {"Cistitis Aguda (IVU Baja)": 0.96, "Pielonefritis Aguda (IVU Alta)": 0.97},
                "Negativo": {"Cistitis Aguda (IVU Baja)": 0.04, "Pielonefritis Aguda (IVU Alta)": 0.03}
            }
        }

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

    def restaurar_por_defecto(self):
        self.P_enfermedad_base = copy.deepcopy(self._default_priors)
        self.P_sintoma = copy.deepcopy(self._default_conditionals)

    def normalizar(self, prob: dict) -> dict:
        total = sum(prob.values())
        if total <= 0:
            n = len(prob)
            return {k: 1.0 / n for k in prob}
        return {k: v / total for k, v in prob.items()}

    def mapear_signos_vitales(self, constantes: dict) -> dict:
        edad = float(constantes.get("edad", 30))
        temp = float(constantes.get("temperatura", 37.0))
        spo2 = float(constantes.get("spo2", 98))
        pas  = float(constantes.get("pas", 120))
        pad  = float(constantes.get("pad", 80))
        fc   = float(constantes.get("fc", 80))
        fr   = float(constantes.get("fr", 16))

        return {
            "Fiebre Alta":   temp >= 38.5,
            "Febrícula":     37.3 <= temp < 38.5,
            "Hipoxia Leve":  92 <= spo2 < 95,
            "Hipoxia Severa": spo2 < 92,
            "Hipertensión":  pas >= 140 or pad >= 90,
            "Hipotensión":   pas < 90,
            "Taquicardia":   fc > 100,
            "Bradicardia":   fc < 60,
            "Taquipnea":     fr > 20,
            "Edad Avanzada": edad >= 65,
        }

    def aplicar_antecedentes(self, prob_base: dict, antecedentes: dict) -> dict:
        prob = {k: math.log(max(v, self.LAPLACE_ALPHA)) for k, v in prob_base.items()}

        # Asma
        if antecedentes.get("Asma"):
            prob["Crisis Asmática Aguda"] = prob.get("Crisis Asmática Aguda", 0) + math.log(3.0)
            prob["Bronquitis Aguda"]      = prob.get("Bronquitis Aguda", 0)      + math.log(1.5)

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
            prob["Pielonefritis Aguda (IVU Alta)"] = prob.get("Pielonefritis Aguda (IVU Alta)", 0) + math.log(2.0)

        # Tabaquismo
        if antecedentes.get("Tabaquismo"):
            prob["Exacerbación Aguda de EPOC"] = prob.get("Exacerbación Aguda de EPOC", 0) + math.log(2.2)
            prob["Infarto Agudo de Miocardio (IAM)"] = prob.get("Infarto Agudo de Miocardio (IAM)", 0) + math.log(1.7)
            prob["Bronquitis Aguda"]   = prob.get("Bronquitis Aguda", 0)   + math.log(1.5)

        # Meningitis
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

        # Viaje Reciente a Zona Endémica
        if antecedentes.get("Viaje Reciente a Zona Endémica"):
            prob["Dengue No Grave (Clásico)"] = prob.get("Dengue No Grave (Clásico)", 0) + math.log(4.0)
            prob["Dengue Grave"]              = prob.get("Dengue Grave", 0)              + math.log(4.0)
            prob["Fiebre Zika"]               = prob.get("Fiebre Zika", 0)               + math.log(4.0)
            prob["Fiebre Chikungunya"]        = prob.get("Fiebre Chikungunya", 0)        + math.log(4.0)

        # Consumo de Alimentos en la Calle / Agua No Tratada
        if antecedentes.get("Consumo de Alimentos en la Calle / Agua No Tratada"):
            prob["Gastroenteritis Aguda Viral"]      = prob.get("Gastroenteritis Aguda Viral", 0)      + math.log(2.0)
            prob["Gastroenteritis Aguda Bacteriana"] = prob.get("Gastroenteritis Aguda Bacteriana", 0) + math.log(4.0)
            prob["Gastroenteritis Aguda Parasitaria"]  = prob.get("Gastroenteritis Aguda Parasitaria", 0)  + math.log(3.5)

        # Uso Reciente de Antibióticos
        if antecedentes.get("Uso Reciente de Antibióticos"):
            prob["Gastroenteritis Aguda Bacteriana"] = prob.get("Gastroenteritis Aguda Bacteriana", 0) + math.log(1.8)
            prob["Gastroenteritis Aguda Viral"]      = prob.get("Gastroenteritis Aguda Viral", 0)      + math.log(1.5)

        # Contacto con Casos Similares
        if antecedentes.get("Contacto con Casos Similares"):
            prob["Gripe Común / Influenza"]          = prob.get("Gripe Común / Influenza", 0)          + math.log(2.5)
            prob["Varicela (Leve/Moderada)"]         = prob.get("Varicela (Leve/Moderada)", 0)         + math.log(4.0)
            prob["COVID-19"]                         = prob.get("COVID-19", 0)                         + math.log(2.5)
            prob["Resfriado Común (Rinofaringitis)"] = prob.get("Resfriado Común (Rinofaringitis)", 0) + math.log(2.0)

        # Antecedente de Litiasis Renal
        if antecedentes.get("Antecedente de Litiasis Renal"):
            prob["Pielonefritis Aguda (IVU Alta)"]   = prob.get("Pielonefritis Aguda (IVU Alta)", 0)   + math.log(3.0)

        max_log = max(prob.values())
        exp_prob = {k: math.exp(v - max_log) for k, v in prob.items()}
        return self.normalizar(exp_prob)

    def cargar_aprendizaje_clinico(self):
        try:
            from database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dbo.diagnoses WHERE phase = 'final'")
            total_casos_global = cursor.fetchone()[0] or 0
            if total_casos_global == 0:
                cursor.close()
                conn.close()
                return

            cursor.execute("""
                SELECT COALESCE(doctor_override_diagnosis, diagnosis_primary) as disease, COUNT(*) as total_cases
                FROM dbo.diagnoses WHERE phase = 'final'
                GROUP BY COALESCE(doctor_override_diagnosis, diagnosis_primary)
            """)
            counts_enfermedad = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT COALESCE(d.doctor_override_diagnosis, d.diagnosis_primary) as disease, vs.symptom_name, SUM(CAST(vs.is_present AS INT)) as present_count
                FROM dbo.diagnoses d
                JOIN dbo.visit_symptoms vs ON d.visit_id = vs.visit_id
                WHERE d.phase = 'final'
                GROUP BY COALESCE(d.doctor_override_diagnosis, d.diagnosis_primary), vs.symptom_name
            """)
            rows_sintomas = cursor.fetchall()
            counts_sintomas = {}
            for r in rows_sintomas:
                enf, sint, cant = r[0], r[1], r[2]
                if enf not in counts_sintomas:
                    counts_sintomas[enf] = {}
                counts_sintomas[enf][sint] = cant

            cursor.close()
            conn.close()

            N0_priors = 50.0
            w_prior = total_casos_global / (total_casos_global + N0_priors)
            K = len(self.enfermedades)
            alpha_laplace = 1.0
            priors_actualizados = {}
            for enf in self.enfermedades:
                p_base = self.P_enfermedad_base.get(enf, 1.0 / K)
                cant_enf = counts_enfermedad.get(enf, 0)
                p_obs = (cant_enf + alpha_laplace) / (total_casos_global + alpha_laplace * K)
                priors_actualizados[enf] = (1.0 - w_prior) * p_base + w_prior * p_obs
            self.P_enfermedad_base = priors_actualizados

            N0_sint = 10.0
            beta_laplace = 0.5
            for sint, dict_enf in self.P_sintoma.items():
                for enf in self.enfermedades:
                    cant_enf = counts_enfermedad.get(enf, 0)
                    if cant_enf > 0:
                        w_sint = cant_enf / (cant_enf + N0_sint)
                        p_s_base = dict_enf.get(enf, self.LAPLACE_ALPHA)
                        cant_sint_presente = counts_sintomas.get(enf, {}).get(sint, 0)
                        p_s_obs = (cant_sint_presente + beta_laplace) / (cant_enf + beta_laplace * 2)
                        dict_enf[enf] = (1.0 - w_sint) * p_s_base + w_sint * p_s_obs
            print(f"[Aprendizaje Bayesiano] Modelo actualizado con éxito a partir de {total_casos_global} casos.")
        except Exception as e:
            print(f"[Aprendizaje Bayesiano] Error al cargar aprendizaje clínico: {e}")

    def calcular_diagnostico_preliminar(
        self, constantes: dict, antecedentes: dict, sintomas: dict,
        priors_custom=None, conditionals_custom=None
    ):
        self.cargar_aprendizaje_clinico()
        priors      = priors_custom      if priors_custom      else self.P_enfermedad_base
        conditionals = conditionals_custom if conditionals_custom else self.P_sintoma

        prob_post_antecedentes = self.aplicar_antecedentes(priors, antecedentes)
        log_prob = {e: math.log(max(p, self.LAPLACE_ALPHA)) for e, p in prob_post_antecedentes.items()}

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

        if sintomas.get("Dolor en el Pecho") and (
            antecedentes.get("Cardiopatía") or antecedentes.get("Hipertensión Arterial (HTA)")
        ):
            if "Infarto Agudo de Miocardio (IAM)" in log_prob:
                log_prob["Infarto Agudo de Miocardio (IAM)"] += math.log(1.5)
            if "Miocarditis" in log_prob:
                log_prob["Miocarditis"] += math.log(1.2)

        max_log = max(log_prob.values())
        prob_final = {k: math.exp(v - max_log) for k, v in log_prob.items()}
        return self.normalizar(prob_final), pasos

    def calcular_diagnostico_final(self, prob_preliminar: dict, resultados_pruebas: list):
        log_prob = {e: math.log(max(p, self.LAPLACE_ALPHA)) for e, p in prob_preliminar.items()}
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


# MOTOR CLÍNICO DE IA OFFLINE
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
        if float(temp) >= 38.5:  banderas.append("⚠️ FIEBRE ALTA")
        elif float(temp) >= 37.3: banderas.append("⚠️ FEBRÍCULA")
        if float(spo2) < 92:     banderas.append("🚨 HIPOXIA SEVERA")
        elif float(spo2) < 95:   banderas.append("⚠️ HIPOXIA LEVE")
        if float(pas) >= 140 or float(pad) >= 90: banderas.append("🚨 HTA")
        elif float(pas) < 90:    banderas.append("🚨 HIPOTENSIÓN / SHOCK")
        if float(fc) > 100:      banderas.append("⚠️ TAQUICARDIA")
        if float(fr) > 20:       banderas.append("⚠️ TAQUIPNEA")

        banderas_str = " | ".join(banderas) if banderas else "Ninguna (Signos Estables)"

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
            habits_str = "\n".join([f"*   {h}" for h in meta.get("habits", [])])
            return f"Para la recuperación de **{diagnostico}**, sigue estas indicaciones:\n\n{habits_str}\n\n¿Estás en condiciones de cumplir con estas pautas?"
        elif any(w in msg for w in ["medicamento", "tomar", "pastilla", "jarabe", "receta", "antibiotico", "paracetamol"]):
            meds_str = "\n".join([f"*   {f}" for f in meta.get("medications", [])])
            return f"Respecto al soporte farmacológico para **{diagnostico}**:\n\n{meds_str}\n\n**IMPORTANTE**: Ante señales de alarma, la automedicación puede enmascarar síntomas críticos."
        elif any(w in msg for w in ["peligro", "grave", "emergencia", "alerta", "bandera", "roja"]):
            flags_str = "\n".join([f"*   **{flag}**" for flag in meta.get("red_flags", [])])
            return f"Para **{diagnostico}** (Triage: **{meta.get('alert_level', 'Verde').upper()}**), las señales de alarma que requieren traslado inmediato son:\n\n{flags_str}\n\n¿Experimentas alguno de estos signos ahora?"
        elif any(w in msg for w in ["bayes", "probabilidad", "calculo", "matematica", "como funciona"]):
            return f"El motor aplica el Teorema de Bayes secuencial: partimos de la prevalencia base de **{diagnostico}** en la población. Cada síntoma, signo vital y antecedente actúa como evidencia condicional P(S|E). Calculamos en espacio logarítmico para evitar de desbordamientos. La patología con mayor probabilidad posterior es la sugerida."
        elif any(w in msg for w in ["prueba", "analisis", "examen", "laboratorio", "estudio"]):
            tests_str = "\n".join([f"*   {t}" for t in meta.get("clinical_tests", [])])
            return f"Para confirmar o descartar **{diagnostico}**, los estudios sugeridos son:\n\n{tests_str}\n\n¿Ya realizaste alguno de estos análisis?"
        else:
            return f"Como tu médico internista, ante un diagnóstico de **{diagnostico}**, la prioridad es seguir las pautas de medicación sintomática, respetar las recomendaciones de hábitos y vigilar las señales de alarma. ¿Hay algún síntoma específico sobre el que te gustaría profundizar?"
