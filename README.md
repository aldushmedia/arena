# La skill Arena

Cuando Claude te sigue dando malas respuestas, pon a 100 versiones suyas a pelear a muerte. Una skill
para Claude Code. Gratis, MIT, sin registro, sin API key, nada que conectar.

La usas cuando no te gusta lo que Claude te dio. En lugar de pedirle una y otra vez, `/arena` lanza
100 subagentes y le da a cada uno exactamente la misma tarea, palabra por palabra. Cada uno recibe una
carta de estrategia distinta: una forma de razonar, un flujo de trabajo y una estrategia, así cada uno
ataca la tarea de otra manera. Luego se enfrentan en parejas. Cada uno ataca la solución del otro, cada
uno defiende y corrige la suya, y un juez puntúa el enfrentamiento con una rúbrica escrita. El que
pierde queda fuera. 100 pasan a ser 50, luego 25, 13, 7, 4, 2, 1.

Lo que vuelve es la única solución que sobrevivió, los ataques que superó en el camino y cuántas
rondas le llevó.

**Nunca toca tus archivos.** Cada subagente escribe dentro de `.arena/`. La respuesta ganadora vuelve
a ti, y usarla es tu decisión.

## Instalación

Pega esto en Claude:

```
https://github.com/aldushmedia/arena

Instala esta skill y luego confirma que /arena funciona.
```

O copia la carpeta tú mismo, en Claude Code:

```bash
git clone https://github.com/aldushmedia/arena.git
cp -r arena/skills/arena ~/.claude/skills/
```

O como plugin:

```
/plugin marketplace add aldushmedia/arena
/plugin install arena@arena
```

Claude Code agrupa las skills de un plugin bajo su nombre, así que instalada como plugin aparece como
`/arena:arena`. Si prefieres el `/arena` simple, copia la carpeta. Para un solo proyecto en
lugar de global: copia esa misma carpeta en el `.claude/skills/` de tu repo.

Necesita Claude Code, porque lanza subagentes con la herramienta Agent, y Python 3.8 o más reciente.
No hay nada que instalar con pip.

## Cómo se usa

```
/arena
/arena --quick escribe el titular de nuestra página de precios
/arena --agents 32 arregla el test inestable de tests/test_api.py
/arena --seed 7 planea mi semana de lanzamiento, tengo 6 horas al día
```

Sola, `/arena` toma tu último pedido como la tarea, y la respuesta que no te gustó como la que hay
que superar. Claude también puede usarla sin la barra, cuando dices algo como "esa respuesta es mala,
haz que compitan". Cuando arranca sola así, pregunta antes de gastar nada.

| opción | qué hace |
| --- | --- |
| `--agents N` | N competidores. 100 por defecto. |
| `--quick` | 16 competidores. La opción para el día a día. |
| `--seed S` | La misma semilla da las mismas cartas y el mismo torneo. Por defecto es al azar, y queda registrada. |
| `--wave W` | Subagentes por tanda. 10 por defecto. Súbelo solo si subiste el límite de Claude Code. |

## Cómo funciona

1. **Creación.** N subagentes, una llamada a Agent cada uno. Todos reciben el mismo texto de tarea,
   byte por byte (un test lo comprueba), más una carta de estrategia. Hay 15 modos de razonamiento
   (primeros principios, inversión, analogía, adversario, restricciones primero, ejemplo resuelto,
   socrático, llevar la contraria, pensamiento sistémico y más), 12 flujos de trabajo (borrador,
   crítica, reescritura; esquema primero; pruebas primero; investigar y luego sintetizar; tres
   borradores, elige uno...) y 12 estrategias (lo más simple que funcione, rigor máximo, empatía con
   el usuario primero, casos límite primero, velocidad...). Eso da 2.160 cartas distintas. El
   repartidor le da a cada agente la suya, sin repetir.
