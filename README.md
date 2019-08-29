# ServidorTCPGCC
servidor tcp , enlace a iot de google
Programa para recibir datos de alfun sensor ,, y enviar a la plataforma de iot de google, cuenta tambien con un cliente de pruebas de tcp.
procedimiento
1-crear nodo iot, registro iot, pub y sub
En este caso:
nodo: arduino23gprs
registro iot: bsa-lb-presionlinea1  us-central1
pub:  bsa-lb-lineapresion1  
sub: bsa-lb-presionlodo1

en el commit de 29 agosto 11:38 se agrego un servidor de tcp que tambien publica el dato por iot se llama receptorTCPIOT
tambien se modifica al receptor original para que no envie la respuesta, al parecer ese era el problema de parar el programa
se debe poner un try/catch para manejar el error 