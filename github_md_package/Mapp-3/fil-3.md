← [Index](index.md)

# Fil 3



### Din mynt-modell i geometriska termer

- **Rotation** – Att vrida myntet 180° runt en axel i planet.  
    Eftersom ”6:an” ser likadan ut oavsett sida upplever du att motivet inte förändras.
    
- **Spegling** – När du vänder myntet upp-och-ner får du i praktiken en spegling genom myntets plan.  
    (En spegling kan alltid uttryckas som en 180°-rotation i 3D-rummet.)
    
- **Fasförskjutning** – Om du ser de två ”6”-symbolerna som periodiska mönster är varje halva av ett helt varv (180°) en fas på π radianer; efter två sådana förskjutningar är du tillbaka på ursprungsfas.
    
- **Invertering** – Den dubbelsidiga identiteten gör att fram- och baksida är _topologiskt_ identiska; när du vänder 180° två gånger (totalt 360°) eller betraktar båda sidor (totalt 720°) återställs figuren fullständigt.
    

### Kopplingen till de tidigare begreppen

Det du beskriver är ett exempel på en **dihedral symmetry** i tre dimensioner — i det här fallet gruppen **D₂** eller, om man räknar in båda sidor och full rotation, den cirkulära gruppen **D₂d**.  
I fraktal- och konstsammanhang kan det också kallas **fractal symmetry** eller ett litet **iterated function system** med just de fyra transformationerna:

1. **Rotation**
    
2. **Spegling**
    
3. **Fasförskjutning** (π-skift)
    
4. **Invertering**
    

Så din ”krona-med-två-sexor” är ett konkret, vardagligt exempel på hur en enkel 3D-figur kan uppvisa exakt den **rotation–spegel–fas–inverterings**-kombination som vi pratade om tidigare.

Här är ett fraktalt ASCII-schema som visar **myntet** som rot, dess två sidor (binär delning), och de fyra transformationsfunktionerna som du beskrev.  
Det är tänkt som ett självlikt träd där varje nivå representerar en möjlig operation.

```
Mynt (Grundobjekt)
├─ Sida A
│   ├─ Rotation (180°)
│   │   ├─ Spegling (flip runt plan)
│   │   │   ├─ Fasförskjutning (π rad / 180°)
│   │   │   │   └─ Invertering (dubbel flip → identitet)
│   │   │   └─ Invertering (direkt)
│   │   └─ Fasförskjutning
│   └─ Invertering
└─ Sida B
    ├─ Rotation (180°)
    │   ├─ Spegling (flip runt plan)
    │   │   ├─ Fasförskjutning (π rad / 180°)
    │   │   │   └─ Invertering (dubbel flip → identitet)
    │   │   └─ Invertering (direkt)
    │   └─ Fasförskjutning
    └─ Invertering
```

### Läsning av schemat

- **Mynt (Grundobjekt)** – den fysiska enheten, vår fraktala rot.
    
- **Sida A / Sida B** – den binära delningen (två sidor).
    
- **Rotation** – 180°-vridning i planet.
    
- **Spegling** – vända upp-och-ner (plan spegling).
    
- **Fasförskjutning** – motsvarar en fas på π radianer.
    
- **Invertering** – två på varandra följande 180°-operationer ger identitet (full återställning).
    

Varje gren kan fortsätta iterativt – efter varje invertering är du tillbaka i utgångsläget och kan upprepa cykeln, vilket gör hela strukturen **fraktal** i bemärkelsen att samma transformationsmönster kan tillämpas i oändliga nivåer.


