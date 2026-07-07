import random
import string
import sys
import argparse

ALPHABET = string.ascii_lowercase  

KAMUS = [
    {"kata": "awak",   "arti": "saya / aku"},
    {"kata": "waang",  "arti": "kamu / kau"},
    {"kata": "amak",   "arti": "ibu"},
    {"kata": "apak",   "arti": "ayah / bapak"},
    {"kata": "uda",    "arti": "kakak laki-laki / abang"},
    {"kata": "uni",    "arti": "kakak perempuan / mbak"},
    {"kata": "iyo",    "arti": "iya / ya"},
    {"kata": "indak",  "arti": "tidak"},
    {"kata": "gadang", "arti": "besar"},
    {"kata": "ketek",  "arti": "kecil"},
    {"kata": "lamak",  "arti": "enak / lezat"},
    {"kata": "padeh",  "arti": "pedas"},
]


def garis(ch="=", n=70):
    print(ch * n)


def kotak(title, w=70):
    print("+" + "-" * (w - 2) + "+")
    pad = (w - 2 - len(title)) // 2
    print("|" + " " * pad + title + " " * (w - 2 - len(title) - pad) + "|")
    print("+" + "-" * (w - 2) + "+")


def bar(value, max_value, width=30):
    if max_value == 0:
        filled = 0
    else:
        filled = int((value / max_value) * width)
    return "#" * filled + "-" * (width - filled)


class GeneticDictionarySearch:
    def __init__(self, target, pop_size=8, crossover_rate=0.8, mutation_rate=0.1, rng=None):
        self.target = target.lower()
        self.chrom_len = len(self.target)
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.rng = rng or random.Random()

        self.population = []
        self.fitness_list = []
        self.roulette_table = []
        self.selected_parents = []
        self.crossover_log = []
        self.offspring = []
        self.mutation_log = []
        self.new_population = []
        self.new_fitness_list = []

    def buat_populasi_awal(self):
        self.population = [
            "".join(self.rng.choice(ALPHABET) for _ in range(self.chrom_len))
            for _ in range(self.pop_size)
        ]
        return self.population

    def hitung_fitness(self, populasi):
        hasil = []
        for ind in populasi:
            skor = sum(1 for a, b in zip(ind, self.target) if a == b)
            hasil.append(skor)
        return hasil

    def seleksi_roulette(self):
        total = sum(f + 1 for f in self.fitness_list) 
        kumulatif = 0
        self.roulette_table = []
        for ind, fit in zip(self.population, self.fitness_list):
            prob = (fit + 1) / total
            kumulatif += prob
            self.roulette_table.append({
                "individu": ind, "fitness": fit,
                "probabilitas": prob, "kumulatif": kumulatif
            })

        terpilih = []
        spins = []
        for _ in range(self.pop_size):
            r = self.rng.random()
            spins.append(r)
            for baris in self.roulette_table:
                if r <= baris["kumulatif"]:
                    terpilih.append(baris["individu"])
                    break
        self.selected_parents = terpilih
        self.spins = spins
        return terpilih

    def crossover(self):
        anak = []
        log = []
        parents = self.selected_parents[:]
        self.rng.shuffle(parents)
        for i in range(0, len(parents) - 1, 2):
            p1, p2 = parents[i], parents[i + 1]
            if self.rng.random() < self.crossover_rate and self.chrom_len > 1:
                titik = self.rng.randint(1, self.chrom_len - 1)
                c1 = p1[:titik] + p2[titik:]
                c2 = p2[:titik] + p1[titik:]
                log.append({"induk1": p1, "induk2": p2, "titik": titik, "anak1": c1, "anak2": c2})
            else:
                titik = None
                c1, c2 = p1, p2
                log.append({"induk1": p1, "induk2": p2, "titik": "tidak crossover", "anak1": c1, "anak2": c2})
            anak.extend([c1, c2])
        if len(parents) % 2 == 1:
            anak.append(parents[-1])
        self.offspring = anak[: self.pop_size]
        self.crossover_log = log
        return self.offspring

    def mutasi(self):
        hasil = []
        log = []
        for ind in self.offspring:
            genes = list(ind)
            mutasi_posisi = []
            for i in range(len(genes)):
                if self.rng.random() < self.mutation_rate:
                    lama = genes[i]
                    baru = self.rng.choice(ALPHABET)
                    genes[i] = baru
                    mutasi_posisi.append((i, lama, baru))
            hasil_str = "".join(genes)
            hasil.append(hasil_str)
            log.append({"asal": ind, "hasil": hasil_str, "posisi_mutasi": mutasi_posisi})
        self.new_population = hasil
        self.mutation_log = log
        return hasil

    def evaluasi_generasi_baru(self):
        self.new_fitness_list = self.hitung_fitness(self.new_population)
        return self.new_population, self.new_fitness_list

    def jalankan_satu_generasi(self):
        self.buat_populasi_awal()
        self.fitness_list = self.hitung_fitness(self.population)
        self.seleksi_roulette()
        self.crossover()
        self.mutasi()
        self.evaluasi_generasi_baru()


