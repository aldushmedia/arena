---
name: arena
description: >-
  Pon a 100 versiones de Claude a pelear a muerte por una sola tarea. Lanza N
  subagentes (100 por defecto, 16 con --quick), le da a cada uno exactamente
  la misma tarea más una carta de estrategia distinta (modo de razonamiento,
  flujo de trabajo, estrategia) y luego corre un torneo de eliminación
  directa: se atacan las soluciones entre sí, se defienden y las corrigen, y
  un juez puntúa cada enfrentamiento con una rúbrica escrita hasta que queda
  una sola solución. Úsala cuando el usuario no esté conforme con una
  respuesta, diga que es una mala respuesta, pida que lo intentes otra vez o
  que lo hagas mejor, diga "arena" o pida que compitan.
argument-hint: "[--agents N | --quick] [--seed S] <tarea>"
---

# arena

Para cuando Claude sigue dando una mala respuesta. En lugar de pedirla una y otra vez, esto corre un
torneo: N subagentes reciben exactamente la misma tarea, cada uno la ataca con un modo de
razonamiento, un flujo de trabajo y una estrategia distintos, y luego se atacan entre sí en un torneo
hasta que queda una sola solución. Tú eres el orquestador. Nunca compites y nunca juzgas.

Lo que el usuario escribió después de `/arena`: `$ARGUMENTS`

Si eso está vacío, o todavía parece un marcador de posición, no se pasó nada: toma la tarea de la
conversación.

## La herramienta

Todo el registro del torneo pasa por `bracket.py`, en la carpeta de esta skill:

```bash
python3 "${CLAUDE_SKILL_DIR}/bracket.py" <comando>
```

Abajo, `ARENA` significa exactamente ese comando. Si la ruta parece sin expandir, usa el "Base
directory for this skill" que Claude Code imprimió al inicio de esta skill. El estado vive en
`.arena/<run>/arena.json` en la carpeta actual, y cada comando después de `init` lo encuentra a
través de `.arena/LATEST`.

## Paso 1: dimensiona el torneo, y pide un sí si nadie lo pidió

Lee las opciones del pedido. Todo lo que no es una opción es la tarea.

| opción | significado |
| --- | --- |
| `--agents N` | N competidores. 100 por defecto. |
| `--quick` | 16 competidores. La opción para el día a día. |
| `--seed S` | Fija las cartas y los emparejamientos. Por defecto: al azar, y queda registrada. |
| `--wave W` | Subagentes por tanda. 10 por defecto. Súbelo solo si el usuario subió el límite de Claude Code. |

Si no hay ningún texto de tarea, la tarea es el pedido más reciente del usuario en esta conversación,
y tu última respuesta a ese pedido es la respuesta a superar.

Corre `ARENA plan --agents N` (o `--quick`). Imprime las rondas, las llamadas a subagentes y las
tandas.

- **El usuario pidió la arena** (escribió `/arena`, dijo "arena" o pidió que compitan): dile en una
  línea qué tan grande es, por ejemplo "100 agentes, 7 rondas, 595 llamadas a subagentes", y empieza.
- **Esta skill se activó porque el usuario no está conforme** ("eso está mal", "inténtalo otra vez",
  "mala respuesta") y nunca mencionó la arena: pregunta una vez antes de gastar nada. Ofrece tres
  opciones: la arena completa (100 agentes, 595 llamadas a subagentes), `--quick` (16 agentes, 91
  llamadas) o un reintento normal. Espera la respuesta.

Los subagentes escriben su trabajo en `.arena/`, en la carpeta actual. En el modo de permisos por
defecto, eso es una aprobación por archivo, que en una corrida grande son cientos. Antes de la fase de
creación, sugiere el modo de aceptar ediciones (Shift+Tab) para la corrida. No cambies tú la
configuración del usuario.

## Paso 2: escribe el archivo de la tarea

Este es el paso que decide el resultado. **Los subagentes no pueden ver esta conversación.** Cada
competidor, atacante y juez sabe solo lo que está en el archivo de la tarea, así que escribe
`.arena/task.md` para que se sostenga solo:

- El pedido, con las palabras del usuario donde puedas.
- Cada requisito y restricción que el usuario dio en cualquier parte de la conversación: público,
  extensión, formato, tono, stack, plazo, lo que no debe cambiar.
- El contexto que necesitaría alguien de afuera: las rutas absolutas de los archivos que importan, los
  datos pegados, qué es el producto, las convenciones del código.
- Cómo se ve "terminado", si el usuario lo dijo.
- Si hay una respuesta a superar: qué no le gustó de ella al usuario, con sus palabras.

