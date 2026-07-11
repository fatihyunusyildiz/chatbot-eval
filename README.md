# Black-box Chatbot / RAG Evaluation

Bu proje, sadece chatbot arayüzünden alınan `input -> final output` cevabını kullanarak black-box chatbot/RAG değerlendirmesi yapar. Java/Selenium tarafı chatbot UI'ını sürer, Python tarafı DeepEval/GEval tabanlı değerlendirme yapar ve sonuçları `PASS`, `FAIL` veya `ERROR` olarak döndürür.

## Temel Kararlar

- Python sürümü `3.12.3` olarak sabittir.
- Java tarafı Java 21 ile çalışır.
- Java otomasyonu Python'u sadece CLI contract üzerinden çağırır.
- Python CLI stdout çıktısı JSON result için ayrılmıştır.
- DeepEval/debug/log çıktıları stderr veya artifact dosyalarına yazılır.
- Manual review adımı yoktur.
- Retrieval metrikleri yoktur.
- RAGAS kullanılmaz.

## Repo Yapısı

```text
.
├─ src/                       # Python paketleri ve modülleri
├─ tests/                     # Python testleri
├─ data/                      # Golden dataset dosyaları
├─ examples/                  # Evaluation input örnekleri
├─ java-automation/           # Java 21 + Maven + Cucumber/Selenium otomasyonu
├─ docs/                      # Lokal araç notları
├─ pyproject.toml             # Python paket tanımı
├─ pytest.ini
└─ README.md
```

## Git'e Girmemesi Gerekenler

Aşağıdaki dosya/klasörler lokal üretilir ve `.gitignore` kapsamındadır:

```text
.env
.venv/
.tools/
.idea/
target/
java-automation/target/
.pytest_cache/
.deepeval/
reports/
__pycache__/
*.egg-info/
```

Yeni cihazda bu dosyalar tekrar oluşturulur.

## Ön Gereklilikler

Yeni bir cihazda aşağıdaki araçlar gerekir:

- Python `3.12.3`
- Git
- Google Cloud CLI, Google ADC kullanılacaksa
- Eclipse Temurin JDK 21 veya uyumlu JDK 21
- Apache Maven veya repo altındaki `.tools` yapısına kurulmuş portable Maven
- Chrome, Selenium senaryoları çalıştırılacaksa

## Yeni Cihazda Kurulum

Repo'yu klonladıktan sonra repo root klasöründe çalışın.

```powershell
git clone <repo-url>
cd <repo-folder>
```

Python virtual environment oluşturun:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Lokal environment dosyasını oluşturun:

```powershell
Copy-Item .env.example .env
```

Sonra `.env` içindeki değerleri kendi makinenize göre doldurun.

## Google ADC ile Kullanım

Google Vertex/Gemini kullanılacaksa `.env` içinde en az şu değerler bulunmalıdır:

```dotenv
MODEL_PROVIDER=google_vertex
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_REQUIRE_PROJECT=false
GOOGLE_CHATBOT_MODEL=gemini-2.5-flash
GOOGLE_JUDGE_MODEL=gemini-2.5-flash
```

ADC login:

```powershell
gcloud auth application-default login
gcloud config set project your-gcp-project-id
```

`GOOGLE_CLOUD_PROJECT` boş bırakılırsa proje ID sırasıyla environment değişkenlerinden, ADC'den ve `gcloud config get-value project` çıktısından okunmaya çalışılır. Production veya CI ortamlarında proje ID'yi açıkça vermek daha güvenlidir.

## OpenRouter Fallback

OpenRouter kullanılacaksa `.env` içinde provider değiştirin ve API key girin:

```dotenv
MODEL_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_CHATBOT_MODEL=openrouter/free
OPENROUTER_JUDGE_MODEL=openrouter/free
OPENROUTER_SSL_VERIFY=true
```

`OPENROUTER_SSL_VERIFY=false` sadece geçici sertifika sorunlarında kullanılmalıdır.

## Python Evaluation CLI

Python CLI, Java/Selenium tarafından üretilen evaluation JSON payload'ını değerlendirir.

Metric listesini görmek:

```powershell
python -m chatbot_eval metrics
```

Tek payload değerlendirmek:

```powershell
python -m chatbot_eval evaluate examples\single_turn_evaluation_input.json
python -m chatbot_eval evaluate examples\multi_turn_evaluation_input.json correction_handling
```

Golden dataset üstünden metric probe çalıştırmak:

```powershell
python -m chatbot_eval metric instruction_persistence
python -m chatbot_eval metric correction_handling MT-005
```

Exit code contract:

```text
0 = PASS
1 = FAIL
2 = ERROR
```

Java tarafı bu contract'a bağlıdır. CLI komut adı, stdout JSON formatı ve exit code anlamları korunmalıdır.

## Java Otomasyonu

Java otomasyonu `java-automation/` altında Maven projesi olarak durur. Ana görevleri:

- Chatbot UI'ını Selenium ile açmak
- Golden dataset'teki mesajları chatbot'a göndermek
- Conversation artifact'lerini yazmak
- `evaluation_input.json` üretmek
- Python CLI'ı çağırmak
- Python sonucunu Java assertion'a çevirmek

Java'nın Python'u çağırdığı contract:

```text
<python.executable> -m chatbot_eval evaluate <evaluation_input.json> [metric]
```

Bu değerler şuradan okunur:

```text
java-automation/src/test/resources/config/deepeval.properties
```

Varsayılan config:

```properties
python.executable=..\.venv\Scripts\python.exe
python.workingDirectory=..
deepeval.timeoutSeconds=300
deepeval.artifactDirectory=target/deepeval-artifacts
```

