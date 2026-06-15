/*
 * Registro ordenado de los temas del sitio. El contenido de cada tema se
 * carga aparte en datos/temas/<slug>.js (que rellena MPI.contenidoTemas).
 * "disponible:true" marca los temas ya construidos (los demás salen "pronto").
 *
 * Añade una línea por tema, en orden, y su <script> en index.html.
 */
window.MPI = window.MPI || {};
MPI.temas = [
  { num: 1, slug: 'ejemplo-tema', titulo: 'Tema de ejemplo (formato del spec)', disponible: true }
  // , { num: 2, slug: 'otro-tema', titulo: '...', disponible: false }
];
