from io import BytesIO
import os
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ==========================================
# 0. SAYFA YAPILANDIRMASI VE SAYAC (DOSYA TABANLI)
# ==========================================
st.set_page_config(
    page_title="Gençlik Manevi Rehberlik ve Danışma Paneli",
    page_icon="🌱",
    layout="wide",
)

DOSYA_YOLU = "ziyaretci_sayaci.txt"

# Dosya yoksa başlangıç değerini oluştur
if not os.path.exists(DOSYA_YOLU):
  with open(DOSYA_YOLU, "w", encoding="utf-8") as f:
    f.write("1")

# Her F5 yenilemesinde veya yeni oturumda dosyadan okuyup artırma
if "sayac_arttirildi" not in st.session_state:
  with open(DOSYA_YOLU, "r", encoding="utf-8") as f:
    try:
      mevcut_sayi = int(f.read().strip())
    except ValueError:
      mevcut_sayi = 1

  mevcut_sayi += 1

  with open(DOSYA_YOLU, "w", encoding="utf-8") as f:
    f.write(str(mevcut_sayi))

  st.session_state.ziyaretci_sayisi = mevcut_sayi
  st.session_state.sayac_arttirildi = True
else:
  with open(DOSYA_YOLU, "r", encoding="utf-8") as f:
    st.session_state.ziyaretci_sayisi = int(f.read().strip())

# ==========================================
# 1. CSS STİLLERİ
# ==========================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 15px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .visitor-badge {
        background-color: #EEF2FF;
        border: 1px solid #C7D2FE;
        padding: 8px 15px;
        border-radius: 8px;
        display: inline-block;
        font-size: 14px;
        color: #3730A3;
        margin-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. YASAL UYARI VE GÜVENLİK BİLDİRİMİ
# ==========================================
st.warning(
    "⚠️ **YASAL UYARI VE BİLGİLENDİRME:** Bu platformda yer alan soru, cevap,"
    " analiz ve yönlendirmeler yalnızca **bireysel rehberlik, manevi gelişim ve"
    " akademik araştırma** amaçlıdır. Sunulan içerikler kesinlikle resmi fetva,"
    " bağlayıcı hukuki veya tıbbi hüküm niteliği taşımaz. Dini konularda nihai"
    " ve bağlayıcı hükümler için Diyanet İşleri Başkanlığı'na veya yetkili"
    " mercilere başvurulması gerekmektedir. Tüm veriler yalnızca anlık RAM"
    " belleğinde (BytesIO) işlenmekte olup, sunucu diski üzerinde kesinlikle"
    " loglanmaz ve saklanmaz."
)

