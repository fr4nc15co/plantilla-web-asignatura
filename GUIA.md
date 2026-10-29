# Plantilla de web interactiva por temas — Guía

Esqueleto reutilizable para construir una **web de estudio por temas** de cualquier
asignatura: teoría + visualizadores + simuladores + ejercicios autocorregidos.
Es el mismo motor con el que se hizo la web de *Microprocesadores (PIC32MX)*; aquí
viene **sin contenido**, listo para clonar y rellenar con otra asignatura.

## Filosofía (no la rompas y todo será fácil)

- **Sin build, sin frameworks, sin CDN.** HTML/CSS/JS plano. No hace falta Node.
- **Funciona en dos sitios sin tocar nada:** con doble clic (`file://`) y publicada en
  **GitHub Pages**. Como `file://` bloquea `fetch()` de archivos locales, **el contenido
  va “horneado” en archivos `.js`** que se cargan con `<script>` (no se usa `fetch`).
- **El contenido se escribe en specs JSON** (`datos/_specs/`) y un conversor de Python lo
  traduce a los `.js` de los temas. Editas el JSON, regeneras, listo.
- **Namespace único `window.MPI`.** Scripts clásicos (sin `import`/módulos ES).

## Cómo se ejecuta

- **Para usarla:** doble clic en `index.html` (o publícala en GitHub Pages). Nada más.
- **Para desarrollar:** `python3 herramientas/servidor_dev.py 8765` y abre
  `http://127.0.0.1:8765`. (Ese servidor sirve sin caché, así ves los `.js` recién
  regenerados; con doble clic o un `http.server` normal el navegador cachea y te vuelves loco.)
- **Requisitos:** solo **Python 3.7+** (las herramientas usan únicamente la biblioteca
  estándar: `html`, `json`, `sys`, `pathlib`, `http.server`). **Sin `pip`, sin `venv`, sin
  `requirements.txt`, sin Node.** El propio sitio (HTML/CSS/JS plano) no necesita nada.

---

## 1. Estructura de archivos

```
index.html                      Lista los <script> en orden y arranca todo
assets/
  css/estilos.css               Tema oscuro IDE + estilos de TODOS los componentes  [GENÉRICO]
  js/
    app.js                      Router (#hash) + montaje de componentes + portada    [GENÉRICO*]
    examen.js                   Modo examen: test aleatorio con nota                 [GENÉRICO]
    buscador.js                 Buscador global (Ctrl+K)                             [GENÉRICO]
    resaltar-c.js               Resaltador de sintaxis C       (elige uno en index)  [ELIGE]
    resaltar-py.js              Resaltador de sintaxis Python  (elige uno en index)  [ELIGE]
    temas.js                    Registro ordenado de temas {num, slug, titulo, ...}  [TU CONTENIDO]
    componentes/
      visor-bits.js             Visor interactivo de registros de bits (si aplica)   [GENÉRICO]
      ejercicio-driver.js       Ejercicio de opciones con feedback                   [GENÉRICO]
      <los tuyos>.js            Simuladores específicos de tu asignatura             [TU CONTENIDO]
datos/
  registros.js                  Definiciones de registros para visor-bits (opcional) [TU CONTENIDO]
  _specs/<slug>.json            FUENTE de cada tema (lo que editas)                  [TU CONTENIDO]
  temas/<slug>.js               Generado por el conversor (NO editar a mano)         [GENERADO]
herramientas/
  spec_a_tema.py                Conversor specs JSON -> temas .js                    [GENÉRICO]
  servidor_dev.py               Servidor de desarrollo sin caché                     [GENÉRICO]
```

