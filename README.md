# Astro Kalkulator

Boleh mencari data berkenaan:
- Ijtimak
- Kedudukan Matahari dan Bulan pada waktu Ijtimak
- Waktu Solat
- Arah Kiblat menggunakan bayang-bayang Matahari

Tutorial untuk setup boleh lihat di YouTube https://www.youtube.com/watch?v=oeXbSYYx7hI         

## Installation
Langkah pertama adalah memastikan sistem mempunyai Python

Kemudian copy dulu fail ke dalam folder yang dikehendaki

```ruby
git clone https://github.com/duokino/astrokalkulator.git
```
Boleh juga download ZIP kemudian extract ke folder yang dikehendaki.

Pastikan anda menjalankan file setup.py supaya ia install kesemua file dependency dan database berkaitan

```ruby
python setup.py
```

Untuk memastikan anda menggunakan database kedudukan objek langit (dexxx.bsp) dan juga location.txt yang terkini, disarankan untuk menjalankan file update.py

```ruby
python update.py
```

## Fungsi yang boleh digunakan

### 1. Mendapatkan maklumat berkenaan Ijtimak

lokasi default adalah Batu Pahat. Masukkan tahun hijri dan bulan hijri
```ruby
python ijtimak.py 1446 9
```
<img src="images/ijtimak.jpg" width=900 height=450>

Sekiranya hendak menentukan lokasi berbeza dari default
```ruby
python ijtimak.py --location=telukkemang
```

Sekiranya hari melihat anak bulan sehari kemudian dari Ijtimak (kerana ijtimak berlaku selepas maghrib) maka perlu dimasukkan parameter offset=1
```ruby
python ijtimak.py --offset=1
```

untuk database lokasi boleh didapati dari file database/location.txt

### 2. Melihat kedudukan Matahri dan Bulan ketika Ijtimak 

lokasi default adalah Batu Pahat. masukkan tarikh dalam format (YYYYMMDD)
```ruby
python tunjuk_hilal.py --date=20250228
```
<img src="images/tunjuk_hilal.jpg" width=900 height=450>


### 3. Get map of crescent vibility based on various criteria
There are 6 criteria that are currently available in AHC: MABIMS, Odeh, Wujudul Hilal, Turkey, Danjon, and Itjima Qobla Ghurub.

#### 3.1. Crescent vibility map based on MABIMS criteria
This citeria is currently (as of 2023) used by the goverments of Indonesia, Malaysia, Singapore, and Brunei Darussalam.
```ruby
hl.map_hilal_visibility('MABIMS')
```
<img src="figures/map_mabims_Syawal_1444_2042023.png" width=900 height=450>

#### 3.2. Crescent visibility map based on Odeh criteria
This criteria is proposed by Mohammad Odeh in his 2016 [paper](https://link.springer.com/article/10.1007/s10686-005-9002-5) published in the Journal of Experimantal Astronomy.
```ruby 
hl.map_hilal_visibility('Odeh')
```
<img src="figures/map_odeh_Syawal_1444_2042023.png" width=900 height=450>

#### 3.3. Crescent visibility map based on Terkey criteria
This criteria is proposed by the International Hijri Calendar Union Congress in Istanbul in 2016 to be the criteria for the unified Hijri calendar.
```ruby
hl.map_hilal_visibility('Turkey')
```
<img src="figures/map_turkey_Syawal_1444_2042023.png" width=900 height=450>