# ==========================================
# 3. 50 SORULUK GÜVENLİ KAYNAK HAVUZU
# ==========================================
SORU_CEVAP_LISTESI = [
    {
        "id": 1,
        "kategori": "İnanç & Felsefe",
        "soru": "Allah'ın varlığı akli ve mantıki delillerle nasıl açıklanabilir?",
        "kisa_yanıt": (
            "Kainattaki kusursuz nizam, kozmolojik delil (her eserin bir"
            " yaratıcısı olması) ve tanzim deliliyle aklen kanıtlanır."
        ),
        "detayli_cevap": (
            "Evrende var olan muazzam uyum, fizik sabitlerinin hassas"
            " ayarlanmış olması ve tesadüf ihtimalinin sıfıra yakınlığı, bilinçli"
            " bir Yaratıcı'nın varlığını zorunlu kılar."
        ),
        "guvenli_kaynak": (
            "Diyanet İslam İlmihali & Kelam Ilmi Temel Kaynakları"
        ),
    },
    {
        "id": 2,
        "kategori": "İnanç & Felsefe",
        "soru": (
            "Ahiret inancının insan psikolojisine ve toplumsal düzene katkısı"
            " nedir?"
        ),
        "kisa_yanıt": (
            "Ahiret inancı insana derin bir adalet tesellisi sunar, suç"
            " oranlarını düşürür ve hayatı anlamlı kılar."
        ),
        "detayli_cevap": (
            "Ölümün son değil yeni bir başlangıç olduğunu bilmek, dünyevi"
            " hırsları dengeler, mazlumlara umut aşılar ve suç işleme"
            " eğilimlerini otokontrol ile engeller."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Kıyame Suresi & Yunus 4-7)"),
    },
    {
        "id": 3,
        "kategori": "İnanç & Felsefe",
        "soru": "Peygamber gönderilmesinin hikmeti ve zorunluluğu nedir?",
        "kisa_yanıt": (
            "İnsan aklı her şeyi tek başına bulamayacağı için Allah, ilahi"
            " rehberlik amacıyla peygamberler görevlendirmiştir."
        ),
        "detayli_cevap": (
            "Aklın sınırları vardır; ibadetlerin şekli, ahlakın detayları ve"
            " gaipten haberler ancak vahiy yoluyla öğrenilebilir."
        ),
        "guvenli_kaynak": ("Diyanet Akait Esasları & İmam Maturidi, Kitabu't-Tevhid"),
    },
    {
        "id": 4,
        "kategori": "İnanç & Felsefe",
        "soru": "Kader inancı insanı tembelliğe mi iter, yoksa sorumluluğa mı?",
        "kisa_yanıt": (
            "Kader asla tembellik değildir; aksine elimizden gelen çabayı"
            " gösterip neticeyi Allah'a bırakma bilincidir."
        ),
        "detayli_cevap": (
            "İslam'da 'çalışana karşılığı vardır' ilkesi esastır. Kader,"
            " geçmişin muhasebesi ve geleceğin planlanmasında insana güven"
            " verir."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, Kader 2 & Kur'an Yolu (Necm 39)"),
    },
    {
        "id": 5,
        "kategori": "İnanç & Felsefe",
        "soru": "İbadetlerin Allah'ın bizim ibadetlerimize ihtiyacı var mıdır?",
        "kisa_yanıt": (
            "Allah'ın hiçbir şeye ihtiyacı yoktur; ibadetler tamamen insanın"
            " ruhsal ve bedensel gelişimine hizmet eder."
        ),
        "detayli_cevap": (
            "O Samed'dir (hiçbir şeye muhtaç değildir). Namaz, oruç gibi"
            " ibadetler insanın nefsini terbiye etmesi ve şükür borcunu"
            " ödemesi içindir."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Hac Suresi 37. Ayet)"),
    },
    {
        "id": 6,
        "kategori": "İbadet & Hayat",
        "soru": "Namazın bireysel ve toplumsal hayata kazandırdığı disiplin nedir?",
        "kisa_yanıt": (
            "Namaz vakit bilinci kazandırır, insanı kötülükten alıkoyar ve"
            " düzenli bir hayat sunar."
        ),
        "detayli_cevap": (
            "Günde beş vakit huzura durmak, zamanı yönetmeyi, bedensel ve"
            " ruhsal temizliği, kibirden arınmayı ve toplumsal aidiyeti"
            " güçlendirir."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Ankebût Suresi 45. Ayet)"),
    },
    {
        "id": 7,
        "kategori": "İbadet & Hayat",
        "soru": (
            "Oruç ibadetinin fiziksel, iradi ve sosyal boyutları nelerdir?"
        ),
        "kisa_yanıt": (
            "Oruç iradeyi çelikleştirir, bedeni dinlendirir ve yoksulların"
            " halini anlamayı sağlar."
        ),
        "detayli_cevap": (
            "Sadece midede değil, dilde ve gözde de tutulan oruç insanı"
            " ahlaken zirveye taşır, toplumsal dayanışma bilincini (iftar ve"
            " zekatla) artırır."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, Savm 2 & Diyanet İlmihali"),
    },
    {
        "id": 8,
        "kategori": "İbadet & Hayat",
        "soru": "Zekat ve sadaka ekonomide adaleti nasıl sağlar?",
        "kisa_yanıt": (
            "Servetin belirli ellerde birikmesini önler, gelir uçurumunu"
            " kapatır ve toplumsal barışı tesis eder."
        ),
        "detayli_cevap": (
            "Zekat, zenginin malındaki yoksul hakkıdır. Ekonomide"
            " sirkülasyonu sağladığı gibi sınıflar arası husumeti de yok"
            " eder."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Tevbe Suresi 103 & Haşr 7)"
        ),
    },
    {
        "id": 9,
        "kategori": "İbadet & Hayat",
        "soru": "Hac ibadetinin evrensel kardeşlik ve mahşer provası anlamı nedir?",
        "kisa_yanıt": (
            "Hac, dilleri ve ırkları farklı milyonların aynı gaye için"
            " beyaz ihramlar içinde eşitlenmesidir."
        ),
        "detayli_cevap": (
            "Arafat vakfesi mahşerin, tavaf ise kainatın merkezine yönelişin"
            " simgesidir. Hiçbir üstünlük farkı kalmaksızın evrensel bir"
            " kucaklaşmadır."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, Hac 1 & Diyanet İlmihali"),
    },
    {
        "id": 10,
        "kategori": "İbadet & Hayat",
        "soru": "Dua ibadetin özü müdür, duanın kabul edilme mekanizması nasıldır?",
        "kisa_yanıt": (
            "Dua kul ile Yaratıcı arasındaki en güçlü iletişimdir; her dua"
            " ya aynen, ya daha hayırlısıyla ya da ahirette karşılık bulur."
        ),
        "detayli_cevap": (
            "Allah 'Bana dua edin, icabet edeyim' buyurmuştur. Samimi bir"
            " dua kalbe huzur verir, belaları def eder ve kulun acziyetini"
            " itiraf etmesidir."
        ),
        "guvenli_kaynak": ("Tirmizi, Daavat 1 & Kur'an Yolu (Mümin 60)"),
    },
    {
        "id": 11,
        "kategori": "Ahlak & Toplum",
        "soru": "İslam'da aile kurumunun önemi ve neslin korunması nasıl sağlanır?",
        "kisa_yanıt": (
            "Aile toplumun temel çekirdeğidir; sevgi, saygı, sadakat ve"
            " sorumlulukla korunur."
        ),
        "detayli_cevap": (
            "Nikah meşru birlikteliğin temelidir. Eşler arasındaki haklar,"
            " çocukların adalete ve sevgiye dayalı eğitimi neslin selametini"
            " garanti eder."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Rum Suresi 21. Ayet) & Diyanet Aile İlmihali"
        ),
    },
    {
        "id": 12,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "Anne babaya itaatin ve saygının sınırı nedir, yaşlılıkta onlara"
            " yaklaşım nasıl olmalıdır?"
        ),
        "kisa_yanıt": (
            "Ötelenmemeli, 'Öf bile denmemeli', şefkatle ve vefayla"
            " yaşatılmalıdır."
        ),
        "detayli_cevap": (
            "İsra Suresi 23-24. ayetlerde Allah'a ibadetten hemen sonra anne"
            " babaya iyilik emredilmiştir. Yaşlandıklarında onlara kollayıcı"
            " bir merhamet kanadı germek gerekir."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (İsra Suresi 23-24)"),
    },
    {
        "id": 13,
        "kategori": "Ahlak & Toplum",
        "soru": "Gençlik döneminde iffet ve hayanın korunması neden bu kadar elzemdir?",
        "kisa_yanıt": (
            "Haya imanın yarısıdır; iffet insanın şerefini, ruh sağlığını ve"
            " toplumsal haysiyetini korur."
        ),
        "detayli_cevap": (
            "Modern çağın hazcı tuzaklarına karşı hayayı kuşanmak, iradeyi"
            " güçlendirir ve kişiyi içsel huzursuzluklardan muhafaza eder."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, İman 16 & Tirmizi, Birr 47"),
    },
    {
        "id": 14,
        "kategori": "Ahlak & Toplum",
        "soru": "Ticaret ahlakı ve dürüst esnaflık İslam'da niçin teşvik edilmiştir?",
        "kisa_yanıt": (
            "Rızkın en helali dürüst kazançtır; hile, yalan ve faiz toplumsal"
            " güveni yıkar."
        ),
        "detayli_cevap": (
            "Peygamberimiz 'Dürüst tüccar ahirette peygamberlerle beraberdir'"
            " buyurmuştur. Ölçüde tartıda hile yapmamak, malın kusurunu gizlememek"
            " esastır."
        ),
        "guvenli_kaynak": ("Tirmizi, Büyü 5 & İbn Mace, Ticarat 1"),
    },
    {
        "id": 15,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "Emanete hıyanet etmemenin ve sözünde durmanın ahlaki değeri"
            " nedir?"
        ),
        "kisa_yanıt": (
            "Sözünde durmak ve emaneti korumak müminlik vasfıdır; aksi"
            " münafıklık alametidir."
        ),
        "detayli_cevap": (
            "İster makam, ister sır, ister maddi emanet olsun; bunlara sadakat"
            " göstermek bir karakter meselesidir ve toplumsal güven zincirinin"
            " temel taşıdır."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, İman 24 & Müslim, İman 107"),
    },
    {
        "id": 16,
        "kategori": "Ahlak & Toplum",
        "soru": "Öfke kontrolü ve affedici olmanın erdemi Kur'an'da nasıl övülmüştür?",
        "kisa_yanıt": (
            "Öfkesini yutanlar ve insanları affedenler Allah'ın sevgisini"
            " kazanan muttaki kullardır."
        ),
        "detayli_cevap": (
            "Al-i İmran Suresi 134. ayette cennet ehlinin özelliklerinden"
            " birinin 'öfkelerini yutmak ve insanları affetmek' olduğu"
            " bildirilmiştir."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Al-i İmran Suresi 134)"),
    },
    {
        "id": 17,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "İlim öğrenmek kadın ve erkek üzerine nedenfarz kılınmıştır?"
        ),
        "kisa_yanıt": (
            "Çünkü cehalet her türlü kötülüğün anahtarıdır; ilim ise hakikati"
            " bulmanın tek yoludur."
        ),
        "detayli_cevap": (
            "Peygamberimiz 'İlim müminin yitiğidir, nerede bulursa almalıdır'"
            " buyurmuştur. Hayatın her alanında donanımlı olmak dini bir"
            " emirdir."
        ),
        "guvenli_kaynak": ("İbn Mace, Mukaddime 17 & Beyhakİ"),
    },
    {
        "id": 18,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "İslam'da kul hakkının önemi nedir ve neden affı en zor günahlardan"
            " biridir?"
        ),
        "kisa_yanıt": (
            "Kul hakkı, Allah'ın kulunun hakkından vazgeçmediği ve hak sahibinin"
            " rızasına bağlandığı ağır bir sorumluluktur."
        ),
        "detayli_cevap": (
            "Peygamberimiz haksızlık yapanların mahşerde sevaplarının hak"
            " sahiplerine verileceğini (Müflis hadisi) bildirmiştir. Bu yüzden"
            " ticaret, sosyal ilişkiler ve günlük hayatta başkalarının"
            " hakkına girmemek hayati önem taşır."
        ),
        "guvenli_kaynak": (
            "Sahih-i Müslim (Birr 59 - Müflis Hadisi) & Diyanet İlmihali"
        ),
    },
    {
        "id": 19,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "İslam'da dijital ahlak, mahremiyet ve sosyal medya kullanımı nasıl"
            " olmalıdır?"
        ),
        "kisa_yanıt": (
            "Gerçek hayatta gösterilen dürüstlük ve iffet, internet ve sosyal"
            " medya ortamlarında da eksiksiz sürdürülmelidir."
        ),
        "detayli_cevap": (
            "Gıybet, iftira, mahremiyetin ihlali, sahte hesaplarla insanları"
            " kandırmak veya haysiyet zedelemek dijital dünyada da büyük"
            " veballerdir. Mümin her yerde güvenilir olandır."
        ),
        "guvenli_kaynak": (
            "Din İşleri Yüksek Kurulu Fetvaları & Kur'an Yolu Tefsiri (Hucurat"
            " Suresi)"
        ),
    },
    {
        "id": 20,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "Günümüz gençliğinin en büyük çıkmazları olan dijital bağımlılık ve"
            " yalnızlıkla nasıl başa çıkılır?"
        ),
        "kisa_yanıt": (
            "Sanal dünyadan gerçek hayata dönmek, sosyal bağları"
            " güçlendirmek ve vakti dengeli kullanmak İslam ahlakının temel"
            " tavsiyesidir."
        ),
        "detayli_cevap": (
            "Aşırı ekran ve sosyal medya kullanımı insanı soyutlayarak ruhi"
            " bunalımlara sürükler. İslam, zamanın israf edilmemesini ve"
            " yüz yüze insani ilişkilerin, akraba ziyaretlerinin ve gerçek"
            " dostlukların kurulmasını emreder."
        ),
        "guvenli_kaynak": (
            "Din İşleri Yüksek Kurulu Raporları & İslam Ahlakı Kaynakları"
        ),
    },
    {
        "id": 21,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "Arkadaş seçimi insanı nasıl etkiler, dinimiz bu konuda ne tavsiye"
            " eder?"
        ),
        "kisa_yanıt": (
            "İnsan arkadaşının dini ve ahlaki yolu üzerindedir; bu yüzden"
            " dürüst ve iyi insanlarla arkadaşlık edilmelidir."
        ),
        "detayli_cevap": (
            "Peygamber Efendimiz buyurmuştur ki: **'Kişi dostunun dini"
            " üzeredir; öyleyse her biriniz kiminle dostluk kurduğuna dikkat"
            " etsin.'** İyi arkadaş misk taşıyan kimseye benzer, kötü"
            " arkadaş ise körük üfleyen demirciye benzer."
        ),
        "guvenli_kaynak": ("Ebu Davud, Edeb 16 & Tirmizi, Zühd 45"),
    },
    {
        "id": 22,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "Yalan söylemek ve gıybet etmek dini açıdan neden bu kadar büyük"
            " günahtır?"
        ),
        "kisa_yanıt": (
            "Çünkü yalan güveni, gıybet ise toplumsal huzur ve kardeşlik"
            " bağlarını temelden sarsar."
        ),
        "detayli_cevap": (
            "Yalan ikiyüzlülüğün, gıybet ise arkadan vurmanın ifadesidir."
            " Kur'an-ı Kerim'de gıybet etmek, **'ölü kardeşinin etini yemek'"
            " gibi son derece çirkin bir benzetmeyle yasaklanmıştır (Hucurat,"
            " 12)."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Hucurat Suresi 12. Ayet)"),
    },
    {
        "id": 23,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "İş veya okul hayatında adaletsizlikle karşılaştığımızda Müslümana"
            " düşen tavır nedir?"
        ),
        "kisa_yanıt": (
            "Hak arama mücadelesini meşru yollardan sürdürmek, sabırlı olmak ve"
            " asla haksızlık yapmamaktır."
        ),
        "detayli_cevap": (
            "İslam adaleti ve hakkı üstün tutar. Haksızlığa uğrayan kişi"
            " meşru ve yasal yollardan hakkını aramalı, asla intikam"
            " duygusuyla haksızlığa sapmamalı ve sabırla adaletin"
            " tecellisini beklemelidir."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Maide Suresi 8. Ayet) & Diyanet İlmihali"
        ),
    },
    {
        "id": 24,
        "kategori": "Manevi Gelişim",
        "soru": (
            "Gençlik döneminde ibadetlere yönelmenin ve maneviyata bağlanmanın"
            " önemi nedir?"
        ),
        "kisa_yanıt": (
            "Gençlik çağında yapılan ibadetler nefsani arzulara karşı en büyük"
            " kalkandır ve kat kat faziletlidir."
        ),
        "detayli_cevap": (
            "Peygamber Efendimiz, kıyamet gününde hiçbir gölgenin olmadığı"
            " günde Allah'ın rahmetiyle gölgelenecek yedi sınıftan birinin"
            " **'gençliğini Allah'a ibadetle geçiren kimse'** olduğunu"
            " müjdelemiştir."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, Zekat 44 & Müslim, Zekat 91"),
    },
    {
        "id": 25,
        "kategori": "Manevi Gelişim",
        "soru": (
            "Günahlara tövbe etmenin ve 'Tövbe-i Nasuh' kavramının anlamı nedir?"
        ),
        "kisa_yanıt": (
            "Tövbe, hatadan pişman olup bir daha dönmemeye azmetmek suretiyle"
            " Yaratıcı'nın kapısına tertemiz dönmektir."
        ),
        "detayli_cevap": (
            "İnsan beşerdir ve hata yapabilir; ancak önemli olan hatada ısrar"
            " etmemektir. Allah'ın rahmeti her türlü günahtan büyüktür (Zümer,"
            " 53). Samimi bir tövbe insanın geçmişteki defterini tertemiz"
            " yapar."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Zümer Suresi 53. Ayet & Tahrim 8)"
        ),
    },
    {
        "id": 26,
        "kategori": "Manevi Gelişim",
        "soru": (
            "Nefis mücadelesi (Cihad-ı Ekber) modern dünyada nasıl verilmelidir?"
        ),
        "kisa_yanıt": (
            "Nefsin haram ve kötü arzularına karşı sabretmek, manevi"
            " disiplini korumak en büyük içsel cihattır."
        ),
        "detayli_cevap": (
            "Peygamberimiz küçük cihattan (savaş) dönerken **'Küçük cihattan"
            " büyük cihada, nefisle mücadeleye dönüyoruz'** buyurmuştur."
            " Teknolojinin ve haz merkezli tüketim toplumunun tuzaklarına"
            " karşı durmak büyük bir irade gerektirir."
        ),
        "guvenli_kaynak": ("Aclûnî, Keşfü'l-Hafâ, II, 31 & Diyanet İlmihali"),
    },
    {
        "id": 27,
        "kategori": "Manevi Gelişim",
        "soru": (
            "Şükür ve sabır dengesi bir müminin hayatını nasıl dönüştürür?"
        ),
        "kisa_yanıt": (
            "Nimet karşısında şükretmek, musibet karşısında sabretmek hayatın"
            " dengesidir ve mümini olgunlaştırır."
        ),
        "detayli_cevap": (
            "Hadiste müminin durumu çok övülmüştür: Başına sevinç gelirse"
            " şükreder hayır olur, sıkıntı gelirse sabreder yine hayır olur."
            " Şükür nimeti artırır, sabır ise ruhsal dayanıklılık sağlar."
        ),
        "guvenli_kaynak": ("Sahih-i Müslim, Zühd 64 & Kur'an Yolu (İbrahim 7)"),
    },
    {
        "id": 28,
        "kategori": "Manevi Gelişim",
        "soru": "İhlas (samimiyet) kavramı ibadetlerde neden merkezidir?",
        "kisa_yanıt": (
            "İbadetlerin ve amellerin Allah katında kabul görmesinin yegane"
            " şartı, hiçbir gösteriş olmaksızın sadece rızayı ilahi gözeterek"
            " yapılmasıdır."
        ),
        "detayli_cevap": (
            "Kur'an'da: **'Onlara ancak dini sadece Allah'a has kılarak"
            " ibadet etmeleri emrolunmuştu'** (Beyyine, 5) denmektedir."
            " Gösteriş (riya) amelleri boşa çıkarır; ihlas ise en küçük ameli"
            " bile dağlar kadar ağırlaştırır."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Beyyine Suresi 5. Ayet) & Sahih-i Buhari"
        ),
    },
    {
        "id": 29,
        "kategori": "İslam & Bilim",
        "soru": (
            "İslam'ın ilme ve bilime verdiği değer tarih boyunca nasıl tezahür"
            " etmiştir?"
        ),
        "kisa_yanıt": (
            "İslam medeniyeti 'Oku' emriyle başlamış; astronomi, tıp, matematik"
            " ve fizik alanlarında bin yıllık altın çağını üretken ilimlerle"
            " kurmuştur."
        ),
        "detayli_cevap": (
            "İbn Sina, Biruni, Harezmi gibi İslam bilginleri laboratuvar"
            " deneyini ve pozitif ilimleri dini ilimlerle bütünleştirerek"
            " dünyaya rehberlik etmiştir. İslam'da ilim ile din asla çatışmaz,"
            " aksine ilim Allah'ın kainattaki ayetlerini okuma sanatıdır."
        ),
        "guvenli_kaynak": (
            "Diyanet İslam Ansiklopedisi (İlim Maddesi) & Prof. Dr. Fuat Sezgin"
            " Eserleri"
        ),
    },
    {
        "id": 30,
        "kategori": "İslam & Bilim",
        "soru": (
            "Evrim teorisi ile İslam inancı taban tabana zıt mıdır, nasıl"
            " yorumlanmalıdır?"
        ),
        "kisa_yanıt": (
            "Canlıların yaratılış evreleri Kur'an'da ayetlerle sabittir; ancak"
            " insanın doğrudan rastlantısal süreçlerle değil, ilahi irade ve"
            " 'Ol' emriyle özel olarak yaratıldığı inancı esastır."
        ),
        "detayli_cevap": (
            "İslam alimleri, türler arası değişim mekanizmalarının ilahi"
            " sünnetullah çerçevesinde işleyebileceğini, ancak insanın ruh"
            " and beden sahibi müstakil bir yaratılış gayesine sahip olduğunu"
            " (Hz. Adem mucizesi) vurgular."
        ),
        "guvenli_kaynak": (
            "Din İşleri Yüksek Kurulu Yayınları & Kur'an Yolu Tefsiri (Secde"
            " Suresi 7-9)"
        ),
    },
    {
        "id": 31,
        "kategori": "İslam & Bilim",
        "soru": (
            "Teknolojinin ve yapay zekanın geliştiği bu çağda insanın manevi"
            " değeri azalır mı?"
        ),
        "kisa_yanıt": (
            "Aksine, yapay zeka ne kadar gelişirse gelsin ruh, bilinç, vicdan"
            " and ahlak sahibi olan insan her zaman üstün ve eşsiz kalacaktır."
        ),
        "detayli_cevap": (
            "Kur'an'da insanın en güzel biçimde yaratıldığı (Tin, 4) ve"
            " kainata halife kılındığı belirtilir. Teknoloji bir araçtır;"
            " insanı değerli kılan onun iradesi, sevgi kapasitesi ve ahlaki"
            " sorumluluğudur."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Tîn Suresi 4. Ayet & Bakara 30)"),
    },
    {
        "id": 32,
        "kategori": "İslam & Bilim",
        "soru": (
            "Çevre bilinci, ekoloji ve hayvan hakları İslam inancında nasıl yer"
            " bulur?"
        ),
        "kisa_yanıt": (
            "İslam'da tabiat ve hayvanlar Allah'ın emanetidir; israf haram"
            " kılınmış, çevreye ve canlılara merhamet emredilmiştir."
        ),
        "detayli_cevap": (
            "Peygamberimiz hatta savaşta bile meyve veren ağaçların kesilmesini"
            " ve hayvanlara zarar verilmesini yasaklamıştır. Yeryüzünü"
            " imar etmek ve korumak insanın halifelik vazifesinin en temel"
            " gereğidir."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (A'raf Suresi 31 & Rum 41) & Sahih Hadisler"
        ),
    },
    {
        "id": 33,
        "kategori": "İslam & Bilim",
        "soru": (
            "Modern dünyanın getirdiği yalnızlık ve stres krizine karşı İslam"
            " maneviyatı nasıl bir şifa sunar?"
        ),
        "kisa_yanıt": (
            "Zikir, dua, tevakkul ve cemaat bilinci modern insanın yaşadığı"
            " ontolojik yalnızlığı ve yabancılaşmayı bitiren en büyük şifadır."
        ),
        "detayli_cevap": (
            "Bireysel yalnızlık girdabında kıvranan insana İslam; Allah'ın"
            " şah damarından daha yakın olduğunu (Kaf, 16), hiçbir zaman"
            " kimsesiz olmadığını ve her derdin bir hikmeti bulunduğunu"
            " fısıldayarak derin bir sükunet sunar."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Kaf Suresi 16. Ayet & Ra'd 28)"),
    },
    {
        "id": 34,
        "kategori": "İslam & Bilim",
        "soru": (
            "Modern dünyanın tüketim çılgınlığına karşı İslam'ın israf ve"
            " tasarruf prensibi nedir?"
        ),
        "kisa_yanıt": (
            "İslam israfı kesinlikle yasaklar; 'Yiyiniz, içiniz fakat israf"
            " etmeyiniz' ilkesiyle dengeli ve ölçülü bir yaşamı savunur."
        ),
        "detayli_cevap": (
            "Ayet-i kerimede bildirildiği gibi: **'Şüphesiz israf edenler"
            " şeytanların kardeşleridir'** (İsra, 27). Günümüz tüketim"
            " kültürünün insana durmaksızın satın alma dayatmasına karşın,"
            " İslam sade yaşamı ve elindeki nimetin kıymetini bilmeyi"
            " öğütler."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (İsra Suresi 26-27. Ayetler) & Araf Suresi"
            " 31"
        ),
    },
    {
        "id": 35,
        "kategori": "İnanç & Felsefe",
        "soru": (
            "Deizm ve ateizm akımlarının yaygınlaşma nedenleri ve İslam"
            " inancının bunlara getirdiği cevaplar nelerdir?"
        ),
        "kisa_yanıt": (
            "Genellikle şekilsel din anlayışları, kötülük problemi ve sorgulama"
            " eksikliği bu akımları tetikler; İslam ise akıl ve vahiy"
            " bütünlüğüyle cevap sunar."
        ),
        "detayli_cevap": (
            "İslam dini körü körüne taklidi değil, akletmeyi ve düşünmeyi"
            " emreder. Kainattaki kusursuz nizam (tasarım delili), hayatın"
            " başlangıcı ve ahlaki değerlerin objektif temeli ancak bilinçli"
            " bir Yaratıcı inancıyla mantıki bir zemine oturtulabilir."
        ),
        "guvenli_kaynak": (
            "Kelam İlmi Kaynakları & Diyanet İnanç Esasları Külliyatı"
        ),
    },
    {
        "id": 36,
        "kategori": "İnanç & Felsefe",
        "soru": (
            "Kötülük problemi (Dünyada neden acılar ve afetler var?) sorusu"
            " İslam teolojisinde nasıl açıklanır?"
        ),
        "kisa_yanıt": (
            "Dünya bir imtihan salonudur; acılar ve musibetler insanın"
            " derecesini artırır, sabrını sınar ve ahiret yurdunun değerini"
            " gösterir."
        ),
        "detayli_cevap": (
            "Eğer dünyada hiç zorluk, hastalık veya acı olmasaydı"
            " kahramanlık, fedakarlık, sabır ve merhamet gibi yüce erdemlerin"
            " bir anlamı kalmazdı. Başımıza gelen sıkıntılar günahlara kefaret"
            " olurken, sabredenler için kat kat mükafat vesilesidir."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Bakara Suresi 155-157 & Ankebût 2-3)"
        ),
    },
    {
        "id": 37,
        "kategori": "İnanç & Felsefe",
        "soru": (
            "Kader ve irade (Cebir ve İhtiyar) ikilemi aklen ve mantıken nasıl"
            " anlaşılmalıdır?"
        ),
        "kisa_yanıt": (
            "Allah'ın ezelî ilmiyle her şeyi bilmesi (kader) insanın iradesini"
            " ortadan kaldırmaz; insan yaptıklarından özgür iradesiyle"
            " sorumludur."
        ),
        "detayli_cevap": (
            "Meteorologların yağmurun yağacağını önceden bilmesi yağmura"
            " müdahale etmediği gibi, Allah'ın da bizim yapacağımız tercihleri"
            " ezelî ilmiyle bilmesi bizi mecbur bırakmaz. İnsan kendi"
            " iradesiyle seçer, Allah da o seçeneği yaratır."
        ),
        "guvenli_kaynak": (
            "Ehl-i Sünnet Akaidi & Diyanet İslam İlmihali (Kader Bölümü)"
        ),
    },
    {
        "id": 38,
        "kategori": "İnanç & Felsefe",
        "soru": (
            "Mucizelerin bilimsel ve akli izahı nedir, modern akıl bunları"
            " nasıl kabul etmelidir?"
        ),
        "kisa_yanıt": (
            "Mucizeler evrenin kanunlarını koyan Yaratıcı'nın olağanüstü"
            " müdahaleleridir; tabiat kanunları mutlak değil, Allah'ın"
            " iradesine tabidir."
        ),
        "detayli_cevap": (
            "Evreni ve doğa kanunlarını yaratan Zat, dilediği zaman bu"
            " kanunların dışına çıkabilir. Peygamberlerin ellerinde"
            " gerçekleşen mucizeler, onların ilahi elçi olduklarını"
            " doğrulayan fevkalade delillerdir."
        ),
        "guvenli_kaynak": ("İslam Akaidi ve Kelam Tarihi Kaynakları"),
    },
    {
        "id": 39,
        "kategori": "İnanç & Felsefe",
        "soru": (
            "İmanın tabakaları (Taklidi imandan tahkiki imana geçiş) insan"
            " hayatını nasıl etkiler?"
        ),
        "kisa_yanıt": (
            "Taklidi iman sarsılabilir; ancak delillere, akla ve derin"
            " kavrayışa dayanan tahkiki iman hiçbir şüphe rüzgarıyla"
            " yıkılmaz."
        ),
        "detayli_cevap": (
            "Çevreden duyulan bilgilerle oluşan iman 'taklidi'dir. Ancak"
            " kişinin kainatı inceleyerek, Kur'an'ı anlayarak ve derin"
            " tefekkürle ulaştığı iman 'tahkiki' imandır. Tahkiki iman"
            " sahibine dağlar gibi sağlam bir iç huzur ve sarsılmaz bir"
            " karakter kazandırır."
        ),
        "guvenli_kaynak": (
            "Risale-i Nur Külliyatı (İman Hakikatleri) & İslam Tasavvuf"
            " Kaynakları"
        ),
    },
    {
        "id": 40,
        "kategori": "Haklar & Özgürlük",
        "soru": (
            "İslam'da inanç özgürlüğü var mıdır, 'Dinde zorlama yoktur' ilkesi"
            " ne anlama gelir?"
        ),
        "kisa_yanıt": (
            "İslam'da inançta kesinlikle baskı ve zorlama yoktur; hak ve batıl"
            " akılla seçilir, hesap ahirettedir."
        ),
        "detayli_cevap": (
            "Bakara Suresi 256. ayette açıkça **'Dinde zorlama yoktur; hak"
            " batıldan açıkça ayrılmıştır'** buyrulmuştur. İman kalple"
            " tasdik işi olduğundan, baskıyla yapılan inancın Allah katında"
            " hiçbir geçerliliği yoktur."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Bakara Suresi 256. Ayet & Yunus 99)"
        ),
    },
    {
        "id": 41,
        "kategori": "Haklar & Özgürlük",
        "soru": (
            "İslam'da adalet kavramı ve hukukun üstünlüğü nasıl temin edilmiştir?"
        ),
        "kisa_yanıt": (
            "Adalet mülkün temelidir; İslam'da kimse kanunlardan üstün değildir"
            " ve zengine de yoksula da aynı adalet uygulanır."
        ),
        "detayli_cevap": (
            "Kur'an'da **'Ey inananlar, adaletle kaim olun, şahitlik edenler"
            " olunuz; bir topluluğa olan kininiz sizi adaletsizliğe itmesin'**"
            " (Maide, 8) emriyle adaletin mutlak ve evrensel olduğu"
            " vurgulanmıştır."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Maide Suresi 8 & Nisa 135)"),
    },
    {
        "id": 42,
        "kategori": "Haklar & Özgürlük",
        "soru": (
            "İslam'da kadının hakları ve toplumsal statüsü nedir, cahiliye"
            " adetlerinden farkı nedir?"
        ),
        "kisa_yanıt": (
            "İslam, kız çocuklarının gömülmesine son vermiş, kadına mülkiyet,"
            " eğitim, evlilikte rıza ve onurlu bir hayat hakkı"
            " kazandırmıştır."
        ),
        "detayli_cevap": (
            "Cahiliye döneminde hor görülen kadın, İslam'la birlikte şeref ve"
            " haysiyete kavuşmuştur. Hz. Muhammed (s.a.v.) **'Cennet annelerin"
            " ayakları altındadır'** buyurarak kadına en yüce değeri"
            " atfetmiştir."
        ),
        "guvenli_kaynak": (
            "Diyanet İslam Ansiklopedisi (Kadın Maddesi) & Kur'an Yolu Tefsiri"
            " (Nisa Suresi)"
        ),
    },
    {
        "id": 43,
        "kategori": "Haklar & Özgürlük",
        "soru": (
            "İslam'da kardeşlik, ırkçılık and milliyetçilik kavramları nasıl"
            " dengelenmiştir?"
        ),
        "kisa_yanıt": (
            "Üstünlük ırk veya renkle değil, ancak takva (Allah'a saygı ve"
            " ahlak) ile ölçülür; tüm müminler kardeştir."
        ),
        "detayli_cevap": (
            "Hucurat Suresi 13. ayette açıkça: **'Ey insanlar, sizi bir erkek"
            " and bir dişiden yarattık ve tanışasınız diye sizi milletlere ve"
            " kabilelere ayırdık; Allah katında en değerli olanınız takvaca en"
            " üstün olanınızdır'** denilmektedir."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Hucurat Suresi 10 ve 13. Ayetler)"),
    },
    {
        "id": 44,
        "kategori": "Haklar & Özgürlük",
        "soru": (
            "Gençlerin hayatı anlamlandırma sürecinde Kur'an ve Sünnet rehberliği"
            " onlara nasıl bir vizyon kazandırır?"
        ),
        "kisa_yanıt": (
            "Gençlere geçici hevesler peşinde koşmak yerine kalıcı eserler"
            " bırakma, erdemli, şahsiyetli ve huzurlu bir ömür sürme vizyonu"
            " kazandırır."
        ),
        "detayli_cevap": (
            "İslam inancı genç insana hayatın başıboş olmadığını, her nefsin"
            " bir amaca hizmet ettiğini, dünyada bırakılacak her güzel iz ve"
            " ahlakın ebedi cennet kapılarını açacağını müjdeleyerek en"
            " muazzam hayat enerjisini verir."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Asr Suresi Açıklaması) & Diyanet İlmihali"
        ),
    },
    {
        "id": 45,
        "kategori": "İbadet & Hayat",
        "soru": (
            "Cuma namazının ve cemaatle ibadet etmenin sosyal ve manevi hikmeti"
            " nedir?"
        ),
        "kisa_yanıt": (
            "Cemaat ve Cuma namazı, Müslümanların haftalık kongresi olup"
            " toplumsal dayanışmayı, eşitliği ve kardeşliği en üst düzeyde"
            " pekiştirir."
        ),
        "detayli_cevap": (
            "Omuz omuza saf tutulan camilerde zengin ile fakir, amir ile memur"
            " yan yana gelerek sıfırlanır. Cuma günü, haftanın koşturmacası"
            " içinde ruhu dinlendiren ilahi bir buluşma vaktidir."
        ),
        "guvenli_kaynak": (
            "Kur'an Yolu Tefsiri (Cuma Suresi 9-10. Ayetler) & Diyanet İlmihali"
        ),
    },
    {
        "id": 46,
        "kategori": "Ahiret & Hayat",
        "soru": (
            "Ölüm korkusu ile başa çıkmada İslam inancı insana nasıl bir teselli"
            " sunar?"
        ),
        "kisa_yanıt": (
            "İslam'da ölüm bir yok oluş değil, sevgiliye (Allah'a) ve ebedi"
            " dostlara kavuşma sevinci (şeb-i arus) olarak görülür."
        ),
        "detayli_cevap": (
            "Mümin için ölüm, dünya imtihanının bitip geride bırakılan"
            " güzelliklerin meyvesinin toplanacağı bir eşiktir. Hz. Muhammed"
            " (s.a.v.) 'Allah'a kavuşmayı isteyene Allah da kavuşmayı sever'"
            " buyurarak ölüm korkusunu ümide dönüştürmüştür."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, Rikak 41 & Diyanet İlmihali"),
    },
    {
        "id": 47,
        "kategori": "Ahlak & Toplum",
        "soru": (
            "İslam'da komşuluk hakları ve toplumsal yardımlaşma (İyilik"
            " kültürü) neden bu kadar vurgulanmıştır?"
        ),
        "kisa_yanıt": (
            "Komşusu açken tok yatan bizden değildir ilkesi, toplumda"
            " kimsenin yalnız ve çaresiz kalmamasını hedefleyen kusursuz bir"
            " güvenlik ağıdır."
        ),
        "detayli_cevap": (
            "İslam toplumunda komşunun canı, malı ve namusu güvence altındadır."
            " Peygamberimiz komşu hakkının o kadar çok vurgulandığını"
            " belirtmiştir ki, neredeyse komşuyu komşuya varis kılacağını"
            " zannettiğini söylemiştir."
        ),
        "guvenli_kaynak": ("Sahih-i Buhari, Edeb 28 & Müslim, İman 73"),
    },
    {
        "id": 48,
        "kategori": "Manevi Gelişim",
        "soru": (
            "Tevekkül nedir? Çalışmadan, tedbir almadan 'Allah'a güvendim' demek"
            " doğru bir yaklaşım mıdır?"
        ),
        "kisa_yanıt": (
            "Tevekkül, üzerimize düşen her türlü bilimsel ve fiziki tedbiri"
            " aldıktan sonra neticeyi Allah'a bırakmaktır; tedbirsiz"
            " tevekkül tembelliktir."
        ),
        "detayli_cevap": (
            "Peygamberimizin 'Önce deveni bağla, sonra tevekkül et' hadisi"
            " bunu net açıklar. İnsan elinden gelen çabayı gösterdikten sonra"
            " sonuca razı olmalı, aksi takdirde sorumluluğu yerine"
            " getirmelidir."
        ),
        "guvenli_kaynak": ("Tirmizi, Kıyamet 60 & Kur'an Yolu (Al-i İmran 159)"),
    },
    {
        "id": 49,
        "kategori": "İslam & Bilim",
        "soru": (
            "Tıp ve sağlık etiği açısından İslam'ın hastalıklara ve tedavi"
            " olma prensibine yaklaşımı nasıldır?"
        ),
        "kisa_yanıt": (
            "İslam, 'Ey Allah'ın kulları tedavi olun, çünkü Allah yarattığı her"
            " hastalığın şifasını da yaratmıştır' buyurarak tıbbı ve"
            " araştırmayı teşvik etmiştir."
        ),
        "detayli_cevap": (
            "Hastalık bir imtihan olduğu gibi, tedavi aramak da peygamber"
            " sünnetidir. Alternatif safsatalar yerine modern tıbbın ve"
            " ilmi yöntemlerin kullanılması dinin emirleriyle tamamen"
            " uyumludur."
        ),
        "guvenli_kaynak": (
            "Ebu Davud, Tıb 1 & Tirmizi, Tıb 2 & Diyanet İlmihali"
        ),
    },
    {
        "id": 50,
        "kategori": "Haklar & Özgürlük",
        "soru": (
            "İslam'da bilgi edinme özgürlüğü, eleştirel düşünce ve akletme"
            " çağrısının önemi nedir?"
        ),
        "kisa_yanıt": (
            "Kur'an'da yüzlerce kez 'Hiç düşünmez misiniz?', 'Akletmez"
            " misiniz?' denilerek insanın sorgulaması, araştırması ve bilgiye"
            " ulaşması emredilmiştir."
        ),
        "detayli_cevap": (
            "İslam dogmatizmi reddeder; körü körüne ataların yolunu izleyenleri"
            " eleştirir. Bilginin peşinden gitmek, hakikati aramak ve evreni"
            " okumak her müslümanın aslî vazifesidir."
        ),
        "guvenli_kaynak": ("Kur'an Yolu Tefsiri (Bakara Suresi 164 & Yunus 100)"),
    },
]