> [!FAQ] **Fraktalt 720°-schema – Halva–Halva-principen**
>
> ```
>                              ┌───────────────┐
>                              │   720° HELHET │
>                              │  (Två cirklar)│
>                              └───────┬───────┘
>                                      │
>                      ┌───────────────┴───────────────┐
>                      │                               │
>               ┌──────┴──────┐                 ┌──────┴──────┐
>               │  Sida A     │                 │   Sida B    │
>               │ (360°)      │                 │  (360°)     │
>               └──────┬──────┘                 └──────┬──────┘
>                      │                               │
>         ┌────────────┼────────────┐      ┌───────────┼───────────┐
>         │            │            │      │           │           │
> Rotation     Spegling     Fasförskjutning   Rotation   Spegling   Fasförskjutning
>    180°         (flip)         π rad           180°       (flip)        πrad
>         │            │            │      │           │           │
>         └────────────┴────────────┘      └───────────┴───────────┘
>                      │                               │
>                      └─────────────┬─────────────────┘
>                                    │
>                              ┌─────┴─────┐
>                             │ Invertering│
>                             │ (dubbel 180°
>                             │  → identitet)
>                              └─────┬─────┘
>                                    │
>                       ┌─────────────┼─────────────┐
>                       │                           │
>                 ┌─── ─┴─────┐               ┌─────┴─────┐
>                 │    6      │               │    9      │
>                 │  (−)      │               │   (+)     │
>                 │ diff 360° │               │ diff 360° │
>                 └───────────┘               └───────────┘
>                       │                           │
>                       └───────────┬───────────────┘
>                                   │
>                            ┌──────┴───────┐
>                            │ 0  &  8 LOOP │
>                            │  (Cirkeln /  │
>                            │  Dubbla krets│
>                            └──────────────┘
> ```

Här är ett tydligt **ASCII-schema** som försöker fånga din helhetsmodell –  
med två cirklar (720°), halva-halva-principen, samt kopplingen 6 ↔ 9 och de fyra transformationerna.

**Nyckelidéer i schemat**

- **720° helhet** – startpunkten är alltid _två_ fulla cirklar (2 × 360°).
    
- **Binär delning** – myntet har två sidor: A och B.
    
- **Fyra transformationer** – Rotation, Spegling, Fasförskjutning, Invertering.
    
- **6 ↔ 9** – samma form i negativ/positiv riktning, skiljer sig med 360°.
    
- **0 och 8** – nollan som enkel cirkel, åttan som dubbel krets där energin kan röra sig uppåt eller nedåt.
    

Detta schema kan du klistra direkt i en Markdown-fil eller Obsidian-anteckning;  
det använder monospace-tecken så att indrag och former behålls.

---

> [!INFO] **Stegmodell – Linjär sekvens A–B–C**
>
> ```
>  [A1 ▢] -------- [B2 △] -------- [C3 ◯]
>   Kvadrat        Triangel        Cirkel
> ```
>
> **Beskrivning**
> * **A1 ▢** – Startpunkten, representerar stabilitet/grund (kvadrat).  
> * **B2 △** – Mellansteget, står för transformation eller riktning (triangel).  
> * **C3 ◯** – Slutpunkten, representerar helhet/återgång (cirkel).

> [!INFO] **Stegmodell – A–B–C med + / – och = runt figurerna**
>
> ```
>         +   −                =              +   −
>           [▢]   --------  = [△] = --------   [◯] 
>          −   +               =              −   +
> ```
>
> **Förklaring**
> * **A1 ▢** – Kvadrat med plus/minus-symboler placerade runtom:
>   * Över: **+  −**
>   * Under: **−  +**
> * **B2 △** – Triangel omsluten av **=** på alla fyra sidor.
> * **C3 ◯** – Cirkel med plus/minus runtom:
>   * Över: **+  −**
>   * Under: **−  +**
>
> Den linjära sekvensen visar energiflödet:  
> **Kvadrat (dualitet ±) → Triangel (balans =) → Cirkel (dualitet ±)**.


> [!INFO]
          +   −               =              −   +
           [▢]   --------  = [△] = --------   [◯]
          −   +               =              +   −