`[GENÉRICO]` = reutilízalo tal cual. `app.js*` solo tiene 2 cosas que tocar: el bloque
`MPI.config` del principio (título/subtítulo) y, si quieres, las secciones de portada
(podcast, referencias) que vienen comentadas. `[ELIGE]` = la plantilla trae resaltador de
**C** y de **Python**; carga en `index.html` el del lenguaje de tu asignatura (debe casar
con el campo `"lenguaje"` del spec, §3) y declara ese lenguaje en cada spec. Si no usas
código, quita la línea: `app.js` ya comprueba `if (MPI.resaltarTodo)`. ¿Otro lenguaje?
Copia `resaltar-py.js`, cambia las palabras clave, y declara `"lenguaje"` acorde.
`visor-bits.js`/`registros.js` solo hacen falta si tu asignatura tiene **registros de bits**
(p. ej. un micro); si no, bórralos del `index.html`.

---

## 2. Arranque rápido para una asignatura nueva

0. **Rellena la *ficha de la asignatura* (§5, Fase 0) ANTES de escribir nada.** Es el paso
   que más errores ahorra: fija lenguaje, plataforma, fuente de verdad, recorte y branding.
   La plantilla es **agnóstica de lenguaje y plataforma**; no des por hecho que es C/PIC32
   (su origen) ni Python: pregúntalo y decídelo explícitamente.
1. **Copia esta carpeta** y renómbrala.
2. **`index.html`:** cambia `<title>`, el chip y nombre de la marca, y el pie. Deja cargado
   **solo el resaltador de tu lenguaje** (`resaltar-c.js` o `resaltar-py.js`); si no hay
   código o no hay registros, quita esas líneas (resaltador, `visor-bits.js`, `registros.js`).
3. **`assets/js/app.js`:** edita `MPI.config` (título, subtítulo, `mostrarExamen`).
4. **`assets/js/temas.js`:** define tus temas (uno por línea). Pon `disponible:false` en
   los que aún no existan (saldrán como “pronto”).
5. **Escribe el primer tema:** crea `datos/_specs/<slug>.json` (copia `ejemplo-tema.json`
   como plantilla), pon su `"lenguaje"` (§3), y añade su `<script src="datos/temas/<slug>.js">`
   en `index.html`. **Un tema no está “hecho” hasta tener su(s) interactivo(s) montado(s)**
   (§4), no solo teoría.
6. **Genera:** `python3 herramientas/spec_a_tema.py` (todos) o `... <slug>` (uno).
7. **Verifica:** `python3 herramientas/servidor_dev.py 8765` y abre el navegador.
8. Borra el `ejemplo-tema` (spec, .js, su `<script>` y su línea en `temas.js`) cuando no lo necesites.

El **`ejemplo-tema`** incluido es una demo viva del formato: ábrelo en el navegador y lee
su spec a la vez. Cubre todos los tipos de bloque.

---

## 3. El formato del spec (el contrato)

Un tema es un JSON en `datos/_specs/<slug>.json`:

```jsonc
{
  "slug": "mi-tema",            // = nombre del archivo, sin .json
  "titulo": "Título del tema",
  "temaNum": 1,
  "lenguaje": "python",         // lenguaje de los bloques 'codigo' (-> class="lang-python"). Por defecto "texto".
  "lead": "Entradilla en HTML, 1-2 frases.",
  "secciones": [
    { "titulo": "1.1 ...", "bloques": [ /* ver tipos abajo */ ] }
  ],
  "registros": { /* opcional: defs de registros para los bloques 'registro' */ },
  "ejercicios": { "id": { "titulo","enunciado","contexto","preguntas":[...] } },
  "ejerciciosEnTema": ["id", ...],   // se montan al final del tema
  "tituloEjercicios": "Ejercicios", // opcional: rótulo de esa sección (por defecto "Ejercicio(s)")
  "resumen": ["bullet en HTML", ...]
}
```

**Tipos de bloque** (dentro de `secciones[].bloques[]`):

| tipo | campos | qué hace |
|---|---|---|
| `prosa` | `html` | HTML libre (párrafos, listas, **tablas** con `<table class="tabla-datos">`) |
| `lista` | `ordenada` (bool), `items` (array de HTML) | viñetas o lista numerada |
| `nota` | `html` | recuadro destacado |
| `codigo` | `descripcion` (HTML), `codigo` (texto crudo), `lenguaje` (opcional, anula el del tema) | bloque de código (se escapa solo; `class="lang-<lenguaje>"`) |
| `formula` | `descripcion` (HTML), `mathml` | fórmula en MathML nativo |
| `registro` | `registro` (nombre), `valor` (hex) | monta `visor-bits` con ese registro |

