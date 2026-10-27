"""Une la selección de la fase 2 con la codificación manual (miniaturas, producción, guion) y rasgos automáticos del título.

Uso: python3 codificar_fase2.py datos/videos_fase2.csv > datos/videos_analizados.csv
La codificación manual sale de revisar las hojas de miniaturas y fotogramas y de leer las transcripciones.
"""
import csv, re, sys

# Sistema de miniatura y texto visible, revisados imagen por imagen (orden = hoja de contacto por canal)
THUMB = {
 'SimplePaintOfficial': ['duelo|15G / IMPACT', 'duelo|BULL / CRICKET / MotoGP', 'escena etiquetada|ALIVE / DROWNED',
     'duelo|LEAGUE OF LEGENDS / MINECRAFT', 'duelo|CHERNOBYL / HIROSHIMA', 'duelo|BEFORE / AFTER', 'duelo temporal|2009 / 2019',
     'duelo|TORNADO / TSUNAMI', 'duelo|GRIZZLY / PYTHON', 'collage de personas reales|U.S. MILITARY COUPS', 'duelo temporal|1914 / 1409'],
 'SomeGuyWhoKnowsStuff': ['banner con título completo + collage dibujado|(título completo)'] * 12,
 'SquireExplains/long': ['mascota + texto grande|USELESS.', 'mascota + texto grande|DON\'T GO IN!', 'mascota + comparación temporal|1185 / 1877',
     'mascota + versus|ROME VS ELEPHANTS'],
 'SquireExplains/short': ['mascota + texto en color|THEY CAN\'T FIND OUT', 'mascota + texto en color|THE KAMIKAZE WHO CAME BACK',
     'mascota + texto en color|WHY SPARTA HATED HIM', 'mascota + texto en color|FRANCE BUILT A FAKE PARIS', 'mascota + texto en color|THEY INVADED AN EMPTY ISLAND',
     'mascota + texto en color|THE MARINE WHO COULDN\'T DIE', 'mascota + texto en color|WW2 ENDED 1945 HE STOPPED 1974',
     'mascota + texto en color|1,000 EATEN BY CROCS?', 'mascota + texto en color|HE ALMOST ESCAPED ROME'],
 'TeloPintoFacil': ['trío etiquetado|DELTA FORCE / GREEN BERETS / NIGHT STALKERS', 'cuadrícula de fotos etiquetadas|(nombres de películas)',
     'cuadrícula de iconos etiquetados|(colores de ojos)', 'duelo|BUNDY / GACY', 'cuadrícula de iconos etiquetados|(tipos de tornado)',
     'personaje + texto grande|BESTIA DE OMAHA', 'personaje + texto grande|TODOS IBAN DROGADOS', 'personaje + texto grande|MAD JACK',
     'personaje + escena, sin texto|', 'caricaturas de líderes reales, sin texto|', 'cuadrícula de iconos etiquetados|(errores históricos)'],
 'ThePaintExplainer': ['duelo|URANUS / SATURN', 'cuadrícula de imágenes etiquetadas|(castigos)', 'cuadrícula de fotos etiquetadas|(leyendas)',
     'cuadrícula de fotos etiquetadas|(18 errores)', 'diagrama etiquetado|(niveles del infierno)', 'escena + texto|WATER IS RISING',
     'duelo|EL MEXICANO / CARRILLO', 'duelo sin etiquetas|', 'cuadrícula de fotos etiquetadas|(lugares)', 'cuadrícula de ilustraciones etiquetadas|(mitos)',
     'cuadrícula de fotos etiquetadas|(lugares)', 'cuadrícula de ilustraciones etiquetadas|(proyectos)', 'cuadrícula de fotos etiquetadas|(lugares)'],
 'estrictamente': ['escena + texto corto|SIN TRABAJO', 'escena + pregunta corta|¿PRIMER PAÍS?', 'escena + pregunta corta|¿ERA UN ARMA?',
     'escena + pregunta corta|DORMIR TARD ?', 'escena + pregunta corta|¿PRIMER ESCLAVO?', 'escena + pregunta corta|¿SIN CAMAS?',
     'escena + pregunta corta|¿ESTO ERA LUJO?', 'escena + texto corto|¡ERES EL PRIMERO!', 'escena + pregunta corta|¿POR QUÉ BLANCO?',
     'escena + pregunta corta|¿SIN DORMIR?', 'escena + pregunta corta|¿QUÉ VIERON?', 'escena + pregunta corta|¿CRIANZA PREHISTÓRICA?',
     'escena + pregunta corta|¿NOCHES MORTALES?'],
 'lichsungoaitruyen': ['plantilla banderas + pregunta + personaje|VÌ SAO PHÁP KHÔNG THẮNG NỔI NGUYỄN TRI PHƯƠNG?',
     'plantilla banderas + pregunta + personaje|VÌ SAO 200 NĂM KHÔNG AI TÌM RA MỘ?', 'plantilla banderas + pregunta + personaje|VÌ SAO VUA GIẢ ĐƯỢC ĐÓN NHƯ VUA THẬT?',
     'plantilla banderas + pregunta + personaje|VÌ SAO PHÁP NẤU CHẢY ẤN CỦA GIA LONG?', 'plantilla banderas + pregunta + personaje|VÌ SAO PHÁP CHẮC THẮNG RỒI THUA SẠCH?',
     'plantilla banderas + pregunta + personaje|DÁM GIẾT VUA KHÔNG DÁM LÀM VUA?', 'plantilla banderas + pregunta + personaje|VÌ SAO CÓ ẢNH TỪNG NGƯỜI PHÁP VẪN KHÔNG BẮT ĐƯỢC?',
     'plantilla banderas + pregunta + personaje|VÌ SAO NGƯỜI ANH KHÔNG GIAO NGUYỄN ÁI QUỐC CHO PHÁP?', 'plantilla banderas + pregunta + personaje|500 NĂM LÀ VUA RỒI THÀNH GIẶC',
     'estilo fotográfico realista (rompe plantilla)|PHÁP ĐÁNH VIỆT NAM SAI LẦM THẾ KỶ?', 'plantilla banderas + pregunta + personaje|LÝ BÍ LÀ AI?',
     'plantilla banderas + pregunta + personaje|NAM KỲ NỔI DẬY'],
 'thecrookedexplainer': ['trío etiquetado|GEORGIE PORGIE / RING AROUND THE ROSIE / ORANGES & LEMONS', 'trío etiquetado|STILL ALIVE? / IMMORTAL CELLS / NO PAIN',
     'trío etiquetado|SEES MATH / 2 PAGES AT ONCE / HEARS IT ONCE', 'trío etiquetado|BORN WITH ABS / SEES WITH SOUND / FEELS NO PAIN',
     'trío etiquetado|BROTHER + SISTER / UNCLE + NIECE / DOUBLE COUSINS', 'dúo etiquetado|FAIRY TALE / REAL STORY',
     'trío etiquetado|RUB-A-DUB-DUB / PETER PETER PUMPKIN EATER / HUMPTY DUMPTY', 'dúo etiquetado|1993 DIED / 2013 I WAS HER',
     'trío etiquetado|NO PARACHUTE / FELL WITH HER SEAT / 3 DAYS UNDERWATER', 'dúo etiquetado|CHILD / KILLER',
     'trío etiquetado|KRAMPUS / GRYLA / ODIN', 'trío etiquetado|FETUS IN FETU / TERATOMA / STONE BABY'],
}
# Nivel de producción del interior del video, según los 3 fotogramas automáticos de cada video
PROD = {
 'ThePaintExplainer': 'Paint: monigotes y formas simples + fotos reales + títulos de sección',
 'SimplePaintOfficial': 'Paint: monigotes y formas simples + fotos reales + títulos de sección',
 'TeloPintoFacil': 'Paint con monigotes + fotos reales (antiguos); fondos pintados tipo IA + monigotes (recientes)',
 'SomeGuyWhoKnowsStuff': 'dibujo digital propio, personajes simples y colores planos',
 'thecrookedexplainer': 'mixto: monigotes + fotos y fragmentos reales con subtítulo + imágenes realistas tipo IA',
 'estrictamente': 'fondos pintados tipo IA + personajes simples + subtítulos animados palabra a palabra',
 'lichsungoaitruyen': 'ilustración vectorial detallada y constante + rótulos de fecha',
 'SquireExplains': 'animación vectorial con personajes articulados y mascota constante',
}
# Lectura de las 12 transcripciones (vidIQ, 27-oct-2026)
SCRIPT = {
 'CIYIefUvHq0': ('2ª persona en peligro inminente ("Imagine you\'re a knight...") + paradoja a los 15 s + pregunta central a los 28 s + promesa de volver a la escena',
                 'escena clímax al inicio → viaje cronológico "ahora eres X" por 5 épocas → regreso a la escena (Agincourt) → giro final al presente', 'ninguno'),
 'XuOxszx1TU0': ('premisa paradójica completa en la primera frase ("could never get wounded, because the doctors would find out she was a girl")',
                 'premisa → contexto → empatía ("Imagine...") → giro → diálogo → escalada de cifras → remate de una palabra ("Twice.")', 'ninguno'),
 'TfEYb9B4ovc': ('canción conocida + dato brutal concreto (apuñalado en 1628, la ciudad lo celebró) en 15 s',
                 'cuenta atrás 6→1; cada punto: canción → contexto con nombres y fechas → reinterpretación verso a verso → frase de cierre; el nº1 desmiente un mito', 'ninguno'),
 'PWsO1d05lnM': ('nombre del primer punto + figura ya conocida como oscura (Krampus); sin dato concreto en 15 s',
                 'lista de 7 sin numeración; más adjetivos que datos; menos nombres y fechas', 'suscripción a mitad (7:47)'),
 'rYhAHKZI_xQ': ('2ª persona en 1944 + objeto misterioso con nombre ("el cóctel nazi")',
                 'lista de sustancias no cronológica; cada una abre con una microescena en 2ª persona y cierra con un puente a la siguiente', 'ninguno'),
 'GerlkKMdGP8': ('nombre del primer punto + 2ª persona en el entrenamiento ("Son las 3 de la madrugada y estás temblando dentro del océano")',
                 'escalera de lo más conocido a lo más secreto (SEALs → CIA) con frases de escalada ("lo verdaderamente extremo empieza ahora")', 'suscripción + video siguiente al final'),
 'D0_gBZHx7R4': ('2ª persona hace 15.000 años sin fronteras + contraste con hoy + pregunta a los 48 s + "no empieza donde tú crees"',
                 'argumento cronológico por capas con muchos autores citados → resumen → cierre filosófico en 2ª persona', 'ninguno'),
 'Bs_DgBUJz_M': ('2ª persona moderna (padre con bebé llorando a las 2 a. m.) + 3 adelantos de lo que vendrá',
                 'lista de 8 "cosas" con promesas cumplidas una a una → cierre emocional dirigido al padre', 'ninguno'),
 'vikiJyJtZCs': ('sin gancho: "So, let\'s start. Number 10, black holes."',
                 'cuenta atrás 10→1, ~90 s por punto, tono humorístico y coloquial, remate de "terror" en cada punto', 'suscripción al final'),
 'yMwWSX_cvrc': ('sin introducción: nombre del primer lugar + detalle visual misterioso ("and they aren\'t buildings")',
                 'catálogo de 9 lugares; cada uno: imagen concreta → qué es → qué pasa si intentas entrar → detalle sorprendente', 'Discord al final'),
 'BmCDQHzWb9w': ('sin introducción: nombre + fecha y lugar exactos + detalle cotidiano + presagio ("solid ground")',
                 '6 casos reales narrados con suspense; uno de supervivencia en medio como respiro; remate trágico o irónico en cada uno', 'ninguno'),
 '481WMMxY8UY': ('fecha exacta + cifras (14 barcos, media hora, 450 cañones) + paradoja (100 km, 19 meses, ni 1 km) + héroe conocido',
                 'contexto → biografía → estrategia → "3 razones" → 3 intentos franceses → final con imagen de dos cementerios → avance del siguiente episodio', 'pantalla final al episodio anterior'),
}
SUP = re.compile(r"\b(worst|most|every|all|biggest|deadliest|rarest|strangest|craziest|scariest|luckiest|unluckiest|dumbest|insane|horrifying|entire|cada|tod[oa]s|peor(es)?|m[aá]s|mayor|letal)\b", re.I)

