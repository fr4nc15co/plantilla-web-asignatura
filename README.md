# Web interactiva de estudio por temas — plantilla reutilizable

Esqueleto para construir una **web de estudio por temas** de cualquier asignatura
(teoría + visualizadores + simuladores + ejercicios autocorregidos). Sin build, sin
dependencias: funciona con doble clic (`file://`) y publicada en GitHub Pages.

El manual completo está en **[`GUIA.md`](GUIA.md)**. Este README es solo el **arranque**:
qué subir y qué prompt dar a Claude Code para que lo construya con otra asignatura.

---

## Cómo empezar (3 pasos)

### 1. Copia esta carpeta
Duplícala y renómbrala con el nombre de tu asignatura. Ábrela en Claude Code.

### 2. Sube tu contenido a `contenido/`  ← imprescindible
Claude necesita el material de la asignatura para escribir los temas. Crea una carpeta
`contenido/` y mete dentro, organizado por tipo, **lo que tengas**:

```
contenido/
  Apuntes/         libro o apuntes de teoría
  Transparencias/  las diapositivas de clase  (DEFINEN el temario vigente)
  Examenes/        exámenes, mejor si son resueltos (para los ejercicios)
  Referencia/      datasheet, manual oficial, normas…  (la "fuente de verdad")
```

- **Formato:** lo ideal es pasar los PDF a **Markdown + figuras** (p. ej. con
  [Docling](https://github.com/docling-project/docling)) y subir los `.md`. Si no, sube los
  PDF directamente: Claude Code puede leerlos, aunque el Markdown se maneja mejor.
- **Aviso:** la conversión a Markdown suele corromper lo técnico (código en una línea, tablas
  con basura, fórmulas perdidas). Por eso conviene incluir la **fuente de verdad** (datasheet /
  manual oficial): los datos, fórmulas y código se reconstruyen de ahí, no del Markdown.
- `contenido/` no se publica (está en `.gitignore`); solo se usa para generar los temas.

### 3. Pega este prompt a Claude Code
Rellena los `{...}` y envíalo:

> Quiero construir una **web interactiva de estudio por temas** para la asignatura
> **{ASIGNATURA}** ({titulación/centro}), usando esta plantilla. Lee primero **`GUIA.md`**
> y sigue su metodología y su formato de spec al pie de la letra.
>
> El material está en **`contenido/`** (apuntes, transparencias, exámenes y la referencia
> oficial). Reglas:
> - **Plataforma y lenguaje:** es **{hardware/plataforma}** y **{lenguaje de programación}**.
>   No asumas el origen de la plantilla (micros/C): carga el resaltador de mi lenguaje y
>   declara `"lenguaje"` en los specs. {¿Hay registros de bits que merezcan `visor-bits`, o
>   no aplica y se borran `visor-bits.js`/`registros.js`?}
> - El **temario vigente lo definen {las transparencias / el programa}**: lo que no toquen,
>   fuera (o como “ampliación opcional”). {Indica aquí lo que YA NO se da, si aplica.}
> - La **fuente de verdad** para datos, fórmulas y código es **{datasheet / manual oficial:
>   nombre}**; reconstrúyelos de ahí, no del Markdown corrupto.
> - Fórmulas en **MathML nativo**; todo debe funcionar **offline y en GitHub Pages**.
>
> Hazlo en estas fases (de `GUIA.md §5`), parándote a que yo valide entre ellas:
> 0. **Ficha de la asignatura:** confírmame plataforma/lenguaje, autoridad del temario y
>    recorte, fuente de verdad, branding (título/chip/pie), modo examen y créditos, y
>    guárdalo. NO escribas contenido hasta tener esto claro.
> 1. **Mapa del corpus:** léete el material y propón una **arquitectura de temas** (slug,
>    título, qué entra) y un **catálogo de interactivos** candidatos por tema. Espera mi OK.
> 2. **Autoría:** escribe los specs en `datos/_specs/` y genéralos con
>    `python3 herramientas/spec_a_tema.py`.
> 3. **Verificación adversarial:** revisa cada spec contra la fuente de verdad y corrige
>    (resuelve los ejercicios, recalcula las tablas, comprueba la numeración de secciones).
> 4. **Interactivos del tema:** construye los del catálogo (`GUIA.md §4`) **incrustados en
>    cada tema, no al final** — un tema no está hecho hasta tener sus simuladores, coherentes
>    con los ejemplos del temario (mismos números).
> 5. **Integra** los temas en `assets/js/temas.js` e `index.html`, personaliza
>    `MPI.config` (título/subtítulo) y la marca/pie de `index.html`, y **verifica en el
>    navegador** que todo renderiza sin errores (`servidor_dev.py`).
>
> El _mapa_corpus.json que hay en contenido/ es del temario anterior de la plantilla
> (Microprocesadores PIC32) — no corresponde a este material.
>
> Empieza por la **fase 0** (ficha) y la **fase 1** (arquitectura), y enséñamelas antes de
> escribir nada.

---

## Qué pasará después

- Claude te confirmará primero la **ficha** (plataforma, lenguaje, recorte, branding) y la
  **arquitectura de temas** propuesta para que la ajustes (orden, qué entra, cuáles después).
- Irá **tema a tema**: escribe el spec → lo genera → lo verifica → **monta sus interactivos**
  → lo integra → lo comprueba en el navegador. Puedes pedirle que vaya por tandas. Un tema no
  se da por terminado si es solo teoría: los simuladores **son** el contenido.
- Si en algún momento se corta (límite de sesión), no se pierde nada: los specs quedan en
  disco y el conversor es determinista; basta retomar.

## Notas

- **Requisitos:** solo **Python 3.7+** (biblioteca estándar). Sin `pip`, sin `venv`, sin
  `requirements.txt`, sin Node. Las herramientas son dos scripts (`spec_a_tema.py`,
  `servidor_dev.py`) y el sitio es HTML/CSS/JS plano.
- **Modelo:** da igual cuál uses; los prompts son agnósticos. Para trabajo largo o crítico,
  `/model claude-opus-4-8` (o el más capaz disponible). Ver `GUIA.md`.
- **Orquestación automática (opcional):** `herramientas/flujo_contenido.workflow.js` abanica
  autor+verificador de todos los temas a la vez con la herramienta `Workflow`. Para hacerlo a
  mano no hace falta.
- **Publicar:** ver `GUIA.md §6` (GitHub Pages).
- El tema de ejemplo (`ejemplo-tema`) es una **demo viva del formato**: ábrelo y léete su
  spec a la vez. Bórralo cuando ya no lo necesites.
