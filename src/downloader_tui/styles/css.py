"""Constantes de CSS para tema Monokai."""

MONOKAI_CSS = """
/* ------------------------------------------------------------------
   Escala de espaciado: unica fuente de verdad. Ningun padding ni margen
   de este archivo usa un numero que no salga de aqui.
     $space-0  dentro de un grupo (elementos que van juntos)
     $space-1  entre grupos / canal interno
     $space-2  margen exterior de la columna
   ------------------------------------------------------------------ */
$space-0: 0;
$space-1: 1;
$space-2: 2;

Screen {
    background: #272822;
    color: #f8f8f2;
}

/* Envoltura que centra la columna del formulario, como la pantalla de
   bienvenida de opencode. Tiene que ser un contenedor propio: cuando el Screen
   tiene hermanos (Header, logo, Footer) su align-horizontal no centra al hijo
   (medido: el contenedor se quedaba en x=0 a 120 columnas). */
.composer-area {
    width: 100%;
    height: 1fr;
    align-horizontal: center;
}

.ascii-logo {
    text-align: center;
    color: #ae81ff;
    height: auto;
    padding: $space-0;
    /* Es un grupo mas del bloque: abre su hueco como los demas. */
    margin-bottom: $space-1;
}

/* Espaciador elastico: se reparte el alto sobrante con su gemelo, de modo que
   el bloque de contenido quede centrado verticalmente. En una ventana sin
   altura de sobra ambos miden 0 y el area simplemente se desplaza. */
.relleno-flexible {
    height: 1fr;
    /* Sin esto, cada espaciador ocupa 1 fila aunque no sobre altura y en una
       ventana pequena se pierden 2 filas que hacen falta. */
    min-height: 0;
}

/* Los divisores usan una cadena mas larga que cualquier terminal. Con
   text-wrap: nowrap + height: 1 + overflow: hidden nunca se parten en dos
   lineas: antes, con una cadena de 80 en un hueco de 76, dejaban un trozo
   huerfano de 4 caracteres en la linea siguiente.
   Su margen superior es el hueco que abre cada grupo, siempre el mismo. */
.divider {
    color: #75715e;
    text-align: center;
    text-wrap: nowrap;
    overflow: hidden;
    height: 1;
    margin: $space-1 $space-0 $space-0 $space-0;
}

/* max-width: la columna del formulario no se estira en terminales anchos.
   Sin esto, a 120 columnas el input de URL medía 116 y el bloque se veia
   desparramado. 80 es el minimo que deja entrar la fila de 6 botones
   (72 columnas) con holgura; en terminales de 80 o menos ocupa todo el ancho. */
.main-container {
    width: 100%;
    max-width: 80;
    height: 1fr;
    padding: $space-0 $space-2;
    overflow-y: auto;
}

/* Envoltura de una fila que debe ir centrada (pestañas, botones, barra de
   progreso). Tiene que ser un contenedor de UN solo hijo: con varios hermanos,
   el align-horizontal del contenedor padre no centra al hijo. */
.fila-centrada {
    width: 100%;
    height: auto;
    align-horizontal: center;
}

/* height: auto es imprescindible: sin declararla, este Vertical se comporta
   como contenedor flexible, colapsa a 1 fila y deja el Input de URL fuera de
   la pantalla (medido: Vertical region=(2,16,96,1) con el Input en y=18). */
.input-group {
    height: auto;
    margin: $space-0;
}

/* Caja de URL con barra de acento a la izquierda y sin borde alrededor, como
   el prompt de opencode. Al quitar los bordes superior e inferior la caja pasa
   de 3 filas a 2. */
Input {
    background: #3e3d32;
    border: none;
    border-left: solid #ae81ff;
    color: #f8f8f2;
    height: 2;
    padding: $space-0 $space-1;
}

Input:focus {
    background: #4e4d3e;
    border-left: solid #cc99ff;
}

/* height: auto (no 1) para que la linea de validacion desaparezca mientras
   esta vacia y solo ocupe fila cuando hay algo que decir. */
.validation {
    height: auto;
    margin: $space-0;
}

.sites-hint {
    height: auto;
    max-height: 2;
    margin: $space-0;
    text-align: center;
    text-wrap: wrap;
}

.tab-group {
    margin: $space-0;
    height: 3;
    width: auto;
}

/* Estilo comun de los dos grupos de botones: mismo fondo, mismo foco y SIN
   borde (estilo plano, como la caja de prompt de opencode). Ademas de la
   estetica, el borde costaba 12 columnas: la fila de 6 botones medía 71 de las
   74 utiles y, al llenar el ancho, su centrado no se veia.
   Sin borde la altura se quedaria en 1 fila, asi que se fija en 3 con relleno
   vertical: el boton sigue siendo un blanco comodo para el raton. */
.tab-group Button,
.button-group Button {
    /* $space-2 y no $space-1: sin borde, con una sola columna de separacion los
       botones se leian como un bloque continuo. */
    margin-right: $space-2;
    background: #3e3d32;
    color: #f8f8f2;
    border: none;
    height: 3;
    padding: $space-1 $space-0;
}

/* El ultimo boton de cada fila no lleva margen a la derecha: ese margen
   invisible desplazaba el centrado una columna hacia la izquierda. */
.tab-group Button:last-of-type,
.button-group Button:last-of-type {
    margin-right: $space-0;
}

/* El ancho minimo si difiere por rol, y es deliberado: 3 pestañas pueden ser
   anchas (16), pero 6 botones de accion a 16 columnas son 101 columnas y no
   caben en un terminal de 80 (los dos ultimos quedaban fuera de pantalla). */
.tab-group Button {
    min-width: 16;
}

.button-group Button {
    min-width: 8;
}

.tab-group Button:hover,
.button-group Button:hover,
.tab-group Button:focus,
.button-group Button:focus,
.tab-group Button.focused,
.button-group Button.focused {
    background: #75715e;
    color: #272822;
    /* Sin borde hace falta otra senal de foco: negrita ademas del color. */
    text-style: bold;
}

.tab-group Button.-primary,
.button-group Button.-primary {
    background: #ae81ff;
    color: #272822;
    text-style: bold;
}

/* Con foco, el boton primario se aclara: si no, un primario enfocado se veria
   igual que uno sin enfocar y se perderia la senal de donde esta el foco. */
.tab-group Button.-primary:hover,
.button-group Button.-primary:hover,
.tab-group Button.-primary:focus,
.button-group Button.-primary:focus,
.tab-group Button.-primary.focused,
.button-group Button.-primary.focused {
    background: #cc99ff;
    color: #272822;
}

.button-group {
    margin: $space-0;
    width: auto;
    height: auto;
}

/* Selector de tema de la pantalla de Configuracion. */
OptionList {
    background: #3e3d32;
    border: solid #75715e;
    color: #f8f8f2;
    margin: $space-0;
}

OptionList:focus {
    border: solid #ae81ff;
}

OptionList > .option-list--option-highlighted {
    background: #ae81ff;
    color: #272822;
}

.privacy-notice {
    margin-top: $space-1;
    padding: $space-1;
    background: #1e1f1c;
    border: solid #75715e;
    text-align: center;
    text-wrap: wrap;
}

.nav-hint {
    margin-top: $space-1;
    padding: $space-1;
    background: #1e1f1c;
    border: solid #75715e;
    text-align: center;
    color: #75715e;
}

/* status y progress son el mismo grupo (estado de la descarga): sin hueco
   entre ellos. El hueco del grupo lo abre status. */
.status {
    margin: $space-1 $space-0 $space-0 $space-0;
    height: 1;
}

#progress {
    margin: $space-0;
    background: #3e3d32;
    color: #ae81ff;
    /* Mas estrecha que la columna: a ancho completo, centrarla no significa
       nada. */
    width: 40;
}

.log {
    height: 12;
    background: #1e1f1c;
    border: solid #75715e;
    color: #f8f8f2;
    margin: $space-0;
    padding: $space-1;
}

/* El Collapsible trae padding propio por defecto (0 0 1 1) que se sumaba al
   del Log de dentro: doble padding alrededor del mismo contenido. */
#log_collapsible {
    margin-top: $space-1;
    padding: $space-0;
}

.title {
    text-align: center;
    color: #ae81ff;
    padding: $space-1;
    margin-bottom: $space-1;
}

.settings-list {
    margin: $space-1 $space-0;
}

.settings-list Label {
    margin-top: $space-1;
    color: #ae81ff;
}

.sites-content {
    padding: $space-1 $space-2;
    color: #f8f8f2;
    overflow-y: auto;
    height: 100%;
}

DataTable {
    height: 100%;
    background: #272822;
}

DataTable > .datatable--header {
    background: #3e3d32;
    color: #ae81ff;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #ae81ff;
    color: #272822;
}

.dialog {
    width: 60;
    height: auto;
    padding: $space-2;
    border: solid #ae81ff;
    background: #3e3d32;
}

.dialog-title {
    text-align: center;
    color: #ae81ff;
    margin-bottom: $space-1;
}

.dialog-message {
    text-align: center;
    color: #f8f8f2;
    margin-bottom: $space-2;
}

.dialog-buttons {
    width: 100%;
}

.dialog-buttons Button {
    margin: $space-0 $space-1;
}

/* Header y Footer con border necesitan 3 filas (borde + contenido + borde).
   Con height: 2 el contenido se quedaba en 0 filas y se veian cajas vacias:
   ni el titulo de la app ni las teclas del pie llegaban a dibujarse.
   Sin borde y con 1 fila cada uno, ambos son utiles y se ahorran 2 filas. */
Header {
    background: #3e3d32;
    color: #f8f8f2;
    border: none;
    height: 1;
}

Footer {
    background: #3e3d32;
    color: #75715e;
    border: none;
    height: 1;
}

Footer .key {
    color: #ae81ff;
}

Collapsible {
    border: solid #75715e;
    background: #272822;
}

Collapsible.-collapsed {
    border: solid #75715e;
}

CollapsibleTitle {
    color: #ae81ff;
    background: #3e3d32;
}
"""
