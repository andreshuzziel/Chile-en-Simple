# El Poder en Simple — genera elecciones_chile.html (dashboard electoral estilo Decide Chile)
# Sin bases de datos: todo sale del snapshot oficial elecciones_resultados.json (Servel)
# y de la geografía horneada elecciones_geografia.json (opcional: sin ella la página
# cae al mapa de franjas, nunca se rompe).
import json

with open('/home/user/template_elecciones.html', encoding='utf-8') as f:
    tpl = f.read()
with open('/home/user/elecciones_resultados.json', encoding='utf-8') as f:
    data = f.read()

try:
    with open('/home/user/elecciones_geografia.json', encoding='utf-8') as f:
        json.load(f)  # validar antes de inyectar
    with open('/home/user/elecciones_geografia.json', encoding='utf-8') as f:
        geom = f.read().strip()
except FileNotFoundError:
    geom = 'null'

html = tpl.replace('/*__DATA__*/', data)
html = html.replace('/*__GEOM__*/', geom)
assert 'const DATA = {' in html, 'no se inyectó el JSON'
assert 'const GEOM =' in html, 'falta el ancla GEOM en el molde'
with open('/home/user/elecciones_chile.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f'OK elecciones_chile.html ({len(html):,} bytes)')
