#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera calendario_votaciones.json: todas las votaciones de leyes de 2026 con el
voto nominal de cada diputad@ (a favor S / en contra N / abstención A; el resto =
ausente), más el nombre oficial de cada boletín. Sin base de datos: JSON en disco.

Fuentes (Mirada al Congreso sobre datos abiertos oficiales de la Cámara):
  · api/votacionesxano     → todas las votaciones del año
  · api/votacionesDetalle  → voto de cada diputad@ en una votación (param=id)
  · api/votaciones         → nombre oficial del proyecto (param=boletín)
"""
import json, time, datetime, urllib.request, sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

NS = {'c': 'http://opendata.camara.cl/camaradiputados/v1'}
UA = {'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36'}
SALIDA = '/home/user/calendario_votaciones.json'
ANIO = 2026


def post(url, payload, timeout=30, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=UA)
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception as e:
            last = e
            time.sleep(1 + i)
    raise last


def votaciones_anio():
    raw = post('https://www.miradaalcongreso.com/api/votacionesxano', {'param': ANIO}, timeout=60)
    root = ET.fromstring(raw)
    filas = []
    for v in root.findall('c:Votacion', NS):
        def g(t):
            e = v.find('c:' + t, NS)
            return (e.text or '').strip() if e is not None else ''
        filas.append({'id': g('Id'), 'desc': g('Descripcion'), 'fecha': g('Fecha'),
                      'resultado': g('Resultado'), 'tipo': g('Tipo'),
                      'si': int(g('TotalSi') or 0), 'no': int(g('TotalNo') or 0),
                      'abst': int(g('TotalAbstencion') or 0)})
    return filas


_cache_nombres = {}
def nombre_boletin(bol):
    if bol in _cache_nombres:
        return _cache_nombres[bol]
    nom = None
    try:
        r = post('https://www.miradaalcongreso.com/api/votaciones', {'param': bol}, timeout=25, tries=2)
        n = ET.fromstring(r).find('c:Nombre', NS)
        if n is not None and n.text:
            nom = (n.text or '').strip()
    except Exception:
        pass
    _cache_nombres[bol] = nom
    return nom


def detalle_nominal(v):
    """Devuelve (id, {'S':[ids],'N':[ids],'A':[ids]}) o (id, None)."""
    try:
        raw = post('https://www.miradaalcongreso.com/api/votacionesDetalle', {'param': int(v['id'])})
        root = ET.fromstring(raw)
        nv = root.find('c:Votos', NS)
        OP = {'1': 'S', '0': 'N', '2': 'A'}
        out = {'S': [], 'N': [], 'A': []}
        if nv is not None:
            for vo in nv.findall('c:Voto', NS):
                op = OP.get(vo.find('c:OpcionVoto', NS).attrib.get('Valor'))
                idc = vo.find('c:Diputado', NS).find('c:Id', NS).text
                if op and idc:
                    out[op].append(str(idc))
        return v['id'], out
    except Exception as e:
        print(f'    [fallo detalle {v["id"]}: {e}]', flush=True)
        return v['id'], None


def main():
    print('1/4 votaciones del año…', flush=True)
    filas = votaciones_anio()
    print(f'  {len(filas)} votaciones', flush=True)
    leys = [f for f in filas if f['tipo'] == 'Proyecto de Ley' and f['desc'].startswith('Boletín')]
    print(f'2/4 votos nominales de {len(leys)} votaciones de ley…', flush=True)
    nominales, ok = {}, 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(detalle_nominal, v): v for v in leys}
        for fut in as_completed(futs):
            vid, votos = fut.result()
            nominales[vid] = votos
            ok += votos is not None
            if ok % 50 == 0:
                print(f'  …{ok}/{len(leys)}', flush=True)
    print(f'  nominales OK: {ok}/{len(leys)}', flush=True)
    print('3/4 nombres oficiales de boletines…', flush=True)
    bols = sorted({f['desc'].replace('Boletín N° ', '') for f in filas if f['desc'].startswith('Boletín')})
    nombres = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(nombre_boletin, b): b for b in bols}
        for fut in as_completed(futs):
            b = futs[fut]
            try:
                n = fut.result()
                if n:
                    nombres[b] = n
            except Exception:
                pass
    print(f'  con nombre: {len(nombres)}/{len(bols)}', flush=True)
    out = {'fuente': {'organismo': 'Cámara de Diputadas y Diputados (datos abiertos oficiales, vía Mirada al Congreso)',
                      'anio': ANIO,
                      'descargado': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                      'nota': 'S = a favor · N = en contra · A = abstención; l@s demás diputad@s en ejercicio no votaron (ausencia/pareo)'},
           'votaciones': [], 'nombres': nombres}
    for f in filas:
        bol = f['desc'].replace('Boletín N° ', '') if f['desc'].startswith('Boletín') else None
        out['votaciones'].append({
            'id': f['id'], 'fecha': f['fecha'][:10], 'tipo': f['tipo'],
            'resultado': f['resultado'], 'desc': f['desc'],
            'boletin': bol, 'titulo': nombres.get(bol),
            'si': f['si'], 'no': f['no'], 'abst': f['abst'],
            'nominal': nominales.get(f['id'])})
    json.dump(out, open(SALIDA, 'w'), ensure_ascii=False)
    print(f'OK {SALIDA} · {len(out["votaciones"])} votaciones · '
          f'{sum(1 for v in out["votaciones"] if v["nominal"])} con voto nominal', flush=True)


if __name__ == '__main__':
    main()