No agregues requisitos que el usuario nunca dio. No escribas tu propia idea de la respuesta correcta:
eso empuja a 100 agentes hacia el mismo lado, que es justo lo contrario de lo que se busca.

Si hay una respuesta anterior con la que el usuario no quedó conforme, escríbela palabra por palabra
en `.arena/baseline.md`.

## Paso 3: init

```bash
ARENA init --agents N --seed S --task-file .arena/task.md --baseline-file .arena/baseline.md
```

Deja fuera `--baseline-file` cuando no hay nada que superar, y `--seed` para tener una al azar. `init`
copia la tarea en la carpeta de la corrida, le reparte a cada competidor una carta de estrategia
distinta sin repetir, empareja la ronda 1 y escribe `arena.json`.

## Paso 4: el ciclo

Llévalo siempre con `ARENA next`. Lee el estado en disco y te dice el siguiente paso y el comando
exacto.

Cada fase que corre subagentes funciona igual:

1. `ARENA prompts <fase>` escribe un brief por trabajo y lista, en tandas, los trabajos que faltan.
2. Lanza **una tanda a la vez**: un solo mensaje con una llamada a la herramienta Agent por cada
   trabajo de esa tanda (en versiones viejas de Claude Code, la herramienta Agent se llama Task). Cada
   llamada es:
   - `subagent_type`: `general-purpose`
   - `description`: `arena <id del trabajo>`
   - `prompt`: `Lee <ruta del brief> y síguelo al pie de la letra. Es todo tu brief.`
   - `run_in_background`: false, donde la herramienta tenga esa opción, para que la tanda vuelva
     junta.

   Espera a que cada agente de la tanda responda antes de lanzar la siguiente.
3. Después de la última tanda, corre `ARENA next`. Si falta una salida, te manda de vuelta a la misma
   fase, y entonces `prompts` lista solo los trabajos que faltan. Córrelos otra vez una sola vez. Si un
   trabajo falla dos veces, escribe la línea `SIN SALIDA` en cada uno de sus archivos de salida
   (`ARENA check <fase>` los lista) y sigue. Un ataque que falta cuenta como ningún ataque. Una
   solución que falta pierde su enfrentamiento. Un juez que falla dos veces recibe una tercera corrida
   nueva: nunca decidas tú un enfrentamiento.

El orden por el que te lleva `next`:

- **spawn** (creación), una vez: cada competidor escribe su propia solución a la tarea.
- luego, en cada ronda: **attack** (ataque, dos por enfrentamiento) → **defend** (defensa, dos por
  enfrentamiento) → **judge** (juicio, uno por enfrentamiento) → `ARENA collect` → `ARENA advance`.
- **final**, una vez, solo cuando hay una respuesta a superar: un juez compara al campeón con la
  respuesta que el usuario rechazó, sin saber cuál es cuál. Luego `ARENA collect`.
- `next` imprime LISTO: ve al paso 5.

Después de cada `advance`, dale al usuario una línea, como "Ronda 2 terminada: quedan 25 de 100." Nada
más. Nunca pegues en el chat emparejamientos, ataques, veredictos ni soluciones.

Por qué en tandas: Claude Code corre como máximo 10 llamadas a herramientas a la vez por defecto (la
configuración `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`). Así que la creación de 100 agentes son 10
tandas de 10, y una arena de 100 agentes son 70 tandas en total, 71 con la comparación final.

## Paso 5: el resultado

Corre `ARENA winner` y luego lee el archivo de la solución del campeón en la ruta que imprime. Es el
único archivo de solución que lees en toda la corrida. Dale al usuario:

1. **La solución ganadora**, completa.
2. **Por qué ganó**: los ataques que superó, según `winner`, en una lista corta. Su carta en una línea
   (modo de razonamiento + flujo de trabajo + estrategia).
3. **Las rondas**: por ejemplo "7 rondas, entraron 100 agentes, queda 1."
4. **Contra la respuesta que rechazaste**, si había una: los puntajes de la comparación final, con
   honestidad. Si la respuesta vieja sacó más puntos, dilo claro y muestra las dos.
5. Dónde está el registro completo: la carpeta de la corrida.

Si la solución cambia archivos del proyecto del usuario, no la apliques. Pregunta: ¿la aplico o la
cambio?

## Reglas para el orquestador

- Tú corres el torneo. No compites, no atacas, no juzgas y nunca eliges a un ganador. `collect`
  registra lo que decidieron los jueces. `record` es solo para corregir el registro cuando el usuario
  te lo pide.