Para **montar cualquier otro componente**, usa un bloque `prosa` con un `<div>` de montaje
(ver §4). En `registros` defines los registros locales del tema (no pisa los ya curados en
`datos/registros.js`). Cada ejercicio de `ejercicios` tiene `preguntas`, y cada pregunta:
`texto`, `opciones` (array), `correcta` (índice 0-based), `explicacion` (HTML).

> **Regla de oro de las fórmulas:** MathML nativo, no LaTeX/KaTeX — así funciona offline
> sin librerías. El conversor añade `class="formula"` automáticamente.

---

## 4. Crear un componente interactivo

El patrón (mira `visor-bits.js` o `ejercicio-driver.js` como ejemplos completos):

**a) Escribe `assets/js/componentes/mi-sim.js`:**

```js
window.MPI = window.MPI || {};
MPI.componentes = MPI.componentes || {};
(function () {
  MPI.componentes['mi-sim'] = function (el, cfg) {
    // 'el' es el <div> contenedor; 'cfg' es el data-config ya parseado (objeto).
    el.classList.add('mpi-mi-sim');
    el.innerHTML = '<div class="mpi-sim-cab">Mi simulador</div>' +
                   '<input type="range" min="0" max="100" value="50">' +
                   '<div class="ms-out"></div>';
    var sl = el.querySelector('input');
    function pintar() { el.querySelector('.ms-out').textContent = 'valor = ' + sl.value; }
    sl.addEventListener('input', pintar);
    pintar();
  };
})();
```

**b) Regístralo en `index.html`** (en el bloque de componentes):
`<script src="assets/js/componentes/mi-sim.js"></script>`

**c) Añade su CSS** al final de `assets/css/estilos.css` (usa las variables `--bg`, `--acento`,
`--mono`… para que case con el tema).

**d) Móntalo** desde un bloque `prosa` del spec:
`<div class="mpi-mount" data-componente="mi-sim" data-config='{\"min\":0}'></div>`

`app.js` busca todos los `.mpi-mount`, lee `data-componente` y `data-config`, y llama a
`MPI.componentes[nombre](el, cfg)`. Si el componente genera código, llama a
`MPI.resaltarTodo(el)` al final para resaltarlo.

**Los interactivos NO son un extra que se deja para el final: son el contenido.** Una web
que es solo teoría + fórmulas se percibe como "vacía" (lección real: pasó en la primera
asignatura). Trata cada tema como **incompleto hasta que tiene su(s) simulador(es)
montado(s)** dentro de sus secciones —no en una tanda final—. El catálogo de interactivos
se decide en la Fase 1 (§5) y se construye tema a tema, junto con la teoría.

**Consejos** (de la experiencia construyendo estas webs): haz que el componente sea
*coherente con un ejemplo del temario* (mismos números, mismos resultados), añade un modo
“paso a paso” para los algoritmos, y verifica siempre en el navegador con `preview`/consola
tras montarlo. Antes de inventar uno desde cero, mira si **otra asignatura ya tiene un
componente reutilizable** (su CSS y su patrón son los mismos): copiar y adaptar texto/datos
es mucho más rápido.

---

## 5. Flujo con IA: del material de origen a los temas verificados

Así se construyó el contenido de estas webs, y es lo más reutilizable. Cada fase tiene su
**plantilla de prompt** (cópiala y rellena los `{...}`).

### Qué modelo usar en cada fase

El gasto no se reparte por igual: **las fases 2 y 3 son el 80-90 % del total** (N temas ×
corpus), mientras que la ficha, el mapa y la orquestación son ruido presupuestario — ahí usa
siempre el modelo bueno.

