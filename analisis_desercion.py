"""Análisis de deserción estudiantil: auditoría, limpieza y preguntas.

Proyecto Integrador 3 · Nuevas Tecnologías
Autor: Santiago Arango
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })


def explorar(df):
    """Paso 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    """
    # RESPUESTA A LA PREGUNTA:
    # Sí. asistencia_pct y horas_trabajo_semana aparecen como texto (str) aunque
    # deberían ser números. Pasa porque algunas celdas tienen el símbolo % (por
    # ejemplo "100%") o un guion "-" escrito donde faltaba el dato, y con un solo
    # valor así pandas deja toda la columna como texto.
    print("=" * 60)
    print("PASO 1: PRIMERA MIRADA AL DATASET")
    print("=" * 60)

    print("\nForma del dataset (filas, columnas):", df.shape)

    print("\nTipos de datos y nulos (info):")
    df.info()

    print("\nEstadísticas de las columnas numéricas (describe):")
    print(df.describe())

    for col in ["programa", "jornada", "genero", "estado"]:
        print("\nValores de la columna", col, "(value_counts):")
        print(df[col].value_counts(dropna=False))


def auditar(df):
    """Paso 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    """
    # RESPUESTA A LA PREGUNTA:
    # Los más graves son los faltantes disfrazados y los valores imposibles, porque
    # pandas no los detecta solo y se cuelan en los promedios sin avisar. Por ejemplo,
    # los 999 de distancia_km suben el promedio de distancia de 17 a 32 km, y los
    # promedios de 45 o 78 suben el promedio académico (3.76 con ellos, 3.65 sin ellos). Los nulos reales sí se ven
    # con isnull(), y los duplicados inflan los conteos pero son pocos.
    print("\n" + "=" * 60)
    print("PASO 2: AUDITORÍA DE CALIDAD (solo se cuenta, no se corrige)")
    print("=" * 60)

    # --- Nulos reales ---
    print("\n1) Nulos reales por columna:")
    print(df.isnull().sum())

    # Revisar también textos escritos a mano como 'nan' o 'NA'
    textos_nulos = ["nan", "NaN", "NA", "N/A", "null", "None", ""]
    total_textos = 0
    for col in df.columns:
        if df[col].dtype == "str":
            total_textos = total_textos + df[col].isin(textos_nulos).sum()
    print("\nCeldas con el texto 'nan', 'NA', 'null' o vacío escrito a mano:", total_textos)

    # --- Faltantes disfrazados ---
    print("\n2) Faltantes disfrazados:")
    print("Guiones '-' en asistencia_pct:", (df["asistencia_pct"] == "-").sum())
    print("Guiones '-' en horas_trabajo_semana:", (df["horas_trabajo_semana"] == "-").sum())
    print("Valores 999 en distancia_km:", (df["distancia_km"] == 999).sum())
    # Los guiones de horas, ¿son de personas que no trabajan?
    print("Guiones en horas de personas que NO trabajan:",
          ((df["horas_trabajo_semana"] == "-") & (df["trabaja"] == "no")).sum())
    print("Guiones en horas de personas que SÍ trabajan:",
          ((df["horas_trabajo_semana"] == "-") & (df["trabaja"] == "sí")).sum())

    # --- Formato inconsistente ---
    print("\n3) Formatos inconsistentes:")
    print("Celdas de asistencia_pct con el signo %:",
          df["asistencia_pct"].str.contains("%", regex=False).sum())
    print("Fechas en formato AAAA-MM-DD:",
          df["fecha_matricula"].str.contains("-", regex=False).sum())
    print("Fechas en formato DD/MM/AAAA:",
          df["fecha_matricula"].str.contains("/", regex=False).sum())

    # --- Valores imposibles ---
    horas = pd.to_numeric(df["horas_trabajo_semana"], errors="coerce")
    print("\n4) Valores imposibles:")
    print("Edades fuera del rango 15 a 60:", ((df["edad"] < 15) | (df["edad"] > 60)).sum())
    print("Promedios mayores a 5:", (df["promedio_acumulado"] > 5).sum())
    print("Promedios menores a 0:", (df["promedio_acumulado"] < 0).sum())
    print("Horas de trabajo mayores a 100 por semana:", (horas > 100).sum())

    # --- Duplicados ---
    print("\n5) Duplicados:")
    print("Filas duplicadas (iguales en todas las columnas):", df.duplicated().sum())
    print("id_estudiante repetidos:", df["id_estudiante"].duplicated().sum())

    # --- Errores tipográficos ---
    print("\n6) Errores tipográficos (cantidad de valores distintos por columna):")
    for col in ["programa", "jornada", "genero", "ciudad_procedencia"]:
        print(col, "-> distintos:", df[col].nunique(), "| válidos:", len(VALIDOS[col]))


def convertir_numericos(df):
    """Paso 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
    # ---- asistencia_pct ----
    # Primero se cuentan los problemas (antes de convertir, para no perder el registro)
    con_porcentaje = df["asistencia_pct"].str.contains("%", regex=False).sum()
    con_guion = (df["asistencia_pct"] == "-").sum()

    df["asistencia_pct"] = df["asistencia_pct"].str.replace("%", "", regex=False)
    registrar("convertir_numericos", "asistencia_pct", "quitar el símbolo %", con_porcentaje,
              "El % es solo un símbolo; el número ya está en escala de 0 a 100. "
              "Quitarlo permite calcular promedios y cuartiles.")

    df["asistencia_pct"] = df["asistencia_pct"].replace("-", np.nan)
    registrar("convertir_numericos", "asistencia_pct", "cambiar el guion '-' por nulo", con_guion,
              "El guion significa que no hay dato. Es un faltante disfrazado: se vuelve "
              "nulo real para no inventar una asistencia.")

    df["asistencia_pct"] = pd.to_numeric(df["asistencia_pct"], errors="coerce")
    registrar("convertir_numericos", "asistencia_pct", "convertir la columna a número", len(df),
              "La columna era texto; con pd.to_numeric(errors='coerce') queda numérica "
              "y ya se puede usar en estadísticas.")

    # ---- horas_trabajo_semana ----
    guiones_horas = (df["horas_trabajo_semana"] == "-").sum()
    df["horas_trabajo_semana"] = df["horas_trabajo_semana"].replace("-", np.nan)
    df["horas_trabajo_semana"] = pd.to_numeric(df["horas_trabajo_semana"], errors="coerce")
    registrar("convertir_numericos", "horas_trabajo_semana",
              "cambiar el guion '-' por nulo y convertir a número", guiones_horas,
              "Los guiones eran texto y volvían la columna de texto. Se pasan a nulo "
              "y se convierte a número. En el paso 8 se decide su valor final.")

    # ---- distancia_km ----
    cantidad_999 = (df["distancia_km"] == 999).sum()
    df["distancia_km"] = df["distancia_km"].replace(999, np.nan)
    registrar("convertir_numericos", "distancia_km", "cambiar 999 por nulo", cantidad_999,
              "999 km no es una distancia real; es un código de 'sin dato'. "
              "Si se deja, sube mucho el promedio de distancia.")

    return df