- Cada subagente recibe la tarea a través de su brief, que `prompts` arma a partir del único archivo
  de la tarea, idéntico byte por byte para todos. Nunca parafrasees la tarea para un agente ni le
  agregues una pista a la llamada de un agente.
- No leas soluciones, ataques ni veredictos durante la corrida. Son cientos. El estado está en disco,
  y `next`, `status` y `pairings` son todo lo que necesitas.
- Si tu contexto se compacta a mitad de la corrida, no se pierde nada. Corre `ARENA status`, luego
  `ARENA next`, y sigue.
- Corre cada comando `ARENA` desde la carpeta donde corriste `init`. Ahí vive `.arena/LATEST`.
- Los subagentes solo escriben dentro de `.arena/`. Si alguno escribió en otro lugar, avísale al
  usuario.
- Si el usuario dice que pares, para. `ARENA status` muestra hasta dónde llegó, y `ARENA next` lo
  retoma después.

## Las plantillas de los briefs

`bracket.py` las rellena (los `{{placeholders}}`) y escribe un brief por trabajo, así que lo que ves
aquí es exactamente lo que se le dice a cada subagente. Nunca edites el brief de un solo agente.

### Competidor, en la fase de creación

<!-- template:competitor -->
```text
Eres el competidor {{agent}} en una arena de {{n}}. Los {{n}} competidores recibieron exactamente la misma tarea, palabra por palabra. Lo único que te hace distinto es la carta de estrategia de abajo: decide cómo atacas la tarea. Tu solución va a ser atacada por otros competidores y puntuada por un juez, ronda tras ronda, hasta que quede una sola solución.

=== LA TAREA (idéntica para todos los competidores) ===
{{task}}
=== FIN DE LA TAREA ===

{{baseline_note}}

=== TU CARTA DE ESTRATEGIA ===
Modo de razonamiento: {{reasoning_name}}. {{reasoning_how}}
Flujo de trabajo: {{workflow_name}}. {{workflow_how}}
Estrategia: {{strategy_name}}. {{strategy_how}}
=== FIN DE LA CARTA ===

Cómo trabajar:
1. Usa la carta de verdad. Piensa en el modo de razonamiento, sigue los pasos del flujo de trabajo en orden y deja que la estrategia decida cada compromiso. Una respuesta genérica con el nombre de la carta encima va a perder.
2. Cumple cada requisito que plantea la tarea. El juez te puntúa contra la tarea, no contra tu carta.
3. No puedes preguntarle nada al usuario. Donde la tarea sea ambigua, toma la lectura más razonable y explícala en una sección corta de Supuestos.
4. Espera ataques: fallas concretas, contraejemplos, requisitos que se te pasaron. Cierra esos huecos antes de entregar.
5. No crees, edites ni borres nada fuera de {{arena_dir}}. Lee todo lo que la tarea indique. Si la tarea es de código, pon los cambios exactos en tu solución (archivos completos o un diff unificado) en lugar de aplicarlos. Si tu flujo de trabajo necesita espacio para borradores, usa {{arena_dir}}/scratch/{{agent}}/.

Escribe tu solución en {{out}}: la solución en sí, escrita para la persona que la pidió. Deja fuera tus borradores y tu proceso. Incluye una lista de verificación, pruebas o notas sobre compromisos solo donde ayuden a esa persona a usar la respuesta. No digas nada sobre la arena, tu carta ni tu número de competidor: los jueces puntúan el trabajo sin saber de quién es.

Cuando el archivo esté escrito, responde con esta línea y nada más:
LISTO {{agent}} <cantidad de palabras de tu solución>
```
<!-- /template:competitor -->

### Atacante, en cada ronda

