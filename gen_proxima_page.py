# El Poder en Simple — genera proxima_eleccion.html a partir de template_proxima.html
# + proxima_eleccion_resultados.json (si no existe, se construye desde proxima_eleccion.json
# en estado "esperando"). Sin bases de datos.
import json, os, subprocess, sys
RES = '/home/user/proxima_eleccion_resultados.json'
if not os.path.exists(RES):
    subprocess.run([sys.executable, '/home/user/gen_proxima_eleccion.py'], check=True)
tpl = open('/home/user/template_proxima.html', encoding='utf-8').read()
data = open(RES, encoding='utf-8').read()
json.loads(data)
html = tpl.replace('/*__DATA__*/', data)
assert 'const DATA = {' in html
open('/home/user/proxima_eleccion.html', 'w', encoding='utf-8').write(html)
print(f'OK proxima_eleccion.html ({len(html):,} bytes)')