def unificar_categorias(df):
    """Paso 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    """
    # RESPUESTA A LA PREGUNTA:
    # Son el mismo valor: "Bogotá", "BOGOTÁ", "Bogota" y "bogota"; "Medellín",
    # "Medellin" y "medellin"; "Psicología" y "Psicologia"; "Ingeniería de Sistemas"
    # e "Ingenieria de Sistemas"; "Diurna" y "diurna"; "Nocturna", "nocturna" y
    # "NOCTURNA"; "Femenino", "F" y "femenino"; "Masculino" y "M".
    # NO se debe unificar "Otra ciudad" con ninguna ciudad: es una categoría propia
    # que agrupa varias ciudades distintas, no es un error de escritura.

    # Después de strip() y lower() todos los valores quedan en minúsculas, por eso las
    # claves del diccionario van en minúsculas (también las que ya estaban bien).
    diccionarios = {
        "programa": {
            "administración de empresas": "Administración de Empresas",
            "contaduría pública": "Contaduría Pública",
            "derecho": "Derecho",
            "psicología": "Psicología",
            "psicologia": "Psicología",
            "ingeniería de sistemas": "Ingeniería de Sistemas",
            "ingenieria de sistemas": "Ingeniería de Sistemas",
            "ingeniería industrial": "Ingeniería Industrial",
            "enfermería": "Enfermería",
            "diseño gráfico": "Diseño Gráfico",
        },
        "jornada": {
            "diurna": "Diurna",
            "nocturna": "Nocturna",
            "fin de semana": "Fin de semana",
        },
        "genero": {
            "femenino": "Femenino",
            "f": "Femenino",
            "masculino": "Masculino",
            "m": "Masculino",
        },
        "ciudad_procedencia": {
            "bogotá": "Bogotá",
            "bogota": "Bogotá",
            "medellín": "Medellín",
            "medellin": "Medellín",
            "cali": "Cali",
            "bucaramanga": "Bucaramanga",
            "rionegro": "Rionegro",
            "barranquilla": "Barranquilla",
            "otra ciudad": "Otra ciudad",
        },
    }

    for col in ["programa", "jornada", "genero", "ciudad_procedencia"]:
        antes = df[col].copy()
        # 1) quitar espacios y pasar a minúsculas  2) cambiar cada variante por el valor correcto
        df[col] = df[col].str.strip().str.lower()
        df[col] = df[col].replace(diccionarios[col])

        # Contar cuántas celdas cambiaron de verdad (los nulos se comparan como texto vacío)
        cambiadas = (antes.fillna("") != df[col].fillna("")).sum()

        # Comprobar que todos los valores quedaron en la lista de válidos
        todo_ok = df[col].dropna().isin(VALIDOS[col]).all()
        print("Columna", col, "- celdas corregidas:", cambiadas, "- todos válidos:", todo_ok)

        registrar("unificar_categorias", col,
                  "quitar espacios, pasar a minúsculas y unificar variantes", cambiadas,
                  "Eran el mismo valor escrito distinto (tildes, mayúsculas, espacios o "
                  "abreviaturas). Si no se unifican, pandas los cuenta como grupos separados "
                  "y las tasas por grupo salen mal.")

    return df


