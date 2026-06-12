from pathlib import Path
import sys
from colorama import Fore
import ffmpeg

from util import highlight_text, print_status, safe_remove_file
import whisper
from whisper.utils import get_writer


# Extract audio using ffmpeg
def extract_audio(input_video: str):
    """Extrai audio de um arquivo em mp4 para um arquivo wav de mesmo nome, e retorna o nome do arquivo.

    Args:
        input_video (str): O arquivo de vídeo. Necessário estar formato mp4.

    Returns:
        _type_: O nome do arquivo wav
    """
    output_audio = f"{input_video.replace('.mp4', '.wav')}"
    
    print_status(f"Extraindo áudio do vídeo {input_video}...", Fore.YELLOW)
    ffmpeg.input(input_video).output(output_audio, loglevel="error").run(overwrite_output=True)

    print_status(f"Áudio extraído para {output_audio}!", Fore.GREEN)
    
    return output_audio

def add_captions_to_video(input_video: str, remove_original_file: bool = False):
    """
    Adiciona legendas a um vídeo MP4 usando o Whisper para transcrever o áudio.

    Args:
        input_video (str): O caminho para o arquivo de vídeo MP4 de entrada.
        remove_original_file (bool): Se True, o arquivo de vídeo original será removido após a conclusão.

    Returns:
        str: O caminho para o arquivo de vídeo MKV de saída com as legendas.
    """
    output_video = input_video.replace('.mp4', '.mkv')

    # Carregar o modelo Whisper
    print_status("Carregando o modelo Whisper...", Fore.BLUE)
    model = whisper.load_model("small")
    print_status("Modelo carregado com sucesso!", Fore.GREEN)
    
    print_status("Iniciando a extração de áudio e transcrição...", Fore.YELLOW)

    print_status(f"Processando vídeo do vídeo: {output_video}", Fore.CYAN)
    
    audio_file = extract_audio(input_video)
    
    print_status(f"Transcrevendo áudio do vídeo {output_video}...", Fore.YELLOW)
    
    result = model.transcribe(audio_file, verbose=True, fp16=False, word_timestamps=True)

    # Save as an SRT file
    srt_writer = get_writer("srt", './')
    srt_writer(result, audio_file)

    srt_file = f"{str(Path(input_video)).replace('.mp4', '.srt')}"
    print_status(f"Legendas salvas em: {srt_file}", Fore.GREEN)

    print_status("Adicionar legenda ao vídeo...", Fore.YELLOW)

    video_in = ffmpeg.input(input_video)
    srt_in = ffmpeg.input(srt_file)

    ffmpeg.\
        output(
            video_in['v'],       # Select original video stream
            video_in['a'],       # Select original audio stream
            srt_in['s'],         # Select subtitle stream
            output_video,
            c='copy',            # Stream copy for fast execution
            **{'c:s': 'ass', 'metadata:s:s:0': 'language=eng'}).run(overwrite_output=True)

    print(f"Arquivo final MKV com legendas e áudio original salvo como: {highlight_text(output_video, Fore.GREEN)}")
    
    # Limpeza de arquivos temporários
    print_status("Removendo arquivos temporários de adição de legendas...", Fore.YELLOW)
    
    safe_remove_file(audio_file)
    safe_remove_file(srt_file)

    if remove_original_file:
        safe_remove_file(input_video)

    print_status(f"Processo de adição de legendas para {input_video} concluído!", Fore.GREEN)

    return output_video


if __name__ == "__main__":
    # Usage: python add-captions-to-video.py [file] [remove-original]
    # Por algum motivo, 'python' não consta no sys.argv, então conta a partir disso

    if len(sys.argv) < 2:
        print("Usage: python add-captions-to-video.py [file] [remove-original]")
        print("Use remove-original apenas se quiser que o arquivo original seja apagado! Caso contrário não precisa escrever...")
        sys.exit(1)

    remove_original_file = False

    if 'remove-original' in str(sys.argv):
        remove_original_file = True

    add_captions_to_video(sys.argv[1], remove_original_file)