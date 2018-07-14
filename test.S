.code32
.data
label_0: .asciz "Hello World!"
.bss
.lcomm bss_tmp, 4
.text
.globl main
main:
finit
pushl $label_0
call printf
add $4, %esp
pushl $0
call exit