def convertir_fechas(df):
    """Paso 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    # Contar cuántas estaban en el segundo formato ANTES de convertir
    en_segundo_formato = df["fecha_matricula"].str.contains("/", regex=False).sum()

    # Cada formato se intenta por separado; lo que no coincide queda como NaT
    fecha_iso = pd.to_datetime(df["fecha_matricula"], format="%Y-%m-%d", errors="coerce")
    fecha_dmy = pd.to_datetime(df["fecha_matricula"], format="%d/%m/%Y", errors="coerce")

    # Juntar los dos resultados: donde el primero es nulo, se usa el segundo
    df["fecha_matricula"] = fecha_iso.fillna(fecha_dmy)

    print("Fechas que no se pudieron convertir:", df["fecha_matricula"].isnull().sum())

    registrar("convertir_fechas", "fecha_matricula",
              "convertir a fecha con los formatos AAAA-MM-DD y DD/MM/AAAA", en_segundo_formato,
              "La columna tenía dos formatos mezclados. Se usó un formato explícito para cada "
              "uno, así no se confunde el día con el mes (03/04 puede ser 3 de abril o 4 de marzo).")

    return df


def eliminar_duplicados(df):
    """Paso 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Pista: duplicated() y drop_duplicates(), con reset_index(drop=True).
    """
    # RESPUESTA A LA PREGUNTA:
    # No es posible. Cada estudiante tiene un id_estudiante único, y dos estudiantes
    # distintos tendrían ids distintos. Además, la cantidad de filas duplicadas es la
    # misma que la de ids repetidos, así que son el mismo estudiante cargado dos veces.
    duplicadas = df.duplicated().sum()
    ids_repetidos = df["id_estudiante"].duplicated().sum()
    print("Filas duplicadas:", duplicadas, "| ids repetidos:", ids_repetidos)

    df = df.drop_duplicates().reset_index(drop=True)

    registrar("eliminar_duplicados", "todas", "eliminar filas duplicadas (se conserva la primera)",
              duplicadas,
              "Eran filas idénticas en todas las columnas, con el mismo id_estudiante: el mismo "
              "estudiante registrado dos veces. Dejarlas cuenta dos veces al mismo estudiante.")
    return df


def tratar_faltantes(df):
    """Paso 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    # RESPUESTAS A LAS PREGUNTAS:
    # - No se puede inventar una nota. Si se imputa el promedio, todos esos estudiantes
    #   quedarían con una nota que no es suya y se achatarían las diferencias entre grupos.
    # - En ciudad y tipo de colegio es mejor marcar 'Sin dato': así no se pierden estudiantes
    #   (y sus demás datos), y no se inventa una ciudad o un colegio.
    # - Los nulos de motivo_retiro NO son errores: la columna solo aplica a los desertores.

    # ---- promedio_acumulado: eliminar las filas ----
    nulos_promedio = df["promedio_acumulado"].isnull().sum()
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("tratar_faltantes", "promedio_acumulado", "eliminar filas con promedio nulo",
              nulos_promedio,
              "Una nota no se puede inventar. Imputar el promedio de todos haría que estos "
              "estudiantes parezcan iguales al resto y escondería diferencias reales. "
              "Se usó subset para no borrar filas por nulos de otras columnas.")

    # ---- ciudad_procedencia: marcar como 'Sin dato' ----
    nulos_ciudad = df["ciudad_procedencia"].isnull().sum()
    df["ciudad_procedencia"] = df["ciudad_procedencia"].fillna("Sin dato")
    registrar("tratar_faltantes", "ciudad_procedencia", "reemplazar nulos por 'Sin dato'",
              nulos_ciudad,
              "No se conoce la ciudad y no se debe inventar. Eliminar la fila perdería un "
              "estudiante completo por un dato secundario; 'Sin dato' los conserva y se ve claro.")

    # ---- tipo_colegio: marcar como 'Sin dato' ----
    nulos_colegio = df["tipo_colegio"].isnull().sum()
    df["tipo_colegio"] = df["tipo_colegio"].fillna("Sin dato")
    registrar("tratar_faltantes", "tipo_colegio", "reemplazar nulos por 'Sin dato'",
              nulos_colegio,
              "Mismo caso que la ciudad: no sabemos si el colegio era público o privado, "
              "así que no se asigna uno al azar y no se elimina al estudiante.")

    # ---- motivo_retiro: no se toca ----
    nulos_motivo = df["motivo_retiro"].isnull().sum()
    desertores_sin_motivo = (df["estado"].eq("desertor") & df["motivo_retiro"].isnull()).sum()
    print("Nulos de motivo_retiro:", nulos_motivo,
          "| desertores sin motivo (esos sí serían error):", desertores_sin_motivo)
    registrar("tratar_faltantes", "motivo_retiro", "dejar los nulos como están (no se modifica)", 0,
              "Son nulos esperados: " + str(nulos_motivo) + " estudiantes activos o graduados, "
              "a quienes no les aplica un motivo de retiro. Ningún desertor tiene el motivo vacío.")

    return df


