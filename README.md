# Mini-C
#Attention
打开、词法、语意、汇编功能正常，在三平台下均可用
运行功能暂时只能在Linux下可用，如有依赖问题请按照报错安装相关依赖，原因是64位Linux下的gcc可以通过添加-m32命令顺利将32位AT&T汇编语言转为.out可运行文件
win下和mac os下应该适当的配置gcc环境也可以达到目的，暂未测试
如果报错关于"icon.ico"找不到，请注释掉 root.iconbitmap('./icon.ico')

#Tips
只实现了source.c文件中出现的文法，还有很多文法状态没有实现 如int a=2;printf("%d",a+b);等
.S文件为生成的汇编文件，可自行用gcc命令转换.out
test.c文件为简单的HW文件

#Test Environment
Ubuntu 16.04
Windows 18.03
Mac OS 未知版本
Python version: 3.5
