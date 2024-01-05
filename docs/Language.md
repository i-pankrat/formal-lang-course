# Language

В данном файле описан абстрактный синтаксис языка, его конкретный синтаксис т примеры.

### Абстрактный синтаксис

```
prog = List<stmt>

stmt =
  | bind of var * expr
  | print of expr

val =
  | String of string
  | Int of int
  | Regex of regex
  | Graph of graph

expr =
  | Var of string                // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda = var * expr

```

### Конкретный синтаксис

```
prog = (stmt '\n')*

stmt ->
    | 'let' VAR '=' expr
    | 'print' expr

expr ->
  | '(' expr ')'
  | VAR
  | val
  | map
  | filter
  | intersect
  | concat
  | union
  | star
  | contains

lambda -> ( 'fun' var '->' expr )

set -> var
  | '{' expr (',' expr)* '}'
  | 'set()'
  | 'get_start' '(' graph ')'
  | 'get_final' '(' graph ')'
  | 'get_reachable' '(' graph ')'
  | 'get_vertices' '(' graph ')'
  | 'get_edges' '(' graph ')'
  | 'get_labels' '(' graph ')'
  | '(' set ')'

val ->
  | STRING
  | INT
  | BOOL
  | graph
  | regex

regex -> 'r' STRING

graph ->
  | var
  | 'set_start' '(' set ',' graph ')'
  | 'set_final' '(' set ',' graph ')'
  | 'add_start' '(' (INT | STRING) ',' graph ')'
  | 'add_final' '(' (INT | STRING) ',' graph ')'
  | 'load_from_file' '(' STRING ')'
  | 'load_by_name' '(' STRING ')'

map -> 'map' '(' lambda ',' expr ')'
filter -> 'filter' '(' lambda ',' expr ')'
intersect -> '(' expr '&' expr ')'
concat -> (' expr '+' expr ')'
union -> '(' expr 'u' expr ')'
star -> '(' expr ')' '*'
contains -> expr 'in' set
BOOL --> 'True' | 'False'
INT -> '-'? [1-9][0-9]*
VAR -> [a-zA-Z_][a-zA-Z0-9_]*
STRING -> '"' ~[\n]* '"'
```

### Примеры запросов на языке

Загрузка графа из файла и назначение всех его вершин стартовыми и финальными

```
let graph = load_from_file("./some_graph.dot")
let vertices_set = get_vertices(graph)
let graph = set_start(vertices_set, graph)
let graph = set_final(vertices_set, graph)
print graph
```

Пересечение двух графов и просмотр их меток
```
let f_graph = load_from_file("./graph1")
let s_graph = load_by_name("graph2")
let intersect_graph = (f_graph & s_graph)
let intersect_labels = get_labels(intersect_graph)
print intersect_labels
```

Работа с регулярными выражениями
```
let r1 = r"true"
let r2 = r"false"
let r3 = r"do love"
let r4 = r"do not love"
let r12 = (r1 u r2)
let r34 = (r3 u r4)
let final = (r12 + r34)
print (final)*
```

Пересечение графа и регулярного выражения
```
let my_graph = load_by_name("bool_graph")
let my_regex = r"true | false"
let intersection = (my_graph & my_regex)
let reachable_vertices = get_reachable(intersection)
print reachable_vertices
```

Работа с лямбдами
```
let my_graph = load_from_file("./filename")
let vertices = get_vertices(my_graph)
let filtered_vertices = filter((fun x -> x in {"A", "B"}), vertices)
let mapped_vertices = map((fun x -> True), get_final(my_graph))
print filtered_vertices
print mapped_vertices
```
