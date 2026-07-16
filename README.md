# TikTok PDF Organizer

Automação desktop criada para eliminar o tempo gasto relacionando manualmente
etiquetas e DANFEs.

O aplicativo compara os códigos de rastreio e gera automaticamente um novo PDF
na sequência correta:

```text
Etiqueta 1 → DANFE 1 → Etiqueta 2 → DANFE 2 → ...
```

> Projeto independente, sem vínculo oficial com o TikTok ou TikTok Shop.

## O principal problema resolvido: tempo

Sem a automação, cada pedido exige abrir dois documentos, localizar visualmente
o mesmo tracking de 13 dígitos, conferir os números e reorganizar as páginas uma
por uma. Além de repetitivo, o processo fica mais demorado conforme aumenta a
quantidade de pedidos e cria espaço para erros de associação.

O TikTok PDF Organizer substitui essa conferência manual: o usuário seleciona
o PDF de etiquetas e o PDF de DANFEs, e o programa encontra os pares em poucos
passos. A ordem original dos DANFEs não importa.

O resultado é menos tempo gasto em uma tarefa operacional repetitiva e mais
segurança de que cada etiqueta será acompanhada pelo documento correto.

## Como funciona

1. O programa lê o texto de todas as páginas;
2. Localiza trackings com exatamente 13 dígitos iniciados por `332`;
3. Cria um índice de páginas para cada documento;
4. Compara os códigos por igualdade exata;
5. Preserva a ordem das etiquetas;
6. Adiciona o DANFE correspondente logo após cada etiqueta;
7. Informa documentos e páginas que ficaram sem correspondência.

## Segurança do pareamento

- Não captura 13 dígitos dentro de sequências numéricas maiores;
- Interrompe o processamento ao encontrar tracking duplicado;
- Interrompe quando uma página contém mais de um tracking reconhecido;
- Impede que o arquivo final sobrescreva os PDFs de entrada;
- Informa etiquetas e DANFEs sem par;
- Informa páginas nas quais nenhum tracking foi reconhecido;
- Processa os arquivos localmente, sem enviá-los para servidores.

## Interface

A interface utiliza um visual roxo com painel central inspirado em glassmorphism.
Ela exibe os arquivos selecionados, só libera o botão principal quando os dois
PDFs estão prontos e processa documentos grandes em segundo plano para manter a
janela responsiva.

## PDFs fictícios para teste

A pasta `examples` contém documentos sem dados reais:

- `01_etiquetas_teste.pdf`: três etiquetas na ordem A, B e C;
- `02_danfes_teste_fora_de_ordem.pdf`: DANFEs na ordem C, A e B;
- `03_resultado_esperado.pdf`: resultado correto com seis páginas intercaladas.

Para recriar os exemplos:

```powershell
py scripts\create_sample_pdfs.py
```

## Tecnologias

- Python;
- PyMuPDF;
- pypdf;
- CustomTkinter;
- Pillow;
- PyInstaller.

## Como executar

Requer Python 3.10 ou superior.

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py main.py
```

## Testes automatizados

Os testes criam PDFs temporários e comprovam que o programa utiliza o mesmo
tracking, mesmo quando os DANFEs estão fora de ordem.

```powershell
py -m unittest discover -s tests -v
```

## Gerar executável no Windows

```bat
build.bat
```

O executável será criado em `dist\TikTokPDFOrganizer`.

## Privacidade

PDFs reais, XMLs fiscais, executáveis e pastas de build estão bloqueados pelo
`.gitignore`. Apenas os documentos inteiramente fictícios da pasta `examples`
podem ser publicados no repositório.

## Autor

Desenvolvido por [Luiz Othávio](https://github.com/luizww).