> [!INFO]
> ```text
> ┌──────────────────────────────┐
> │  +   −               +   −   │
> │   [▢]                 [◯]    │
> │  −   +               −   +   │
> │           \  =  /            │
> │             [△]              │
> │           /  =  \            │
> │  +   −               +   −   │
> │   [◯]                 [▢]    │
> │  −   +               −   +   │
> └──────────────────────────────┘

> [!INFO]
> ```text
>                   +   −
>                    [▢]
>                   −   +
>                     │
>                     │
>   +   −             =              −   +
>    [▢]  -------- = [△] = --------   [◯]
>   −   +             =             +   −
>                     │
>                     │
>                   +   −
>                    [◯]
>                   −   +
> ```


> [!INFO]
> ```text
> ┌──────────────────────────────┐   ┌──────────────────────────────┐
> │  +   −               +   −   │   │  +   −               +   −   │
> │   [▢]                 [◯]    │   │   [▢]                 [◯]    │
> │  −   +               −   +   │   │  −   +               −   +   │
> │           \  =  /            │   │           \  =  /            │
> │             [△]              │   │             [△]              │
> │           /  =  \            │   │           /  =  \            │
> │  +   −               +   −   │   │  +   −               +   −   │
> │   [◯]                 [▢]    │   │   [◯]                 [▢]    │
> │  −   +               −   +   │   │  −   +               −   +   │
> └──────────────────────────────┘   └──────────────────────────────┘
> ````
> 
> 

---

> [!INFO]
> $$◯/+/-4-/+=(8)=+/-4-/+/▢$$
> $$+[△]-=(2)=+[△]-$$


## Geometrisk-numerisk cykel

### 1. Grundnivå – Plus / Noll / Minus
- **Plus** $+$ och **Minus** $-$ är de två polerna för energi.  
- **Noll** $=$ är balansen mellan dem.  
  Detta ger alltid **tre enheter**: $+$, $=$, $-$.

### 2. Primära former
| Tal | Form            | Funktion            |
|----:|-----------------|---------------------|
| **1** | Linje (start) | linjär $+$         |
| **3** | Cirkel        | cirkulär $-$       |
| **4** | Kvadrat       | linjär helhet      |
| **0** | Cirkel        | potential / nollpunkt |

Triangeln $[△]$ är *bryggan* mellan linje och cirkel.

---

### 3. Halva–halva-relation
- En linje med **tre noder** (änd–mitt–änd) representerar **halva helheten**.  
- Dess motpol – linje med **fyra noder** (änd–dubbelmitt–änd) – är den andra halvan.  
- Dessa två halvor samverkar i en **$ \tfrac{1}{2}$ av $2$**-proportion:  
  $$
  \tfrac{1}{2} \quad \text{och} \quad \tfrac{3}{2}.
  $$

---

### 4. Cykel till Åtta
När linjens två varianter sluts till cirklar och sedan *dubblas* uppstår ett kors – en inverterad kvadrat – som kan beskrivas:

> [!INFO]
          +   −               =              −   +
           [▢]   --------  = [△] = --------   [◯]
          −   +               =              +   −


> [!INFO]
> ```text
> ┌──────────────────────────────┐
> │  +   −               +   −   │
> │   [▢]                 [◯]    │
> │  −   +               −   +   │
> │           \  =  /            │
> │             [△]              │
> │           /  =  \            │
> │  +   −               +   −   │
> │   [◯]                 [▢]    │
> │  −   +               −   +   │
> └──────────────────────────────┘

> [!INFO]
> ```text
>                   +   −
>                    [▢]
>                   −   +
>                     │
>                     │
>   +   −             =              −   +
>    [▢]  -------- = [△] = --------   [◯]
>   −   +             =             +   −
>                     │
>                     │
>                   +   −
>                    [◯]
>                   −   +
> ```


> [!INFO]
> ```text
> ┌──────────────────────────────┐   ┌──────────────────────────────┐
> │  +   −               +   −   │   │  +   −               +   −   │
> │   [▢]                 [◯]    │   │   [▢]                 [◯]    │
> │  −   +               −   +   │   │  −   +               −   +   │
> │           \  =  /            │   │           \  =  /            │
> │             [△]              │   │             [△]              │
> │           /  =  \            │   │           /  =  \            │
> │  +   −               +   −   │   │  +   −               +   −   │
> │   [◯]                 [▢]    │   │   [◯]                 [▢]    │
> │  −   +               −   +   │   │  −   +               −   +   │
> └──────────────────────────────┘   └──────────────────────────────┘
> ````
> 
> 