<!-- template:attacker -->
```text
Eres el competidor {{agent}} en la ronda {{round}} de una arena, enfrentamiento {{match}}. Tu oponente es {{target}}. Solo uno de los dos sale de este enfrentamiento. Ahora tu trabajo es atacar la solución de tu oponente.

=== LA TAREA (idéntica para todos los competidores) ===
{{task}}
=== FIN DE LA TAREA ===

Tu carta de estrategia es el lente con el que buscas fallas:
Modo de razonamiento: {{reasoning_name}}. {{reasoning_how}}
Flujo de trabajo: {{workflow_name}}. {{workflow_how}}
Estrategia: {{strategy_name}}. {{strategy_how}}

Lee la solución de tu oponente: {{target_solution}}
Puedes leer la tuya para comparar: {{own_solution}}. Ataca la suya por sus méritos frente a la tarea, no por ser distinta de la tuya.

Encuentra los problemas reales:
- INCORRECTO: errores de hecho, errores de lógica, bugs, afirmaciones falsas.
- FALTA: un requisito que plantea la tarea y que se salta o cumple a medias. Cita el requisito.
- SE ROMPE: una entrada, un escenario o un caso límite concreto donde falla. Da el contraejemplo exacto.
- VAGO: un lugar donde el usuario no podría actuar sin adivinar.

Reglas:
- Cada ataque tiene que ser específico y verificable: señala la parte exacta, di qué está mal y por qué.
- Nada de elogios, nada de resúmenes y nada de detalles de estilo, salvo que le impidan al usuario usarla.
- No inventes requisitos que la tarea no plantea. No ataques el enfoque, solo lo que hace mal.
- Como máximo 7 ataques, del más fuerte al más débil. Si solo encuentras 2 reales, escribe 2.
- Etiqueta cada uno como FATAL (incorrecta o inservible para la tarea), GRAVE (un hueco real) o MENOR.
- No crees, edites ni borres ningún archivo salvo el de abajo.

Escribe los ataques en {{out}} con este formato:
ATAQUE 1 [FATAL|GRAVE|MENOR] <título en una línea>
Dónde: <cita o ubicación>
Problema: <qué está mal, con el contraejemplo o el requisito que falta>
(y lo mismo para cada ataque que siga)

Cuando el archivo esté escrito, responde con esta línea y nada más:
ATACADO {{target}} <cantidad de ataques> (<cantidad que son FATAL> fatales)
```
<!-- /template:attacker -->

### Defensor, en cada ronda

<!-- template:defender -->
```text
Eres el competidor {{agent}} en la ronda {{round}} de una arena, enfrentamiento {{match}}. Tu oponente {{attacker}} atacó tu solución. Ahora la defiendes y la corriges. Un juez va a puntuar tu solución corregida contra la de tu oponente, incluido qué tan bien manejó cada uno los ataques que recibió.

=== LA TAREA (idéntica para todos los competidores) ===
{{task}}
=== FIN DE LA TAREA ===

Tu carta de estrategia. Mantén tu enfoque: es la razón por la que sigues aquí.
Modo de razonamiento: {{reasoning_name}}. {{reasoning_how}}
Flujo de trabajo: {{workflow_name}}. {{workflow_how}}
Estrategia: {{strategy_name}}. {{strategy_how}}

Tu solución actual: {{own_solution}}
Los ataques contra ella: {{attacks}}

Haz esto:
1. Toma cada ataque, uno por uno, y decide con honestidad. Marca ACEPTO si tiene razón, y corrígelo. Marca REFUTO si está equivocado, y muestra por qué con evidencia de la tarea, de tu solución o de una verificación concreta. Una refutación que solo insiste en que tienes razón cuenta como aceptación. Aceptar una falla real y corregirla puntúa mejor que defenderla.
2. Escribe tu solución corregida: la solución completa, que se sostenga sola, con cada punto aceptado corregido. El juez lee solo este archivo, así que nunca escribas "ver la versión anterior". No digas nada sobre la arena ni sobre tu carta.
3. Corrige lo que te atacaron y cualquier cosa que los ataques te hicieron notar. No empieces de cero y no copies a tu oponente.
4. Si el archivo de ataques está vacío o dice SIN SALIDA, no te atacaron: escribe NO RECIBÍ ATAQUES como tu defensa, y vuelve a entregar tu solución solo con las correcciones que sabes que necesita.
5. No crees, edites ni borres nada fuera de {{arena_dir}}.

Escribe tu defensa punto por punto en {{defense_out}} con este formato:
ATAQUE 1: ACEPTO|REFUTO. <de una a tres líneas>
(una entrada por ataque)

Escribe tu solución corregida en {{solution_out}}.

Cuando los dos archivos estén escritos, responde con esta línea y nada más:
DEFENDIDO {{agent}} aceptados <n> refutados <n>
```
<!-- /template:defender -->

### Juez, uno por enfrentamiento

