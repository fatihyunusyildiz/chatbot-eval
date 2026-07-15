# Offline Python Wheelhouse Kurulumu

Bu doküman, `chatbot-eval` projesinin Python/DeepEval bağımlılıklarını internet erişimi olmayan bir Windows bilgisayara taşımak için kullanılır.

Kapsam sadece Python tarafıdır. Java/Maven/Selenium bağımlılıkları bu dokümanın kapsamında değildir.

## Hedef Ortam

Wheelhouse şu ortam için hazırlanmalıdır:

```text
OS: Windows 64-bit
Python: 3.12.3
```

Offline bilgisayarda farklı Python sürümü veya farklı işletim sistemi varsa bu wheelhouse güvenilir şekilde çalışmayabilir. Özellikle `pandas`, `numpy`, `pydantic-core`, `aiohttp`, `grpcio`, `pywin32` gibi paketler platforma özel wheel dosyaları kullanır.

## Wheelhouse Mantığı

Normalde pip bağımlılıkları PyPI üzerinden indirir:

```powershell
python -m pip install chatbot-eval
```

Offline kurulumda pip internete çıkmaz. Bunun yerine önceden hazırlanmış `.whl` dosyalarının bulunduğu klasörden kurulum yapar:

```powershell
python -m pip install --no-index --find-links .\offline-python-wheelhouse chatbot-eval
```

Anlamı:

```text
--no-index      PyPI'a/internete gitme
--find-links    paketleri bu klasörde ara
```

## İnternetli Bilgisayarda Wheelhouse Hazırlama

Repo root klasöründe çalışın.

Python sürümünü kontrol edin:

```powershell
py -3.12 --version
```

Beklenen:

```text
Python 3.12.3
```

Wheelhouse klasörünü oluşturun:

```powershell
New-Item -ItemType Directory -Force offline-python-wheelhouse
```

Projeyi ve tüm Python bağımlılıklarını wheel olarak hazırlayın:

```powershell
py -3.12 -m pip wheel --wheel-dir offline-python-wheelhouse .
```

Opsiyonel sertifika bağımlılığı da gerekiyorsa:

```powershell
py -3.12 -m pip wheel --wheel-dir offline-python-wheelhouse ".[certs]"
```

Kontrol edin:

```powershell
Get-ChildItem offline-python-wheelhouse -Filter *.whl | Measure-Object
Get-ChildItem offline-python-wheelhouse -Filter chatbot_eval*.whl
```

`chatbot_eval-0.1.0-py3-none-any.whl` dosyası görünmelidir.

## Offline Bilgisayara Taşınacaklar

Aşağıdakileri USB/disk/kurum içi dosya paylaşımı ile offline bilgisayara taşıyın:

```text
offline-python-wheelhouse/
chatbot-eval proje klasörü veya proje zip'i
Python 3.12.3 installer, offline bilgisayarda Python yoksa
```

`offline-python-wheelhouse/` klasörü Git'e commitlenmek zorunda değildir. Büyük ve platforma özel bir dağıtım artifact'idir.

## Offline Bilgisayarda Kurulum

Repo root klasöründe çalışın.

Python sanal ortamını oluşturun:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Wheelhouse klasörü repo içindeyse:

```powershell
python -m pip install --no-index --find-links .\offline-python-wheelhouse chatbot-eval
```

Wheelhouse klasörü farklı bir dizindeyse:

```powershell
python -m pip install --no-index --find-links C:\path\to\offline-python-wheelhouse chatbot-eval
```

Kurulumu doğrulayın:

```powershell
python -m chatbot_eval metrics
```

Beklenen çıktı JSON formatında metric listesidir.

Örnek hata contract kontrolü:

```powershell
python -m chatbot_eval evaluate examples\missing.json
```

Beklenen davranış:

```text
status = ERROR
exit code = 2
```

## Geliştirme Modunda Kurulum

Offline bilgisayarda kaynak kod üzerinde geliştirme yapılacaksa editable install kullanılabilir:

```powershell
python -m pip install --no-index --find-links .\offline-python-wheelhouse -e . --no-build-isolation
```

Bu modda proje kodu değiştikçe tekrar wheel üretmeden Python importları güncel kodu kullanır.

## Güncelleme Akışı

Projede Python bağımlılığı değişirse veya `pyproject.toml` güncellenirse wheelhouse tekrar üretilmelidir:

```powershell
Remove-Item -Recurse -Force offline-python-wheelhouse
New-Item -ItemType Directory -Force offline-python-wheelhouse
py -3.12 -m pip wheel --wheel-dir offline-python-wheelhouse .
```

Sonra yeni `offline-python-wheelhouse/` klasörü offline bilgisayara tekrar taşınır.

## Sık Hatalar

### No matching distribution found

Sebep genelde wheelhouse içinde eksik veya uyumsuz wheel olmasıdır.

Kontrol edin:

```powershell
py -3.12 --version
Get-ChildItem offline-python-wheelhouse -Filter *.whl
```

Offline makine Python sürümü internetli makinedekiyle aynı olmalıdır.

### pip internete çıkmaya çalışıyor

Komutta `--no-index` olduğundan emin olun:

```powershell
python -m pip install --no-index --find-links .\offline-python-wheelhouse chatbot-eval
```

### Python paketi bulunamıyor

Proje wheel dosyasının wheelhouse içinde olduğundan emin olun:

```powershell
Get-ChildItem offline-python-wheelhouse -Filter chatbot_eval*.whl
```

Gerekirse doğrudan wheel dosyasını kurun:

```powershell
python -m pip install --no-index --find-links .\offline-python-wheelhouse .\offline-python-wheelhouse\chatbot_eval-0.1.0-py3-none-any.whl
```

### Judge model çalışmıyor

Python bağımlılıkları offline kurulabilir, fakat Google/Gemini veya OpenRouter judge modeli internet gerektirir.

Tam offline değerlendirme için ileride local judge provider gerekir. Bu durumda CLI contract değişmemelidir:

```text
python -m chatbot_eval evaluate <evaluation_input.json> [metric]
```

Exit code contract aynı kalmalıdır:

```text
0 = PASS
1 = FAIL
2 = ERROR
```

## Git Notu

Aşağıdaki dosya/klasörler Git'e eklenmemelidir:

```text
offline-python-wheelhouse/
.offline-wheel-test-venv/
.venv/
build/
```

Bu doküman Git'e eklenebilir:

```text
docs/offline-python-wheelhouse.md
```