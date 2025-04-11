# 🎲 HexPlayer 🤖

> **¡Bienvenido!**  
> Este proyecto implementa un agente inteligente para jugar **Hex** utilizando una combinación de heurísticas avanzadas y un algoritmo de búsqueda eficiente.

---

## 🌟 Introducción

El jugador IA combina tres pilares fundamentales:

- **Heurísticas posicionales:** Evalúa cada celda del tablero con criterios estratégicos.
- **Búsqueda Minimax con poda alfa-beta:** Optimiza la exploración de jugadas en el árbol de decisiones.
- **Ajustes dinámicos:** Adapta las heurísticas y la búsqueda según las condiciones del juego y el tiempo disponible.

---

## 📊 Heurísticas Estratégicas

### 1. **Peso a los Bordes (`edge_weights`)**

- **Objetivo:**  
  Favorecer las celdas cercanas a los bordes, reforzando la estrategia del jugador.

- **Efectividad:**  
  Controlar los bordes facilita la construcción de puentes ganadores y fortalece la posición estratégica.

---

### 2. **Peso al Centro (`center_weights`)**

- **Objetivo:**  
  Valorar las posiciones centrales para maximizar la conectividad.

- **Efectividad:**  
  Las celdas centrales cuentan con más vecinos (hasta 6) en comparación con los bordes, ampliando las oportunidades de expansión y conexión.

---

### 3. **Bonificación por Puentes (`bridge_bonus`)**

- **Objetivo:**  
  Incentivar la creación de "puentes" diagonales, que generan conexiones robustas.

- **Efectividad:**  
  La formación de puentes permite que dos piezas conecten de forma tal que se dificulte su bloqueo por el adversario, ofreciendo un camino dual.

---

### 4. **Penalización por Cercanía al Oponente (`opponent_penalty`)**

- **Objetivo:**  
  Desincentivar la colocación en zonas dominadas o influenciadas por el oponente.

- **Efectividad:**  
  Al evitar ubicaciones vulnerables, se refuerza la propia estrategia y se dificulta la acción ofensiva del rival.

---

## 🔍 Función de Evaluación Global

La evaluación de cada jugada se realiza mediante una función que integra de forma ponderada las diferentes heurísticas:

\[
\text{Valor} = 0.6P + 0.3C + 0.1A + 0.3M
\]

donde:

- **\( P \):** Control posicional (Bordes)  
- **\( C \):** Conexiones potenciales (Bonificación por Puentes)  
- **\( A \):** Control de área (Penalización por Cercanía al Oponente)  
- **\( M \):** Influencia central  

Esta combinación asegura que cada movimiento se valore tanto por su potencial ofensivo como por su capacidad para bloquear al enemigo.

---

## 🎯 Ordenamiento de Movimientos

Para optimizar el rendimiento durante el juego, se realiza una priorización de movimientos:

1. **Ordenación Descendente:**  
   Los movimientos se clasifican según su score, asegurándose que las jugadas más prometedoras se evalúen primero.

2. **Poda Tardía:**  
   Se elimina el 40% inferior de movimientos en fases avanzadas, reduciendo la complejidad y focalizando los recursos en las jugadas más relevantes.

---

## ⏳ Profundidad Iterativa

Para garantizar el equilibrio entre calidad de decisión y tiempo de cómputo, se implementa un sistema de profundidad iterativa:

- **Evaluación en tiempo real:**  
  Antes de aumentar la profundidad de la búsqueda, se verifica el tiempo disponible.
  
- **Decisión adaptativa:**  
  Si se alcanza el límite de tiempo, se retorna la mejor jugada evaluada hasta el momento, en lugar de forzar una búsqueda más profunda.

Esta metodología permite al jugador IA responder eficientemente sin comprometer la toma de decisiones en condiciones de presión.

---

## 🚀 Conclusión

Este proyecto integra técnicas de IA para crear un **HexPlayer** robusto y adaptativo. Con una combinación de heurísticas posicionales y una búsqueda Minimax inteligente, el jugador está preparado para competir.
(Más información técnica sobre la implementación en Documentación.pdf)
---

*¡Buena suerte y que comience la partida!*
