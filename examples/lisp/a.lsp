#(* 4 (+ 1 2))
#(exp 3 4)
#(mod 7 2)
#(cdr '(1 2 3))
#(cddr '(1 2 3 4 5))
#(caddr '(1 2 3 4 5))
#(quote (+ 1 2))
#(lambda (x) x)
#((lambda (x) (+ x 1)) 3)
#(define inc
#    (lambda (x) (+ x 1)))
#(inc 4)

(define factorial
    (lambda (n)
        (? (<= n 1) 1 (* n (factorial (- n 1))))))
(factorial 5)

(cond 
    ((eq 1 2) 1)
    ((eq 2 3) 2)
    (else 3))

(eval '(+ 1 2))
(eval (+ 1 2))
eval