| Fase / tarea | Modelo | Effort | Por qué |
|---|---|---|---|
| **0** Ficha de la asignatura | Opus 5.5 | medium | Pocos tokens, pero cada error se propaga a los N temas. |
| **0.5** Docling, inventario del material | Haiku 5.5 | low | Mecánico y verificable a ojo. |
| **0.5** Diagnóstico de qué quedó corrupto | Sonnet 5.5 | high | Lectura larga, juicio acotado. |
| **1** Mapa del corpus | Opus 5.5 | xhigh | Un solo tiro del que cuelga todo lo demás. Fable 5.1 si el corpus es enorme o se contradice. |
| **2** Autoría de un spec (×N) | Sonnet 5.5 | high | El grueso del gasto, y con verificación detrás. **Opus 5.5** en temas con MathML, tablas numéricas, registros o código real. |
| **3** Verificación adversarial (×N) | Opus 5.5 | xhigh | Resolver ejercicios y recalcular tablas es razonamiento puro, y es la última línea de defensa. Fable 5.1 si hay tabla de referencia crítica. **Haiku aquí no.** |
| **4** Interactivos | Opus 5.5 | high | Código + pedagogía + depuración en navegador. Sonnet 5.5 para componentes triviales (slider → salida). |
| **5** Contraste con transparencias | Sonnet 5.5 | high | Dos documentos largos, salida en informe, sin editar. |
| Regenerar, integrar, checklist §7 | Haiku 5.5 | low | Determinista y comprobable. |
| Verificar en el navegador | Haiku 5.5 | low | Sonnet 5.5 si hay que diagnosticar por qué no monta. |
| Publicar en GitHub Pages (§6) | Haiku 5.5 | low | Secuencia de `git`. |
| Orquestación (sesión principal) | Opus 5.5 | — | Decide qué se relanza y qué se da por bueno. |

IDs y precio por millón de tokens (entrada/salida): `claude-haiku-5-5` ($0,10/$0,50),
`claude-sonnet-5-5` ($2/$10), `claude-opus-5-5` ($4/$20, el modelo por defecto),
`claude-fable-5-1` ($10/$50). En Claude Code se eligen con `/model`; en el workflow, con
`opts.model` (`'haiku'`, `'sonnet'`, `'opus'`, `'fable'`).

**Cuatro reglas que cambian la decisión:**

1. **Sube el effort antes de bajar de modelo.** Sonnet 5.5 a `xhigh` suele salir mejor y más
   barato que Opus a `medium`. Y ojo: el effort por defecto de Opus 5.5 es `medium`, no
   `high`; si no lo pones explícito, pagas Opus y recibes menos de lo que crees.
2. **El salto Opus/Sonnet ya solo es 2×** ($4/$20 frente a $2/$10). Si los temas son
   técnicos, escribir bien a la primera sale más barato que una Fase 3 que corrige mucho.
3. **No mezcles modelos entre autores de temas distintos.** La caché de prompt es *por
   modelo*: si abanicas 10 temas sobre el mismo corpus, un solo modelo para todos los autores
   reutiliza la caché; mezclarlos la rompe. Saca del lote solo el tema excepcional.
4. **Autor ≠ verificador aunque coincida el modelo.** El valor de la Fase 3 está en el
   contexto limpio —un agente que no escribió el spec—, y el verificador nunca va por debajo
   del autor.

### Fase 0 — Ficha de la asignatura (decídela y guárdala ANTES de escribir)
Este es el paso que más errores ahorra. La plantilla **no es C/PIC32 ni Python por
defecto**: es agnóstica, y su origen (micros) no debe condicionar la asignatura nueva. Antes
de escribir contenido, establece y **confirma con el usuario** estas decisiones, y guárdalas
en un artefacto (`ficha-asignatura.json` o una memoria del proyecto) para no re-preguntarlas
ni derivar:

1. **Plataforma / hardware** y **lenguaje de programación** (→ qué resaltador cargar y qué
   poner en `"lenguaje"`). **¿Hay registros de bits** que merezcan `visor-bits`, o no aplica
   (y se borran `visor-bits.js`/`registros.js`)?
