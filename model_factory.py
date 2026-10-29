import os
from typing import Sequence, Any, Optional, Iterator
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import Runnable

load_dotenv()

# ==============================================================================
# 1. Sabit Model & .env Tabanlı API Key Havuzu (Key Rotation Pool)
# ==============================================================================
# Model asla düşürülmez; tüm projede en güçlü ve güncel 'gemini-3.8-flash' kullanılır!
TARGET_MODEL = "gemini-3.8-flash"

def _get_key_pool() -> list[str]:
    """Tüm API anahtarlarını GÜVENLİ bir şekilde yalnızca .env dosyasından okur."""
    raw = os.getenv("GOOGLE_API_KEYS")
    if raw:
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if keys:
            return keys
            
    single_key = os.getenv("GOOGLE_API_KEY")
    if single_key:
        return [single_key.strip()]
        
    raise ValueError(
        "HATA: .env dosyasında geçerli bir API anahtarı bulunamadı! "
        "Lütfen .env dosyanıza GOOGLE_API_KEYS tanımlayınız."
    )

API_KEY_POOL = _get_key_pool()

def _print_key_rotate_warning(old_index: int, new_index: int, reason: str):
    """API anahtarı değiştiğinde konsola dikkat çekici bir rotasyon kartı basar."""
    border = "═" * 72
    print(f"\n{border}")
    print("🔄   [API KEY ROTASYONU / FAILOVER ACTIVATED]")
    print(border)
    print(f"  • Model       : '{TARGET_MODEL}' (SABİT - Model Asla Değişmedi)")
    print(f"  • Önceki Key  : Key #{old_index + 1} (Kota / Geçici Yoğunluk)")
    print(f"  • Hata Sebebi : {reason[:60]}...")
    print(f"  • Yeni Key    : ➔ Key #{new_index + 1} devreye alındı!")
    print(f"{border}\n")

# ==============================================================================
# 2. Key-Rotating LLM Sınıfı
# ==============================================================================
class KeyRotatingGeminiLLM(Runnable):
    """
    Modeli sabit tutup (gemini-3.8-flash), kota veya hata durumunda
    .env'den okunan API anahtarları arasında anında rotasyon yapan kurumsal sınıf.
    """
    def __init__(
        self,
        api_keys: list[str] = API_KEY_POOL,
        model_name: str = TARGET_MODEL,
        temperature: float = 0.2,
        tools: Optional[Sequence[Any]] = None,
        structured_schema: Optional[Any] = None,
        structured_kwargs: Optional[dict] = None,
        active_index: int = 0
    ):
        self.api_keys = api_keys
        self.model_name = model_name
        self.temperature = temperature
        self.tools = tools
        self.structured_schema = structured_schema
        self.structured_kwargs = structured_kwargs or {}
        self.active_index = active_index % len(api_keys)

    def _create_model_for_key(self, api_key: str):
        """Belirtilen anahtarla modeli oluşturur ve varsa tool / schema bağlar."""
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=self.temperature,
            max_retries=0  # Hata durumunda beklemeden bir sonraki anahtara geç!
        )
        if self.tools:
            llm = llm.bind_tools(self.tools)
        if self.structured_schema:
            llm = llm.with_structured_output(self.structured_schema, **self.structured_kwargs)
        return llm

    def invoke(self, input: Any, config: Optional[dict] = None, **kwargs) -> Any:
        total_keys = len(self.api_keys)
        last_exception = None

        for attempt in range(total_keys):
            idx = (self.active_index + attempt) % total_keys
            key = self.api_keys[idx]
            model = self._create_model_for_key(key)

            try:
                response = model.invoke(input, config=config, **kwargs)
                self.active_index = idx
                return response
            except Exception as e:
                last_exception = e
                next_idx = (idx + 1) % total_keys
                _print_key_rotate_warning(
                    old_index=idx,
                    new_index=next_idx,
                    reason=str(e)
                )
                continue

        raise last_exception

    def stream(self, input: Any, config: Optional[dict] = None, **kwargs) -> Iterator[Any]:
        total_keys = len(self.api_keys)
        last_exception = None

        for attempt in range(total_keys):
            idx = (self.active_index + attempt) % total_keys
            key = self.api_keys[idx]
            model = self._create_model_for_key(key)

            try:
                for chunk in model.stream(input, config=config, **kwargs):
                    yield chunk
                self.active_index = idx
                return
            except Exception as e:
                last_exception = e
                next_idx = (idx + 1) % total_keys
                _print_key_rotate_warning(
                    old_index=idx,
                    new_index=next_idx,
                    reason=str(e)
                )
                continue

        raise last_exception

    def bind_tools(self, tools: Sequence[Any], **kwargs):
        """ToolNode uyumluluğu için araç bağlama metodu."""
        return KeyRotatingGeminiLLM(
            api_keys=self.api_keys,
            model_name=self.model_name,
            temperature=self.temperature,
            tools=tools,
            structured_schema=self.structured_schema,
            structured_kwargs=self.structured_kwargs,
            active_index=self.active_index
        )

    def with_structured_output(self, schema: Any, **kwargs):
        """Pydantic şemalarıyla yapılandırılmış çıktı metodu."""
        return KeyRotatingGeminiLLM(
            api_keys=self.api_keys,
            model_name=self.model_name,
            temperature=self.temperature,
            tools=self.tools,
            structured_schema=schema,
            structured_kwargs=kwargs,
            active_index=self.active_index
        )

# ==============================================================================
# 3. Genel Model Fabrikası Fonksiyonu
# ==============================================================================
def get_gemini_llm(temperature: float = 0.2, tools: Optional[Sequence[Any]] = None):
    """
    Her zaman 'gemini-3.8-flash' kullanan ve .env'deki API anahtarları arasında
    otomatik rotasyon yapan dayanıklı LLM nesnesini döner.
    """
    return KeyRotatingGeminiLLM(
        api_keys=API_KEY_POOL,
        model_name=TARGET_MODEL,
        temperature=temperature,
        tools=tools
    )

if __name__ == "__main__":
    print(f"Aktif Model: {TARGET_MODEL}")
    print(f".env'den Okunan API Anahtarı Sayısı: {len(API_KEY_POOL)}")
    llm = get_gemini_llm()
    print("Rotasyon mekanizması test ediliyor...")
    res = llm.invoke("Merhaba! Sistem çalışıyor mu?")
    print("Test Başarılı! Yanıt alındı.")
