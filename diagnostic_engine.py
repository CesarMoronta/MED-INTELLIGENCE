# -*- coding: utf-8 -*-
import time
import math
import copy

from clinical_metadata import CLINICAL_METADATA


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
                "Negativo": {"Gripe Común / Influenza": 0.02, "COVID-19": 0.02, "COVID-19 Grave": 0.02, "Resfriado Común (Rinofaringitis)": 0.40},
                "Positivo para Influenza A / B": {"Gripe Común / Influenza": 0.98, "COVID-19": 0.00, "Resfriado Común (Rinofaringitis)": 0.01},
                "Positivo para SARS-CoV-2 (COVID-19)": {"COVID-19": 0.98, "COVID-19 Grave": 0.98, "Gripe Común / Influenza": 0.00},
                "Positivo para Virus Sincitial Respiratorio (VSR)": {"Bronquitis Aguda": 0.35, "Resfriado Común (Rinofaringitis)": 0.15},
                "Positivo para Adenovirus / Co-infección viral": {"Resfriado Común (Rinofaringitis)": 0.20, "Faringoamigdalitis Viral": 0.45}
            },
            "Hemograma Completo": {
                "Normal (Valores de referencia estables)": {"Gripe Común / Influenza": 0.75, "Migraña Severa": 0.98, "Resfriado Común (Rinofaringitis)": 0.85, "Reflujo Gastroesofágico (ERGE)": 0.95, "Cistitis Aguda (IVU Baja)": 0.80},
                "Leucocitosis leve con linfocitosis (Infección viral)": {"Gripe Común / Influenza": 0.20, "Faringoamigdalitis Viral": 0.45, "Bronquitis Aguda": 0.30, "COVID-19": 0.40},
                "Leucocitosis marcada con neutrofilia y desviación a la izquierda (Infección bacteriana)": {"Neumonía": 0.92, "Bronquitis Aguda": 0.55, "Faringoamigdalitis Estreptocócica": 0.85, "Pielonefritis Aguda (IVU Alta)": 0.90, "Gastroenteritis Aguda Bacteriana": 0.82},
                "Leucopenia y trombocitopenia moderada (Sospecha de virosis/dengue)": {"Dengue No Grave (Clásico)": 0.90, "Fiebre Zika": 0.50, "COVID-19": 0.30},
                "Trombocitopenia severa <100,000/mm³ y hemoconcentración Hct >20% (Dengue Grave)": {"Dengue Grave": 0.97, "Dengue No Grave (Clásico)": 0.08},
                "Anemia microcítica hipocrómica (Deficiencia de hierro / Pérdida crónica)": {"Úlcera Péptica No Complicada": 0.35, "Gastritis Aguda": 0.15}
            },
            "Glucosa en Ayunas": {
                "Normal en adulto sano (70-99 mg/dL)": {"Diabetes Mellitus Tipo 2": 0.01},
                "Normal ajustado por edad/gestación": {"Diabetes Mellitus Tipo 2": 0.02},
                "Hipoglucemia clínica (<70 mg/dL)": {"Diabetes Mellitus Tipo 2": 0.01},
                "Hipoglucemia severa (<55 mg/dL)": {"Diabetes Mellitus Tipo 2": 0.00},
                "Glucemia basal alterada / Prediabetes (100-125 mg/dL)": {"Diabetes Mellitus Tipo 2": 0.35},
                "Hiperglucemia clínica compatible con Diabetes (>=126 mg/dL)": {"Diabetes Mellitus Tipo 2": 0.98},
                "Hiperglucemia severa en crisis (>250 mg/dL)": {"Diabetes Mellitus Tipo 2": 0.60}
            },
            "Hemoglobina Glicosilada (HbA1c)": {
                "Normal (<5.7%)": {"Diabetes Mellitus Tipo 2": 0.02},
                "Rango de prediabetes (5.7% - 6.4%)": {"Diabetes Mellitus Tipo 2": 0.40},
                "Diabetes Mellitus establecida (>=6.5%)": {"Diabetes Mellitus Tipo 2": 0.97},
                "Diabetes con mal control metabólico (>=8.0%)": {"Diabetes Mellitus Tipo 2": 0.70}
            },
            "Radiografía de Tórax": {
                "Normal (Campos pulmonares libres)": {"Bronquitis Aguda": 0.75, "Gripe Común / Influenza": 0.70, "Crisis Asmática Aguda": 0.70, "Resfriado Común (Rinofaringitis)": 0.95, "Reflujo Gastroesofágico (ERGE)": 0.98, "Neumonía": 0.05},
                "Consolidación lobar única (Neumonía bacteriana típica)": {"Neumonía": 0.95, "Bronquitis Aguda": 0.01},
                "Infiltrados intersticiales bilaterales (Patrón atípico / Viral)": {"COVID-19": 0.80, "COVID-19 Grave": 0.90, "Neumonía": 0.50},
                "Infiltrados parahiliares difusos y congestión vascular": {"Insuficiencia Cardíaca Congestiva (ICC)": 0.85, "Neumonía": 0.15},
                "Hiperinsuflación pulmonar y aplanamiento diafragmático (Atrapamiento aéreo - Asma/EPOC)": {"Crisis Asmática Aguda": 0.85, "Exacerbación Aguda de EPOC": 0.90},
                "Atelectasia segmentaria": {"Bronquitis Aguda": 0.08, "Neumonía": 0.12}
            },
            "Antígeno NS1 (Dengue)": {
                "Negativo": {"Dengue No Grave (Clásico)": 0.05, "Dengue Grave": 0.05},
                "Positivo débil (Fase inicial de viremia)": {"Dengue No Grave (Clásico)": 0.60, "Dengue Grave": 0.40},
                "Positivo fuerte (Confirmatorio de Dengue agudo)": {"Dengue No Grave (Clásico)": 0.98, "Dengue Grave": 0.98}
            },
            "Troponina I": {
                "Normal (<0.04 ng/mL)": {"Infarto Agudo de Miocardio (IAM)": 0.02, "Miocarditis": 0.20},
                "Elevación limítrofe (0.04 - 0.4 ng/mL - Daño miocárdico leve)": {"Miocarditis": 0.60, "Infarto Agudo de Miocardio (IAM)": 0.15, "Insuficiencia Cardíaca Congestiva (ICC)": 0.30},
                "Elevación patológica franca (>0.4 ng/mL - Compatible con IAM)": {"Infarto Agudo de Miocardio (IAM)": 0.98, "Miocarditis": 0.40}
            },
            "ECG de 12 Derivaciones": {
                "Normal (Ritmo sinusal, eje normal)": {"Infarto Agudo de Miocardio (IAM)": 0.03, "Migraña Severa": 0.95},
                "Taquicardia sinusal inespecífica": {"Crisis Asmática Aguda": 0.40, "Gripe Común / Influenza": 0.30, "Miocarditis": 0.35, "Tromboembolismo Pulmonar": 0.50},
                "Elevación difusa del segmento ST con concavidad superior (Sugerente de Miocarditis)": {"Miocarditis": 0.92, "Infarto Agudo de Miocardio (IAM)": 0.05},
                "Elevación del segmento ST localizada con ondas T hiperagudas (IAM en curso)": {"Infarto Agudo de Miocardio (IAM)": 0.95, "Miocarditis": 0.01},
                "Descenso del segmento ST / Inversión de onda T (Isquemia subendocárdica)": {"Infarto Agudo de Miocardio (IAM)": 0.60, "Miocarditis": 0.50, "Insuficiencia Cardíaca Congestiva (ICC)": 0.40},
                "Bloqueo de rama izquierda de nueva aparición": {"Infarto Agudo de Miocardio (IAM)": 0.88},
                "Signo S1Q3T3 y taquicardia (Sobrecarga de ventrículo derecho - TEP)": {"Tromboembolismo Pulmonar": 0.90, "Crisis Asmática Aguda": 0.05}
            },
            "Dímero D": {
                "Normal (<500 ng/mL)": {"Tromboembolismo Pulmonar": 0.02, "COVID-19 Grave": 0.10},
                "Elevación moderada (500 - 1000 ng/mL - Inespecífico)": {"COVID-19 Grave": 0.60, "Tromboembolismo Pulmonar": 0.30, "Dengue Grave": 0.40},
                "Elevación crítica (>1000 ng/mL - Alta sospecha de TEP / Trombosis)": {"Tromboembolismo Pulmonar": 0.95, "COVID-19 Grave": 0.50, "Dengue Grave": 0.35}
            },
            "Punción Lumbar (LCR)": {
                "Normal (Líquido claro, presión normal)": {"Encefalitis": 0.03, "Migraña Severa": 0.90},
                "Pleocitosis linfocitaria con proteínas moderadamente elevadas y glucosa normal (Encefalitis viral)": {"Encefalitis": 0.95, "Accidente Cerebrovascular (ACV)": 0.02},
                "Pleocitosis neutrofílica con hiperproteinorraquia e hipoglucorraquia (Meningitis bacteriana)": {"Encefalitis": 0.20},
                "Líquido hemático / Xantocrómico (Hemorragia subaracnoidea)": {"Accidente Cerebrovascular (ACV)": 0.35, "Encefalitis": 0.01}
            },
            "TC de Cráneo": {
                "Normal (Sin alteraciones estructurales)": {"Migraña Severa": 0.99, "Accidente Cerebrovascular (ACV)": 0.10, "Encefalitis": 0.45},
                "Isquemia cerebral aguda / Zona hipodensa temprana (Infarto isquémico)": {"Accidente Cerebrovascular (ACV)": 0.60, "Migraña Severa": 0.00},
                "Hemorragia intraparenquimatosa o subaracnoidea aguda (Foco hiperdenso)": {"Accidente Cerebrovascular (ACV)": 0.38, "Migraña Severa": 0.00},
                "Edema cerebral difuso / Pérdida de surcos (Encefalitis severa)": {"Encefalitis": 0.50, "Accidente Cerebrovascular (ACV)": 0.05, "Migraña Severa": 0.00},
                "Efecto de masa con desviación de línea media": {"Encefalitis": 0.20, "Accidente Cerebrovascular (ACV)": 0.12, "Migraña Severa": 0.00}
            },
            "Flujometría (Peak Flow)": {
                "Normal / Zona verde (>=80% del valor teórico)": {"Crisis Asmática Aguda": 0.05, "Exacerbación Aguda de EPOC": 0.15},
                "Limitación moderada / Zona amarilla (50% - 79% del valor teórico)": {"Crisis Asmática Aguda": 0.65, "Exacerbación Aguda de EPOC": 0.55},
                "Obstrucción severa / Zona roja (<50% del valor teórico)": {"Crisis Asmática Aguda": 0.90, "Exacerbación Aguda de EPOC": 0.70}
            },
            "Otoscopia": {
                "Normal (Conducto despejado, tímpano translúcido)": {"Otitis Media Aguda": 0.03, "Otitis Externa Aguda": 0.04},
                "Conducto auditivo eritematoso, edematoso y con detritos purulentos (Otitis externa)": {"Otitis Externa Aguda": 0.95, "Otitis Media Aguda": 0.08},
                "Membrana timpánica eritematosa, abombada y opaca (Otitis media aguda)": {"Otitis Media Aguda": 0.96, "Otitis Externa Aguda": 0.02},
                "Perforación timpánica con otorrea activa": {"Otitis Media Aguda": 0.40, "Otitis Externa Aguda": 0.05}
            },
            "TC de Senos Paranasales": {
                "Normal (Senos aireados)": {"Sinusitis Aguda": 0.04},
                "Engrosamiento mucoso leve inespecífico": {"Sinusitis Aguda": 0.35},
                "Oclusión del complejo ostiomeatal y niveles hidroaéreos (Sinusitis aguda)": {"Sinusitis Aguda": 0.98}
            },
            "Gasometría Arterial": {
                "Normal (pH, PaO2 y PaCO2 en rangos estables)": {"Gripe Común / Influenza": 0.85, "Migraña Severa": 0.98},
                "Hipoxia leve sin hipercapnia (PaO2 60-79 mmHg)": {"Exacerbación Aguda de EPOC": 0.40, "COVID-19 Grave": 0.25, "Tromboembolismo Pulmonar": 0.35},
                "Hipoxia severa / Insuficiencia respiratoria aguda (PaO2 <60 mmHg)": {"COVID-19 Grave": 0.90, "Exacerbación Aguda de EPOC": 0.82, "Tromboembolismo Pulmonar": 0.85},
                "Acidosis respiratoria compensada (Retención de CO2)": {"Exacerbación Aguda de EPOC": 0.70, "Crisis Asmática Aguda": 0.25}
            },
            "NT-proBNP": {
                "Normal (<125 pg/mL)": {"Insuficiencia Cardíaca Congestiva (ICC)": 0.02, "Miocarditis": 0.15},
                "Elevación moderada (125 - 450 pg/mL - Compensado)": {"Miocarditis": 0.58, "Insuficiencia Cardíaca Congestiva (ICC)": 0.40},
                "Elevación severa (>450 pg/mL en jóvenes / >900 pg/mL en mayores - ICC descompensada)": {"Insuficiencia Cardíaca Congestiva (ICC)": 0.96, "Miocarditis": 0.35}
            },
            "Prueba rápida de estreptococo": {
                "Negativa": {"Faringoamigdalitis Estreptocócica": 0.04, "Faringoamigdalitis Viral": 0.96},
                "Positiva débil": {"Faringoamigdalitis Estreptocócica": 0.50, "Faringoamigdalitis Viral": 0.08},
                "Positiva franca para Streptococcus pyogenes (Grupo A)": {"Faringoamigdalitis Estreptocócica": 0.98, "Faringoamigdalitis Viral": 0.01}
            },
            "Angio-TC Pulmonar": {
                "Normal (Árbol arterial pulmonar permeable)": {"Tromboembolismo Pulmonar": 0.02},
                "Defecto de llenado segmentario o subsegmentario (TEP leve/moderado)": {"Tromboembolismo Pulmonar": 0.60},
                "Defecto de llenado masivo / Arterias principales (TEP severo / de alto riesgo)": {"Tromboembolismo Pulmonar": 0.98}
            },
            "Examen General de Orina (EGO)": {
                "Normal (Clara, sin sedimentos patológicos)": {"Cistitis Aguda (IVU Baja)": 0.03, "Pielonefritis Aguda (IVU Alta)": 0.02, "Diabetes Mellitus Tipo 2": 0.50},
                "Glucosuria aislada (sin signos de infección)": {"Diabetes Mellitus Tipo 2": 0.85, "Cistitis Aguda (IVU Baja)": 0.05},
                "Microalbuminuria o proteinuria leve": {"Diabetes Mellitus Tipo 2": 0.45, "Pielonefritis Aguda (IVU Alta)": 0.15},
                "Leucocituria moderada y nitritos positivos (Sugerente de infección)": {"Cistitis Aguda (IVU Baja)": 0.88, "Pielonefritis Aguda (IVU Alta)": 0.70},
                "Leucocituria marcada, bacterias abundantes y hematuria microscópica": {"Cistitis Aguda (IVU Baja)": 0.96, "Pielonefritis Aguda (IVU Alta)": 0.92}
            },
            "Endoscopia Digestiva Alta": {
                "Mucosa gástrica y esofágica normal": {"Reflujo Gastroesofágico (ERGE)": 0.10, "Gastritis Aguda": 0.05, "Úlcera Péptica No Complicada": 0.03},
                "Esofagitis por reflujo activa (Grados A/B)": {"Reflujo Gastroesofágico (ERGE)": 0.92},
                "Gastritis eritematosa antral (Asociada a Helicobacter pylori)": {"Gastritis Aguda": 0.88, "Úlcera Péptica No Complicada": 0.40, "Reflujo Gastroesofágico (ERGE)": 0.12},
                "Gastritis erosiva difusa con sangrado en capa": {"Gastritis Aguda": 0.75, "Úlcera Péptica No Complicada": 0.25},
                "Úlcera gástrica o duodenal activa sin sangrado reciente": {"Úlcera Péptica No Complicada": 0.98, "Gastritis Aguda": 0.15},
                "Estenosis o esófago de Barrett": {"Reflujo Gastroesofágico (ERGE)": 0.20}
            },
            "Urocultivo": {
                "Negativo (Sin desarrollo bacteriano)": {"Cistitis Aguda (IVU Baja)": 0.03, "Pielonefritis Aguda (IVU Alta)": 0.02},
                "Contaminación de muestra (<10,000 UFC/mL - Flora mixta)": {"Cistitis Aguda (IVU Baja)": 0.10, "Pielonefritis Aguda (IVU Alta)": 0.08},
                "Positivo para Escherichia coli (>100,000 UFC/mL - Infección activa)": {"Cistitis Aguda (IVU Baja)": 0.85, "Pielonefritis Aguda (IVU Alta)": 0.85},
                "Positivo para Klebsiella pneumoniae (>100,000 UFC/mL)": {"Cistitis Aguda (IVU Baja)": 0.65, "Pielonefritis Aguda (IVU Alta)": 0.70},
                "Positivo para Proteus mirabilis (>100,000 UFC/mL - Orina alcalina)": {"Cistitis Aguda (IVU Baja)": 0.50, "Pielonefritis Aguda (IVU Alta)": 0.55},
                "Bacteriuria significativa de otras especies (10,000 - 100,000 UFC/mL)": {"Cistitis Aguda (IVU Baja)": 0.40, "Pielonefritis Aguda (IVU Alta)": 0.45}
            },
            "Examen Neurológico": {
                "Completamente normal (Sin focalidad neurológica)": {"Migraña Severa": 0.99, "Encefalitis": 0.05, "Accidente Cerebrovascular (ACV)": 0.08},
                "Déficit motor o sensitivo focal agudo (Sospecha de ACV)": {"Accidente Cerebrovascular (ACV)": 0.95, "Encefalitis": 0.20, "Migraña Severa": 0.01},
                "Alteración del estado mental, desorientación o confusión (Encefalitis/Delirium)": {"Encefalitis": 0.90, "Accidente Cerebrovascular (ACV)": 0.40, "Migraña Severa": 0.01},
                "Signos meníngeos presentes (Rigidez de nuca, Kerning/Brudzinski)": {"Encefalitis": 0.80, "Accidente Cerebrovascular (ACV)": 0.02, "Migraña Severa": 0.00},
                "Alteración de pares craneales aislada": {"Accidente Cerebrovascular (ACV)": 0.35, "Encefalitis": 0.15}
            },
            "Coprocultivo": {
                "Negativo para bacterias enteropatógenas": {"Gastroenteritis Aguda Viral": 0.99, "Gastroenteritis Aguda Parasitaria": 0.95, "Gastroenteritis Aguda Bacteriana": 0.12},
                "Positivo para Salmonella enterica": {"Gastroenteritis Aguda Bacteriana": 0.80, "Gastroenteritis Aguda Viral": 0.00},
                "Positivo para Shigella dysenteriae (Disentería bacilar)": {"Gastroenteritis Aguda Bacteriana": 0.85, "Gastroenteritis Aguda Viral": 0.00},
                "Positivo para Campylobacter jejuni": {"Gastroenteritis Aguda Bacteriana": 0.78, "Gastroenteritis Aguda Viral": 0.00}
            },
            "Examen Coproparasitológico Seriados": {
                "Negativo (No se observan parásitos)": {"Gastroenteritis Aguda Viral": 0.98, "Gastroenteritis Aguda Bacteriana": 0.95, "Gastroenteritis Aguda Parasitaria": 0.15},
                "Positivo para quistes de Giardia lamblia": {"Gastroenteritis Aguda Parasitaria": 0.92, "Gastroenteritis Aguda Viral": 0.00},
                "Positivo para trofozoítos de Entamoeba histolytica": {"Gastroenteritis Aguda Parasitaria": 0.88, "Gastroenteritis Aguda Viral": 0.00},
                "Presencia de huevos de helmintos": {"Gastroenteritis Aguda Parasitaria": 0.70, "Gastroenteritis Aguda Viral": 0.00}
            },
            "Electrólitos Séricos": {
                "Normal (Sodio, Potasio, Cloro estables)": {"Gastroenteritis Aguda Viral": 0.65, "Gastroenteritis Aguda Bacteriana": 0.50, "Gastroenteritis Aguda Parasitaria": 0.75, "Migraña Severa": 0.99},
                "Hipopotasemia leve o moderada (Potasio 3.0 - 3.4 mEq/L)": {"Gastroenteritis Aguda Bacteriana": 0.38, "Gastroenteritis Aguda Viral": 0.28, "Gastroenteritis Aguda Parasitaria": 0.20},
                "Hipopotasemia severa (Potasio <3.0 mEq/L)": {"Gastroenteritis Aguda Bacteriana": 0.52, "Gastroenteritis Aguda Viral": 0.42, "Gastroenteritis Aguda Parasitaria": 0.12},
                "Hiponatremia dilucional (Sodio <135 mEq/L)": {"Gastroenteritis Aguda Bacteriana": 0.20, "Gastroenteritis Aguda Viral": 0.18}
            },
            "Ecografía Renal": {
                "Normal (Siluetas renales conservadas)": {"Cistitis Aguda (IVU Baja)": 0.95, "Pielonefritis Aguda (IVU Alta)": 0.22},
                "Ectasia piélica o hidronefrosis leve sin obstrucción litiásica": {"Pielonefritis Aguda (IVU Alta)": 0.45, "Cistitis Aguda (IVU Baja)": 0.08},
                "Signos de edema renal o absceso parenquimatoso (Pielonefritis complicada)": {"Pielonefritis Aguda (IVU Alta)": 0.88, "Cistitis Aguda (IVU Baja)": 0.02},
                "Litiasis renal con sombra acústica posterior": {"Pielonefritis Aguda (IVU Alta)": 0.30, "Cistitis Aguda (IVU Baja)": 0.10}
            },
            "Electroencefalograma (EEG)": {
                "Normal (Actividad de fondo organizada)": {"Migraña Severa": 0.98, "Encefalitis": 0.15, "Accidente Cerebrovascular (ACV)": 0.80},
                "Actividad lenta focal temporal (Asociada a Encefalitis)": {"Encefalitis": 0.90, "Accidente Cerebrovascular (ACV)": 0.15},
                "Actividad lenta difusa inespecífica": {"Encefalitis": 0.65, "Accidente Cerebrovascular (ACV)": 0.35, "Migraña Severa": 0.05},
                "Descargas epileptiformes paroxísticas": {"Encefalitis": 0.50, "Accidente Cerebrovascular (ACV)": 0.18, "Migraña Severa": 0.01}
            },
            "Resonancia Magnética de Cerebro": {
                "Normal (Sin áreas de restricción a la difusión)": {"Migraña Severa": 0.99, "Encefalitis": 0.05, "Accidente Cerebrovascular (ACV)": 0.02},
                "Hiperintensidades en secuencias T2/FLAIR en lóbulos temporales (Encefalitis herpética)": {"Encefalitis": 0.96, "Accidente Cerebrovascular (ACV)": 0.01},
                "Restricción a la difusión compatible con isquemia aguda cerebral": {"Accidente Cerebrovascular (ACV)": 0.98, "Encefalitis": 0.02},
                "Foco de hemorragia aguda lobar": {"Accidente Cerebrovascular (ACV)": 0.95, "Encefalitis": 0.01}
            },
            "Prueba de PCR en Sangre u Orina (Zika)": {
                "Negativa": {"Fiebre Zika": 0.02},
                "Positiva (Fase aguda de Zika)": {"Fiebre Zika": 0.98}
            },
            "Serología (Chikungunya IgM)": {
                "Negativa": {"Fiebre Chikungunya": 0.02},
                "Positiva (Infección por Chikungunya)": {"Fiebre Chikungunya": 0.98}
            },
            "PCR específico (Chikungunya)": {
                "Negativa": {"Fiebre Chikungunya": 0.02},
                "Positiva (Detección de ARN de Chikungunya)": {"Fiebre Chikungunya": 0.98}
            },
            "Prueba rápida de Antígeno SARS-CoV-2": {
                "Negativa": {"COVID-19": 0.04, "COVID-19 Grave": 0.04},
                "Positiva débil (Carga viral baja)": {"COVID-19": 0.85, "COVID-19 Grave": 0.70},
                "Positiva franca (Alta carga de SARS-CoV-2)": {"COVID-19": 0.96, "COVID-19 Grave": 0.98}
            },
            "PCR Nasofaríngeo": {
                "Negativo": {"COVID-19": 0.01, "COVID-19 Grave": 0.01},
                "Positivo para SARS-CoV-2": {"COVID-19": 0.99, "COVID-19 Grave": 0.99}
            },
            "Prueba rápida de Dengue (Antígeno NS1 / IgM-IgG)": {
                "Negativa": {"Dengue No Grave (Clásico)": 0.04, "Dengue Grave": 0.04},
                "Antígeno NS1 Positivo (Fiebre del Dengue activa)": {"Dengue No Grave (Clásico)": 0.95, "Dengue Grave": 0.95},
                "Anticuerpos IgM Positivos (Infección reciente)": {"Dengue No Grave (Clásico)": 0.90, "Dengue Grave": 0.88},
                "Anticuerpos IgG e IgM Positivos (Re-infección o fase tardía)": {"Dengue No Grave (Clásico)": 0.96, "Dengue Grave": 0.96}
            },
            "Signo del Trago": {
                "Negativo (Sin dolor al tacto)": {"Otitis Externa Aguda": 0.04, "Otitis Media Aguda": 0.85},
                "Positivo bilateral leve": {"Otitis Externa Aguda": 0.35, "Otitis Media Aguda": 0.25},
                "Positivo unilateral severo (Dolor exquisito compatible con Otitis Externa)": {"Otitis Externa Aguda": 0.98, "Otitis Media Aguda": 0.10}
            },
            "Palpación de la Mastoides": {
                "Sin dolor a la presión": {"Otitis Media Aguda": 0.12},
                "Dolor a la palpación / Tracción leve (Sugerente de complicación de Otitis Media)": {"Otitis Media Aguda": 0.95}
            },
            "Presión sobre Senos Paranasales": {
                "Sin dolor a la presión": {"Sinusitis Aguda": 0.06},
                "Dolor a la presión sobre senos maxilares o frontales (Sinusitis activa)": {"Sinusitis Aguda": 0.98}
            },
            "Examen Clínico Nasofaríngeo": {
                "Normal (Mucosa rosada y húmeda)": {"Resfriado Común (Rinofaringitis)": 0.05, "Gripe Común / Influenza": 0.45},
                "Mucosa eritematosa, edematosa con rinorrea clara (Resfriado/Virosis)": {"Resfriado Común (Rinofaringitis)": 0.96, "Gripe Común / Influenza": 0.65},
                "Hipertrofia de cornetes y secreción mucopurulenta": {"Sinusitis Aguda": 0.88, "Resfriado Común (Rinofaringitis)": 0.20}
            },
            "Examen Clínico Visual": {
                "Piel limpia, sin lesiones activas": {"Varicela (Leve/Moderada)": 0.01, "Fiebre Zika": 0.40},
                "Lesiones pleomórficas en diferentes estadios (máculas, pápulas, vesículas y costras - Varicela)": {"Varicela (Leve/Moderada)": 0.99},
                "Rash eritematoso difuso no vesicular": {"Fiebre Zika": 0.92, "Dengue No Grave (Clásico)": 0.50}
            },
            "PCR del líquido de la vesícula": {
                "Negativo": {"Varicela (Leve/Moderada)": 0.02},
                "Positivo para Virus Varicela-Zóster": {"Varicela (Leve/Moderada)": 0.98}
            },
            "Criterios de Centor": {
                "0-1 puntos (Baja probabilidad, manejo sintomático)": {"Faringoamigdalitis Viral": 0.90, "Faringoamigdalitis Estreptocócica": 0.05},
                "2-3 puntos (Probabilidad intermedia, requiere prueba rápida)": {"Faringoamigdalitis Estreptocócica": 0.45, "Faringoamigdalitis Viral": 0.40},
                "4-5 puntos (Alta probabilidad de origen estreptocócico)": {"Faringoamigdalitis Estreptocócica": 0.90, "Faringoamigdalitis Viral": 0.05}
            },
            "pH-metría de 24 horas": {
                "Normal (Exposición ácida fisiológica)": {"Reflujo Gastroesofágico (ERGE)": 0.04},
                "Confirmatorio de reflujo ácido patológico (DeMeester score >14.7)": {"Reflujo Gastroesofágico (ERGE)": 0.98}
            },
            "Prueba para H. pylori": {
                "Negativo": {"Gastritis Aguda": 0.25, "Úlcera Péptica No Complicada": 0.15, "Reflujo Gastroesofágico (ERGE)": 0.85},
                "Positivo para Helicobacter pylori": {"Gastritis Aguda": 0.85, "Úlcera Péptica No Complicada": 0.92, "Reflujo Gastroesofágico (ERGE)": 0.15}
            },
            "Ecocardiograma": {
                "Normal (Estructura y contractilidad conservadas)": {"Tromboembolismo Pulmonar": 0.20, "Insuficiencia Cardíaca Congestiva (ICC)": 0.04},
                "Signos de sobrecarga del ventrículo derecho y aplanamiento septal (Sospecha de TEP)": {"Tromboembolismo Pulmonar": 0.92, "Insuficiencia Cardíaca Congestiva (ICC)": 0.10},
                "Fracción de eyección disminuida FEVI <40% (Falla cardíaca sistólica)": {"Insuficiencia Cardíaca Congestiva (ICC)": 0.95, "Miocarditis": 0.35},
                "Derrame pericárdico leve a moderado sin taponamiento": {"Miocarditis": 0.45, "Insuficiencia Cardíaca Congestiva (ICC)": 0.15}
            },
            "Resonancia Magnética Cardíaca": {
                "Normal": {"Miocarditis": 0.04},
                "Criterios de Lake Louise positivos (Edema miocárdico e hiperemia compatible con Miocarditis)": {"Miocarditis": 0.98}
            },
            "Ecografía Abdominal": {
                "Normal (Órganos sólidos sin alteraciones)": {"Dengue Grave": 0.12},
                "Presencia de ascitis leve y/o derrame pleural derecho (Dengue Grave / Fuga plasmática)": {"Dengue Grave": 0.94, "Dengue No Grave (Clásico)": 0.01},
                "Esplenomegalia reactiva": {"Dengue No Grave (Clásico)": 0.30, "Dengue Grave": 0.40}
            },
            "Auscultación Pulmonar": {
                "Normal / Murmullo vesicular conservado": {"Crisis Asmática Aguda": 0.05, "Exacerbación Aguda de EPOC": 0.10, "Migraña Severa": 0.99},
                "Sibilancias espiratorias bilaterales difusas": {"Crisis Asmática Aguda": 0.95, "Bronquitis Aguda": 0.40, "Neumonía": 0.30},
                "Roncus y sibilancias bilaterales dispersas": {"Exacerbación Aguda de EPOC": 0.90, "Bronquitis Aguda": 0.50},
                "Crepitantes basales unilaterales (Sugerente de consolidación)": {"Neumonía": 0.95},
                "Disminución de murmullo vesicular unilateral": {"Neumonía": 0.40}
            },
            "Proteína C Reactiva (PCR)": {
                "Normal (<5 mg/L)": {"Migraña Severa": 0.95, "Neumonía": 0.10},
                "Elevación leve a moderada (5 - 40 mg/L - Proceso inflamatorio/viral)": {"Miocarditis": 0.40, "Sinusitis Aguda": 0.50},
                "Elevación marcada (>40 mg/L - Alta sospecha de infección bacteriana o inflamación sistémica aguda)": {"Neumonía": 0.90, "Miocarditis": 0.70, "Pielonefritis Aguda (IVU Alta)": 0.80, "Sinusitis Aguda": 0.60}
            },
            "Prueba de Antígeno en Heces": {
                "Negativa": {"Gastroenteritis Aguda Parasitaria": 0.10},
                "Positiva para Giardia lamblia": {"Gastroenteritis Aguda Parasitaria": 0.90},
                "Positiva para Entamoeba histolytica": {"Gastroenteritis Aguda Parasitaria": 0.85},
                "Positiva para Helicobacter pylori (Antígeno en heces)": {"Gastritis Aguda": 0.80, "Úlcera Péptica No Complicada": 0.85}
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
