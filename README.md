# Bonobo Economy Bot
## Configuración
Hay que crear un archivo con el nombre de settings.json y debe contener:
```
{
  "prefix" : "!",
  "token" : "Token del bot de discord",
  "mongoUser": "Usuario de la base de datos",
  "mongoPassword": "Contraseña de la base de datos"
  "dev_ids": ["ids de desarrolladores string"],
  "max_decimals": int
  "economy_name": "str",
  "coin_name": "str",
  "initial_number_of_coins": 0.0
}
``` 

## Comando para pruebas unitarias
`pytest ./tests/`