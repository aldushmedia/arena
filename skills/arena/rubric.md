# La rúbrica de la arena

Cada enfrentamiento de la arena se puntúa con esta página. El juez puntúa las dos soluciones,
`bracket.py` hace las cuentas, y pasa el total ponderado más alto. La otra queda eliminada.

## Los cinco criterios

Cada criterio se puntúa de 0 a 10. El peso es cuánto vale sobre el total de 100 puntos. La primera
columna es el nombre del criterio tal como va en el JSON del veredicto.

| criterio | peso | la pregunta |
| --- | --- | --- |
| correctness | 30 | **Corrección.** ¿Está bien? Sin afirmaciones falsas, sin errores de lógica, sin bugs, nada que confunda al usuario. |
| completeness | 25 | **Completitud.** ¿Cumple cada requisito que la tarea plantea de verdad? Se juzga contra el texto de la tarea, no contra lo que al juez le habría gustado. |
| specificity | 15 | **Especificidad.** ¿El usuario podría actuar ya mismo sin adivinar? Pasos, valores, nombres y código exactos. |
| robustness | 20 | **Robustez.** ¿Resiste los ataques de este enfrentamiento? Corregidos, refutados con razón o todavía en pie. |
| clarity | 10 | **Claridad.** ¿Es fácil de leer y de usar, con una extensión que le queda a la tarea? |

Total ponderado = (correctness x 30 + completeness x 25 + specificity x 15 + robustness x 20 + clarity x 10) / 10.
Eso da un número de 0 a 100.

## Referencias

Usa toda la escala. Un 7 no es un valor amable por defecto.

**Corrección (correctness)**
- 10: nada mal que puedas encontrar después de revisarlo tú mismo.
- 7: deslices menores que no cambian el resultado para el usuario.
- 4: al menos un error real con el que el usuario va a tropezar.
- 0 a 2: está mal en lo central, o causaría daño si se usa.

**Completitud (completeness)**
- 10: cumple por completo cada requisito planteado.
- 7: toca cada requisito, y uno queda flojo.
- 4: falta un requisito planteado.
- 0 a 2: responde una pregunta distinta de la que se hizo.

**Especificidad (specificity)**
- 10: el usuario puede actuar de inmediato sobre cada parte.
- 7: casi todo es concreto, con uno o dos lugares que requieren adivinar.
- 4: mucho "considera", "asegúrate" y "depende" sin la respuesta en sí.
- 0 a 2: consejos genéricos que servirían para cualquier tarea.

**Robustez (robustness)**
- 10: cada ataque de este enfrentamiento está corregido en la solución corregida o refutado con razón, y no se rompió nada nuevo.
- 7: un ataque MENOR sigue en pie.
- 4: un ataque GRAVE sigue en pie, o una corrección que rompió otra cosa.
- 0 a 2: un ataque FATAL sigue en pie.

Si falta el archivo de ataques, el oponente no planteó nada. Puntúa la robustez con las fallas que
encontraste tú.

**Claridad (clarity)**
- 10: la forma deja claro cómo usarla. Sin relleno.
- 7: está bien, con algo de relleno o una sección confusa.
- 4: el usuario tiene que escarbar para encontrar la respuesta.
- 0 a 2: cuesta seguirla.

## La regla de lo fatal

Marca una solución como `fatal` solo cuando verificaste una falla que la hace incorrecta o inservible
para la tarea: código que no puede funcionar, una afirmación central falsa, una restricción dura
incumplida, la pregunta equivocada respondida. Una solución fatal no puede ganarle a una que no lo es,
digan lo que digan los totales. Si las dos son fatales, deciden los totales.

## Empates

No hay empates. En un empate exacto, gana la solución con menos ataques en pie. Si eso también está
parejo, gana el mayor puntaje de corrección. Si eso también está parejo, elige la que le darías al
usuario, y explica por qué en la razón.

## Lo que el juez no premia

- **La extensión.** Más largo no es mejor. Una respuesta ajustada que cumple cada requisito le gana a
  una larga que cumple los mismos.
- **La seguridad.** Una defensa que dice "corregido" no es prueba. Revisa la solución corregida.
- **El enfoque.** El juez nunca ve las cartas de estrategia y no intenta adivinarlas. Puntúa el
  trabajo, no el método que lo produjo.
- **Hablar de la calidad.** "Esta solución robusta y completa" no suma nada. La solución tiene que ser
  robusta y completa.
- **Coincidir con el gusto del juez** donde la tarea no lo pide.