2. **Ataque.** Las soluciones se emparejan, y el emparejamiento evita poner frente a frente a dos
   agentes con el mismo modo de razonamiento. Cada lado ataca la solución del otro a través de su
   propia carta: qué está mal, qué requisito se le pasó, la entrada exacta que la rompe. Hasta 7
   ataques, etiquetados FATAL, GRAVE o MENOR.
3. **Defensa.** Cada lado responde cada ataque que recibió, aceptándolo o refutándolo con evidencia,
   y luego reescribe su solución para corregir todo lo que aceptó.
4. **Juicio.** Un subagente juez aparte lee las dos soluciones corregidas, revisa él mismo cada ataque
   y las puntúa con [la rúbrica](skills/arena/rubric.md): corrección 30, completitud frente a la
   tarea 25, robustez ante los ataques 20, especificidad 15, claridad 10. El juez nunca ve las
   cartas. `bracket.py` hace las cuentas: pasa el total más alto, y una solución con una falla fatal
   verificada no puede ganarle a una sin fallas fatales. El que pierde queda fuera.
5. **Repetir.** Los sobrevivientes llevan sus soluciones corregidas a la ronda siguiente. Un número
   impar significa un pase libre, nunca dos veces para el mismo agente mientras otro esté esperando
   uno.
6. **Resultado.** Queda una solución. Recibes esa solución, los ataques que superó, su carta y la
   cantidad de rondas. Si empezaste con una respuesta que rechazaste, un último juez compara a ciegas
   la ganadora con esa respuesta, y la skill te dice el puntaje, aunque gane la respuesta vieja.

El torneo de 100 agentes, según `python3 skills/arena/bracket.py plan`:

```
  ronda     vivos  parejas  libre  llamadas a subagentes  tandas
  creación    100        -      -                    100      10
         1    100       50      -                    250      25
         2     50       25      -                    125      13
         3     25       12     sí                     60       8
         4     13        6     sí                     30       5
         5      7        3     sí                     15       3
         6      4        2      -                     10       3
         7      2        1      -                      5       3
  total                                              595      70

  vivos por ronda: 100 -> 50 -> 25 -> 13 -> 7 -> 4 -> 2 -> 1
```

Todo el torneo vive en un solo archivo JSON, que maneja `bracket.py`. La sesión principal de Claude
solo corre el ciclo y nunca lee los cientos de archivos de soluciones: cada subagente escribe su
trabajo en disco y responde con una línea, así que el contexto principal guarda los recibos y el
registro, no el trabajo. Si la conversación se compacta a mitad de camino, `bracket.py next` lo retoma
desde el archivo.

## Lo que cuesta

La skill es gratis. Los tokens son tuyos, y 100 agentes son muchos tokens.

| agentes | rondas | llamadas a subagentes | tandas de 10 |
| --- | --- | --- | --- |
| 100, por defecto | 7 | 595 | 70 |
| 64 | 6 | 379 | 49 |
| 32 | 5 | 187 | 28 |
| 16, `--quick` | 4 | 91 | 16 |
| 8 | 3 | 43 | 10 |

Suma una llamada cuando hay una respuesta rechazada que superar. Cada llamada lee la tarea y una o
dos soluciones, así que la cuenta crece con el tamaño de la tarea. Usa `--quick` o `--agents 16` para
lo de todos los días y guarda los 100 completos para la respuesta que importa. La skill imprime estos
números antes de empezar, y `python3 skills/arena/bracket.py plan --agents N` los imprime cuando
quieras.

## La herramienta

`bracket.py` es Python con la biblioteca estándar. Es la razón por la que el orquestador nunca pierde
la cuenta.

```bash
python3 bracket.py plan --agents 100        # rondas, llamadas, tandas. No escribe nada
python3 bracket.py init --agents 100 --seed 7 --task-file task.md [--baseline-file old.md]
python3 bracket.py next                     # qué hacer ahora, con el comando exacto
python3 bracket.py prompts attack           # escribe cada brief de subagente y lista los trabajos en tandas
python3 bracket.py pairings                 # los enfrentamientos de esta ronda, incluido el pase libre
python3 bracket.py collect                  # registra los veredictos de los jueces
python3 bracket.py record r3-m07 a042 --reason "..."   # o registra uno a mano
python3 bracket.py advance                  # elimina a los perdedores y empareja a los sobrevivientes
python3 bracket.py status                   # vivos y eliminados, por ronda
python3 bracket.py winner                   # el sobreviviente, los ataques que superó, las rondas
```

