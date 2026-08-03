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