rows = list(csv.DictReader(open(sys.argv[1])))
cols = list(rows[0].keys()) + ['titulo_caracteres', 'titulo_pregunta', 'titulo_numero', 'titulo_superlativo_o_totalidad',
        'titulo_segunda_persona', 'sistema_miniatura', 'texto_miniatura', 'produccion_interior', 'transcrito', 'hook', 'estructura', 'llamada_a_la_accion']
w = csv.DictWriter(sys.stdout, fieldnames=cols); w.writeheader()
pos = {}
for r in rows:
    key = r['handle'] + ('/' + r['tab'] if r['handle'] == 'SquireExplains' else '')
    i = pos.get(key, 0); pos[key] = i + 1
    sysm, text = THUMB[key][i].split('|', 1)
    t = r['title']
    s = SCRIPT.get(r['id'])
    r.update(titulo_caracteres=len(t), titulo_pregunta='sí' if '?' in t else 'no', titulo_numero='sí' if re.search(r'\d', t) else 'no',
             titulo_superlativo_o_totalidad='sí' if SUP.search(t) else 'no', titulo_segunda_persona='sí' if re.search(r"\b(you|your|tú|tu|eres)\b", t, re.I) else 'no',
             sistema_miniatura=sysm, texto_miniatura=text, produccion_interior=PROD[r['handle']], transcrito='sí' if s else 'no',
             hook=s[0] if s else '', estructura=s[1] if s else '', llamada_a_la_accion=s[2] if s else '')
    w.writerow(r)
