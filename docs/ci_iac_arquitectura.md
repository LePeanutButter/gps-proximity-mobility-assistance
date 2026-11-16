# CI e infraestructura como código

## Alcance

La infraestructura AWS está aislada en `infra/aws/terraform/` y la CI sólo
valida archivos y pruebas. Ningún workflow ejecuta `terraform apply`,
`terraform destroy`, `terraform plan` contra una cuenta ni publica firmware.

## Workflows

### `ci-tests.yml`

Se ejecuta en `push`, `pull_request` y `workflow_dispatch` cuando cambian el
firmware, pruebas o documentación relacionada. Ejecuta:

- `python -m unittest discover -s tests -v`
- compilación sintáctica de `src` y `tests`;
- búsqueda básica de patrones de credenciales;
- publicación del artefacto de pruebas cuando existe.

No necesita credenciales AWS.

### `ci-terraform.yml`

Se ejecuta cuando cambia `infra/aws/terraform/`. Ejecuta:

```text
terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
```

`terraform init` descarga el proveedor y crea únicamente metadatos locales
ignorados. `validate` no demuestra permisos, cuotas, existencia de una cuenta
válida ni costos; tampoco reemplaza una revisión manual de `terraform plan`.

El job deshabilita la consulta de metadatos EC2 y no configura credenciales
AWS. Los permisos del workflow son sólo `contents: read`.

## Wokwi

No se añade actualmente `ci-wokwi.yml`. El repositorio contiene
`src/diagram.json`, pero no contiene `wokwi.toml`, un script de arranque
automatizado, un criterio de éxito no ambiguo ni un token de CLI. Ejecutar una
simulación sin esos elementos produciría una validación aparente, no una
prueba reproducible.

Para habilitarlo posteriormente se necesita:

1. confirmar compatibilidad del firmware MicroPython, `network` y `umqtt.simple`
   con la versión de Wokwi elegida;
2. añadir `wokwi.toml` y un script de prueba con timeout;
3. definir una aserción observable sobre la salida serial;
4. guardar `WOKWI_CLI_TOKEN` únicamente como secreto si la CLI lo requiere;
5. crear un workflow separado que no bloquee las pruebas Python/Terraform.

## Riesgos de CI

- Los workflows no reciben secretos AWS.
- Pull requests no tienen permisos de escritura.
- No existe backend remoto Terraform en CI.
- No se generan certificados ni claves privadas.
- Los artefactos no deben contener `terraform.tfstate`, `.tfvars` locales,
  certificados o logs con secretos.
