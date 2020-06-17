# Meteoros Floripa - Site

![Build](https://github.com/Meteoros-Floripa/site/workflows/Build/badge.svg)

Capturas das estações associadas a [BRAMON](https://www.bramonmeteor.org) from [TLP](https://www.mrprompt.com.br) meteor stations.

## Configurando o site

Edite o arquivo `_config.yml` nos seguintes campos:

```
...
title: <INSIRA AQUI O TÍTULO PADRÃO DO SITE>
description: <INSIRA AQUI UMA BREVE DESCRIÇÃO PARA O SITE>
url: <INSIRA AQUI O ENDEREÇO COMPLETO DO SEU SITE. EX.: https://meteoros.floripa.br>
city: <INSIRA AQUI SUA CIDADE>
google_analytics: <INSIRA AQUI SEU CÓDIGO DO GOOGLE ANALYTICS - SE POSSUIR>
s3_bucket: <INSIRA AQUI O BUCKET DO S3 A SER UTILIZADO PARA ARMAZENAR AS CAPTURAS>
s3_bucket_url: <INSIRA AQUI O ENDEREÇO COMPLETO DO SEU BUCKET. EX: "https://meteoros.s3.amazonaws.com/">

build:
  prefix: <INSIRA AQUI O PREFIXO DE SUA ESTAÇÃO. EX: TLP>
  days: <DIAS A SER SINCRONIZADO - RECOMENDÁVEL 2 A 5>
  captures: <OS DIRETÓRIOS COM AS CAPTURAS DO UFO, SEGUINDO O PADRÃO [ESTACAO]/[ANO]/... - UM DIRETÓRIO POR LINHA> 
    - "C:\bramon\!data"
    - "D:"
    - "E:"
    - "F:"

stations: <ESTACOES A SEREM EXIBIDAS NO SITE - UMA POR LINHA>
  - TLP1
  - TLP2
```

Após atualizar o arquivo de configurações, rode o script `first-run.bat` encontrado dentro do diretório `bin`.

## Rodando localmente

Caso você possua o `Docker` instalado, você pode utilizar o container pronto para ver seu site rodando localmente.

```console
docker-compose up
```