def tratar_imposibles(df):
    """Paso 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    # RESPUESTAS A LAS PREGUNTAS:
    # - Un 45 no puede ser una nota en escala de 0 a 5. Se vuelve nulo y se trata como
    #   cualquier otro promedio nulo (se eliminan esas filas), porque no se puede saber
    #   cuál era la nota real: dividir entre 10 o entre 20 sería adivinar.
    # - Una edad imposible se reemplaza por la mediana de las edades válidas, porque
    #   la mediana casi no cambia con valores extremos.
    # - Si el estudiante no trabaja, tiene 0 horas. En código: loc con dos condiciones
    #   entre paréntesis (trabaja == 'no' y horas nulas).

    # ---- edad: fuera de 15 a 60 -> mediana de las edades válidas ----
    edad_mala = (df["edad"] < 15) | (df["edad"] > 60)
    cantidad_edad = edad_mala.sum()
    mediana_edad = df.loc[~edad_mala, "edad"].median()
    df.loc[edad_mala, "edad"] = mediana_edad
    registrar("tratar_imposibles", "edad",
              "reemplazar edades fuera de 15 a 60 por la mediana (" + str(mediana_edad) + ")",
              cantidad_edad,
              "Edades de 12 y de 150 años no son posibles en estudiantes de educación superior; "
              "son errores de registro. La mediana no se afecta por extremos, y son muy pocas filas.")

    # ---- promedio_acumulado: fuera de 0 a 5 -> nulo -> eliminar fila ----
    promedio_malo = (df["promedio_acumulado"] > 5) | (df["promedio_acumulado"] < 0)
    cantidad_promedio = promedio_malo.sum()
    df.loc[promedio_malo, "promedio_acumulado"] = np.nan
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("tratar_imposibles", "promedio_acumulado",
              "convertir promedios fuera de 0 a 5 en nulo y eliminar esas filas", cantidad_promedio,
              "Valores como 45, 62 o 78 no existen en la escala de 0 a 5. No se sabe cuál era la "
              "nota real (dividir entre 10 daría 6.2, que tampoco sirve), así que no se inventa: "
              "se trata como un nulo de promedio y se elimina la fila.")

    # ---- horas_trabajo_semana ----
    # Regla 1: si no trabaja y las horas están nulas -> 0 horas
    sin_trabajo = (df["trabaja"] == "no") & (df["horas_trabajo_semana"].isnull())
    cantidad_cero = sin_trabajo.sum()
    df.loc[sin_trabajo, "horas_trabajo_semana"] = 0
    registrar("tratar_imposibles", "horas_trabajo_semana",
              "poner 0 horas a quienes no trabajan y tenían guion", cantidad_cero,
              "Una persona que no trabaja tiene 0 horas de trabajo; el guion no era un dato "
              "perdido sino un 0. La regla depende de la columna trabaja, por eso no se usa "
              "un reemplazo general.")

    # Regla 2: más de 100 horas por semana -> nulo -> mediana de quienes trabajan
    horas_malas = df["horas_trabajo_semana"] > 100
    cantidad_horas = horas_malas.sum()
    df.loc[horas_malas, "horas_trabajo_semana"] = np.nan
    mediana_horas = df.loc[df["trabaja"] == "sí", "horas_trabajo_semana"].median()
    df.loc[horas_malas, "horas_trabajo_semana"] = mediana_horas
    registrar("tratar_imposibles", "horas_trabajo_semana",
              "reemplazar horas mayores a 100 por la mediana de quienes trabajan (" +
              str(mediana_horas) + ")", cantidad_horas,
              "Trabajar más de 100 horas a la semana, además de estudiar, no es realista "
              "(la semana tiene 168 horas). Se usa la mediana de quienes sí trabajan porque "
              "no se afecta por extremos.")

    print("Horas de trabajo nulas después de limpiar:", df["horas_trabajo_semana"].isnull().sum())
    return df


def crear_variables(df):
    """Paso 9 del Word: variables nuevas para el análisis.

    Crea:
    - desertor: True si estado es 'desertor', False si no.
    - cuartil_asistencia: divide asistencia_pct en cuatro grupos iguales con pd.qcut.
    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    """
    # RESPUESTA A LA PREGUNTA:
    # Con valores exactos habría casi un grupo por cada número (80.1, 80.2...) y cada
    # grupo tendría muy pocos estudiantes, así que las tasas serían inestables. Con
    # cuartiles quedan 4 grupos del mismo tamaño y el patrón se ve fácil.

    df["desertor"] = df["estado"].eq("desertor")
    registrar("crear_variables", "desertor", "crear columna True/False (estado == 'desertor')",
              len(df),
              "Con True/False el promedio de la columna es directamente la tasa de deserción "
              "de cada grupo.")

    df["cuartil_asistencia"] = pd.qcut(df["asistencia_pct"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    con_cuartil = df["cuartil_asistencia"].notnull().sum()
    registrar("crear_variables", "cuartil_asistencia",
              "crear 4 grupos de asistencia con pd.qcut (Q1 baja ... Q4 alta)", con_cuartil,
              "Los cuartiles dan grupos de tamaño parecido, así las tasas son comparables. "
              "Los estudiantes sin asistencia (nulo) quedan sin cuartil.")

    print("Desertores (True):", df["desertor"].sum(), "de", len(df), "estudiantes")
    print("Estudiantes por cuartil de asistencia:")
    print(df["cuartil_asistencia"].value_counts().sort_index())
    print("Estudiantes sin cuartil (asistencia nula):", df["cuartil_asistencia"].isnull().sum())
    return df


# Paleta propia del proyecto (verde azulado + coral)
COLOR_PRINCIPAL = "#0f766e"
COLOR_ACENTO = "#f97360"
COLOR_TEXTO = "#1e293b"


def estilo_graficos():
    """Aplica un estilo común a todos los gráficos."""
    sns.set_theme(style="whitegrid", font_scale=1.0)
    plt.rcParams.update({
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.titlelocation": "left",
        "axes.edgecolor": "#cbd5e1",
        "axes.labelcolor": COLOR_TEXTO,
        "text.color": COLOR_TEXTO,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": "#e2e8f0",
        "figure.facecolor": "white",
    })


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original.

    Pista: sns.heatmap(df.isnull(), cbar=False)
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    estilo_graficos()
    plt.figure(figsize=(12, 6))
    # Fondo claro = dato presente; color acento = celda vacía
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False,
                cmap=sns.color_palette(["#f1f5f9", COLOR_ACENTO], as_cmap=True))
    plt.title("Gráfico 1 · Celdas vacías en el dataset original (en coral)")
    plt.xlabel("")
    plt.ylabel("Registros (una línea por estudiante)")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "mapa_faltantes.png", dpi=130)
    plt.show()
    plt.close()


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar.

    Pregunta: ¿qué cambió en cada distribución? ¿Por qué?
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    estilo_graficos()
    fig, ejes = plt.subplots(2, 2, figsize=(11, 7))

    # Columna izquierda: antes de limpiar. Columna derecha: después de limpiar.
    variables = [("promedio_acumulado", "Promedio acumulado"), ("edad", "Edad")]
    for fila, (col, nombre) in enumerate(variables):
        sns.boxplot(x=antes[col], ax=ejes[fila, 0], color="#fecaca",
                    linecolor=COLOR_ACENTO, flierprops={"markerfacecolor": COLOR_ACENTO})
        ejes[fila, 0].set_title(nombre + " · sin limpiar")
        ejes[fila, 0].set_xlabel("")
        sns.boxplot(x=despues[col], ax=ejes[fila, 1], color="#99f6e4",
                    linecolor=COLOR_PRINCIPAL, flierprops={"markerfacecolor": COLOR_PRINCIPAL})
        ejes[fila, 1].set_title(nombre + " · limpio")
        ejes[fila, 1].set_xlabel("")

    fig.suptitle("Gráfico 2 · Distribuciones antes y después de la limpieza",
                 x=0.01, ha="left", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(GRAFICOS / "distribuciones_antes_despues.png", dpi=130)
    plt.show()
    plt.close()


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa.

    Pista: df.groupby("programa")["desertor"].mean()
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    estilo_graficos()
    tabla = df.groupby("programa").agg(tasa=("desertor", "mean"),
                                       estudiantes=("desertor", "size"))
    tabla = tabla.sort_values("tasa", ascending=True)
    promedio_general = df["desertor"].mean()

    fig, ax = plt.subplots(figsize=(11, 6))
    # Barras horizontales: en coral los programas por encima de la tasa general
    colores = [COLOR_ACENTO if t > promedio_general else COLOR_PRINCIPAL for t in tabla["tasa"]]
    etiquetas = [nombre + "  (n=" + str(n) + ")" for nombre, n in zip(tabla.index, tabla["estudiantes"])]
    ax.barh(etiquetas, tabla["tasa"] * 100, color=colores, height=0.65)
    for i, t in enumerate(tabla["tasa"]):
        ax.text(t * 100 - 0.6, i, f"{t * 100:.1f}%", va="center", ha="right",
                color="white", fontweight="bold", fontsize=10)
    ax.axvline(promedio_general * 100, color="#64748b", linestyle="--", linewidth=1)
    ax.text(promedio_general * 100 + 0.4, len(tabla) - 0.45,
            f"tasa general {promedio_general * 100:.1f}%", color="#64748b", fontsize=9)
    ax.set_xlim(0, tabla["tasa"].max() * 100 + 4)
    ax.set_title("Gráfico 3 · Deserción por programa académico")
    ax.set_xlabel("Tasa de deserción (%)")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "tasa_desercion_por_programa.png", dpi=130)
    plt.show()
    plt.close()


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia.

    Pista: df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    """
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    estilo_graficos()
    tabla = df.groupby("cuartil_asistencia", observed=True).agg(
        tasa=("desertor", "mean"), estudiantes=("desertor", "size"))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = list(range(len(tabla)))
    valores = tabla["tasa"] * 100
    # De coral (asistencia baja) a verde azulado (asistencia alta)
    colores = [COLOR_ACENTO, "#fdba74", "#5eead4", COLOR_PRINCIPAL][:len(tabla)]
    ax.bar(x, valores, color=colores, width=0.62, edgecolor="white")
    for i, v in enumerate(valores):
        ax.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([str(c) + "\n(n=" + str(n) + ")" for c, n in zip(tabla.index, tabla["estudiantes"])])
    ax.set_ylim(0, valores.max() + 10)
    ax.set_title("Gráfico 4 · Deserción según cuartil de asistencia")
    ax.set_xlabel("Cuartil de asistencia (Q1 = asiste menos, Q4 = asiste más)")
    ax.set_ylabel("Tasa de deserción (%)")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "tasa_desercion_por_asistencia.png", dpi=130)
    plt.show()
    plt.close()