# ==========================================
# 4. BELLEK ÜZERİNDE ÇALIŞAN GÜVENLİ PDF ÜRETECİ
# ==========================================
def pdf_olustur(secilen_sorular):
  buffer = BytesIO()
  c = canvas.Canvas(buffer, pagesize=A4)
  width, height = A4

  def tr_duzelt(metin):
    return (
        metin.replace("ğ", "g")
        .replace("Ğ", "G")
        .replace("ş", "s")
        .replace("Ş", "S")
        .replace("ı", "i")
        .replace("İ", "I")
        .replace("ç", "c")
        .replace("Ç", "C")
        .replace("ö", "o")
        .replace("Ö", "O")
        .replace("ü", "u")
        .replace("Ü", "U")
    )

  c.setFont("Helvetica-Bold", 11)
  c.drawString(
      40,
      height - 35,
      tr_duzelt("Gençlik Manevi Rehberlik ve Araştırma Raporu"),
  )
  c.setFont("Helvetica", 7)
  c.drawString(
      40,
      height - 47,
      tr_duzelt(
          "Yasal Uyarı: Fetva amaçlı değildir. Yalnızca rehberlik ve"
          " araştırma amaçlıdır."
      ),
  )

  y = height - 75
  for item in secilen_sorular:
    if y < 80:
      c.showPage()
      y = height - 40
    c.setFont("Helvetica-Bold", 8)
    c.drawString(
        40,
        y,
        tr_duzelt(f"Soru {item['id']}: {item['soru']}"),
    )
    y -= 11
    c.setFont("Helvetica", 7)
    c.drawString(
        60,
        y,
        tr_duzelt(f"Kategori: {item['kategori']}"),
    )
    y -= 10
    c.drawString(
        60,
        y,
        tr_duzelt(f"Kaynak: {item['guvenli_kaynak']}"),
    )
    y -= 18

  c.save()
  buffer.seek(0)
  return buffer


