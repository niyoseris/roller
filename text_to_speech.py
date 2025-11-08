# Text to Speech örneği - Google Gemini API kullanarak
# pip install google-genai

import base64
import mimetypes
import os
import re
import struct
from google import genai
from google.genai import types
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


def save_binary_file(file_name, data):
    """Ses dosyasını kaydeder"""
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"Dosya kaydedildi: {file_name}")


def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Ham ses verisini WAV formatına dönüştürür
    
    Args:
        audio_data: Ham ses verisi
        mime_type: Ses verisinin MIME tipi
        
    Returns:
        WAV formatında ses verisi
    """
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size

    # WAV header oluştur
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",          # ChunkID
        chunk_size,       # ChunkSize
        b"WAVE",          # Format
        b"fmt ",          # Subchunk1ID
        16,               # Subchunk1Size (PCM için 16)
        1,                # AudioFormat (PCM için 1)
        num_channels,     # Kanal sayısı
        sample_rate,      # Örnekleme hızı
        byte_rate,        # ByteRate
        block_align,      # BlockAlign
        bits_per_sample,  # Bit derinliği
        b"data",          # Subchunk2ID
        data_size         # Ses verisi boyutu
    )
    return header + audio_data


def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """MIME tipinden ses parametrelerini çıkarır
    
    Args:
        mime_type: Ses MIME tipi (örn: "audio/L16;rate=24000")
        
    Returns:
        Bit derinliği ve örnekleme hızı içeren dict
    """
    bits_per_sample = 16
    rate = 24000

    parts = mime_type.split(";")
    for param in parts:
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                pass
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass

    return {"bits_per_sample": bits_per_sample, "rate": rate}


def generate_speech(text: str, voice_name: str = "Charon", output_prefix: str = "output"):
    """Metinden ses oluşturur
    
    Args:
        text: Seslendirilecek metin
        voice_name: Kullanılacak ses (Charon, Zephyr, Puck, vb.)
        output_prefix: Çıktı dosya adı öneki
    """
    # API istemcisi oluştur
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-preview-tts"
    
    # İçerik oluştur
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=text),
            ],
        ),
    ]
    
    # Yapılandırma
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name
                )
            ),
        ),
    )

    print(f"Ses oluşturuluyor... (Ses: {voice_name})")
    
    # Ses üret ve kaydet
    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
            
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"{output_prefix}_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            
            if file_extension is None:
                file_extension = ".wav"
                data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            if hasattr(chunk, 'text'):
                print(chunk.text)


def generate_multi_speaker_speech(speakers_text: dict, output_prefix: str = "dialog"):
    """Çoklu konuşmacı ile diyalog oluşturur
    
    Args:
        speakers_text: {"Speaker 1": {"text": "...", "voice": "Charon"}, ...}
        output_prefix: Çıktı dosya adı öneki
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-preview-tts"
    
    # Diyalog metnini oluştur
    dialog_text = ""
    for speaker, config in speakers_text.items():
        dialog_text += f"{speaker}: {config['text']}\n"
    
    # Konuşmacı yapılandırmalarını oluştur
    speaker_configs = []
    for speaker, config in speakers_text.items():
        speaker_configs.append(
            types.SpeakerVoiceConfig(
                speaker=speaker,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=config.get("voice", "Charon")
                    )
                ),
            )
        )
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=dialog_text),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=speaker_configs
            ),
        ),
    )

    print(f"Çoklu konuşmacı diyalogu oluşturuluyor...")
    
    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
            
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"{output_prefix}_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            
            if file_extension is None:
                file_extension = ".wav"
                data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            if hasattr(chunk, 'text'):
                print(chunk.text)


if __name__ == "__main__":
    # Örnek 1: Tek konuşmacı (Charon sesi)
    print("=== Örnek 1: Tek Konuşmacı ===")
    turkish_text = """Merhaba! Ben Charon sesi ile konuşuyorum. 
    Google Gemini'nin text-to-speech özelliği ile Türkçe metin seslendirebiliyoruz."""
    
    generate_speech(
        text=turkish_text,
        voice_name="Charon",
        output_prefix="turkce_ses"
    )
    
    print("\n=== Örnek 2: Çoklu Konuşmacı ===")
    # Örnek 2: Çoklu konuşmacı diyalog
    dialog = {
        "Ahmet": {
            "text": "Merhaba! Bugün hava çok güzel değil mi?",
            "voice": "Charon"
        },
        "Ayşe": {
            "text": "Evet, harika bir gün. Dışarı çıkıp yürüyüş yapmak istiyorum.",
            "voice": "Aoede"
        }
    }
    
    generate_multi_speaker_speech(
        speakers_text=dialog,
        output_prefix="diyalog"
    )
    
    print("\n✅ Tüm ses dosyaları oluşturuldu!")
