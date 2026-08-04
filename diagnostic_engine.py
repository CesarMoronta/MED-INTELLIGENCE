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
                "Positivo": {"Gripe Común / Influenza": 0.95, "COVID-19": 0.95, "COVID-19 Grave": 0.95, "Resfriado Común (Rinofaringitis)": 0.60},
                "Negativo": {"Gripe Común / Influenza": 0.02, "COVID-19": 0.02, "COVID-19 Grave": 0.02, "Resfriado Común (Rinofaringitis)": 0.40}
            },
            "Hemograma Completo": {
                "Leucocitosis con neutrofilia": {"Neumonía": 0.88, "Bronquitis Aguda": 0.65, "Faringoamigdalitis Estreptocócica": 0.82, "Pielonefritis Aguda (IVU Alta)": 0.85, "Gastroenteritis Aguda Bacteriana": 0.70},
                "Leucopenia con linfocitosis": {"Dengue No Grave (Clásico)": 0.90, "Dengue Grave": 0.92, "COVID-19": 0.55, "Gripe Común / Influenza": 0.45},
                "Hemoconcentración y trombocitopenia": {"Dengue Grave": 0.95, "Dengue No Grave (Clásico)": 0.40},
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
                "Consolidación lobar / alveolar": {"Neumonía": 0.92, "COVID-19 Grave": 0.85},
                "Infiltrados bilaterales en vidrio deslustrado": {"COVID-19": 0.80, "COVID-19 Grave": 0.90, "Neumonía": 0.60},
                "Hiperinsuflación pulmonar / Aumento de trama": {"Crisis Asmática Aguda": 0.75, "Exacerbación Aguda de EPOC": 0.80},
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
                "Elevación ST / Ondas Q agudas": {"Infarto Agudo de Miocardio (IAM)": 0.92},
                "Inversión de onda T / Descenso ST": {"Infarto Agudo de Miocardio (IAM)": 0.60, "Miocarditis": 0.50},
                "Taquicardia sinusal / Signo S1Q3T3": {"Tromboembolismo Pulmonar": 0.85, "Crisis Asmática Aguda": 0.40},
                "Normal": {"Infarto Agudo de Miocardio (IAM)": 0.05, "Migraña Severa": 0.90, "Crisis Asmática Aguda": 0.55}
            },
            "Dímero D": {
                "Elevado": {"Tromboembolismo Pulmonar": 0.88, "COVID-19 Grave": 0.70, "Dengue Grave": 0.60},
                "Normal": {"Tromboembolismo Pulmonar": 0.10}
            },
            "Punción Lumbar (LCR)": {
                "Pleocitosis linfocitaria / Proteínas elevadas": {"Encefalitis": 0.92, "Accidente Cerebrovascular (ACV)": 0.08},
                "Normal": {"Encefalitis": 0.05, "Migraña Severa": 0.85}
            },
            "TC de Cráneo": {
                "Normal": {"Migraña Severa": 0.99, "Accidente Cerebrovascular (ACV)": 0.15, "Encefalitis": 0.50},
                "Hemorragia intracraneal aguda": {"Accidente Cerebrovascular (ACV)": 0.40, "Migraña Severa": 0.00},
                "Isquemia cerebral aguda / Infarto hiperagudo": {"Accidente Cerebrovascular (ACV)": 0.55, "Migraña Severa": 0.00},
                "Edema cerebral / Efecto de masa": {"Encefalitis": 0.45, "Accidente Cerebrovascular (ACV)": 0.10, "Migraña Severa": 0.00}
            },
            "Flujometría (Peak Flow)": {
                "PEF <60%": {"Crisis Asmática Aguda": 0.90, "Exacerbación Aguda de EPOC": 0.75},
                "Normal": {"Crisis Asmática Aguda": 0.10, "Exacerbación Aguda de EPOC": 0.20}
            },
            "Otoscopia": {
                "Membrana timpánica abombada / Eritematosa": {"Otitis Media Aguda": 0.95},
                "CAE eritematoso / Edematoso / Con detritos": {"Otitis Externa Aguda": 0.92},
                "Normal": {"Otitis Media Aguda": 0.05, "Otitis Externa Aguda": 0.08}
            },
            "TC de Senos Paranasales": {
                "Niveles hidroaéreos / Engrosamiento mucoso": {"Sinusitis Aguda": 0.95},
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
                "Patológico (Leucocituria / Nitritos + / Glucosuria)": {"Cistitis Aguda (IVU Baja)": 0.95, "Pielonefritis Aguda (IVU Alta)": 0.96, "Diabetes Mellitus Tipo 2": 0.40},
                "Normal": {"Cistitis Aguda (IVU Baja)": 0.05, "Pielonefritis Aguda (IVU Alta)": 0.04, "Diabetes Mellitus Tipo 2": 0.60}
            },
            "Endoscopia Digestiva Alta": {
                "Esofagitis / Hernia hiatal": {"Reflujo Gastroesofágico (ERGE)": 0.85},
                "Erosiones superficiales / Mucosa eritematosa": {"Gastritis Aguda": 0.90},
                "Úlcera péptica activa / Visualizada": {"Úlcera Péptica No Complicada": 0.95},
                "Normal": {"Reflujo Gastroesofágico (ERGE)": 0.15, "Gastritis Aguda": 0.10, "Úlcera Péptica No Complicada": 0.05}
            },
            "Urocultivo": {
                "Positivo (>100,000 UFC)": {"Cistitis Aguda (IVU Baja)": 0.96, "Pielonefritis Aguda (IVU Alta)": 0.97},
                "Negativo": {"Cistitis Aguda (IVU Baja)": 0.04, "Pielonefritis Aguda (IVU Alta)": 0.03}
            },
            "Examen Neurológico": {
                "Normal": {"Migraña Severa": 0.99, "Encefalitis": 0.05, "Accidente Cerebrovascular (ACV)": 0.08},
                "Déficit motor o sensitivo focal": {"Accidente Cerebrovascular (ACV)": 0.92, "Encefalitis": 0.25, "Migraña Severa": 0.01},
                "Alteración del estado mental / Confusión": {"Encefalitis": 0.85, "Accidente Cerebrovascular (ACV)": 0.30, "Migraña Severa": 0.01},
                "Rigidez de nuca / Signos meníngeos": {"Encefalitis": 0.60, "Accidente Cerebrovascular (ACV)": 0.02, "Migraña Severa": 0.00}
            },
            "Coprocultivo": {
                "Negativo para bacterias patógenas": {"Gastroenteritis Aguda Viral": 0.99, "Gastroenteritis Aguda Parasitaria": 0.95, "Gastroenteritis Aguda Bacteriana": 0.15},
                "Positivo para bacterias patógenas (Salmonella/Shigella/Campylobacter)": {"Gastroenteritis Aguda Bacteriana": 0.85, "Gastroenteritis Aguda Viral": 0.00, "Gastroenteritis Aguda Parasitaria": 0.00}
            },
            "Examen Coproparasitológico Seriados": {
                "Negativo": {"Gastroenteritis Aguda Viral": 0.98, "Gastroenteritis Aguda Bacteriana": 0.95, "Gastroenteritis Aguda Parasitaria": 0.15},
                "Presencia de quistes o trofozoítos (Giardia/Amebas)": {"Gastroenteritis Aguda Parasitaria": 0.85, "Gastroenteritis Aguda Viral": 0.00, "Gastroenteritis Aguda Bacteriana": 0.00}
            },
            "Electrólitos Séricos": {
                "Normal": {"Gastroenteritis Aguda Viral": 0.65, "Gastroenteritis Aguda Bacteriana": 0.55, "Gastroenteritis Aguda Parasitaria": 0.75, "Migraña Severa": 0.99},
                "Hipopotasemia / Alteración hidroelectrolítica": {"Gastroenteritis Aguda Bacteriana": 0.45, "Gastroenteritis Aguda Viral": 0.35, "Gastroenteritis Aguda Parasitaria": 0.25, "Migraña Severa": 0.01}
            },
            "Ecografía Renal": {
                "Normal": {"Cistitis Aguda (IVU Baja)": 0.95, "Pielonefritis Aguda (IVU Alta)": 0.25},
                "Ectasia piélica / Signos inflamatorios o absceso renal": {"Pielonefritis Aguda (IVU Alta)": 0.75, "Cistitis Aguda (IVU Baja)": 0.05}
            },
            "Electroencefalograma (EEG)": {
                "Normal": {"Migraña Severa": 0.98, "Encefalitis": 0.20, "Accidente Cerebrovascular (ACV)": 0.80},
                "Actividad lenta focal o difusa / Descargas paroxísticas": {"Encefalitis": 0.80, "Accidente Cerebrovascular (ACV)": 0.20, "Migraña Severa": 0.02}
            },
            "Resonancia Magnética de Cerebro": {
                "Normal": {"Migraña Severa": 0.99, "Encefalitis": 0.10, "Accidente Cerebrovascular (ACV)": 0.05},
                "Hiperintensidades en lóbulos temporales (compatible con Encefalitis herpética)": {"Encefalitis": 0.90, "Accidente Cerebrovascular (ACV)": 0.01},
                "Lesión isquémica o hemorrágica aguda": {"Accidente Cerebrovascular (ACV)": 0.95, "Encefalitis": 0.05}
            },
            "Prueba de PCR en Sangre u Orina (Zika)": {
                "Positiva": {"Fiebre Zika": 0.98},
                "Negativa": {"Fiebre Zika": 0.02}
            },
            "Serología (Chikungunya IgM)": {
                "Positiva": {"Fiebre Chikungunya": 0.98},
                "Negativa": {"Fiebre Chikungunya": 0.02}
            },
            "PCR específico (Chikungunya)": {
                "Positiva": {"Fiebre Chikungunya": 0.98},
                "Negativa": {"Fiebre Chikungunya": 0.02}
            },
            "Prueba rápida de Antígeno SARS-CoV-2": {
                "Positiva": {"COVID-19": 0.95, "COVID-19 Grave": 0.95},
                "Negativa": {"COVID-19": 0.05, "COVID-19 Grave": 0.05}
            },
            "PCR Nasofaríngeo": {
                "Positivo": {"COVID-19": 0.98, "COVID-19 Grave": 0.98},
                "Negativo": {"COVID-19": 0.02, "COVID-19 Grave": 0.02}
            },
            "Prueba rápida de Dengue (Antígeno NS1 / IgM-IgG)": {
                "Positiva": {"Dengue No Grave (Clásico)": 0.97, "Dengue Grave": 0.97},
                "Negativa": {"Dengue No Grave (Clásico)": 0.05, "Dengue Grave": 0.05}
            },
            "Signo del Trago": {
                "Positivo (Dolor intenso)": {"Otitis Externa Aguda": 0.95, "Otitis Media Aguda": 0.15},
                "Negativo": {"Otitis Externa Aguda": 0.05, "Otitis Media Aguda": 0.85}
            },
            "Palpación de la Mastoides": {
                "Dolor a la palpación / Tracción leve": {"Otitis Media Aguda": 0.92},
                "Sin dolor": {"Otitis Media Aguda": 0.08}
            },
            "Presión sobre Senos Paranasales": {
                "Dolor a la presión": {"Sinusitis Aguda": 0.95},
                "Sin dolor": {"Sinusitis Aguda": 0.05}
            },
            "Examen Clínico Nasofaríngeo": {
                "Eritema de mucosa nasal / Rinorrea clara": {"Resfriado Común (Rinofaringitis)": 0.92, "Gripe Común / Influenza": 0.50},
                "Normal": {"Resfriado Común (Rinofaringitis)": 0.08}
            },
            "Examen Clínico Visual": {
                "Lesiones pleomórficas en diferentes estadios (máculas, pápulas, vesículas, costras)": {"Varicela (Leve/Moderada)": 0.99},
                "Normal": {"Varicela (Leve/Moderada)": 0.01}
            },
            "PCR del líquido de la vesícula": {
                "Positivo": {"Varicela (Leve/Moderada)": 0.98},
                "Negativo": {"Varicela (Leve/Moderada)": 0.02}
            },
            "Criterios de Centor": {
                "0-2 puntos (sugiere causa viral)": {"Faringoamigdalitis Viral": 0.92, "Faringoamigdalitis Estreptocócica": 0.15},
                ">=3 puntos (alta sospecha bacteriana)": {"Faringoamigdalitis Estreptocócica": 0.85, "Faringoamigdalitis Viral": 0.08}
            },
            "pH-metría de 24 horas": {
                "Confirmatorio de reflujo ácido": {"Reflujo Gastroesofágico (ERGE)": 0.95},
                "Normal": {"Reflujo Gastroesofágico (ERGE)": 0.05}
            },
            "Prueba para H. pylori": {
                "Positivo": {"Gastritis Aguda": 0.80, "Úlcera Péptica No Complicada": 0.90, "Reflujo Gastroesofágico (ERGE)": 0.10},
                "Negativo": {"Gastritis Aguda": 0.20, "Úlcera Péptica No Complicada": 0.10, "Reflujo Gastroesofágico (ERGE)": 0.90}
            },
            "Ecocardiograma": {
                "Signos de sobrecarga del ventrículo derecho": {"Tromboembolismo Pulmonar": 0.80},
                "Normal / FEVI conservada": {"Tromboembolismo Pulmonar": 0.20}
            },
            "Resonancia Magnética Cardíaca": {
                "Criterios de Lake Louise positivos": {"Miocarditis": 0.95},
                "Normal": {"Miocarditis": 0.05}
            },
            "Ecografía Abdominal": {
                "Presencia de ascitis o derrame pleural": {"Dengue Grave": 0.85},
                "Normal": {"Dengue Grave": 0.15}
            },
            "Auscultación Pulmonar": {
                "Sibilancias espiratorias bilaterales difusas": {"Crisis Asmática Aguda": 0.95, "Bronquitis Aguda": 0.40, "Neumonía": 0.30},
                "Roncus y sibilancias bilaterales dispersas": {"Exacerbación Aguda de EPOC": 0.90, "Bronquitis Aguda": 0.50},
                "Normal / Murmullo vesicular conservado": {"Crisis Asmática Aguda": 0.05, "Exacerbación Aguda de EPOC": 0.10, "Migraña Severa": 0.99}
            },
            "Proteína C Reactiva (PCR)": {
                "Elevada": {"Neumonía": 0.90, "Miocarditis": 0.70, "Pielonefritis Aguda (IVU Alta)": 0.80, "Sinusitis Aguda": 0.60},
                "Normal": {"Migraña Severa": 0.95, "Neumonía": 0.10}
            },
            "Prueba de Antígeno en Heces": {
                "Positiva para Giardia o amebas": {"Gastroenteritis Aguda Parasitaria": 0.90},
                "Negativa": {"Gastroenteritis Aguda Parasitaria": 0.10}
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
