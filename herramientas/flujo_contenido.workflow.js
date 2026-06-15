/*
 * flujo_contenido.workflow.js — PLANTILLA de orquestación multi-agente para
 * generar y verificar el contenido de los temas (la mitad "inteligente" del
 * flujo descrito en GUIA.md §5).
 *
 * NO es un script de Node: es un guion para la herramienta `Workflow` de
 * Claude Code (se ejecuta con la tool Workflow, no con `node`). Sirve para
 * relanzar el procesado en otra sesión sin re-inventar la orquestación.
 *
 * CÓMO USARLO
 *   1) Pide explícitamente un workflow (la tool requiere opt-in: di "usa un
 *      workflow" o invoca con la keyword acordada).
 *   2) Pasa los temas a generar en `args` (array de {slug, titulo, alcance}).
 *   3) Elige el modelo al lanzar: por defecto los agentes heredan el modelo de
 *      la sesión (pon /model claude-opus-4-8 antes), o fija opts.model por agente.
 *   4) Al terminar, regenera los .js:  python3 herramientas/spec_a_tema.py --sin-aviso
 *      e intégralos en temas.js e index.html, y verifica en el navegador.
 *
 * Estado en disco = a prueba de cortes: si el workflow muere por límite de
 * sesión, los specs ya escritos quedan en datos/_specs/ y el conversor es
 * determinista; se retoma sin perder nada.
 */

export const meta = {
  name: 'flujo-contenido',
  description: 'Genera (autor) y verifica (adversarial) los specs de los temas de la asignatura',
  phases: [
    { title: 'Autoría',      detail: 'un agente escribe el spec JSON de cada tema' },
    { title: 'Verificación', detail: 'un agente revisa cada spec contra la fuente de verdad y corrige en sitio' }
  ]
};

// --- Personaliza para tu asignatura -----------------------------------------
const ASIGNATURA     = '{ASIGNATURA}';
const CARPETA_FUENTE = 'contenido/';            // material (transparencias, libro, exámenes)
const FUENTE_VERDAD  = '{datasheet/manual oficial}';  // de dónde se reconstruyen datos/fórmulas/código
// Temas a procesar: pásalos en `args`, o usa este valor por defecto.
const TEMAS = (Array.isArray(args) && args.length) ? args : [
  // { slug: 'mi-tema', titulo: 'Mi tema', alcance: 'qué entra según el temario' },
];
// ----------------------------------------------------------------------------

const SCHEMA_VERIF = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    confianza: { type: 'string', enum: ['alta', 'media', 'baja'] },
    correcciones: { type: 'array', items: { type: 'string' } },
    erroresGraves: { type: 'array', items: { type: 'string' } }
  },
  required: ['slug', 'confianza', 'correcciones', 'erroresGraves'],
  additionalProperties: false
};

function promptAutor(t) {
  return `Eres autor de contenido docente de ${ASIGNATURA}. Escribe el spec ` +
    `datos/_specs/${t.slug}.json siguiendo EXACTAMENTE el contrato de GUIA.md §3 ` +
    `(bloques prosa/lista/nota/codigo/formula/registro; + registros, ejercicios, ` +
    `ejerciciosEnTema, resumen). Alcance de este tema: ${t.alcance || t.titulo}. ` +
    `Fuentes por orden de autoridad: ${FUENTE_VERDAD} (datos, fórmulas, código) y el ` +
    `material en ${CARPETA_FUENTE} (qué entra y con qué enfoque). Reglas: ciñe el ` +
    `alcance a lo que vea el temario vigente; reconstruye fórmulas/código/tablas desde ` +
    `la fuente de verdad, NO desde el Markdown corrupto de Docling; fórmulas en MathML ` +
    `nativo; 1-2 ejercicios inspirados en los exámenes. Devuelve solo el archivo escrito.`;
}

function promptVerificador(t) {
  return `Eres revisor técnico adversarial. Lee datos/_specs/${t.slug}.json y la fuente ` +
    `de verdad ${FUENTE_VERDAD}. Comprueba con desconfianza: valores y campos de ` +
    `registros, sintaxis y corrección del código, fórmulas (MathML válido) y validez del ` +
    `JSON. Con ESPECIAL cuidado (aquí se cuelan los errores): (1) Ejercicios — *resuelve tú ` +
    `mismo* cada uno y verifica la coherencia lógica/física entre enunciado, contexto, ` +
    `explicacion y la opción 'correcta', no solo el índice. (2) Números — *recalcula* cada ` +
    `tabla y ejemplo numérico y cuádralo cifra a cifra con la fuente (vigila constantes y ` +
    `unidades). (3) Numeración de secciones coincide con la fuente, sin saltos, y nada fuera ` +
    `del recorte. CORRIGE los errores en el propio archivo (Edit/Write). Devuelve confianza ` +
    `(alta/media/baja), correcciones aplicadas y errores graves. slug = "${t.slug}".`;
}

// Pipeline: cada tema fluye autor -> verificador de forma independiente
// (sin barrera entre fases: un tema puede estar verificándose mientras otro
//  aún se escribe). Para fijar Opus 4.8 por agente: opts.model = 'opus'.
const resultados = await pipeline(
  TEMAS,
  (t) => agent(promptAutor(t), { label: `autor:${t.slug}`, phase: 'Autoría' })
           .then(() => t),                       // el agente escribe el archivo; pasamos el tema
  (t) => agent(promptVerificador(t), {
           label: `verifica:${t.slug}`, phase: 'Verificación', schema: SCHEMA_VERIF
         })
);

return {
  procesados: resultados.filter(Boolean).length,
  resumen: resultados.filter(Boolean)
};
