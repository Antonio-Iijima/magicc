### NOTES
---

#### Deremer-Penello Algorithm

- **A.** Compute which nonterminals are nullable.
- **B.** Initialize **Read** to **DR**: one set (bit vector of length the number of terminals) for each
nonterminal transition, by inspection of the transition's successor state.
- **C.** Compute reads: one list of nonterminal transitions per nonterminal transition, by
inspection of the successor state of the latter transition.
- **D.** Apply algorithm **Digraph** to **reads** to compute **Read**; if a cycle is detected, announce
that the grammar is not LR(k) for any k.
- **E.** Compute **includes** and **lookback**: one list of nonterminal transitions per nonterminal
transition and reduction, respectively, by inspection of each nonterminal transition and
associated production right parts, and by considering nullable nonterminals appropriately.
- **F.** Apply algorithm **Digraph** to **includes** to compute **Follow**: use the same sets as
initialized in part **B** and completed in part **D**, both as initial values and as workspace.
If a cycle is detected in which a **Read** set is nonempty, announce that (as we conjecture)
the grammar is not LR(k) for any k.
- **G.** Union the **Follow** sets to form the **LA** sets according to the **l o o k b a c k** links computed
in part F.
- **H.** Check for conflicts; if none, announce that the grammar is LALR(1)--we have a parser.


### Naming
---

Major changes to this project will no longer be published here.

Future development will be done in a new repository
under the name [*Pecora*](https://github.com/Antonio-Iijima/pecora.git).
Note that we had to choose the clade *Pecora* 
to include both the *Cervidae* (Elkhound) and the *Bovidae* (Yacc, Bison, etc.).
This project will draw inspiration from all of them.
The algorithm is a novel RNGIELALR (Right-Nulled General Inadequacy Elimination Lookahead LR) approach, which unifies elements from multiple proven parsing techniques into a single state-of-the-art design.


### To-do
---

- Rewrite module references using OOP
