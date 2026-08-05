# -*- coding: utf-8 -*-
CLINICAL_METADATA = {
    "Gripe Común / Influenza": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Familiar",
        "summary": "Infección viral aguda de las vías respiratorias. Altamente contagiosa, generalmente autolimitada en pacientes sanos.",
        "clinical_tests": [
            "**Panel Viral Respiratorio (PCR)**: Positivo para Influenza A / B o SARS-CoV-2.",
            "**Hemograma Completo**: Normal (Valores de referencia estables)"
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
            "**Radiografía de Tórax**: Consolidación lobar única (Neumonía bacteriana típica).",
            "**Hemograma Completo**: Leucocitosis marcada con neutrofilia y desviación a la izquierda (Infección bacteriana).",
            "**Proteína C Reactiva (PCR)**: Elevación marcada (>40 mg/L - Alta sospecha de infección bacteriana o inflamación sistémica aguda)."
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
            "**Auscultación Pulmonar**: Roncus y sibilancias bilaterales dispersas."
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
            "**Flujometría (Peak Flow)**: Obstrucción severa / Zona roja (<50% del valor teórico).",
            "**Auscultación Pulmonar**: Sibilancias espiratorias bilaterales difusas."
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
            "**Gasometría Arterial**: Hipoxia severa / Insuficiencia respiratoria aguda (PaO2 <60 mmHg).",
            "**Radiografía de Tórax**: Hiperinsuflación pulmonar y aplanamiento diafragmático (Atrapamiento aéreo - Asma/EPOC)."
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
            "**ECG de 12 Derivaciones**: Elevación del segmento ST localizada con ondas T hiperagudas (IAM en curso).",
            "**Troponina I**: Elevación patológica franca (>0.4 ng/mL - Compatible con IAM)."
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
            "**Ecocardiograma**: Fracción de eyección disminuida FEVI <40% (Falla cardíaca sistólica).",
            "**NT-proBNP**: Elevación severa (>450 pg/mL en jóvenes / >900 pg/mL en mayores - ICC descompensada).",
            "**Radiografía de Tórax**: Infiltrados parahiliares difusos y congestión vascular."
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
            "**Resonancia Magnética Cardíaca**: Criterios de Lake Louise positivos (Edema miocárdico e hiperemia compatible con Miocarditis).",
            "**Troponina I**: Elevación patológica franca (>0.4 ng/mL - Compatible con IAM).",
            "**ECG de 12 Derivaciones**: Descenso del segmento ST / Inversión de onda T (Isquemia subendocárdica)."
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
            "**Punción Lumbar (LCR)**: Pleocitosis linfocitaria con proteínas moderadamente elevadas y glucosa normal (Encefalitis viral).",
            "**Resonancia Magnética de Cerebro**: Hiperintensidades en secuencias T2/FLAIR en lóbulos temporales (Encefalitis herpética).",
            "**Electroencefalograma (EEG)**: Actividad lenta focal temporal (Asociada a Encefalitis)."
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
            "**TC de Cráneo**: Isquemia cerebral aguda / Zona hipodensa temprana (Infarto isquémico).",
            "**Resonancia Magnética de Cerebro**: Restricción a la difusión compatible con isquemia aguda cerebral."
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
    "Migraña Común / Moderada": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Familiar / Neurología",
        "summary": "Cefalea primaria recurrente de intensidad leve a moderada, de carácter pulsátil, unilateral o bilateral, que suele ceder con analgésicos comunes.",
        "clinical_tests": [
            "**Examen Neurológico**: Completamente normal (Sin focalidad neurológica).",
            "**TC de Cráneo**: Normal (Sin alteraciones estructurales)."
        ],
        "habits": [
            "Reposo en una habitación tranquila, con luz tenue y sin ruidos.",
            "Mantener un diario de dolor para identificar desencadenantes (comidas, falta de sueño, estrés).",
            "Mantener un horario de sueño regular y una buena hidratación."
        ],
        "medications": [
            "Ibuprofeno 400mg o Paracetamol 500mg - 1g vía oral ante los primeros síntomas.",
            "Cafeína combinada con analgésicos para potenciar el efecto.",
            "**ADVERTENCIA**: Limitar el uso de analgésicos a un máximo de 2-3 días por semana para evitar cefalea de rebote."
        ],
        "red_flags": [
            "Cefalea que empeora progresivamente a lo largo de los días.",
            "Cefalea de inicio repentino e inusualmente severo (cefalea en trueno).",
            "Asociación con fiebre alta o rigidez de nuca."
        ]
    },
    "Migraña Severa": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Neurología",
        "summary": "Crisis migrañosa severa y debilitante, acompañada de intolerancia extrema a estímulos sensoriales (fotofobia/fonofobia) y vómitos incoercibles, o con presencia de aura visual.",
        "clinical_tests": [
            "**Examen Neurológico**: Completamente normal (Sin focalidad neurológica).",
            "**TC de Cráneo**: Normal (Sin alteraciones estructurales)."
        ],
        "habits": [
            "Reposo absoluto en una habitación completamente oscura, fresca y silenciosa.",
            "Colocar compresas frías sobre la frente o sienes.",
            "Evitar de forma absoluta factores desencadenantes (quesos maduros, chocolate, vino tinto)."
        ],
        "medications": [
            "Triptanos (Sumatriptán 50-100mg) al inicio de la cefalea.",
            "Antieméticos (Metoclopramida 10mg) vía oral para los vómitos y náuseas.",
            "**ADVERTENCIA**: Evitar triptanos en pacientes con antecedentes de cardiopatía isquémica o ACV."
        ],
        "red_flags": [
            "Aparición de déficit neurológico persistente posterior a la crisis.",
            "Vómitos incoercibles que impidan la hidratación oral.",
            "Cefalea que no responde a triptanos tras 24 horas."
        ]
    },
    "Dengue No Grave (Clásico)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Infectología",
        "summary": "Infección viral transmitida por el mosquito Aedes aegypti. Caracterizada por fiebre alta repentina y dolores corporales intensos.",
        "clinical_tests": [
            "**Prueba rápida de Dengue (Antígeno NS1 / IgM-IgG)**: Antígeno NS1 Positivo (Fiebre del Dengue activa).",
            "**Hemograma Completo**: Leucopenia y trombocitopenia moderada (Sospecha de virosis/dengue)"
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
            "**Hemograma Completo**: Leucopenia y trombocitopenia moderada (Sospecha de virosis/dengue)",
            "**Ecografía Abdominal**: Presencia de ascitis leve y/o derrame pleural derecho (Dengue Grave / Fuga plasmática)."
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
            "**Prueba de PCR en Sangre u Orina (Zika)**: Positiva (Fase aguda de Zika).",
            "**Hemograma Completo**: Normal (Valores de referencia estables)"
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
            "**Serología (Chikungunya IgM)**: Positiva (Infección por Chikungunya).",
            "**PCR específico (Chikungunya)**: Positiva (Detección de ARN de Chikungunya)"
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
            "**Otoscopia**: Membrana timpánica eritematosa, abombada y opaca (Otitis media aguda).",
            "**Palpación de la Mastoides**: Dolor a la palpación / Tracción leve (Sugerente de complicación de Otitis Media)."
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
            "**Otoscopia**: Conducto auditivo eritematoso, edematoso y con detritos purulentos (Otitis externa).",
            "**Signo del Trago**: Positivo unilateral severo (Dolor exquisito compatible con Otitis Externa)"
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
            "**Presión sobre Senos Paranasales**: Dolor a la presión sobre senos maxilares o frontales (Sinusitis activa).",
            "**TC de Senos Paranasales**: Oclusión del complejo ostiomeatal y niveles hidroaéreos (Sinusitis aguda)."
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
            "**Prueba rápida de Antígeno SARS-CoV-2**: Positiva franca (Alta carga de SARS-CoV-2).",
            "**PCR Nasofaríngeo**: Positivo para SARS-CoV-2."
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
            "**Radiografía de Tórax**: Infiltrados intersticiales bilaterales (Patrón atípico / Viral).",
            "**Gasometría Arterial**: Hipoxia severa / Insuficiencia respiratoria aguda (PaO2 <60 mmHg).",
            "**Dímero D**: Elevación crítica (>1000 ng/mL - Alta sospecha de TEP / Trombosis)."
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
            "**Criterios de Centor**: 0-1 puntos (Baja probabilidad, manejo sintomático).",
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
            "**Criterios de Centor**: 4-5 puntos (Alta probabilidad de origen estreptocócico).",
            "**Prueba rápida de estreptococo**: Positiva franca para Streptococcus pyogenes (Grupo A)."
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
            "**Angio-TC Pulmonar**: Defecto de llenado segmentario o subsegmentario (TEP leve/moderado).",
            "**Dímero D**: Elevación crítica (>1000 ng/mL - Alta sospecha de TEP / Trombosis).",
            "**Ecocardiograma**: Signos de sobrecarga del ventrículo derecho y aplanamiento septal (Sospecha de TEP)."
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
    "Diabetes Mellitus Tipo 2 (Controlada)": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Endocrinología / Medicina General",
        "summary": "Estado estable de diabetes en el que los niveles de glucosa se mantienen cerca del rango meta mediante estilo de vida y/o medicación.",
        "clinical_tests": [
            "**Glucosa en Ayunas**: Glucemia basal estable (<130 mg/dL en pacientes bajo tratamiento).",
            "**Hemoglobina Glicosilada (HbA1c)**: Control metabólico óptimo o aceptable (<7.0%)."
        ],
        "habits": [
            "Actividad física aeróbica regular (mínimo 150 minutos por semana).",
            "Dieta baja en carbohidratos simples y alta en fibra.",
            "Monitoreo periódico de glucosa capilar y cuidado diario de los pies."
        ],
        "medications": [
            "Metformina 850mg vía oral con la comida principal.",
            "Monitoreo y ajuste farmacológico por el médico de cabecera.",
            "**ADVERTENCIA**: Mantener adherencia terapéutica para prevenir complicaciones micro y macrovasculares crónicas."
        ],
        "red_flags": [
            "Glucemias capilares persistentemente por encima de 200 mg/dL.",
            "Aparición de hormigueo, entumecimiento o heridas en los pies.",
            "Visión borrosa de inicio reciente."
        ]
    },
    "Diabetes Mellitus Tipo 2 (Descompensada)": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Endocrinología / Medicina Interna / Urgencias",
        "summary": "Pérdida del control metabólico caracterizada por hiperglucemia marcada, poliuria, polidipsia y riesgo de crisis hiperglucémicas (cetoacidosis o estado hiperosmolar).",
        "clinical_tests": [
            "**Glucosa en Ayunas**: Hiperglucemia marcada (>200 mg/dL o en crisis >250 mg/dL).",
            "**Hemoglobina Glicosilada (HbA1c)**: Mal control metabólico (>=8.0%).",
            "**Examen General de Orina (EGO)**: Glucosuria marcada y presencia de cuerpos cetónicos (en caso de cetoacidosis)."
        ],
        "habits": [
            "Reposo físico inmediato y control horario de glucemias.",
            "Hidratación oral abundante con agua (evitar bebidas azucaradas de forma absoluta).",
            "Seguimiento médico estrecho para ajuste de insulinoterapia o fármacos orales."
        ],
        "medications": [
            "Insulinoterapia de rescate o ajuste de dosis de insulina basal/prandial según esquema médico.",
            "Reposición hídrica oral o endovenosa enérgica.",
            "**ADVERTENCIA**: La presencia de cetonuria con hiperglucemia requiere atención médica urgente."
        ],
        "red_flags": [
            "Aliento con olor frutal dulce, respiración rápida y profunda (de Kussmaul), náuseas y vómitos.",
            "Estado mental alterado, confusión, letargia o somnolencia extrema.",
            "Deshidratación severa con boca seca, ausencia de sudoración y orina escasa."
        ]
    },
    "Gastroenteritis Aguda Viral": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Gastroenterología",
        "summary": "Inflamación gastrointestinal viral (ej. Rotavirus, Norovirus) que causa diarrea líquida explosiva y vómitos. Muy contagiosa.",
        "clinical_tests": [
            "**Coprocultivo**: Negativo para bacterias enteropatógenas.",
            "**Electrólitos Séricos**: Normal (Sodio, Potasio, Cloro estables)"
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
            "**Coprocultivo**: Positivo para Salmonella enterica.",
            "**Hemograma Completo**: Leucocitosis marcada con neutrofilia y desviación a la izquierda (Infección bacteriana)."
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
            "**Examen Coproparasitológico Seriados**: Positivo para quistes de Giardia lamblia.",
            "**Prueba de Antígeno en Heces**: Positiva para Giardia lamblia."
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
            "**Examen Clínico Nasofaríngeo**: Mucosa eritematosa, edematosa con rinorrea clara (Resfriado/Virosis).",
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
            "**Examen General de Orina (EGO)**: Leucocituria moderada y nitritos positivos (Sugerente de infección).",
            "**Urocultivo**: Positivo para Escherichia coli (>100,000 UFC/mL - Infección activa)."
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
            "**Examen General de Orina (EGO)**: Leucocituria marcada, bacterias abundantes y hematuria microscópica.",
            "**Urocultivo**: Positivo para Escherichia coli (>100,000 UFC/mL - Infección activa).",
            "**Hemograma Completo**: Leucocitosis marcada con neutrofilia y desviación a la izquierda (Infección bacteriana).",
            "**Ecografía Renal**: Signos de edema renal o absceso parenquimatoso (Pielonefritis complicada)."
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
            "**Endoscopia Digestiva Alta**: Esofagitis por reflujo activa (Grados A/B).",
            "**pH-metría de 24 horas**: Confirmatorio de reflujo ácido patológico (DeMeester score >14.7)."
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
    "Gastritis Aguda Leve": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Medicina General / Gastroenterología",
        "summary": "Inflamación transitoria de la mucosa gástrica caracterizada por dispepsia, acidez y dolor epigástrico leve, frecuentemente autolimitada.",
        "clinical_tests": [
            "**Endoscopia Digestiva Alta**: Mucosa con eritema leve, sin erosiones ni sangrado activo.",
            "**Prueba para H. pylori**: Negativo o Positivo (según etiología)."
        ],
        "habits": [
            "Dieta blanda fraccionada, libre de irritantes (grasas, condimentos, cítricos, picantes).",
            "Evitar de forma absoluta el tabaco y el alcohol.",
            "No acostarse inmediatamente después de comer."
        ],
        "medications": [
            "Omeprazol 20mg diario en ayunas.",
            "Sucralfato o antiácidos orales como protector de la mucosa.",
            "**ADVERTENCIA**: No consumir medicamentos antiinflamatorios (AINEs) sin protección gástrica."
        ],
        "red_flags": [
            "Dolor epigástrico que empeora significativamente.",
            "Vómitos persistentes que impiden la alimentación.",
            "Aparición de heces oscuras."
        ]
    },
    "Gastritis Erosiva / Sangrante": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Gastroenterología",
        "summary": "Forma severa de gastritis caracterizada por erosiones en la mucosa gástrica con riesgo de hemorragia digestiva alta, manifestándose con dolor intenso y sangrado.",
        "clinical_tests": [
            "**Endoscopia Digestiva Alta**: Presencia de múltiples erosiones en la mucosa con áreas de sangrado en capa.",
            "**Hemograma Completo**: Anemia microcítica o normocítica (si hay sangrado crónico/agudo)."
        ],
        "habits": [
            "Reposo relativo y dieta líquida o blanda estricta según tolerancia.",
            "Suspensión absoluta e inmediata de alcohol, tabaco y cualquier fármaco antiinflamatorio (AINE).",
            "Evitar esfuerzos físicos intensos."
        ],
        "medications": [
            "Esomeprazol 40mg cada 12 horas vía oral o endovenoso.",
            "Sucralfato en suspensión (1g cada 6 horas) como protector local de las erosiones.",
            "**ADVERTENCIA**: Requiere valoración endoscópica oportuna para descartar sangrado activo mayor."
        ],
        "red_flags": [
            "Vómitos con sangre fresca o con aspecto de 'poso de café' (hematemesis).",
            "Heces negras, alquitranadas y fétidas (melenas).",
            "Signos de shock (palidez extrema, sudoración fría, mareo o desmayo al ponerse de pie)."
        ]
    },
    "Úlcera Péptica No Complicada": {
        "alert_level": "Amarillo",
        "color": "#f59e0b",
        "specialist": "Gastroenterología / Medicina Interna",
        "summary": "Lesión profunda en la mucosa del estómago o duodeno. Caracterizada por dolor epigástrico quemante que se alivia o empeora con la comida.",
        "clinical_tests": [
            "**Endoscopia Digestiva Alta**: Úlcera gástrica o duodenal activa sin sangrado reciente.",
            "**Prueba para H. pylori**: Positivo para Helicobacter pylori."
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
            "**Examen Clínico Visual**: Lesiones pleomórficas en diferentes estadios (máculas, pápulas, vesículas y costras - Varicela).",
            "**PCR del líquido de la vesícula**: Positivo para Virus Varicela-Zóster."
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
    },
    "Conjuntivitis Aguda": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Oftalmología / Medicina General",
        "summary": "Inflamación o infección de la conjuntiva ocular, de etiología viral, bacteriana o alérgica, caracterizada por ojo rojo y secreción.",
        "clinical_tests": [
            "**Examen Clínico Ocular**: Inyección conjuntival, presencia de secreción (purulenta o serosa) y edema palpebral.",
            "**Frotis de Secreción Ocular**: Útil en casos crónicos o severos para identificar bacterias."
        ],
        "habits": [
            "No frotarse los ojos bajo ninguna circunstancia.",
            "Limpiar las secreciones de los ojos con una gasa estéril humedecida en solución salina, usando una gasa diferente para cada ojo.",
            "Lavado de manos frecuente y no compartir toallas ni almohadas para evitar el contagio."
        ],
        "medications": [
            "Gotas oftálmicas de Tobramicina o Ciprofloxacino (1 gota cada 4 horas por 7 días en caso de sospecha bacteriana).",
            "Lágrimas artificiales para aliviar el ardor y la resequedad.",
            "**ADVERTENCIA**: Evitar el uso de gotas oftálmicas con corticoides sin indicación explícita del oftalmólogo."
        ],
        "red_flags": [
            "Dolor ocular severo o disminución de la agudeza visual (visión borrosa).",
            "Sensibilidad extrema a la luz (fotofobia severa).",
            "Falta de mejoría clínica tras 48 horas de tratamiento antibiótico."
        ]
    },
    "Síndrome Metabólico / Estrés Metabólico": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Endocrinología / Medicina Interna",
        "summary": "Conjunto de alteraciones metabólicas que aumentan el riesgo de enfermedad cardiovascular y diabetes, incluyendo obesidad abdominal, hipertensión y dislipidemia.",
        "clinical_tests": [
            "**Perfil Lipídico**: Triglicéridos elevados (>150 mg/dL) y colesterol HDL bajo (<40 mg/dL en hombres / <50 mg/dL en mujeres).",
            "**Glucosa en Ayunas**: Glucemia en ayunas alterada (100-125 mg/dL).",
            "**Presión Arterial**: Presión elevada de forma sostenida (>=130/85 mmHg)."
        ],
        "habits": [
            "Pérdida de peso gradual mediante restricción calórica moderada y saludable.",
            "Realizar al menos 150-300 minutos de ejercicio aeróbico de intensidad moderada por semana.",
            "Dieta de estilo mediterráneo (rica en vegetales, grasas saludables y pescado; baja en ultraprocesados)."
        ],
        "medications": [
            "Tratamiento dirigido a los componentes individuales (Metformina para prediabetes, estatinas para dislipidemia, antihipertensivos).",
            "Multivitamínicos o suplementación si se documentan deficiencias.",
            "**ADVERTENCIA**: El pilar fundamental de este síndrome es el cambio en el estilo de vida, no los medicamentos aislados."
        ],
        "red_flags": [
            "Aparición de dolor de pecho opresivo al realizar esfuerzos físicos.",
            "Dificultad repentina para respirar.",
            "Niveles de glucosa en ayunas superiores a 126 mg/dL en múltiples tomas."
        ]
    },
    "Ansiedad Generalizada / Trastorno de Pánico": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Psiquiatría / Psicología Clínica",
        "summary": "Trastorno caracterizado por preocupación excesiva y persistente, o crisis súbitas de miedo intenso con manifestaciones físicas como palpitaciones y disnea.",
        "clinical_tests": [
            "**Examen Físico y ECG**: Ritmo sinusal normal o taquicardia sinusal benigna (descarta causas cardíacas orgánicas).",
            "**Pruebas de Función Tiroidea (TSH)**: Normal (descarta hipertiroidismo como causa de la ansiedad)."
        ],
        "habits": [
            "Practicar técnicas de respiración diafragmática profunda y relajación muscular progresiva.",
            "Evitar estimulantes como cafeína, nicotina, alcohol y bebidas energéticas.",
            "Establecer una rutina de ejercicio físico regular y mantener buenos hábitos de sueño."
        ],
        "medications": [
            "Inhibidores Selectivos de la Recaptación de Serotonina (ISRS) como Sertralina o Escitalopram (bajo prescripción médica).",
            "Benzodiacepinas de forma transitoria y con estricto control médico para crisis agudas.",
            "**ADVERTENCIA**: Las benzodiacepinas pueden causar dependencia física y psicológica si se usan a largo plazo."
        ],
        "red_flags": [
            "Ideación suicida activa o deseos de autolesionarse.",
            "Ataques de pánico tan frecuentes que impidan realizar actividades básicas cotidianas.",
            "Dolor torácico que no cede con la relajación y se acompaña de sudoración fría (sospecha de causa cardíaca)."
        ]
    },
    "Anemia Ferropénica": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Hematología / Medicina Interna / Medicina General",
        "summary": "Disminución de la concentración de hemoglobina y glóbulos rojos debido a la deficiencia de hierro, provocando fatiga y palidez.",
        "clinical_tests": [
            "**Hemograma Completo**: Anemia microcítica hipocrómica (Hemoglobina baja, VCM <80 fL, HCM <27 pg).",
            "**Perfil de Hierro**: Ferritina sérica disminuida (<15 ng/mL - Confirmatorio de deficiencia de hierro)."
        ],
        "habits": [
            "Incrementar el consumo de alimentos ricos en hierro hemo (carnes rojas, hígado, pescado).",
            "Consumir alimentos ricos en vitamina C (cítricos) junto con alérgenos o alimentos ricos en hierro para mejorar su absorción.",
            "Evitar tomar té, café o lácteos junto con las comidas, ya que inhiben la absorción de hierro."
        ],
        "medications": [
            "Sulfato Ferroso 325mg (65mg de hierro elemental) una o dos veces al día vía oral, preferiblemente con el estómago vacío.",
            "**ADVERTENCIA**: El hierro oral puede causar efectos secundarios gastrointestinales como estreñimiento y heces oscuras."
        ],
        "red_flags": [
            "Disnea o fatiga extrema con mínimos esfuerzos cotidianos.",
            "Palpitaciones continuas o dolor de pecho.",
            "Sangrado activo evidente (menorragia masiva, sangrado digestivo)."
        ]
    },
    "Hipotiroidismo Clínico": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Endocrinología",
        "summary": "Deficiencia de hormona tiroidea caracterizada por una ralentización general de las funciones metabólicas corporales.",
        "clinical_tests": [
            "**Perfil Tiroideo (TSH y T4 Libre)**: TSH elevada (>4.5 uUI/mL) con T4 Libre disminuida (Hipotiroidismo establecido).",
            "**Anticuerpos Anti-TPO**: Elevados en caso de sospecha de Tiroiditis de Hashimoto."
        ],
        "habits": [
            "Tomar la hormona tiroidea estrictamente en ayunas, al menos 30 a 60 minutos antes del desayuno.",
            "Mantener una dieta rica en fibra para combatir el estreñimiento crónico.",
            "Realizar ejercicio regular para mejorar los niveles de energía y el estado de ánimo."
        ],
        "medications": [
            "Levotiroxina sódica vía oral en dosis ajustadas individualmente por el endocrinólogo (generalmente comenzando con 25-50 mcg/día).",
            "**ADVERTENCIA**: No cambiar de marca comercial de Levotiroxina sin consultar al médico, debido a variaciones de biodisponibilidad."
        ],
        "red_flags": [
            "Aparición de hinchazón generalizada marcada, somnolencia extrema y lentitud mental severa (sospecha de coma mixedematoso).",
            "Frecuencia cardíaca extremadamente baja (<50 bpm) con mareos o desmayos.",
            "Aparición de dolor torácico tras iniciar el tratamiento con Levotiroxina."
        ]
    },
    "Lumbalgia Mecánica": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Traumatología / Fisiatría / Medicina General",
        "summary": "Dolor localizado en la región lumbar baja de etiología musculoesquelética, agravado por el movimiento y aliviado por el reposo.",
        "clinical_tests": [
            "**Examen Físico (Prueba de Laségue)**: Negativa (Descarta compresión radicular aguda de tipo ciática).",
            "**Radiografía de Columna Lumbar**: Descarte de fracturas o listesis, puede mostrar signos leves de artrosis."
        ],
        "habits": [
            "Evitar el reposo en cama prolongado (no más de 48 horas); mantenerse activo dentro de los límites del dolor.",
            "Aplicar calor local seco durante 15-20 minutos, 3 veces al día en la zona dolorosa.",
            "Adoptar posturas correctas al sentarse, agacharse (doblar rodillas) y levantar objetos pesados."
        ],
        "medications": [
            "AINEs (Ibuprofeno 400mg cada 8 horas o Naproxeno 250-500mg cada 12 horas) por un máximo de 5-7 días.",
            "Relajantes musculares (Ciclobenzaprina 5-10mg antes de dormir) si hay espasmo muscular evidente.",
            "**ADVERTENCIA**: El uso de fajas lumbares por períodos prolongados debilita la musculatura estabilizadora del torso."
        ],
        "red_flags": [
            "Pérdida súbita de la fuerza en las piernas o dificultad para caminar.",
            "Pérdida del control de los esfínteres (incontinencia urinaria o fecal - Síndrome de Cola de Caballo).",
            "Dolor lumbar persistente que no mejora en reposo, de predominio nocturno y acompañado de fiebre."
        ]
    },
    "Rinitis Alérgica": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Alergología / Otorrinolaringología / Medicina General",
        "summary": "Reacción inflamatoria de la mucosa nasal mediada por IgE tras la exposición a alérgenos como polvo, polen o pelo de animales.",
        "clinical_tests": [
            "**Examen Clínico Nasal (Rinoscopia)**: Mucosa nasal pálida, edematosa, con presencia de rinorrea acuosa abundante.",
            "**Pruebas Cutáneas (Prick Test)**: Identificación de alérgenos causales específicos."
        ],
        "habits": [
            "Minimizar la exposición a alérgenos conocidos (evitar alfombras, usar fundas antiácaros, ventilar la habitación).",
            "Realizar lavados nasales diarios con solución salina para remover alérgenos físicamente.",
            "Evitar el contacto directo con mascotas si se documenta alergia a su epitelio."
        ],
        "medications": [
            "Antihistamínicos orales de segunda generación (Loratadina 10mg o Cetirizina 10mg una vez al día) para estornudos y prurito.",
            "Corticoides nasales en spray (Fluticasona o Mometasona) una aplicación en cada fosa nasal diariamente.",
            "**ADVERTENCIA**: Los descongestionantes nasales tópicos (Oximetazolina) no deben usarse por más de 3-5 días por riesgo de rinitis medicamentosa."
        ],
        "red_flags": [
            "Aparición de dificultad severa para respirar o sibilancias (asociación con crisis asmática).",
            "Dolor facial severo, fiebre y secreción nasal espesa y purulenta unilateral (sospecha de sinusitis bacteriana secundaria).",
            "Sangrado nasal recurrente y abundante (epistaxis)."
        ]
    },
    "Dermatitis Atópica": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Dermatología / Pediatría / Medicina General",
        "summary": "Trastorno cutáneo inflamatorio crónico y pruriginoso, común en pacientes con antecedentes de atopia (asma, rinitis), caracterizado por eczema.",
        "clinical_tests": [
            "**Examen Clínico Dermatológico**: Placas eritematosas, secas y descamativas localizadas principalmente en pliegues flexurales (codos, rodillas).",
            "**Determinación de IgE Sérica**: Frecuentemente elevada en pacientes atópicos."
        ],
        "habits": [
            "Mantener la piel profundamente hidratada aplicando cremas emolientes sin perfume inmediatamente después del baño.",
            "Tomar baños cortos (5-10 minutos) con agua templada y jabones syndet (sin detergentes artificiales).",
            "Usar ropa de algodón holgada y evitar tejidos sintéticos o lana."
        ],
        "medications": [
            "Corticoides tópicos de baja o moderada potencia (Hidrocortisona al 1% o Mometasona) aplicados en las placas activas por períodos cortos.",
            "Antihistamínicos orales para el control del prurito intenso, especialmente por las noches.",
            "**ADVERTENCIA**: El uso prolongado de corticoides tópicos potentes puede causar atrofia cutánea."
        ],
        "red_flags": [
            "Aparición de costras melicéricas (color miel), pus o enrojecimiento que se extiende rápidamente (sospecha de sobreinfección bacteriana por Staphylococcus aureus).",
            "Prurito intratable que interrumpe de forma grave el sueño cotidiano.",
            "Erupción vesicular dolorosa diseminada."
        ]
    },
    "Reflujo Laringofaríngeo": {
        "alert_level": "Verde",
        "color": "#10b981",
        "specialist": "Otorrinolaringología / Gastroenterología",
        "summary": "Retorno del contenido gástrico hacia la laringe y faringe, causando irritación en las vías aéreas superiores sin necesariamente causar pirosis.",
        "clinical_tests": [
            "**Laringoscopia Directa/Indirecta**: Eritema interaritenoideo, edema de cuerdas vocales (sugerente de reflujo ácido local).",
            "**pH-metría de doble canal de 24 horas**: Confirmación de reflujo laringofaríngeo ácido."
        ],
        "habits": [
            "Evitar comer al menos 3 horas antes de acostarse.",
            "Fraccionar las comidas en porciones pequeñas a lo largo del día.",
            "Evitar alimentos que relajen el esfínter esofágico inferior (café, menta, alcohol, grasas y cítricos)."
        ],
        "medications": [
            "Inhibidores de la bomba de protones (Esomeprazol 40mg o Pantoprazol 40mg) en dosis doble (antes del desayuno y antes de la cena) por 8 a 12 semanas.",
            "Procinéticos (Itoprida o Domperidona) antes de las comidas principales.",
            "**ADVERTENCIA**: Esta patología requiere tratamientos más prolongados que el reflujo gastroesofágico típico."
        ],
        "red_flags": [
            "Dificultad progresiva para tragar alimentos sólidos o líquidos (disfagia).",
            "Pérdida de peso significativa involuntaria.",
            "Tos con sangre o cambios persistentes en la voz que no mejoran tras 4-6 semanas de tratamiento."
        ]
    }
}