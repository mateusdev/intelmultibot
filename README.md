# Intelligence Gathering Bot

Bot criado como um desafio pessoal e uma ideia de projeto para a junção de diversas plataformas, sites, e informações obtidas de fontes OSINT, formando um framework de informações e inteligência acessível a todos.

Atualmente temos alguns módulos funcionais:
 - Obtenção de informações de domínio (whois)
 - Checagem da validade de e-mails
 - Checagem da sintaxe e semântica de um CPF, bem como o cálculo de dígitos verificadores
 - Reconhecimento DNS histórico passivo de subdomínios de um domínio principal
 - GEO-IP e geração do link no googlemaps
 - Checagem de um IP/domínio em blacklists

## Instalação
Alguns programas que necessitam estar instalados:

 - Firefox em uma versão atualizada
 - Python 3.7+
 - Módulo python3-venv

Após isso, é necessário criar um ambiente virtual, utilizando o venv, e ativá-lo:

<code>python3 -m venv virtual_intel</code>

<code>source virtual_intel/bin/activate</code>

<br>
Navegue até a pasta do intelmultibot, então:

<code>chmod +x geckodriver</code>

<code>pip3 install -r requirements.txt</code>

<br>
Crie um bot  no BotFather (https://t.me/BotFather) e a inclua a chave de API gerada na variável "token", em main.py

Por fim, execute o projeto com <code>python3 main.py</code>, visite seu bot e teste :)


*NOTA: testamos apenas em ambientes linux derivados do debian.*


### Sobre o idealizador/primeiro programador :)

Mateus Gualberto
Estudante de Ciência da Computação e Segurança da Informação; hacker "OSINT" e futuro analista de malware.
Amante de Linux, Engenharia reversa e de softwares livres/opensource.

Membro do projeto RSI - Residência em Segurança da Informação (http://www.rsi.dc.ufc.br/).
Gostaria de agradecê-los, pois sem eles esse projeto não teria sido possível :)

### Links de contato:

E-mail profissional: profissional.mateus.gualberto@gmail.com

Linkedin: https://www.linkedin.com/in/mateus-gualberto-santos/

RSI: http://rsi.dc.ufc.br/
