#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text-to-Speech basit test dosyası
Charon sesi ile Türkçe metin oluşturur
"""

from text_to_speech import generate_speech, generate_multi_speaker_speech
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


def test_single_speaker():
    """Tek konuşmacı testi - Charon sesi"""
    print("=" * 50)
    print("TEST 1: Tek Konuşmacı (Charon)")
    print("=" * 50)
    
    text = """Merhaba! Ben Charon sesi ile konuşuyorum. 
    Google Gemini'nin yapay zeka destekli text-to-speech teknolojisi 
    ile Türkçe metinleri doğal bir şekilde seslendirebiliyorum."""
    
    generate_speech(
        text=text,
        voice_name="Charon",
        output_prefix="test_charon"
    )
    print("✓ Test 1 tamamlandı!\n")


def test_multi_speaker():
    """Çoklu konuşmacı testi"""
    print("=" * 50)
    print("TEST 2: Çoklu Konuşmacı Diyalog")
    print("=" * 50)
    
    dialog = {
        "Ahmet": {
            "text": "Merhaba Ayşe! Bugün projemiz hakkında konuşabilir miyiz?",
            "voice": "Charon"
        },
        "Ayşe": {
            "text": "Tabii ki Ahmet. Hangi konuyu tartışmak istersin?",
            "voice": "Aoede"
        },
        "Ahmet": {
            "text": "Öncelikle text-to-speech entegrasyonunu tamamladık.",
            "voice": "Charon"
        },
        "Ayşe": {
            "text": "Harika! Charon sesi çok doğal gelmiş.",
            "voice": "Aoede"
        }
    }
    
    generate_multi_speaker_speech(
        speakers_text=dialog,
        output_prefix="test_diyalog"
    )
    print("✓ Test 2 tamamlandı!\n")


def test_different_voices():
    """Farklı sesler ile test"""
    print("=" * 50)
    print("TEST 3: Farklı Sesler")
    print("=" * 50)
    
    voices = ["Charon", "Zephyr", "Puck"]
    text = "Bu ses testi örneğidir."
    
    for voice in voices:
        print(f"\n📢 {voice} sesi test ediliyor...")
        generate_speech(
            text=f"Merhaba, ben {voice} sesi. {text}",
            voice_name=voice,
            output_prefix=f"test_{voice.lower()}"
        )
    
    print("\n✓ Test 3 tamamlandı!\n")


def test_long_text():
    """Uzun metin testi"""
    print("=" * 50)
    print("TEST 4: Uzun Metin")
    print("=" * 50)
    
    long_text = """
    Yapay zeka teknolojileri son yıllarda inanılmaz bir gelişim gösterdi.
    
    Text-to-speech sistemleri artık çok daha doğal ve insan benzeri sesler üretebiliyor.
    Google Gemini API'si ile farklı dillerde, farklı tonlarda konuşmalar oluşturabiliriz.
    
    Charon sesi özellikle Türkçe metinler için mükemmel bir seçenek.
    Derin ve net bir tonu var.
    
    Bu teknoloji sayesinde sesli kitaplar, podcast'ler, eğitim materyalleri 
    ve daha birçok içerik türü kolayca oluşturulabiliyor.
    
    Gelecekte bu teknolojinin daha da gelişeceğini ve hayatımızın 
    birçok alanında kullanılacağını göreceğiz.
    """
    
    generate_speech(
        text=long_text,
        voice_name="Charon",
        output_prefix="test_uzun_metin"
    )
    print("✓ Test 4 tamamlandı!\n")


def main():
    """Ana test fonksiyonu"""
    # API anahtarı kontrolü
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ HATA: GEMINI_API_KEY çevre değişkeni bulunamadı!")
        print("Lütfen .env dosyasında API anahtarınızı kontrol edin.")
        return
    
    print("\n🎙️  TEXT-TO-SPEECH TEST PROGRAMI 🎙️\n")
    print("Google Gemini API - Charon Sesi Test\n")
    
    try:
        # Test 1: Tek konuşmacı
        test_single_speaker()
        
        # Test 2: Çoklu konuşmacı
        test_multi_speaker()
        
        # Test 3: Farklı sesler
        # test_different_voices()  # İsteğe bağlı, yorum satırından çıkarabilirsiniz
        
        # Test 4: Uzun metin
        # test_long_text()  # İsteğe bağlı, yorum satırından çıkarabilirsiniz
        
        print("\n" + "=" * 50)
        print("✅ TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
        print("=" * 50)
        print("\n📁 Oluşturulan dosyaları kontrol edin:")
        print("   - test_charon_*.wav")
        print("   - test_diyalog_*.wav")
        print()
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        print("\nLütfen şunları kontrol edin:")
        print("1. GEMINI_API_KEY doğru mu?")
        print("2. google-genai paketi yüklü mü? (pip install google-genai)")
        print("3. İnternet bağlantınız var mı?")


if __name__ == "__main__":
    main()
