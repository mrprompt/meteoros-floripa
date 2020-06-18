# Meteoros Floripa - Site

![Build](https://github.com/Meteoros-Floripa/site/workflows/Build/badge.svg)

Capturas das estações [TLP](https://www.mrprompt.com.br) associadas da [BRAMON](https://www.bramonmeteor.org).

## Iniciando

#### GitHub

Para iniciar, é necessário uma conta no [GitHub](https://github.com) para que possamos utilizar o 
[Github Pages](https://help.github.com/pt/github/working-with-github-pages).

Caso você não possua uma, crie agora para utilizar este recurso ou configure o Jekyll localmente. Efetuando um build
local, você pode publicar diretamente o diretório `_site` em seu servidor.


#### Python 

Para iniciar, você precisa ter o [Python 3.7+](https://www.python.org/) instalado em sua máquina e com o `PATH` 
corretamente configurado. Após isso, entre no diretório `bin` do projeto e instale as dependências com:

```console
pip install -r requirements.txt 
```

#### AWS

Com o Python devidamente configurado, é hora de configurar as credenciais da [AWS](https://aws.amazon.com/). 
Caso você não tenha experiência com os serviços da [AWS](https://aws.amazon.com/), recomendo a 
leitura [deste link](https://docs.aws.amazon.com/pt_br/AmazonS3/latest/dev/WebsiteHosting.html). 

Para isso, você pode seguir dois modos:

- configurar diretamente as variáveis de ambiente
- criar o arquivo de credenciais em seu diretório home.

Independente do modo escolhido, agora é hora de criar o `bucket` no S3 para armazenar as capturas, não esqueça de 
deixar o bucket público para leitura.

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

## Publicando

Com as coleções criadas (`_captures`, `_data`, `_posts`, `_stations` e `_watches`) agora é hora de publicar seu site,
para isso, habilite o Github-Pages em seu repositório e se necessário, configure um domínio para o mesmo - e não 
esqueça de atualizar o domínio no arquivo `_config.yml`.

Para efetuar a publicação do site, você precisa apenas rodar o script `publish.bat` localizado no diretório `bin` do 
projeto, o mesmo irá atualizar os arquivos necessários, efetuar um commit e um push para o repositório, em alguns minutos
seu site estará publicado - dependendo do número de capturas e etc, o tempo do build pode variar bastante.

## Rodando localmente

Caso você possua o `Docker` instalado, você pode utilizar o container pronto para ver seu site rodando localmente.

```console
docker-compose up
```