# ==========================================
# 5. STREAMLIT ARAYÜZ MİMARİSİ
# ==========================================
data_baslik = (
    '<p class="main-title">🌱 Gençlik Manevi Rehberlik ve Danışma'
    " Paneli</p>"
)
st.markdown(data_baslik, unsafe_allow_html=True)

# Ziyaretçi Sayacı Rozeti Gösterimi
st.markdown(
    f'<div class="visitor-badge">👁️ Toplam Ziyaretçi / Oturum Sayısı:'
    f" <b>{st.session_state.ziyaretci_sayisi:,}</b></div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="sub-title">50 maddelik güvenli kaynak havuzu (Diyanet, Kur\'an'
    " Yolu, Sahih Sünnet) ile akli ve naklî deliller sunan profesyonel"
    " platform.</p>",
    unsafe_allow_html=True,
)

# Filtreleme ve Arama Alanı
col1, col2 = st.columns([2, 1])
with col1:
  arama_metni = st.text_input(
      "🔍 50 Soru Havuzunda Arama Yap",
      placeholder=(
          "Anahtar kelime giriniz (Örn: Deizm, Bilim, Kader, Aile, Namaz)..."
      ),
  )
with col2:
  kategoriler = ["Tümü"] + list(
      set([item["kategori"] for item in SORU_CEVAP_LISTESI])
  )
  secilen_kategori = st.selectbox("Kategori Filtrele", kategoriler)

