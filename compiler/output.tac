; ============ INÍCIO DO PROGRAMA ============
x = 0 ; var x: INT

; ======== LOOP WHILE ========
WHILE1_START: ; início do loop
; Operação binária:
t1 = x LESS 10
if t1 == false goto WHILE1_END
; Início do bloco
; Operação binária: PLUS
t2 = x PLUS 1
; Atribuição para x
x = t2
; Operação binária: EQUAL
t3 = x EQUAL 5

; ========= ESTRUTURA IF =========
if t3 == false goto IF2_ELSE
; THEN branch:
; Início do bloco
g = x ; const g: INT
; Break - saindo do loop
goto WHILE1_END
; Fim do bloco
goto IF2_END
IF2_ELSE:
; ELSE branch:
; Início do bloco
g = 10 ; const g: INT
; Continue - reiniciando loop
goto WHILE1_START
; Fim do bloco
IF2_END:
; ======= FIM DA ESTRUTURA IF =======
; Fim do bloco
goto WHILE1_START ; volta para o início do loop
WHILE1_END: ; fim do loop
; ===== FIM DO LOOP WHILE =====
; ============= FIM DO PROGRAMA =============