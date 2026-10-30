"""
Pydantic Schemas for Department Structured Outputs.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class PRDSpecOutput(BaseModel):
    """CPO / Ürün Lideri çıktısı."""
    app_name: str = Field(description="Uygulamanın akılda kalıcı, profesyonel adı (Örn: 'FinRisk Dashboard Pro')")
    app_slug: str = Field(description="Klasör ve dosya sistemi için güvenli slug (Örn: 'finrisk_dashboard')")
    app_type: Literal["Streamlit Web App", "FastAPI REST Service", "CLI & Automation Tool"] = Field(
        description="Kullanıcı amacına en uygun uygulama mimarisi türü"
    )
    purpose_summary: str = Field(description="Uygulamanın çözdüğü somut iş problemi ve sunduğu değerin 2-3 cümlelik özeti")
    target_users: str = Field(description="Hedef kullanıcı kitlesi ve kullanım senaryosu")
    core_features: List[str] = Field(description="MVP kapsamında yer alacak 4-6 adet somut özellik")
    user_flow_steps: List[str] = Field(description="Kullanıcının uygulamayı açtığında izleyeceği 3-5 adımlık temel akış")
    initial_seed_data_description: str = Field(
        description="Kullanıcının ilk açılışta boş ekran görmemesi için SQLite veya mock veri olarak yüklenecek zengin başlangıç verilerinin tanımı"
    )
    full_prd_markdown: str = Field(description="Mühendislerin tek seferde anlayabileceği detaylı PRD teknik şartnamesi")


class ArchitectureSpecOutput(BaseModel):
    """CTO / Baş Sistem Mimarı çıktısı."""
    tech_stack: List[str] = Field(
        description="Kullanılacak somut teknolojiler (Örn: ['Python 3.12', 'Streamlit', 'SQLite3', 'Pandas', 'Altair'])"
    )
    database_choice: str = Field(description="Veri saklama katmanı seçimi ve gerekçesi (Örn: 'SQLite3 yerel kalıcı veritabanı')")
    entrypoint_file: str = Field(description="Uygulamanın ana çalıştırma giriş dosyası (Örn: 'app.py' veya 'main.py')")
    planned_files: List[dict] = Field(
        description="Geliştirilecek her dosyanın adı ve sorumluluk özeti (Örn: [{'filename': 'app.py', 'purpose': 'Streamlit arayüzü'}, {'filename': 'database.py', 'purpose': 'SQLite CRUD işlemleri'}])"
    )
    data_models_summary: str = Field(description="Veritabanı tabloları veya Pydantic veri modellerinin şeması")
    component_contracts: str = Field(description="Dosyaların birbirini nasıl çağıracağı ve hangi fonksiyonları sunacağı")
    architecture_summary_markdown: str = Field(description="Geliştirici ekibe yönelik mimari kılavuz ve teknik şartname")


class GeneratedFileItem(BaseModel):
    """Üretilen tek bir dosya."""
    filename: str = Field(description="Dosya adı (Örn: 'app.py', 'database.py', 'services.py')")
    content: str = Field(description="Dosyanın eksiksiz, çalışan, kısaltılmamış tam Python kaynak kodu")
    loc: int = Field(description="Bu dosyadaki satır sayısı")


class CodeBundleOutput(BaseModel):
    """Kıdemli Yazılım Mühendisi tam kod paketi çıktısı."""
    summary: str = Field(description="Kodlanan uygulamanın teknik özeti ve modül yapısı")
    files: List[GeneratedFileItem] = Field(description="Uygulamanın tüm kaynak kod dosyaları listesi")


class QAReviewOutput(BaseModel):
    """QA & Güvenlik Lideri denetim çıktısı."""
    passed: bool = Field(description="Kod üretim kalitesi, hata yönetimi ve PRD uyumu onaylandı mı?")
    overall_quality_score: int = Field(description="1-100 arası genel kod kalitesi puanı")
    identified_issues: List[str] = Field(description="Tespit edilen mantıksal, sözdizimsel veya eksik özellik hataları")
    remedy_instructions: str = Field(description="Hatalar varsa Kıdemli Mühendisin bunları nasıl düzelteceğine dair somut talimatlar")
    detailed_report_markdown: str = Field(description="Yönetici için hazırlanmış kapsamlı QA & Güvenlik Raporu")


class DirectorRouteOutput(BaseModel):
    """Stüdyo Direktörü yönlendirme kararı."""
    next_node: Literal["Product_Lead", "System_Architect", "Lead_Developer", "QA_Security_Lead", "Deployment_Gate"] = Field(
        description="Mevcut stüdyo durumuna göre işi devralacak bir sonraki departman düğümü"
    )
    reasoning: str = Field(description="Bu departmanın seçilme gerekçesi ve döngü stratejisi")