def responder_preguntas(df):
    """Paso 10 del Word: las cinco preguntas de la institución.

    Cada pregunta debe imprimir el resultado con el número de estudiantes por grupo.
    Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
    Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
    Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
    Pregunta 4: ¿Cuántas materias reprobadas tienen en promedio los desertores frente a los activos?
                (Excluye a los graduados.)
    Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
                (Usa cuartil_asistencia.)
    """
    print("\n" + "=" * 60)
    print("PASO 10: LAS CINCO PREGUNTAS")
    print("=" * 60)

    # ---- Pregunta 1: tasa de deserción por programa ----
    print("\nPREGUNTA 1: ¿Qué programa tiene la tasa de deserción más alta?")
    p1 = df.groupby("programa").agg(tasa=("desertor", "mean"),
                                    estudiantes=("desertor", "size"))
    p1 = p1.sort_values("tasa", ascending=False)
    p1["tasa_%"] = (p1["tasa"] * 100).round(1)
    print(p1[["tasa_%", "estudiantes"]])
    print("Respuesta: el programa con mayor deserción es", p1.index[0],
          "con", p1["tasa_%"].iloc[0], "% (", p1["estudiantes"].iloc[0], "estudiantes ).")

    # ---- Pregunta 2: becados vs no becados ----
    print("\nPREGUNTA 2: ¿Hay diferencia en la deserción entre becados y no becados?")
    p2 = df.groupby("beca").agg(tasa=("desertor", "mean"),
                                estudiantes=("desertor", "size"))
    p2["tasa_%"] = (p2["tasa"] * 100).round(1)
    print(p2[["tasa_%", "estudiantes"]])
    diferencia = (p2.loc["no", "tasa"] - p2.loc["sí", "tasa"]) * 100
    print("Diferencia (no becados - becados):", round(diferencia, 1), "puntos porcentuales.")

    # ---- Pregunta 3: promedio por jornada ----
    print("\nPREGUNTA 3: ¿Qué jornada tiene el menor promedio acumulado?")
    p3 = df.groupby("jornada").agg(promedio=("promedio_acumulado", "mean"),
                                   estudiantes=("promedio_acumulado", "size"))
    p3 = p3.sort_values("promedio")
    p3["promedio"] = p3["promedio"].round(3)
    print(p3)
    print("Respuesta: la jornada con menor promedio es", p3.index[0],
          "con", p3["promedio"].iloc[0], "(", p3["estudiantes"].iloc[0], "estudiantes ).")

    # ---- Pregunta 4: materias reprobadas, desertores vs activos ----
    # Se excluyen los graduados porque no son desertores ni activos: ya terminaron la carrera
    # y mezclarlos cambiaría el promedio de uno de los dos grupos de la comparación.
    print("\nPREGUNTA 4: ¿Cuántas materias reprobadas tienen en promedio desertores y activos?")
    sin_graduados = df[df["estado"] != "graduado"]
    p4 = sin_graduados.groupby("estado").agg(
        reprobadas_promedio=("materias_reprobadas", "mean"),
        estudiantes=("materias_reprobadas", "size"))
    p4["reprobadas_promedio"] = p4["reprobadas_promedio"].round(3)
    print(p4)

    # ---- Pregunta 5: deserción por cuartil de asistencia ----
    print("\nPREGUNTA 5: ¿La deserción aumenta conforme baja la asistencia?")
    p5 = df.groupby("cuartil_asistencia", observed=True).agg(
        tasa=("desertor", "mean"),
        asistencia_promedio=("asistencia_pct", "mean"),
        estudiantes=("desertor", "size"))
    p5["tasa_%"] = (p5["tasa"] * 100).round(1)
    p5["asistencia_promedio"] = p5["asistencia_promedio"].round(1)
    print(p5[["tasa_%", "asistencia_promedio", "estudiantes"]])
    print("Estudiantes sin dato de asistencia (no entran en esta pregunta):",
          df["asistencia_pct"].isnull().sum())


