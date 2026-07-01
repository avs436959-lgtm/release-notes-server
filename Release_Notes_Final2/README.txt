Release Notes Platform - veritabanli surum

Kullanim:
1. Bu klasoru komple gonder: "Release Notes Platform portable-db".
2. Karsi bilgisayarda klasoru ac.
3. start.bat dosyasina cift tikla.
4. Tarayici otomatik acilir. Acilmazsa siyah pencerede yazan http://127.0.0.1:... adresini kopyalayip Chrome, Edge veya Firefox'ta ac.

Veriler nerede saklanir?
- Varsayilan durumda tum yayinlar ve ayarlar release_notes.db dosyasina kaydedilir.
- MongoDB acarsan veriler MongoDB'ye kaydedilir.
- MongoDB icin MONGODB_SETUP.txt dosyasini oku.
- Ayni bilgisayarda farkli tarayicilar ayni veritabanini gorur.
- Ayni MongoDB baglantisi kullanilirsa farkli bilgisayarlar da ayni veriyi gorur.

Onemli:
- Uygulamayi kullanirken start.bat ile acilan pencere kapanmamali.
- index.html dosyasina direkt cift tiklarsan ortak veritabani yerine tarayici yedegi calisir.
- MongoDB acik degilse bu yerel veritabanidir. Ayni anda farkli bilgisayarlardan ortak kullanmak icin MongoDB gibi online veritabani gerekir.