Los tests corren un torneo completo de 100 agentes por esa línea de comandos con ganadores al azar y
comprueban que termina con exactamente un sobreviviente, además de 16, 7 y 1 agentes, las garantías
del repartidor y cada fase, de la creación a la comparación final, con subagentes de prueba:

```bash
python3 -m unittest discover -s tests -v
```

## La letra pequeña

**"100 versiones de Claude" significa 100 subagentes del modelo que estás usando.** No 100 modelos
distintos. Lo que los hace distintos es la carta. El repartidor garantiza que no haya dos agentes con
la misma carta, que cada modo de razonamiento, flujo de trabajo y estrategia se reparta de la forma
más pareja posible y que, hasta 144 agentes, no haya dos agentes que compartan siquiera dos de sus
tres partes.

**Un competidor es su carta más su archivo de solución.** Los subagentes no recuerdan nada entre
llamadas, así que cuando el competidor a017 ataca en la ronda 3, es un subagente nuevo que recibe la
carta de a017 y la última solución de a017. 100 competidores, 595 llamadas.

**"La mejor respuesta" significa la que sobrevivió a cada enfrentamiento.** Los jueces también son
Claude, y puntúan con una rúbrica escrita que está en este repo para que la leas y la cambies. Lo que
recibes es la respuesta más fuerte que encontró este torneo, no una prueba de que es correcta. Por eso
te muestra los ataques que superó, y por eso te dice directamente cuando la respuesta que rechazaste
sacó más puntos.

**Los 100 agentes no corren todos en el mismo momento.** Claude Code corre como máximo 10 llamadas a
herramientas a la vez por defecto (la configuración `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`), así que
la arena corre en tandas de 10. La creación son 10 tandas, la corrida completa de 100 agentes son 70,
y lleva un rato. Si subes ese límite, pasa `--wave` para que coincida.

**Espera pedidos de permiso, salvo que permitas las ediciones.** Cada subagente escribe un archivo en
`.arena/`, y en el modo de permisos por defecto eso es una aprobación por archivo. Córrela en el modo
de aceptar ediciones (Shift+Tab).

**Los subagentes no pueden ver tu chat.** La skill escribe un archivo de tarea que se sostiene solo, y
ese archivo es todo lo que los 100 agentes llegan a saber. Si un requisito nunca llegó al archivo, los
100 lo pasan por alto. Está en `.arena/<run>/task.md` por si quieres revisarlo.

**Nunca edita tu proyecto.** Los cambios de código vuelven como un diff o como archivos completos
dentro de la respuesta ganadora. Aplicarlos es tu decisión, y la skill te pregunta.

**La misma semilla da las mismas cartas y el mismo torneo.** No las mismas respuestas. El modelo no es
determinista.

**No arregla una tarea mal planteada.** Si entra una tarea vaga, salen 100 versiones de algo vago.

## Archivos

```
skills/arena/SKILL.md          los pasos de la orquestación y el brief exacto que recibe cada subagente
skills/arena/bracket.py        la máquina de estados del torneo, solo con la biblioteca estándar
skills/arena/strategies.json   15 modos de razonamiento, 12 flujos de trabajo, 12 estrategias. Edítalo con libertad
skills/arena/rubric.md         los cinco criterios con los que puntúa cada juez
tests/test_bracket.py          los tests
```

La lógica de `bracket.py` es la del proyecto original; sus mensajes están traducidos al español.

## Créditos

Traducción y adaptación al español por Aldush Media. Basada en un proyecto original con licencia MIT;
su aviso de copyright se conserva en `LICENSE`.

## Licencia

MIT. Tómala, cámbiala, publícala. Ver `LICENSE`.
