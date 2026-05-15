# Web Scraper LookMovie2

Este repositório contém ferramentas para automatizar a extração de vídeos e links de vídeo do site lookmovie2.

## Descrição
O projeto consiste em scripts Python projetados para realizar a obtenção de links de episódios do site lookmovie2. Obtém os arquivos `.m3u8` e passa para o ffmpeg baixar automaticamente.

## Como Usar

### 1. Scraper
O script `scraper` é responsável baixar um vídeo mp4 do filme/episódio contido no link.
*   **Como executar:**
    ```bash
    python scraper.py "https://lookmovie2.com/filme/nome-do-filme" "C:\\caminho\\da\\pasta"
    ```
*   **O que faz:** Obtem um vídeo mp4 do filme/episódio contido no link e salva na pasta

### 2. Get Video Links
O script `get-video-links` foca especificamente na extração de URLs de vídeo de uma determinada série.
*   **Como executar:**
    ```bash
    python get-video-links.py "https://lookmovie2.com/serie/nome-da-serie" "arquivo.txt"
    ```
*   **O que faz:** Varre as páginas da série e obtém todos os links para baixar posteriormente.

## Requisitos
*   Python 3.x
*   FFmpeg >= 7.1.1
*   Poetry >= 2.4.1

