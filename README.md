# Economy Bot

Economy bot es un Bot de discord programado en python que simula una economia basica.
El bot esta programado en python utilizando la api [Discord.py](https://discordpy.readthedocs.io/en/stable/),
y la base de datos [MongoDB Atlas](https://www.mongodb.com/atlas/database).


## Funcionamiento

El usuario inicia la interaccion con la aplicacion al usar el comando de `registro`, posteriormente tiene acceso a las siguientes funcionalidades:
* Transacciones: utilizando el comando `transferir ($cantidad) (@receptor)` se pueden enviar monedas a otro usuario registrado
* Productos: utilizando el comando `producto ($precio) (info)` se puede crear un producto al cual demas usuarios registrados pueden acceder

Los usuarios con permiso de administrador en el servidor pueden tienen acceso a las siguientes funcionalidades:
* Imprimir: utilizando el comando `imprimir ($cantidad) (@usuario)` se pueden crear monedas y asignarlas a un usuario
* Expropiar: utilizando el comando `expropiar ($cantidad) (@usuario)` se puede quitar monedas y de un usuario
<!-- * Forgado: utilizando el comando `initforge` se pueden crear monedas cada cierto tiempo, para aaaa -->


## Configuración

Se debe crear una App en el [portal de desarrolladores de discord](https://discord.com/developers/applications) y a partir de este obtener el Token del bot.
<br>
Para la base de datos se debe configurar un cluster en [MongoDB Atlas](https://cloud.mongodb.com/) y sus respectivas credenciales, ademas de
configurar la IP del servidor en donde se ejecute el Bot.

La aplicacion utiliza un archivo de configuracion con el nombre de ```settings.json```, el cual debe contener:

```json
{
  "token" : "TokenTokenTokenTok.enToken.TokenTokenTokenTokenTo-kenToken | Token del bot de discord (string)",
  "mongoUser": "mongouser | Usuario de la base de datos (string)",
  "mongoPassword": "mongopassword | Contraseña de la base de datos (string)",
  "max_decimals": "2 | Numero de decimales usados para los calculos monetarios (int)",

  "prefix" : "$ | Prefijo de los comandos del Bot (char)",
  "economy_name": "Discord-conomy | Nombre de la economia del servidor (string)",
  "coin_name": "discoin | Nombre de la moneda del servidor (string)",
  "initial_number_of_coins": "1.0 | Numero de monedas otorgadas al registrarse un usuario (float)",
  "forge_time_span": "15 | Intervalo de segundos de cada forjado (int)",
  "forge_quantity": "1.0 | Numero de monedas otorgadas por forjado (float)"
}
``` 

## Pruebas Unitarias

En la seccion de tests estan las pruebas unitarias, utilizar este comando para ejecutarlas:

```sh
pytest ./tests/
```