2. **Autoridad del temario y recorte:** ¿quién define lo vigente —transparencias, programa—?
   ¿Qué partes del libro **ya NO se dan** (fuera o "ampliación opcional")?
3. **Fuente de verdad** para datos/fórmulas/código (datasheet, libro oficial, normas…).
4. **Interactivos incrustados** en cada tema desde el principio (asume que sí; §4).
5. **División de temas** (p. ej. ¿un tema grande se parte en 9a/9b?).
6. **Branding:** título, subtítulo, chip, institución, pie.
7. **Modo examen** sí/no y **créditos** (autor del libro, autor de las transparencias).

> Pregunta lo que no esté claro en el material **antes** de la Fase 1; las respuestas
> condicionan slugs, lenguaje, recorte y qué componentes-base sobran.

### Fase 0.5 — Preparar el material
Pasa los PDF (apuntes, transparencias, exámenes, datasheets) a Markdown + figuras (p. ej.
con **Docling**). Aviso: la conversión corrompe a menudo lo técnico (código en una línea,
tablas con basura, fórmulas perdidas). **Estrategia de dos fuentes:** usa el Markdown para
la *estructura y la prosa*, pero **reconstruye los datos críticos** (fórmulas, tablas,
código, valores) desde la *fuente de verdad* (el datasheet / libro oficial), no desde el
Markdown corrupto.

### Fase 1 — Mapa del corpus (1 agente)
> Eres analista de contenido docente. Te paso el material de la asignatura **{ASIGNATURA}**
> en `{CARPETA_CONTENIDO}` (apuntes, transparencias, exámenes). Léelo y devuélveme:
> (1) una **arquitectura de N temas** (slug, título, qué entra en cada uno), respetando que
> **el temario lo definen {LAS_TRANSPARENCIAS/EL_PROGRAMA}** — lo que no toquen, fuera o como
> “ampliación opcional”; (2) por cada tema, un **catálogo de interactivos** candidatos
> (visualizadores, simuladores, ejercicios) priorizados por valor pedagógico; (3) qué partes
> del material están corruptas y cuál es la **fuente de verdad** para reconstruir los datos.
> No escribas contenido todavía. Devuelve un JSON con el mapa.

### Fase 2 — Autoría de un tema (1 agente por tema, en paralelo)
> Eres autor de contenido docente de **{ASIGNATURA}**. Escribe el spec
> `datos/_specs/{SLUG}.json` siguiendo EXACTAMENTE el contrato de `GUIA.md §3`
> (bloques prosa/lista/nota/codigo/formula/registro; + registros, ejercicios,
> ejerciciosEnTema, resumen). Fuentes, por orden de autoridad: **{FUENTE_DE_VERDAD}**
> (datos, fórmulas, código) y las transparencias (qué entra y con qué enfoque). Reglas:
> ciñe el alcance a lo que vea el temario vigente; reconstruye fórmulas/código/tablas desde
> la fuente de verdad, NO desde el Markdown corrupto; las fórmulas en MathML nativo; incluye
> 1-2 ejercicios inspirados en los exámenes. Devuelve solo el archivo escrito.

### Fase 3 — Verificación adversarial (1 agente por tema)
> Eres revisor técnico adversarial. Lee `datos/_specs/{SLUG}.json` y la fuente de verdad
> **{FUENTE_DE_VERDAD}**. Comprueba con desconfianza: valores y campos de registros,
> sintaxis y corrección del código, fórmulas (MathML válido) y validez del JSON. Además,
> con especial cuidado (aquí es donde se cuelan los errores):
> - **Ejercicios — coherencia, no solo el índice:** *resuelve tú mismo* cada ejercicio y
>   verifica que `enunciado`, `contexto`, `explicacion` y la opción `correcta` son
>   **lógica y físicamente coherentes entre sí** (un `correcta` correcto con una explicación
>   que se contradice es un error grave).
> - **Números — reprodúcelos:** **recalcula** cada tabla y cada ejemplo numérico y compáralo
>   con los valores de la fuente; si hay una tabla de referencia, debe cuadrar cifra a cifra
>   (vigila constantes como β, T₀, unidades).
> - **Numeración y alcance:** la numeración de secciones coincide con la fuente, sin saltos;
>   y no se ha colado contenido fuera del recorte de la ficha (Fase 0).
>
> **Corrige los errores en el propio archivo** (Edit/Write). Devuelve: nivel de confianza
> (alta/media/baja), lista de correcciones aplicadas y errores graves encontrados.