def tampilkan_kamus():
    kotak("KAMUS BAHASA MINANGKABAU - SUMATERA BARAT")
    print(f"{'No':<4}{'Kata Dayak':<15}{'Arti (Bahasa Indonesia)':<30}")
    garis("-")
    for i, d in enumerate(KAMUS, 1):
        print(f"{i:<4}{d['kata']:<15}{d['arti']:<30}")
    garis("-")
    print(f"Total data kamus: {len(KAMUS)} kata\n")


def cari_kata(kata):
    kata = kata.lower().strip()
    for d in KAMUS:
        if d["kata"] == kata:
            print(f'\n>> Kata "{kata}" ditemukan!  Arti: {d["arti"]}\n')
            return d
    print(f'\n>> Kata "{kata}" TIDAK ditemukan dalam kamus.\n')
    return None


def tampilkan_populasi(ga, judul="POPULASI AWAL"):
    kotak(judul)
    for i, ind in enumerate(ga.population, 1):
        print(f"  Individu-{i}: {ind}")
    print()


def tampilkan_fitness(ga):
    kotak("PERHITUNGAN FITNESS (target: '%s')" % ga.target)
    print(f"{'Individu':<10}{'Kromosom':<12}{'Fitness':<10}{'Grafik'}")
    garis("-")
    for i, (ind, fit) in enumerate(zip(ga.population, ga.fitness_list), 1):
        print(f"Individu-{i:<3}{ind:<12}{fit:<10}[{bar(fit, ga.chrom_len)}] {fit}/{ga.chrom_len}")
    garis("-")
    terbaik = max(ga.fitness_list)
    print(f"Fitness terbaik populasi awal: {terbaik}/{ga.chrom_len}\n")


def tampilkan_roulette(ga):
    kotak("SELEKSI ROULETTE WHEEL")
    print(f"{'Individu':<12}{'Fitness':<9}{'Prob.':<10}{'Kumulatif':<10}")
    garis("-")
    for i, r in enumerate(ga.roulette_table, 1):
        print(f"{r['individu']:<12}{r['fitness']:<9}{r['probabilitas']:.3f}     {r['kumulatif']:.3f}")
    garis("-")
    print("Hasil spin roda roulette (angka acak 0-1) & individu terpilih:")
    for i, (spin, terpilih) in enumerate(zip(ga.spins, ga.selected_parents), 1):
        print(f"  Spin-{i}: r={spin:.3f}  -> terpilih: {terpilih}")
    print()


def tampilkan_crossover(ga):
    kotak("PROSES CROSSOVER (Single-Point)")
    for i, c in enumerate(ga.crossover_log, 1):
        print(f"Pasangan-{i}:")
        print(f"  Induk 1 : {c['induk1']}")
        print(f"  Induk 2 : {c['induk2']}")
        print(f"  Titik potong : {c['titik']}")
        print(f"  Anak 1  : {c['anak1']}")
        print(f"  Anak 2  : {c['anak2']}")
        garis("-", 40)
    print()


def tampilkan_mutasi(ga):
    kotak("PROSES MUTASI")
    for i, m in enumerate(ga.mutation_log, 1):
        print(f"Kromosom-{i}: {m['asal']} -> {m['hasil']}")
        if m["posisi_mutasi"]:
            for pos, lama, baru in m["posisi_mutasi"]:
                print(f"    * mutasi posisi {pos}: '{lama}' -> '{baru}'")
        else:
            print("    (tidak ada mutasi)")
    print()


