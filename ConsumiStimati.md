# Stime di Consumo Dati

Questo documento fornisce delle stime di consumo di dati in base a diverse situazioni, come il consumo di dati al secondo, per 150 ore totali, e per più persone. Le stime sono state calcolate in base a vari scenari di utilizzo.

---

## 1. **Consumo di Dati: 140 GB in 4 Ore**

Se consumi **140 GB** in **4 ore**, il consumo di dati al secondo può essere calcolato come segue:

### Consumo per Ora:
\[
\frac{140 \, \text{GB}}{4 \, \text{ore}} = 35 \, \text{GB/ora}
\]

### Consumo per Secondo:
\[
\frac{140 \, \text{GB}}{4 \, \text{ore} \times 3600 \, \text{secondi/ora}} = \frac{140 \, \text{GB}}{14400 \, \text{secondi}} \approx 0,00972 \, \text{GB/secondo} = 9,72 \, \text{MB/secondo}
\]

---

## 2. **Consumo in 150 Ore (140 GB in 4 Ore)**

Per calcolare il consumo in **150 ore**, utilizziamo il consumo medio di **35 GB/ora**:

\[
35 \, \text{GB/ora} \times 150 \, \text{ore} = 5250 \, \text{GB}
\]

Quindi, in **150 ore**, il consumo totale sarebbe **5250 GB**.

---

## 3. **Consumo di Dati per Persona (100 Persone)**

Se **100 persone** consumano **9,72 MB/s** ciascuna, il consumo totale al secondo sarebbe:

\[
9,72 \, \text{MB/s} \times 100 \, \text{persone} = 9720 \, \text{KB/s}
\]

Per calcolare il consumo per persona:

\[
\frac{9720 \, \text{KB/s}}{100} = 97,2 \, \text{KB/s}
\]

Ogni persona consuma quindi **97,2 KB/s**.

---

## 4. **Calcolo del Consumo per Persona per Restare sotto i 5000 GB (150 Ore, 100 Persone)**

Per rimanere sotto i **5000 GB** di consumo totale in **150 ore**, calcoliamo il massimo consumo per persona al secondo:

1. Totale dei dati (5000 GB in KB):

\[
5000 \, \text{GB} \times 1000000 = 5000000000 \, \text{KB}
\]

2. Totale dei secondi in 150 ore:

\[
150 \, \text{ore} \times 3600 \, \text{secondi/ora} = 540000 \, \text{secondi}
\]

3. Consumo massimo per persona:

\[
\frac{5000000000 \, \text{KB}}{540000 \, \text{secondi} \times 100 \, \text{persone}} = 92,59 \, \text{KB/s}
\]

Quindi, ogni persona può consumare al massimo **92,59 KB/s** per non superare i **5000 GB** totali in **150 ore**.

---

## 5. **Consumo per Persona per 200 GB (150 Ore, 25 Persone)**

Se il totale di dati è **200 GB** in **150 ore** per **25 persone**, il consumo massimo per persona al secondo sarà:

1. Totale dei dati (200 GB in KB):

\[
200 \, \text{GB} \times 1000000 = 200000000 \, \text{KB}
\]

2. Consumo massimo per persona al secondo:

\[
\frac{200000000 \, \text{KB}}{540000 \, \text{secondi} \times 25 \, \text{persone}} = 14,81 \, \text{KB/s}
\]

Quindi, per **200 GB** totali in **150 ore** per **25 persone**, ogni persona può consumare **14,81 KB/s** al secondo.

---

## 6. **Consumo per Guardare Video su Twitch a 160p**

Guardando video a **160p** su **Twitch**, il consumo di dati è stimato a **125 KB/s**. Questo valore può variare a seconda della compressione e della qualità della trasmissione, ma prendiamo **125 KB/s** come media.

### Consumo per Persona in 150 Ore:

1. Totale dei secondi in 150 ore:

\[
150 \, \text{ore} \times 3600 \, \text{secondi/ora} = 540000 \, \text{secondi}
\]

2. Consumo totale per persona in 150 ore:

\[
125 \, \text{KB/s} \times 540000 \, \text{secondi} = 67500000 \, \text{KB}
\]

3. Convertito in GB:

\[
\frac{67500000 \, \text{KB}}{1000000} = 67,5 \, \text{GB}
\]

### Consumo per 25 Persone in 150 Ore:

Se **25 persone** guardano video su **Twitch a 160p**, il consumo totale sarà:

\[
67,5 \, \text{GB} \times 25 = 1687,5 \, \text{GB} = 1,6875 \, \text{TB}
\]

---

## Riepilogo dei Risultati

1. **Consumo per Persona al Secondo (160p su Twitch)**: **125 KB/s**
2. **Consumo Totale per Persona in 150 Ore**: **67,5 GB**
3. **Consumo Totale per 25 Persone in 150 Ore**: **1,6875 TB**

---

### Considerazioni Finali

Le stime di consumo possono variare a seconda della qualità video, del tipo di flusso (ad esempio, video in diretta o registrato), della compressione utilizzata e di altre variabili tecniche. Queste stime sono basate su valori medi e possono essere utilizzate come base per calcolare il consumo di dati in scenari simili.