def numeros_reflexiones(df):
    """Extra: números que apoyan las tres reflexiones del README (es un apoyo extra, no un paso del taller)."""
    print("\n" + "=" * 60)
    print("NÚMEROS DE APOYO PARA LAS REFLEXIONES")
    print("=" * 60)

    # Reflexión 1: ¿los becados y no becados se parecen en otras cosas?
    print("\nBecados vs no becados: promedio académico y estrato promedio")
    r1 = df.groupby("beca").agg(promedio=("promedio_acumulado", "mean"),
                                estrato=("estrato", "mean"),
                                estudiantes=("beca", "size"))
    print(r1.round(2))

    # Reflexión 2: motivo_retiro solo existe cuando el estudiante ya desertó
    print("\nPorcentaje de estudiantes con motivo_retiro lleno, según el estado")
    print(df.groupby("estado")["motivo_retiro"].apply(lambda s: s.notnull().mean()).round(2))

    # Reflexión 3: variables sensibles frente a otras variables
    for col in ["genero", "estrato", "ciudad_procedencia", "trabaja"]:
        print("\nTasa de deserción por", col)
        t = df.groupby(col).agg(tasa=("desertor", "mean"), estudiantes=("desertor", "size"))
        t["tasa"] = (t["tasa"] * 100).round(1)
        print(t)


def guardar(df):
    """Paso 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    numeros_reflexiones(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)


if __name__ == "__main__":
    main()