def tampilkan_generasi_baru(ga):
    kotak("HASIL GENERASI KE-1")
    print(f"{'Individu':<10}{'Kromosom':<12}{'Fitness':<10}{'Grafik'}")
    garis("-")
    for i, (ind, fit) in enumerate(zip(ga.new_population, ga.new_fitness_list), 1):
        print(f"Individu-{i:<3}{ind:<12}{fit:<10}[{bar(fit, ga.chrom_len)}] {fit}/{ga.chrom_len}")
    garis("-")
    fit_awal_terbaik = max(ga.fitness_list)
    fit_baru_terbaik = max(ga.new_fitness_list)
    print(f"Fitness terbaik generasi awal : {fit_awal_terbaik}/{ga.chrom_len}")
    print(f"Fitness terbaik generasi ke-1  : {fit_baru_terbaik}/{ga.chrom_len}")
    if fit_baru_terbaik == ga.chrom_len:
        idx = ga.new_fitness_list.index(fit_baru_terbaik)
        print(f'>> Kata target "{ga.target}" DITEMUKAN pada individu: {ga.new_population[idx]}')
    elif fit_baru_terbaik > fit_awal_terbaik:
        print(">> Populasi mengalami peningkatan fitness (evolusi mendekati target).")
    else:
        print(">> Fitness belum meningkat, perlu generasi tambahan.")
    print()

MENU_TEXT = """
=== Kamus Bahasa Daerah (Minangkabau - Sumatera Barat) ===

 1. Tampilkan Kamus
 2. Cari Kata
 3. Jalankan Algoritma Genetika
 4. Tampilkan Populasi
 5. Hasil Fitness
 6. Seleksi Roulette
 7. Cross Over
 8. Mutasi
 9. Generasi Baru
10. Keluar
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None, help="seed untuk hasil GA yang konsisten (opsional)")
    args = parser.parse_args()

    rng = random.Random(args.seed) if args.seed is not None else random.Random()
    ga = None

    while True:
        print(MENU_TEXT)
        try:
            pilihan = input("Pilih menu (1-10): ").strip()
        except EOFError:
            break

        if pilihan == "1":
            tampilkan_kamus()
        elif pilihan == "2":
            kata = input("Masukkan kata yang dicari: ")
            cari_kata(kata)
        elif pilihan == "3":
            target = input("Masukkan kata target untuk dicari dengan GA (harus ada di kamus): ").strip().lower()
            if not any(d["kata"] == target for d in KAMUS):
                print(f'>> Kata "{target}" tidak ada dalam kamus. Menu 3 dibatalkan.\n')
                continue
            ga = GeneticDictionarySearch(target, pop_size=8, crossover_rate=0.8, mutation_rate=0.1, rng=rng)
            ga.jalankan_satu_generasi()
            print(f'\n>> Algoritma Genetika dijalankan untuk mencari kata "{target}".')
            print(">> Gunakan menu 4-9 untuk melihat detail tiap tahap proses.\n")
        elif pilihan == "4":
            if ga:
                tampilkan_populasi(ga)
            else:
                print(">> Jalankan menu 3 terlebih dahulu.\n")
        elif pilihan == "5":
            if ga:
                tampilkan_fitness(ga)
            else:
                print(">> Jalankan menu 3 terlebih dahulu.\n")
        elif pilihan == "6":
            if ga:
                tampilkan_roulette(ga)
            else:
                print(">> Jalankan menu 3 terlebih dahulu.\n")
        elif pilihan == "7":
            if ga:
                tampilkan_crossover(ga)
            else:
                print(">> Jalankan menu 3 terlebih dahulu.\n")
        elif pilihan == "8":
            if ga:
                tampilkan_mutasi(ga)
            else:
                print(">> Jalankan menu 3 terlebih dahulu.\n")
        elif pilihan == "9":
            if ga:
                tampilkan_generasi_baru(ga)
            else:
                print(">> Jalankan menu 3 terlebih dahulu.\n")
        elif pilihan == "10":
            print("Terima kasih. Program selesai.")
            break
        else:
            print(">> Pilihan tidak valid.\n")


if __name__ == "__main__":
    main()