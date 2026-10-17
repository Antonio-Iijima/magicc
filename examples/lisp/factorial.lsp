(define factorial
  (lambda (n)
    (cond
      ((<= n 1) 1)
      (else (* n (factorial (- n 1)))))))


(let ((a 1) (b 3)) (+ a b))
; (let ((a 1) (b (* a 2))) (+ a b))

(let* ((a 2) (b (* a 2)) (c (** b 2))) (+ a (+ b c)))

(letrec 
  (
    (is-even? (lambda (n) (or (== 0 n) (is-odd? (- n 1)))))
    (is-odd? (lambda (n) (or (== 0 n) (is-even? (- n 1)))))
  ) (is-even? 11))

(letrec (
  (f (lambda (n) (? (<= n 1) 1 (* n (f (- n 1))))))
) (f 5))

; (letrec ((a b) (b 2)) (+ a b))