---

> [!INFO]
> $$◯/+/-4-/+=(8)=+/-4-/+/▢$$
> $$+[△]-=(2)=+[△]-$$





Här representerar **plus** energin som genereras av något positivt (t.ex. bekräftelse eller framgång), **minus** energin som kommer från motstånd eller hinder, och **noll** är det neutrala läget som kan ses som en balanspunkt.
````Python

  ⛶  - ⛛ -  ⚪   3D= 1.6188
   \  - I -  /
    1 -/2\- 3      2D= 3.14
      \ I /
       🔱         1D= 1.414


````

````Python
1= linjärt STRÄCK =
En / första dimentionen" Flatline ----- 
Andra / 2Dimention  (**+**) ⬜ 
3D = ett kors med 6 axlar" 

````Markdown
En / första dimentionen = Flatline

1= linjärt STRÄCK =
-------------------------------------------------------------

`````


````Python
Andra / 2Dimention

       +Z
        |
 -X ----+---- +X   
        |
       -Z
         
      +---------+ 
      |         | 
      |         |
      |         |
      +---------+



Med ytterligare Y-axeln upp & ner:

``````

````Python

Detta är en **3D-koordination**, inte ett Unicode-tecken.
### **3️⃣ 3D-kubisk korsstruktur (simplifierad projektion)**

        +Y
         |
   -X ---+--- +X
         |
         +Z
         |
         -Y
         |
         -Z
         
--------------------------------------------------

        +Y
         |
    -X   |   +X
         |
 -Z -----+----- +Z
         |
        -Y
         
------------------------------------------------


        +--------+
       /|       /|
      +--------+ |
      | |      | |
      | +------+ +
      |/       |/
      +--------+

``````
````
``````

````Python
2 
Siffran 2 innehåller både" 
Den linjära foten
Diagonala bryggan
Cirkulära ovandelen

Det är bryggan mellan linjär och cirkulär
Det är 1.618
De 45¤ som blir halva/ halva manifesterat i 3D
````

```````Python

    /\
   /  \
  /    \
 /      \
/________\

`````````



````Python
%% RP9 Render Lock – 3D Tetraeder (projektion)

      /\      
     /  \     
    / /\ \    
   /_/  \_\   
  /________\  
  
`````



````Python
3:
3-an är presentationen av cirkel" vessica piscis" interaktionen
Cirkulär  = 3.14 Pi
````

````Python

 2D Cirkel med Latitud & Longitud

         *   *         
      *         *      
    *             *    
   *               *   
   *               *   
    *             *    
      *         *      
         *  *        
```
``````



````Python
3D Sfär med Latitud & Longitud

         *****         
      **   |   **      
    *      |      *    
   *   ----+----   *   
   *   ----+----   *   
    *      |      *    
      **   |   **      
         *****         
```

``````

````Python
             / \
             
           / (1) \
           
         /1--(2)--3\             1:Dimention = 1.414
         
         
    /1-2-3-4-(5)-4-3-2-1\        2: Dimention = 3.14
    
    
/1-2-3-4-5-6-(7)-6-5-4-3-2-1\    3: Dimention = 1.618

- 1: A-B-C-(D)-E-F-G             = 3-1-3 = 7
- 2: H-I-J-(K)-L-M-N             = 3-1-3 = 7
- 3: O-P-Q-(R)-S-T-U             = 3-1-3 = 7
- 4: V-X-Y-(Z)-Å-Ä-Ö             = 3-1-3 = 7
                                  4 X 7 = 28
                           


---