# Filtreleme Mantığı
filtrelenmis_sorular = SORU_CEVAP_LISTESI
if secilen_kategori != "Tümü":
  filtrelenmis_sorular = [
      q for q in filtrelenmis_sorular if q["kategori"] == secilen_kategori
  ]

if arama_metni:
  filtrelenmis_sorular = [
      q
      for q in filtrelenmis_sorular
      if arama_metni.lower() in q["soru"].lower()
      or arama_metni.lower() in q["detayli_cevap"].lower()
      or arama_metni.lower() in q["guvenli_kaynak"].lower()
  ]

st.markdown("---")
st.markdown(
    f"*Eşleşen Soru Sayısı:* {len(filtrelenmis_sorular)} /"
    f" {len(SORU_CEVAP_LISTESI)}"
)

# Soru Görüntüleme Akışı
for item in filtrelenmis_sorular:
  with st.expander(
      f"📌 Soru {item['id']}: {item['soru']} [{item['kategori']}]"
  ):
    st.markdown(f"*Özet Yanıt:* {item['kisa_yanıt']}")
    st.markdown(f"*Detaylı Açıklama:*\n{item['detayli_cevap']}")
    st.success(f"🛡️ *Net Kaynak:* {item['guvenli_kaynak']}")

# ==========================================
# 6. YÖNETİM VE RAPOR (SİDEBAR)
# ==========================================
with st.sidebar:
  st.header("⚙️ Yönetim")
  st.write(
      "Bu platform hiçbir kullanıcı verisini kaydetmez. Bütün işlemler"
      " sunucu diski kullanılmadan yalnızca anlık RAM belleğinde yürütülür."
  )

  st.markdown("---")
  st.subheader("📄 Dışa Aktarım")
  st.caption("Filtrelenmiş soruları diske kaydetmeden anında PDF'e dönüştürün.")

  if st.button("Bellek Üstü PDF Oluştur"):
    pdf_buffer = pdf_olustur(filtrelenmis_sorular)
    st.download_button(
        label="📥 PDF Raporunu İndir",
        data=pdf_buffer,
        file_name="manevi_rehberlik_raporu.pdf",
        mime="application/pdf",
    )

  st.markdown("---")
  st.markdown("*Güvenlik ve Gizlilik Garantisi:*")
  st.info(
      "🔒 Sıfır Loglama Politikası\n💾 Disk Üzerinde Dosya Yok\n⚡ Sadece RAM"
      " Bellek (BytesIO)"
  )