<!-- template:judge -->
```text
Eres el juez del enfrentamiento {{match}}, ronda {{round}}, en una arena. Dos soluciones a la misma tarea se enfrentaron: cada una atacó a la otra, y luego defendió y corrigió la suya. Puntúa las dos con la rúbrica. La que saque más puntos pasa y la otra queda eliminada.

=== LA TAREA (idéntica para todos los competidores) ===
{{task}}
=== FIN DE LA TAREA ===

Lee primero la rúbrica: {{rubric}}

Solución {{first}}
- solución corregida: {{first_solution}}
- ataques que recibió: {{first_attacks}}
- su defensa: {{first_defense}}

Solución {{second}}
- solución corregida: {{second_solution}}
- ataques que recibió: {{second_attacks}}
- su defensa: {{second_defense}}

Cómo juzgar:
1. Lee completas las dos soluciones corregidas antes de puntuar cualquiera.
2. Por cada ataque, revisa tú mismo la solución corregida y márcalo como CORREGIDO, REFUTADO (solo si la refutación de verdad tiene razón) o EN PIE. Una defensa que dice "corregido" no es prueba. Mira.
3. Busca también las fallas que se les pasaron a los atacantes.
4. Puntúa cada criterio de 0 a 10 con las referencias de la rúbrica. Pon fatal en true solo para una falla que verificaste y que hace que la solución sea incorrecta o inservible para la tarea.
5. Gana el total ponderado más alto (los pesos están en la rúbrica). Una solución fatal no puede ganarle a una que no lo es. En un empate exacto, gana la que tiene menos ataques en pie, y luego la de mayor correctness.
6. Juzga el trabajo, no lo que se escribe sobre el trabajo. Más largo no es mejor. No sabes la estrategia de ningún competidor y no debes adivinarla.
7. No crees, edites ni borres ningún archivo salvo el veredicto. Si la tarea es de código y correr algo resuelve un ataque, hazlo solo dentro de {{arena_dir}}/scratch/judge-{{match}}/, nunca en el proyecto del usuario.

Escribe este JSON, y nada más, en {{out}}:
{
  "match": "{{match}}",
  "scores": {
    "{{first}}": {"correctness": 0, "completeness": 0, "specificity": 0, "robustness": 0, "clarity": 0, "fatal": false},
    "{{second}}": {"correctness": 0, "completeness": 0, "specificity": 0, "robustness": 0, "clarity": 0, "fatal": false}
  },
  "winner": "{{first}} o {{second}}",
  "reason": "una oración: la diferencia decisiva",
  "survived": ["cada ataque que el ganador recibió y superó, en pocas palabras"],
  "standing": {"{{first}}": ["ataques que siguen en pie"], "{{second}}": ["ataques que siguen en pie"]}
}

Cuando el archivo esté escrito, responde con esta línea y nada más:
GANADOR <id del ganador> <total del ganador>-<total del perdedor>
```
<!-- /template:judge -->

### Comparación final, solo cuando hay una respuesta a superar

<!-- template:final -->
```text
Eres la comparación final de una arena. {{n}} competidores pelearon por una tarea y una sola solución sobrevivió {{rounds}} rondas. Antes de que vuelva al usuario, se compara con la respuesta que el usuario ya rechazó. No se te dice cuál de las dos es cuál. Puntúa lo que tienes enfrente. Cualquiera de las dos puede ganar.

=== LA TAREA ===
{{task}}
=== FIN DE LA TAREA ===

Lee primero la rúbrica: {{rubric}}

Solución X: {{x_solution}}
Solución Y: {{y_solution}}

Cómo juzgar:
1. Lee las dos completas antes de puntuar cualquiera.
2. Atácalas tú mismo: encuentra las fallas concretas más fuertes de cada una, como lo haría un experto hostil. Para el puntaje de robustness, juzga qué tan bien resiste cada una esos ataques.
3. Puntúa cada criterio de 0 a 10 con las referencias de la rúbrica. Pon fatal en true solo para una falla que verificaste y que hace que una solución sea incorrecta o inservible para la tarea.
4. Gana el total ponderado más alto. Una solución fatal no puede ganarle a una que no lo es.
5. Juzga el trabajo, no lo que se escribe sobre el trabajo. Más largo no es mejor.
6. No crees, edites ni borres ningún archivo salvo el veredicto.

Escribe este JSON, y nada más, en {{out}}:
{
  "scores": {
    "X": {"correctness": 0, "completeness": 0, "specificity": 0, "robustness": 0, "clarity": 0, "fatal": false},
    "Y": {"correctness": 0, "completeness": 0, "specificity": 0, "robustness": 0, "clarity": 0, "fatal": false}
  },
  "winner": "X o Y",
  "reason": "una oración: la diferencia decisiva",
  "fixed": ["cada cosa que el ganador hace bien y el otro hace mal, en pocas palabras"]
}

Cuando el archivo esté escrito, responde con esta línea y nada más:
FINAL <X o Y> <total de X>-<total de Y>
```
<!-- /template:final -->
