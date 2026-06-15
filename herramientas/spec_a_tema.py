#!/usr/bin/env python3
"""Convierte specs JSON (datos/_specs/<slug>.json) en archivos de tema JS
(datos/temas/<slug>.js) para la web. Determinista: se puede re-ejecutar.
(Sustituye al antiguo generar_temas.py de la raíz.)

Uso:  python3 herramientas/spec_a_tema.py [slug ...]   (sin args: todos)
      --sin-aviso  no incluye el banner de "pendiente de verificación"

--- Contrato del spec (datos/_specs/<slug>.json) ---
{
  "slug": "...", "titulo": "...", "temaNum": 3, "lead": "html 1-2 frases",
  "lenguaje": "python",          # lenguaje por defecto de los bloques 'codigo' (-> class="lang-python").
                                 #   Carga en index.html el resaltador correspondiente. Por defecto "texto".
  "secciones": [
    { "titulo": "3.1 ...", "bloques": [
        {"tipo":"prosa",   "html":"<p>...</p>"},
        {"tipo":"lista",   "ordenada":false, "items":["html", ...]},
        {"tipo":"nota",    "html":"..."},
        {"tipo":"formula", "mathml":"<math ...>...</math>", "descripcion":"<p>..</p>"},
        {"tipo":"codigo",  "descripcion":"<p>..</p>", "codigo":"código en crudo (se escapa aquí)",
                           "lenguaje":"c"},   # opcional: anula el lenguaje del tema para ESTE bloque
        {"tipo":"registro","registro":"CTRL", "valor":"0x81"}        # monta visor-bits (si tu asignatura tiene registros)
    ]}
  ],
  "registros":   { "CTRL": {"titulo","nota","ancho","campos":[...]} },  # no pisa los ya curados en datos/registros.js
  "ejercicios":  { "id": {"titulo","enunciado","contexto","preguntas":[...]} },
  "ejerciciosEnTema": ["id", ...],   # se montan al final (componente ejercicio-driver)
  "tituloEjercicios": "Ejercicios",  # opcional: título de la sección de ejercicios (por defecto "Ejercicio(s)")
  "resumen": ["bullet html", ...]
}
"""
import html
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SPECS = RAIZ / "datos" / "_specs"
TEMAS = RAIZ / "datos" / "temas"


def esc(texto: str) -> str:
    """Escapa texto plano para incrustarlo en HTML (código)."""
    return html.escape(texto, quote=False)


def render_bloque(b: dict, lenguaje: str = "texto") -> str:
    t = b.get("tipo")
    if t == "prosa":
        return b.get("html", "")
    if t == "lista":
        tag = "ol" if b.get("ordenada") else "ul"
        items = "".join(f"<li>{it}</li>" for it in b.get("items", []))
        return f"<{tag}>{items}</{tag}>"
    if t == "nota":
        return f'<div class="nota">{b.get("html", "")}</div>'
    if t == "codigo":
        desc = b.get("descripcion", "")
        cod = esc(b.get("codigo", ""))
        lang = b.get("lenguaje") or lenguaje or "texto"
        return f'{desc}<pre><code class="lang-{lang}">{cod}</code></pre>'
    if t == "formula":
        desc = b.get("descripcion", "")
        ml = b.get("mathml", "")
        if "class=" not in ml.split(">", 1)[0]:
            ml = ml.replace("<math", '<math class="formula"', 1)
        return f"{desc}{ml}"
    if t == "registro":
        cfg = {"registro": b["registro"]}
        if b.get("valor") is not None:
            cfg["valor"] = b["valor"]
        if b.get("editables"):
            cfg["editables"] = b["editables"]
        cfg_json = json.dumps(cfg, ensure_ascii=False)
        return f'<div class="mpi-mount" data-componente="visor-bits" data-config=\'{cfg_json}\'></div>'
    return f'<p class="mpi-error">[bloque desconocido: {t}]</p>'


def render_tema(spec: dict, con_aviso: bool) -> str:
    partes = []
    lenguaje = spec.get("lenguaje") or "texto"
    partes.append('<header class="tema-cab">')
    partes.append(f'<span class="tema-num">Tema {spec["temaNum"]}</span>')
    partes.append(f'<h1>{spec["titulo"]}</h1>')
    if spec.get("lead"):
        partes.append(f'<p class="tema-lead">{spec["lead"]}</p>')
    partes.append("</header>")
    if con_aviso:
        partes.append('<div class="nota">⚠ Borrador generado automáticamente; '
                      "pendiente de la revisión técnica final contra la fuente de verdad.</div>")

    for sec in spec.get("secciones", []):
        partes.append("<section>")
        partes.append(f'<h2>{sec["titulo"]}</h2>')
        for b in sec.get("bloques", []):
            partes.append(render_bloque(b, lenguaje))
        partes.append("</section>")

    en_tema = spec.get("ejerciciosEnTema") or []
    if en_tema:
        partes.append("<section>")
        titulo_ej = spec.get("tituloEjercicios") or ("Ejercicios" if len(en_tema) > 1 else "Ejercicio")
        partes.append(f"<h2>{titulo_ej}</h2>")
        for ref in en_tema:
            cfg = json.dumps({"ref": ref}, ensure_ascii=False)
            partes.append(f'<div class="mpi-mount" data-componente="ejercicio-driver" data-config=\'{cfg}\'></div>')
        partes.append("</section>")

    if spec.get("resumen"):
        partes.append('<section class="tema-cierre"><h2>Resumen</h2><ul>')
        for punto in spec["resumen"]:
            partes.append(f"<li>{punto}</li>")
        partes.append("</ul></section>")

    return "\n".join(partes)


def generar(slug: str, con_aviso: bool) -> None:
    spec = json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))
    html_tema = render_tema(spec, con_aviso)

    out = []
    out.append("/*")
    out.append(f" * Contenido del tema \"{spec['titulo']}\" (Tema {spec['temaNum']}).")
    out.append(" * GENERADO por herramientas/spec_a_tema.py desde datos/_specs/"
               f"{slug}.json — no editar a mano; edita el spec y regenera.")
    out.append(" */")
    out.append("window.MPI = window.MPI || {};")
    out.append("MPI.contenidoTemas = MPI.contenidoTemas || {};")
    out.append("MPI.ejercicios = MPI.ejercicios || {};")
    out.append("MPI.registros = MPI.registros || {};")
    out.append("")

    for nombre, reg in (spec.get("registros") or {}).items():
        reg = dict(reg)
        reg.setdefault("nombre", nombre)
        out.append(f"if (!MPI.registros[{json.dumps(nombre)}]) "
                   f"MPI.registros[{json.dumps(nombre)}] = {json.dumps(reg, ensure_ascii=False)};")
    for ref, ej in (spec.get("ejercicios") or {}).items():
        out.append(f"MPI.ejercicios[{json.dumps(ref)}] = {json.dumps(ej, ensure_ascii=False)};")

    out.append("")
    out.append(f"MPI.contenidoTemas[{json.dumps(slug)}] = {{")
    out.append(f"  titulo: {json.dumps(spec['titulo'], ensure_ascii=False)},")
    out.append(f"  html: {json.dumps(html_tema, ensure_ascii=False)}")
    out.append("};")

    destino = TEMAS / f"{slug}.js"
    destino.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"OK  {destino.relative_to(RAIZ)}  ({destino.stat().st_size} bytes)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    con_aviso = "--sin-aviso" not in sys.argv
    slugs = args or sorted(p.stem for p in SPECS.glob("*.json"))
    for s in slugs:
        generar(s, con_aviso)
