import os
from pathlib import Path
import smtplib
import sys
from typing import Any, Callable
from colorama import Fore, Style
from dotenv import dotenv_values, load_dotenv
import time
from unidecode import unidecode

load_dotenv()

config = dotenv_values(".env")


def send_status_email(title: str, message: str):
    SENDER_EMAIL = config['SENDER_EMAIL']
    RECEIVER_EMAIL = config['RECEIVER_EMAIL']
    PASSWORD = config['EMAIL_PASSWORD']

    # Configuração do Gmail
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 465 # Porta recomendada para SSL

    if not SENDER_EMAIL or not RECEIVER_EMAIL or not PASSWORD:
        raise Exception("Erro de configuração no .env!")
    
    try:
        # Usa smtplib.SMTP_SSL para conexão segura na porta 465
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            
            # Faz o login usando o e-mail e a Senha de Aplicativo
            server.login(SENDER_EMAIL, PASSWORD)
            
            # Envia o e-mail
            server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], 'Subject: {}\n\n{}'.format(unidecode(title), unidecode(message)))

    except smtplib.SMTPAuthenticationError as e:
        print_status(f"ERRO DE AUTENTICAÇÃO: Verifique se a Senha de Aplicativo do Google está correta e se a Verificação em Duas Etapas está ativada. Detalhes: {e}", Fore.RED)
    except smtplib.SMTPException as e:
        print_status(f"ERRO SMTP: Ocorreu um erro ao se comunicar com o servidor de e-mail. Detalhes: {e}", Fore.RED)
    except KeyboardInterrupt:
        print_status("Interrompido pelo usuário!", Fore.RED)
    except Exception as e:
        print_status(f"ERRO DESCONHECIDO: Não foi possível enviar o e-mail. {e}", Fore.RED)   


def executar_tarefa_com_alerta(
    func: Callable, 
    task_name: str, 
    max_retries: int = 3, 
    retry_delay_sec: int = 5,
    *args, 
    **kwargs
) -> Any:
    """
    Executa uma função com retentativas e envia alertas Pushover em caso de sucesso ou falha.
    """
    
    print(f"\n[INÍCIO] Tarefa: {task_name}")
    
    for attempt in range(max_retries):
        try:
            print(f"Tentativa {attempt + 1} de {max_retries}...")
            
            # 1. Executa a função do usuário
            resultado = func(*args, **kwargs)
            
            # 2. Se for bem-sucedido: Alerta de Sucesso (Prioridade normal)
            # send_status_email(
            #     title=f"SUCESSO: {task_name}",
            #     message=f"A tarefa foi concluída com sucesso na tentativa {attempt + 1}. ",
            # )

            print_status(f"[SUCESSO] Tarefa '{task_name}' concluída.", Fore.GREEN)
            return resultado
        except KeyboardInterrupt:
            print_status("Interrompido pelo usuário!", Fore.RED)
            sys.exit(1)
        except Exception as e:
            # Captura qualquer exceção
            print(f"-> ERRO na Tentativa {attempt + 1}: {type(e).__name__} - {str(e)[:100]}...")
            
            if attempt < max_retries - 1:
                # 3. Se não for a última tentativa: Alerta de Retentativa (Prioridade baixa/normal)
                send_status_email(
                    title=f"Falha Temporária: {task_name}",
                    message=f"Erro: {e}. \n\n Tentando novamente em {retry_delay_sec}s...",
                )
                time.sleep(retry_delay_sec)
            else:
                # 4. Se for a última tentativa: Alerta Crítico (Prioridade alta)
                send_status_email(
                    title=f"FALHA CRÍTICA: {task_name}",
                    message=f"A tarefa falhou permanentemente após {max_retries} tentativas. Erro final: {type(e).__name__} - {e}",
                )
                
                print_status(f"[FALHA CRÍTICA] Tarefa '{task_name}' falhou após {max_retries} tentativas.", Fore.RED)

                raise Exception(f"Tarefa falhou permanentemente. Erro: {e}") from e


def print_status(message, status=Fore.GREEN):
    symbol = ""
    
    if status == Fore.GREEN:
        symbol = "[✓]" + " "
    elif status == Fore.RED:
        symbol = "[X]" + " "
    elif status == Fore.YELLOW:
        symbol = "[⚠]" + " "
    else:
        symbol = "[i]" + " "

    print(f"{status}{symbol}{message}{Style.RESET_ALL}")


def highlight_text(text, status=Fore.GREEN):
    return f"{status}`{text}`{Style.RESET_ALL}"


def safe_remove_file(filepath):
    """Remove arquivo se existir"""
    try:
        file_path = Path(filepath)
        if file_path.exists():
            file_path.unlink()
    except OSError as e:
        print(f"Aviso: Não foi possível remover {filepath}: {e}")


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"

if __name__ == "__main__":
    send_status_email("TITULO", "oie td bem olha oq aconteceu foi o seguinte")