### Fase 4 — Interactivos del tema (no opcional; ver §4)
Por cada tema, construye los componentes de su catálogo (Fase 1): un JS en
`assets/js/componentes/`, su `<script>` en `index.html`, su CSS al final de `estilos.css`, y
el montaje (`.mpi-mount`) en la sección correspondiente del spec. Cada componente debe
reproducir un ejemplo del temario con los **mismos números**. **Un tema no se da por
terminado sin sus interactivos** (esto evita el "no veo contenido").

### (Opcional) Fase 5 — Contraste con las transparencias
> Compara `datos/temas/{SLUG}.js` con sus transparencias en `{CARPETA}`. Devuelve, sin
> editar: (A) temas de las slides que faltan o están infra-tratados; (B) contenido de la web
> que no está en las slides (candidato a “ampliación opcional”); (C) discrepancias de
> valores/fórmulas/nomenclatura; (D) ejemplos/ejercicios de las slides que merezca incorporar.

**Después de cada fase de escritura:** `python3 herramientas/spec_a_tema.py --sin-aviso` para
regenerar los `.js`, integra los temas nuevos en `temas.js` e `index.html`, y verifica en el
navegador que renderizan sin `.mpi-error` ni errores de consola, y que los interactivos
montan e interactúan con los valores correctos.

> **Lección operativa:** los flujos largos de muchos agentes pueden morir por límites de
> sesión. Como el estado vive en disco (specs JSON) y el conversor es determinista y
> re-ejecutable, siempre puedes retomar e integrar resultados parciales sin perder nada.

### Orquestación automática (opcional)
Las fases 2 y 3 se pueden **abanicar a la vez** con la herramienta `Workflow` de Claude Code,
en vez de lanzar los agentes a mano. La plantilla incluye el guion
**`herramientas/flujo_contenido.workflow.js`**: un `pipeline()` autor→verificador por tema
(cada tema avanza independiente). Rellena `ASIGNATURA`, `CARPETA_FUENTE` y `FUENTE_VERDAD`,
pasa los temas en `args` y lánzalo con la tool `Workflow` (requiere opt-in explícito). Los
**modelos** ya vienen fijados por agente (`MODELO_AUTOR`/`MODELO_VERIFICADOR` → `opts.model`)
según la tabla de arriba. Es solo la orquestación; los prompts son los de arriba. Para hacerlo a mano (sin
workflow), no necesitas este archivo — basta con copiar los prompts de §5.

---

## 6. Publicar en GitHub Pages

```bash
cd <tu-carpeta>
git init && git add . && git commit -m "Web de la asignatura"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>
git push -u origin main
# En GitHub: Settings -> Pages -> Branch: main -> Save
```

Queda en `https://<usuario>.github.io/<repo>/`. **No subas** el material de origen pesado:
crea un `.gitignore` con `contenido/`, `.venv/`, `.DS_Store`, etc. La web solo necesita
`index.html`, `assets/` y `datos/`.

---

## 7. Checklist al añadir un tema

- [ ] `datos/_specs/<slug>.json` escrito según §3
- [ ] `python3 herramientas/spec_a_tema.py <slug>` ejecutado
- [ ] `<script src="datos/temas/<slug>.js">` añadido en `index.html`
- [ ] línea del tema en `assets/js/temas.js` (con `disponible:true`)
- [ ] verificado en el navegador: sin `.mpi-error`, consola limpia
- [ ] componentes nuevos: JS en `componentes/` + `<script>` + CSS + montaje
