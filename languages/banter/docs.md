# Banter Documentation

### Table of Contents

- [How to Use Banter](#how-to-use-banter)
  - [Datatypes](#datatypes)
  - [Operators](#operators)
  - [Printing](#printing)
  - [Assignment](#assignment)
  - [Conditionals](#conditionals)
  - [Output](#output)
  - [Goto](#goto)
  - [Comments](#comments)

## How to Use Banter

Banter is an intentionally basic language designed to encourage computational thinking. With only a few basic datatypes and a handful of syntactic structures, Banter forces the user to focus on imperative algorithm design.

### Datatypes

Banter has three datatypes: numbers (integers or floating-point), bools (True or False), and strings. Generally these can be used in any operations that "make sense" (e.g. feel free to add two numbers, but don't try to multiply a string and a bool).

### Operators

The following six arithmetic functions are supported: +, -, / (floating-point division), // (floor division), *, and % (modulus). Parentheses can be used to specify operator precedence.
Valid comparisons are >, >=, <, <=, == (is equal?), and != (is not equal?).
The + operator is overloaded and serves as both scalar addition and string concatenation.

### Printing

`print` statements simply print their output to the terminal.

```
print "Hello World"
```

### Assignment

`let` statements permit assignment in Banter.

```
let x be 1
let y be x + 2
```

### Conditionals

Conditionals are one of the two fundamental control structures in Banter.

```
if x > 1, then
  print "Yes"
else
  print "No"

if x == 1, then
  if y > x,
    print "Good"
```

### Output

`output` statements print their value to the terminal and immediately end the program.

```
let x be 3

if x > 1, then
  output x
else
  output 0

print "This line will never run!"
```

### Goto

`goto` statements are the other main control structure, allowing the program to jump to an arbitrarily located marker statement denoted by an `@`. Note from the second example that markers can also be identifiers.

```
# algorithm to print the first n Fibonacci numbers

let x be 0
let n be 15

let a be 0 
let b be 1

@1
if x < n, then
   print a

   let temp be a + b
   let a be b
   let b be temp

   let x be x + 1

   goto instruction 1
```

```
let a be 3
@a
if a < 0, then
  print "Done"
else
  print a
  let a be a - 1
  goto instruction a 
```

### Comments

```
# I'm a single-line comment

/* And I'm
a multi-line
comment */
```