Bu relative path yapısı repo farklı klasöre klonlansa da çalışacak şekilde tasarlanmıştır. Java komutları repo root'tan çalıştırıldığında helper script Maven'i `java-automation/` altında başlatır ve `..` repo root'a denk gelir.

## Java 21 / Maven Komutları

JDK ve Maven doğrulama:

```powershell
.\java-automation\scripts\mvn-java21.ps1 -version
```

Java unit/smoke testleri:

```powershell
.\java-automation\scripts\mvn-java21.ps1 test
```

Cucumber dry-run, gerçek browser/model çağırmadan step eşleşmesini doğrular:

```powershell
.\java-automation\scripts\mvn-java21.ps1 --% -Dcucumber.execution.dry-run=true -Dcucumber.filter.tags=@deepeval -Pcucumber verify
.\java-automation\scripts\mvn-java21.ps1 --% -Dcucumber.execution.dry-run=true -Dcucumber.filter.tags=@quillbot_deepeval -Pcucumber verify
.\java-automation\scripts\mvn-java21.ps1 --% -Dcucumber.execution.dry-run=true -Dcucumber.filter.tags=@quillbot_smoke -Pcucumber verify
```

Gerçek QuillBot Selenium + DeepEval akışı:

```powershell
.\java-automation\scripts\mvn-java21.ps1 --% -Dchatbot.config=config/quillbot.properties -Dcucumber.filter.tags=@quillbot_deepeval -Pcucumber verify
```

Default/local chatbot config ile çalıştırmak:

```powershell
.\java-automation\scripts\mvn-java21.ps1 --% -Dchatbot.config=config/chatbot.properties -Pcucumber verify
```

## Chatbot UI Config

Test edilen chatbot UI config dosyaları burada durur:

```text
java-automation/src/test/resources/config/chatbot.properties
java-automation/src/test/resources/config/quillbot.properties
```

Yeni bir chatbot için yeni config dosyası oluşturabilirsiniz:

```text
java-automation/src/test/resources/config/my-chatbot.properties
```

Örnek:

```properties
chatbot.url=http://localhost:3000
chatbot.browser=chrome
chatbot.headless=false
chatbot.login.required=false
chatbot.input.selector=[data-testid='chat-input']
chatbot.send.selector=[data-testid='send-button']
chatbot.send.mode=button
chatbot.assistantMessage.selector=[data-testid='assistant-message']
chatbot.newChat.selector=
chatbot.dismiss.selector=
chatbot.response.ignoreTexts=
chatbot.response.timeoutSeconds=60
chatbot.response.stableMillis=1500
```

Çalıştırma:

```powershell
.\java-automation\scripts\mvn-java21.ps1 --% -Dchatbot.config=config/my-chatbot.properties -Pcucumber verify
```

## Cucumber Step'leri

Smoke testlerde kullanılabilecek generic step'ler:

```gherkin
Given chatbot UI is opened
When user sends "Sadece OK yaz."
Then assistant reply should contain "OK"
```

Multi-turn smoke:

```gherkin
Given chatbot UI is opened
When user sends these messages
  | Benim adim Fatih.               |
  | Az once soyledigim ismim neydi? |
Then assistant reply should contain "Fatih"
```

DeepEval evaluation:

```gherkin
Given golden single-turn test case "TC-001" yüklenir
When kullanıcı mesajı chatbot arayüzünde gönderir
Then DeepEval sonucu PASS olmalıdır
```

Metric override ile:

```gherkin
Given golden multi-turn test case "MT-005" yüklenir
When kullanıcı konuşmayı chatbot arayüzünde tamamlar
Then "correction_handling" metriği PASS olmalıdır
```

## Test ve Doğrulama

Python testleri:

```powershell
python -m pytest
```

CLI contract kontrolü:

```powershell
python -m chatbot_eval metrics
python -m chatbot_eval evaluate examples\missing.json
```

Beklenen: missing file için JSON formatında `ERROR` ve exit code `2`.

Java testleri:

```powershell
.\java-automation\scripts\mvn-java21.ps1 test
```

Cucumber step uyumluluğu:

```powershell
.\java-automation\scripts\mvn-java21.ps1 --% -Dcucumber.execution.dry-run=true -Dcucumber.filter.tags=@deepeval -Pcucumber verify
```

## Artifact Çıktıları

Java/Selenium akışı her scenario için şu dosyaları üretir:

```text
java-automation/target/deepeval-artifacts/<test_id>/evaluation_input.json
java-automation/target/deepeval-artifacts/<test_id>/evaluation_result.json
java-automation/target/deepeval-artifacts/<test_id>/conversation.json
java-automation/target/deepeval-artifacts/<test_id>/browser_screenshot.png
java-automation/target/deepeval-artifacts/<test_id>/deepeval_stdout.json
java-automation/target/deepeval-artifacts/<test_id>/deepeval_stderr.log
```

Bu dosyalar build artifact kabul edilir ve Git'e eklenmemelidir.

## Local LLM Judge Notu

İleride judge model local LLM'e alınırsa Java tarafı değişmek zorunda değildir. Java sadece Python CLI contract'ını çağırır:

```text
python -m chatbot_eval evaluate <evaluation_input.json> [metric]
```

Local LLM entegrasyonu Python tarafında yeni provider/client olarak eklenmelidir. Şu contract korunmalıdır:

- stdout sadece JSON result üretir.
- `0 = PASS`, `1 = FAIL`, `2 = ERROR` kalır.
- JSON schema değişmez.
