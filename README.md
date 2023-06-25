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
  //Configuraciones del Bot

  //Token del bot de discord (string)
  "token" : "TokenTokenTokenTokenTok.enToken.TokenTokenTokenTokenTokenTo-kenToken",
  //Usuario de la base de datos (string)
  "mongoUser": "mongouser",
  //Contraseña de la base de datos (string)
  "mongoPassword": "mongopassword",
  //Numero de decimales usados para los calculos monetarios (int)
  "max_decimals": 2,
  
  //Configuraciones de servidor por defecto

  //Prefijo de los comandos del Bot (char)
  "prefix" : "$",
  //Nombre de la economia del servidor (string)
  "economy_name": "Discord-conomy",
  //Nombre de la moneda del servidor (string)
  "coin_name": "discoin",
  //Numero de monedas otorgadas al registrarse un usuario (float)
  "initial_number_of_coins": 1.0
}
``` 

## Pruebas Unitarias

En la seccion de tests estan las pruebas unitarias, utilizar este comando para ejecutarlas:

```sh
pytest ./tests/
```