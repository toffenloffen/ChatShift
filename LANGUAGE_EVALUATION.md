# Multilingual text evaluation — 24 September 2026

## Scope

260 baseline requests: ten synthetic English messages for each of the 26 selectable target languages. English-to-English checks correction. This does not cover all source languages or all language pairs. A further 18 targeted requests used the revised instructions, including six roleplay examples. All requests used the actual CodexTranslator backend; no microphone, game input or delivery was tested.

## Findings and changes

- No request errors in this run. Successful requests are not a translation accuracy score.
- Agent semantic review found the central negation and numeric contrasts generally preserved. This is not an independent native-speaker evaluation.
- Baseline Norwegian/Danish used “healen” for the healer; Dutch produced “heileer”. Targeted revised runs used “healeren” and “Genees” respectively.
- Arabic used a potentially misleading literal tank label. The revised run retained tank as a gaming role. Native-speaker review remains useful.
- Named items were inconsistently translated, including an uncertain Russian rendering. Revised instructions prefer source spellings; all six targeted name retests preserved Stonescale Eels. Person/place transliteration still occurs in some outputs.
- Roleplay instructions now explicitly preserve voice, imagery, emotes, uncertainty and event order instead of asking for concise output. Six examples retained their main dialogue and actions.
- Remaining issues: Hindi still renders locked with a word that can mean closed; Japanese roleplay selects ship captain for ambiguous captain; French marks Aria feminine where the source does not specify gender. Do not claim perfect fidelity.
- The 260 baseline cases were not all rerun after the change. Follow-up results are targeted checks, not proof of improvement across every language.

Baseline request latency: median 1.65s; range 1.15–6.98s. Includes session work, excludes microphone and game insertion. Different samples do not establish a speed improvement.

## Baseline outputs

| Target | Case | Input | Output | Seconds |
| --- | --- | --- | --- | --- |
| English | negation | Do not attack yet. Wait until I am ready. | Do not attack yet. Wait until I am ready. | 2.33 |
| English | roles | Do not heal me. Heal the tank first. | Do not heal me. Heal the tank first. | 1.44 |
| English | numbers | I need fifty stones, not five, and twelve pieces of wood. | I need fifty stones, not five, and twelve pieces of wood. | 1.56 |
| English | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | My cooldown is not ready. Wait ten seconds, not two minutes. | 1.37 |
| English | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | 1.36 |
| English | kick | Interrupt the spell. Do not kick the healer from the group. | Interrupt the spell. Do not kick the healer from the group. | 3.1 |
| English | ordinary | The water tank by the house is leaking. My boss will look at it. | The water tank by the house is leaking. My boss will look at it. | 1.47 |
| English | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | 1.66 |
| English | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | If the door is locked, wait outside. Otherwise, come in. Do not break it. | 2.11 |
| English | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | I don't need healing yet, please wait for me. Can we do the dungeon after the raid? | 1.89 |
| Arabic | negation | Do not attack yet. Wait until I am ready. | لا تهاجموا الآن. انتظروا حتى أكون مستعدًا. | 2.26 |
| Arabic | roles | Do not heal me. Heal the tank first. | لا تعالجني. عالج الدبابة أولًا. | 1.59 |
| Arabic | numbers | I need fifty stones, not five, and twelve pieces of wood. | أحتاج إلى خمسين حجرًا، وليس خمسة، واثنتي عشرة قطعة من الخشب. | 1.48 |
| Arabic | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | فترة الانتظار الخاصة بقدرتي لم تنتهِ بعد. انتظروا عشر ثوانٍ، وليس دقيقتين. | 1.51 |
| Arabic | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | المعالج نفدت لديه المانا. لا تسحبوا المزيد من الوحوش. استخدموا AoE على الأعداء الإضافيين. | 2.36 |
| Arabic | kick | Interrupt the spell. Do not kick the healer from the group. | اقطع تعويذة العدو. لا تطرد المعالج من المجموعة. | 2.94 |
| Arabic | ordinary | The water tank by the house is leaking. My boss will look at it. | خزان المياه بجانب المنزل يتسرّب. سيفحصه مديري. | 1.82 |
| Arabic | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | قابل Aria في تاناريس الساعة 18:30. لا تبع ثعابين Stonescale بعد. | 1.43 |
| Arabic | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | إذا كان الباب مقفلًا، فانتظر في الخارج. وإلا فادخل. لا تكسره. | 1.52 |
| Arabic | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | لا أحتاج إلى هيل الآن، من فضلك انتظرني. هل يمكننا دخول الدنجن بعد الرايد؟ | 1.73 |
| Chinese (Simplified) | negation | Do not attack yet. Wait until I am ready. | 先别攻击。等我准备好了再说。 | 3.11 |
| Chinese (Simplified) | roles | Do not heal me. Heal the tank first. | 别给我治疗。先治疗坦克。 | 6.98 |
| Chinese (Simplified) | numbers | I need fifty stones, not five, and twelve pieces of wood. | 我需要五十块石头，不是五块，还有十二块木头。 | 1.45 |
| Chinese (Simplified) | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | 我的技能还在冷却中。等十秒，不是两分钟。 | 2.38 |
| Chinese (Simplified) | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | 治疗没蓝了。别再拉更多怪。用 AoE 处理小怪。 | 1.46 |
| Chinese (Simplified) | kick | Interrupt the spell. Do not kick the healer from the group. | 打断这个法术。不要把治疗者踢出队伍。 | 2.5 |
| Chinese (Simplified) | ordinary | The water tank by the house is leaking. My boss will look at it. | 房子旁边的水箱漏水了。我的老板会去看看。 | 1.27 |
| Chinese (Simplified) | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | 18:30 在塔纳利斯与 Aria 会合。暂时不要卖掉石鳞鳗。 | 1.35 |
| Chinese (Simplified) | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | 如果门锁着，就在外面等。否则就进来。不要把门弄坏。 | 1.29 |
| Chinese (Simplified) | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | 我暂时还不需要治疗，请等我一下。我们能在团队副本之后打地下城吗？ | 1.68 |
| Czech | negation | Do not attack yet. Wait until I am ready. | Zatím neútočte. Počkejte, až budu připravený. | 2.41 |
| Czech | roles | Do not heal me. Heal the tank first. | Neléč mě. Nejdřív vyléč tanka. | 1.65 |
| Czech | numbers | I need fifty stones, not five, and twelve pieces of wood. | Potřebuji padesát kamenů, ne pět, a dvanáct kusů dřeva. | 2.45 |
| Czech | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Moje schopnost ještě není připravená. Počkej deset sekund, ne dvě minuty. | 1.3 |
| Czech | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healerovi došla mana. Nepřitahujte další moby. Použijte AoE na addy. | 1.56 |
| Czech | kick | Interrupt the spell. Do not kick the healer from the group. | Přeruš kouzlo. Nevyhazuj léčitele ze skupiny. | 2.73 |
| Czech | ordinary | The water tank by the house is leaking. My boss will look at it. | Vodní nádrž u domu protéká. Můj šéf se na ni podívá. | 1.48 |
| Czech | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Sejdi se s Ariou v Tanarisu v 18:30. Zatím ty Stonescale Eels neprodávej. | 3.17 |
| Czech | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Pokud jsou dveře zamčené, počkej venku. Jinak vejdi. Nerozbíjej je. | 1.53 |
| Czech | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Zatím nepotřebuji léčení, prosím počkej na mě. Můžeme jít do dungeonu po raidu? | 1.58 |
| Danish | negation | Do not attack yet. Wait until I am ready. | Angrib ikke endnu. Vent, til jeg er klar. | 2.46 |
| Danish | roles | Do not heal me. Heal the tank first. | Lad være med at heale mig. Heal tanken først. | 1.48 |
| Danish | numbers | I need fifty stones, not five, and twelve pieces of wood. | Jeg skal bruge halvtreds sten, ikke fem, og tolv stykker træ. | 1.61 |
| Danish | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Min cooldown er ikke klar. Vent ti sekunder, ikke to minutter. | 1.51 |
| Danish | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healen er OOM. Træk ikke flere mobs. Brug AoE på adds. | 2.24 |
| Danish | kick | Interrupt the spell. Do not kick the healer from the group. | Afbryd besværgelsen. Smid ikke healeren ud af gruppen. | 2.7 |
| Danish | ordinary | The water tank by the house is leaking. My boss will look at it. | Vandtanken ved huset er utæt. Min chef vil se på den. | 1.65 |
| Danish | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Mød Aria i Tanaris kl. 18.30. Sælg ikke Stonescale Eels endnu. | 1.43 |
| Danish | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Hvis døren er låst, så vent udenfor. Ellers, så kom ind. Bryd den ikke op. | 1.7 |
| Danish | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Jeg har ikke brug for healing endnu, vent venligst på mig. Kan vi tage dungeonen efter raidet? | 2.26 |
| Dutch | negation | Do not attack yet. Wait until I am ready. | Val nog niet aan. Wacht tot ik er klaar voor ben. | 2.27 |
| Dutch | roles | Do not heal me. Heal the tank first. | Heil mij niet. Heileer eerst de tank. | 1.35 |
| Dutch | numbers | I need fifty stones, not five, and twelve pieces of wood. | Ik heb vijftig stenen nodig, geen vijf, en twaalf stukken hout. | 1.27 |
| Dutch | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Mijn cooldown is nog niet klaar. Wacht tien seconden, geen twee minuten. | 2.61 |
| Dutch | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | De healer is OOM. Trek niet meer mobs aan. Gebruik AoE op de adds. | 1.29 |
| Dutch | kick | Interrupt the spell. Do not kick the healer from the group. | Onderbreek de spreuk. Schop de healer niet uit de groep. | 2.97 |
| Dutch | ordinary | The water tank by the house is leaking. My boss will look at it. | De watertank bij het huis lekt. Mijn baas zal ernaar kijken. | 1.37 |
| Dutch | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Ontmoet Aria in Tanaris om 18:30. Verkoop de Stonescale Eels nog niet. | 1.74 |
| Dutch | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Als de deur op slot zit, wacht dan buiten. Kom anders naar binnen. Breek hem niet open. | 1.5 |
| Dutch | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Ik heb nog geen healing nodig, wacht alsjeblieft op me. Kunnen we de dungeon na de raid doen? | 1.43 |
| Finnish | negation | Do not attack yet. Wait until I am ready. | Älä hyökkää vielä. Odota, kunnes olen valmis. | 2.39 |
| Finnish | roles | Do not heal me. Heal the tank first. | Älä paranna minua. Paranna tankki ensin. | 1.7 |
| Finnish | numbers | I need fifty stones, not five, and twelve pieces of wood. | Tarvitsen viisikymmentä kiveä, en viittä, ja kaksitoista puunpalaa. | 1.31 |
| Finnish | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Cooldownini ei ole vielä valmis. Odota kymmenen sekuntia, älä kahta minuuttia. | 1.48 |
| Finnish | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healer on OOM. Älä vedä lisää mobbeja. Käytä AoE:ta addseihin. | 1.45 |
| Finnish | kick | Interrupt the spell. Do not kick the healer from the group. | Keskeytä loitsu. Älä poista parantajaa ryhmästä. | 2.58 |
| Finnish | ordinary | The water tank by the house is leaking. My boss will look at it. | Talon vieressä oleva vesisäiliö vuotaa. Pomoni katsoo sitä. | 1.7 |
| Finnish | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Tapaa Aria Tanariksessa klo 18.30. Älä myy Stonescale Eelejä vielä. | 3.27 |
| Finnish | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Jos ovi on lukossa, odota ulkona. Muuten tule sisään. Älä riko sitä. | 1.95 |
| Finnish | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | En tarvitse vielä healia, odottakaa minua. Voimmeko mennä dungeoniin raidin jälkeen? | 1.95 |
| French | negation | Do not attack yet. Wait until I am ready. | N’attaquez pas encore. Attendez que je sois prêt(e). | 2.67 |
| French | roles | Do not heal me. Heal the tank first. | Ne me soignez pas. Soignez d’abord le tank. | 1.36 |
| French | numbers | I need fifty stones, not five, and twelve pieces of wood. | J’ai besoin de cinquante pierres, pas de cinq, et de douze morceaux de bois. | 2.22 |
| French | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Mon temps de recharge n’est pas terminé. Attends dix secondes, pas deux minutes. | 1.28 |
| French | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Le healer est OOM. N’attirez pas plus de mobs. Utilisez une AoE sur les adds. | 1.52 |
| French | kick | Interrupt the spell. Do not kick the healer from the group. | Interromps le sort. Ne vire pas le soigneur du groupe. | 2.3 |
| French | ordinary | The water tank by the house is leaking. My boss will look at it. | Le réservoir d’eau près de la maison fuit. Mon patron va y jeter un œil. | 1.65 |
| French | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Retrouve Aria à Tanaris à 18 h 30. Ne vends pas encore les anguilles pierre-écailles. | 1.79 |
| French | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Si la porte est verrouillée, attends dehors. Sinon, entre. Ne la casse pas. | 1.48 |
| French | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Je n’ai pas encore besoin de soins, s’il te plaît, attends-moi. On peut faire le donjon après le raid ? | 1.42 |
| German | negation | Do not attack yet. Wait until I am ready. | Greift noch nicht an. Wartet, bis ich bereit bin. | 4.31 |
| German | roles | Do not heal me. Heal the tank first. | Heile mich nicht. Heile zuerst den Tank. | 1.19 |
| German | numbers | I need fifty stones, not five, and twelve pieces of wood. | Ich brauche fünfzig Steine, nicht fünf, und zwölf Stück Holz. | 1.33 |
| German | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Meine Abklingzeit ist noch nicht bereit. Wartet zehn Sekunden, nicht zwei Minuten. | 1.96 |
| German | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Der Heiler ist OOM. Zieht keine weiteren Mobs. Setzt AoE auf die Adds ein. | 1.29 |
| German | kick | Interrupt the spell. Do not kick the healer from the group. | Unterbrich den Zauber. Wirf den Heiler nicht aus der Gruppe. | 2.39 |
| German | ordinary | The water tank by the house is leaking. My boss will look at it. | Der Wassertank beim Haus ist undicht. Mein Chef wird sich das ansehen. | 1.39 |
| German | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Triff Aria in Tanaris um 18:30 Uhr. Verkaufe die Steinschuppenaale noch nicht. | 1.95 |
| German | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Wenn die Tür verschlossen ist, warte draußen. Andernfalls komm herein. Mach sie nicht kaputt. | 1.74 |
| German | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Ich brauche noch keine Heilung, bitte warte auf mich. Können wir den Dungeon nach dem Raid machen? | 1.42 |
| Greek | negation | Do not attack yet. Wait until I am ready. | Μην επιτεθείτε ακόμα. Περιμένετε μέχρι να είμαι έτοιμος. | 2.38 |
| Greek | roles | Do not heal me. Heal the tank first. | Μη με θεραπεύσεις. Θεράπευσε πρώτα το τανκ. | 1.28 |
| Greek | numbers | I need fifty stones, not five, and twelve pieces of wood. | Χρειάζομαι πενήντα πέτρες, όχι πέντε, και δώδεκα κομμάτια ξύλου. | 1.7 |
| Greek | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Το cooldown μου δεν είναι έτοιμο. Περίμενε δέκα δευτερόλεπτα, όχι δύο λεπτά. | 1.37 |
| Greek | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Ο healer είναι OOM. Μην τραβήξεις άλλα mobs. Χρησιμοποίησε AoE στα adds. | 2.89 |
| Greek | kick | Interrupt the spell. Do not kick the healer from the group. | Διέκοψε το ξόρκι. Μην διώξεις τον healer από την ομάδα. | 2.47 |
| Greek | ordinary | The water tank by the house is leaking. My boss will look at it. | Η δεξαμενή νερού δίπλα στο σπίτι έχει διαρροή. Το αφεντικό μου θα την κοιτάξει. | 1.43 |
| Greek | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Συναντήστε την Aria στο Tanaris στις 18:30. Μην πουλήσετε ακόμα τα Stonescale Eels. | 1.59 |
| Greek | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Αν η πόρτα είναι κλειδωμένη, περίμενε απ’ έξω. Διαφορετικά, μπες μέσα. Μην τη σπάσεις. | 2.52 |
| Greek | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Δεν χρειάζομαι heal ακόμα, παρακαλώ περίμενέ με. Μπορούμε να κάνουμε το dungeon μετά το raid; | 1.62 |
| Hindi | negation | Do not attack yet. Wait until I am ready. | अभी हमला मत करो। मेरे तैयार होने तक इंतज़ार करो। | 3.59 |
| Hindi | roles | Do not heal me. Heal the tank first. | मुझे heal मत करो। पहले tank को heal करो। | 3.81 |
| Hindi | numbers | I need fifty stones, not five, and twelve pieces of wood. | मुझे पाँच नहीं, पचास पत्थर और लकड़ी के बारह टुकड़े चाहिए। | 1.89 |
| Hindi | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | मेरा cooldown अभी तैयार नहीं है। दो मिनट नहीं, दस सेकंड इंतज़ार करो। | 1.27 |
| Hindi | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healer का mana खत्म हो गया है। और mobs को pull मत करो। adds पर AoE का इस्तेमाल करो। | 1.42 |
| Hindi | kick | Interrupt the spell. Do not kick the healer from the group. | उसके स्पेल को इंटरप्ट करो। हीलर को ग्रुप से किक मत करो। | 2.59 |
| Hindi | ordinary | The water tank by the house is leaking. My boss will look at it. | घर के पास पानी की टंकी लीक हो रही है। मेरे बॉस उसे देखेंगे। | 1.89 |
| Hindi | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Tanaris में Aria से 18:30 बजे मिलो। Stonescale Eels को अभी मत बेचो। | 1.36 |
| Hindi | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | अगर दरवाज़ा बंद है, तो बाहर इंतज़ार करो। वरना, अंदर आ जाओ। इसे मत तोड़ो। | 2.44 |
| Hindi | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | मुझे अभी हीलिंग की ज़रूरत नहीं है, कृपया मेरा इंतज़ार करो। क्या हम रेड के बाद डंगन कर सकते हैं? | 1.42 |
| Hungarian | negation | Do not attack yet. Wait until I am ready. | Még ne támadjatok. Várjatok, amíg készen állok. | 5.82 |
| Hungarian | roles | Do not heal me. Heal the tank first. | Ne engem gyógyíts. Előbb a tankot gyógyítsd. | 2.75 |
| Hungarian | numbers | I need fifty stones, not five, and twelve pieces of wood. | Ötven kőre van szükségem, nem ötre, és tizenkét darab fára. | 1.62 |
| Hungarian | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | A képességem töltési ideje még nem járt le. Várj tíz másodpercet, ne két percet. | 2.75 |
| Hungarian | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | A healer OOM-on van. Ne húzzatok be több mobot. Használjatok AoE-t az addokra. | 2.81 |
| Hungarian | kick | Interrupt the spell. Do not kick the healer from the group. | Szakítsd meg a varázslatot. Ne rúgd ki a gyógyítót a csapatból. | 2.6 |
| Hungarian | ordinary | The water tank by the house is leaking. My boss will look at it. | A ház melletti víztartály szivárog. A főnököm meg fogja nézni. | 1.34 |
| Hungarian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Találkozz Ariával Tanarisban 18:30-kor. A Stonescale Eeleket még ne add el. | 1.4 |
| Hungarian | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Ha az ajtó zárva van, várj kint. Ha nem, gyere be. Ne törd be. | 1.74 |
| Hungarian | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Még nem kell heal, kérlek, várj meg. Megcsinálhatjuk a dungeont a raid után? | 1.52 |
| Italian | negation | Do not attack yet. Wait until I am ready. | Non attaccare ancora. Aspetta finché non sono pronto. | 2.67 |
| Italian | roles | Do not heal me. Heal the tank first. | Non curare me. Cura prima il tank. | 1.34 |
| Italian | numbers | I need fifty stones, not five, and twelve pieces of wood. | Mi servono cinquanta pietre, non cinque, e dodici pezzi di legno. | 1.45 |
| Italian | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | La mia abilità è ancora in cooldown. Aspetta dieci secondi, non due minuti. | 1.41 |
| Italian | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Il healer è OOM. Non attirare altri mob. Usa l'AoE sugli adds. | 1.44 |
| Italian | kick | Interrupt the spell. Do not kick the healer from the group. | Interrompi l'incantesimo. Non espellere il guaritore dal gruppo. | 2.92 |
| Italian | ordinary | The water tank by the house is leaking. My boss will look at it. | Il serbatoio dell'acqua vicino alla casa perde. Il mio capo lo controllerà. | 1.38 |
| Italian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Incontra Aria a Tanaris alle 18:30. Non vendere ancora le anguille di scaglia di pietra. | 1.61 |
| Italian | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Se la porta è chiusa a chiave, aspetta fuori. Altrimenti, entra. Non sfondarla. | 1.32 |
| Italian | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Non mi serve ancora una cura, per favore aspettami. Possiamo fare il dungeon dopo il raid? | 1.81 |
| Japanese | negation | Do not attack yet. Wait until I am ready. | まだ攻撃しないで。私の準備ができるまで待って。 | 2.58 |
| Japanese | roles | Do not heal me. Heal the tank first. | 私を回復しないで。先にタンクを回復して。 | 1.35 |
| Japanese | numbers | I need fifty stones, not five, and twelve pieces of wood. | 石が50個必要で、5個ではありません。それと木材が12個必要です。 | 1.35 |
| Japanese | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | クールダウンがまだ終わっていません。2分ではなく、10秒待ってください。 | 2.4 |
| Japanese | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | ヒーラーがOOMです。これ以上Mobを釣らないでください。追加の敵にはAoEを使ってください。 | 1.46 |
| Japanese | kick | Interrupt the spell. Do not kick the healer from the group. | その呪文を中断して。ヒーラーをグループから追い出さないで。 | 2.56 |
| Japanese | ordinary | The water tank by the house is leaking. My boss will look at it. | 家のそばにある貯水タンクが漏れている。上司が見てくれる。 | 1.32 |
| Japanese | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | 18:30にTanarisでAriaと会って。Stonescale Eelはまだ売らないで。 | 1.45 |
| Japanese | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | ドアに鍵がかかっていたら外で待って。そうでなければ入ってきて。壊さないで。 | 1.65 |
| Japanese | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | まだヒールは必要ないから、待ってて。レイドの後にダンジョン行ける？ | 1.46 |
| Korean | negation | Do not attack yet. Wait until I am ready. | 아직 공격하지 마세요. 제가 준비될 때까지 기다리세요. | 2.32 |
| Korean | roles | Do not heal me. Heal the tank first. | 저는 치유하지 마세요. 먼저 탱커를 치유하세요. | 1.76 |
| Korean | numbers | I need fifty stones, not five, and twelve pieces of wood. | 돌 50개가 필요해요. 5개가 아니라요. 그리고 나무 12개도요. | 1.54 |
| Korean | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | 제 쿨다운이 아직 돌아오지 않았어요. 2분이 아니라 10초 기다려 주세요. | 1.33 |
| Korean | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | 힐러가 마나가 다 떨어졌어요. 몹을 더 풀링하지 마세요. 추가로 나온 적들에게 광역기를 사용하세요. | 1.51 |
| Korean | kick | Interrupt the spell. Do not kick the healer from the group. | 그 주문을 차단해. 힐러를 파티에서 추방하지 마. | 2.48 |
| Korean | ordinary | The water tank by the house is leaking. My boss will look at it. | 집 옆 물탱크에서 물이 새고 있어. 내 상사가 확인해 볼 거야. | 1.39 |
| Korean | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | 18시 30분에 타나리스에서 Aria를 만나. 아직 Stonescale Eels는 팔지 마. | 1.35 |
| Korean | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | 문이 잠겨 있으면 밖에서 기다려. 그렇지 않으면 들어와. 부수지는 마. | 1.36 |
| Korean | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | 아직 힐 필요 없어, 나 기다려 줘. 레이드 끝나고 던전 갈 수 있을까? | 1.51 |
| Norwegian | negation | Do not attack yet. Wait until I am ready. | Ikke angrip ennå. Vent til jeg er klar. | 2.23 |
| Norwegian | roles | Do not heal me. Heal the tank first. | Ikke heal meg. Heal tanken først. | 1.26 |
| Norwegian | numbers | I need fifty stones, not five, and twelve pieces of wood. | Jeg trenger femti steiner, ikke fem, og tolv vedkubber. | 1.44 |
| Norwegian | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Cooldownen min er ikke klar. Vent ti sekunder, ikke to minutter. | 1.34 |
| Norwegian | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healen er OOM. Ikke pull flere mobs. Bruk AoE på adds. | 2.61 |
| Norwegian | kick | Interrupt the spell. Do not kick the healer from the group. | Avbryt trylleformelen. Ikke kast healeren ut av gruppen. | 2.47 |
| Norwegian | ordinary | The water tank by the house is leaking. My boss will look at it. | Vanntanken ved huset lekker. Sjefen min skal se på den. | 1.22 |
| Norwegian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Møt Aria i Tanaris kl. 18:30. Ikke selg Stonescale Eels ennå. | 1.34 |
| Norwegian | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Hvis døren er låst, vent utenfor. Ellers kan du komme inn. Ikke bryt den opp. | 1.32 |
| Norwegian | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Jeg trenger ikke healing ennå, vent på meg, er du snill. Kan vi ta dungeonen etter raidet? | 1.3 |
| Polish | negation | Do not attack yet. Wait until I am ready. | Na razie nie atakuj. Poczekaj, aż będę gotowy. | 2.54 |
| Polish | roles | Do not heal me. Heal the tank first. | Nie lecz mnie. Najpierw ulecz tanka. | 1.2 |
| Polish | numbers | I need fifty stones, not five, and twelve pieces of wood. | Potrzebuję pięćdziesięciu kamieni, nie pięciu, oraz dwunastu kawałków drewna. | 1.78 |
| Polish | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Mój cooldown jeszcze się nie skończył. Poczekaj dziesięć sekund, nie dwie minuty. | 1.81 |
| Polish | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healer ma OOM. Nie pulluj więcej mobów. Użyj AoE na addach. | 1.31 |
| Polish | kick | Interrupt the spell. Do not kick the healer from the group. | Przerwij rzucanie zaklęcia. Nie wyrzucaj healera z grupy. | 2.6 |
| Polish | ordinary | The water tank by the house is leaking. My boss will look at it. | Zbiornik na wodę przy domu przecieka. Mój szef się tym zajrzy. | 1.75 |
| Polish | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Spotkaj się z Arią w Tanaris o 18:30. Nie sprzedawaj jeszcze Stonescale Eels. | 1.52 |
| Polish | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Jeśli drzwi są zamknięte, poczekaj na zewnątrz. W przeciwnym razie wejdź do środka. Nie wyważaj ich. | 2.36 |
| Polish | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Nie potrzebuję jeszcze leczenia, proszę, poczekaj na mnie. Możemy zrobić dungeon po raidzie? | 2.25 |
| Portuguese | negation | Do not attack yet. Wait until I am ready. | Ainda não ataquem. Esperem até eu estar pronto. | 2.44 |
| Portuguese | roles | Do not heal me. Heal the tank first. | Não me cure. Cure o tank primeiro. | 1.19 |
| Portuguese | numbers | I need fifty stones, not five, and twelve pieces of wood. | Preciso de cinquenta pedras, não cinco, e de doze pedaços de madeira. | 1.36 |
| Portuguese | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Meu cooldown ainda não está disponível. Espere dez segundos, não dois minutos. | 1.28 |
| Portuguese | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | O healer está OOM. Não puxem mais mobs. Usem AoE nos adds. | 1.5 |
| Portuguese | kick | Interrupt the spell. Do not kick the healer from the group. | Interrompa o feitiço. Não expulse o healer do grupo. | 2.65 |
| Portuguese | ordinary | The water tank by the house is leaking. My boss will look at it. | O tanque de água ao lado da casa está vazando. Meu chefe vai dar uma olhada nele. | 1.28 |
| Portuguese | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Encontre a Aria em Tanaris às 18:30. Ainda não venda as enguias Stonescale. | 1.49 |
| Portuguese | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Se a porta estiver trancada, espere do lado de fora. Caso contrário, entre. Não a arrombe. | 1.51 |
| Portuguese | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Ainda não preciso de cura, por favor, espere por mim. Podemos fazer a masmorra depois da raid? | 1.59 |
| Romanian | negation | Do not attack yet. Wait until I am ready. | Nu ataca încă. Așteaptă până sunt gata. | 2.39 |
| Romanian | roles | Do not heal me. Heal the tank first. | Nu mă vindeca. Vindecă mai întâi tankul. | 2.15 |
| Romanian | numbers | I need fifty stones, not five, and twelve pieces of wood. | Am nevoie de cincizeci de pietre, nu de cinci, și de douăsprezece bucăți de lemn. | 1.44 |
| Romanian | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Cooldown-ul meu nu este gata. Așteaptă zece secunde, nu două minute. | 1.28 |
| Romanian | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healerul nu mai are mană. Nu mai trageți alți mobi. Folosiți AoE pe inamicii suplimentari. | 1.41 |
| Romanian | kick | Interrupt the spell. Do not kick the healer from the group. | Întrerupe vraja. Nu da afară healerul din grup. | 2.39 |
| Romanian | ordinary | The water tank by the house is leaking. My boss will look at it. | Rezervorul de apă de lângă casă are o scurgere. Șeful meu se va uita la el. | 1.41 |
| Romanian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Întâlnește-te cu Aria în Tanaris la 18:30. Nu vinde încă anghilele Stonescale. | 1.38 |
| Romanian | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Dacă ușa este încuiată, așteaptă afară. Altfel, intră. Nu o sparge. | 1.66 |
| Romanian | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Nu am nevoie încă de heal, te rog așteaptă-mă. Putem face dungeonul după raid? | 1.85 |
| Russian | negation | Do not attack yet. Wait until I am ready. | Пока не атакуйте. Подождите, пока я не буду готов. | 2.19 |
| Russian | roles | Do not heal me. Heal the tank first. | Не лечи меня. Сначала лечи танка. | 4.3 |
| Russian | numbers | I need fifty stones, not five, and twelve pieces of wood. | Мне нужно пятьдесят камней, а не пять, и двенадцать кусков дерева. | 3.35 |
| Russian | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Моя способность ещё на перезарядке. Подождите десять секунд, а не две минуты. | 1.35 |
| Russian | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | У хила закончилась мана. Не пулльте больше мобов. Используйте AoE по аддам. | 2.6 |
| Russian | kick | Interrupt the spell. Do not kick the healer from the group. | Прерви заклинание. Не исключай хила из группы. | 2.35 |
| Russian | ordinary | The water tank by the house is leaking. My boss will look at it. | Протекает бак с водой возле дома. Мой начальник его осмотрит. | 2.34 |
| Russian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Встреться с Арией в Танарисе в 18:30. Пока не продавай каменную угриль-рыбу. | 1.78 |
| Russian | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Если дверь заперта, подожди снаружи. Иначе заходи. Не взламывай её. | 1.42 |
| Russian | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Мне пока не нужно лечение, пожалуйста, подожди меня. Можем пройти подземелье после рейда? | 1.35 |
| Spanish | negation | Do not attack yet. Wait until I am ready. | No ataques todavía. Espera hasta que esté listo. | 3.83 |
| Spanish | roles | Do not heal me. Heal the tank first. | No me cures. Cura primero al tanque. | 1.58 |
| Spanish | numbers | I need fifty stones, not five, and twelve pieces of wood. | Necesito cincuenta piedras, no cinco, y doce trozos de madera. | 3.16 |
| Spanish | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Mi habilidad aún está en enfriamiento. Espera diez segundos, no dos minutos. | 1.5 |
| Spanish | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | El healer está OOM. No atraigas más mobs. Usa AoE con los adds. | 1.41 |
| Spanish | kick | Interrupt the spell. Do not kick the healer from the group. | Interrumpe el hechizo. No expulses al sanador del grupo. | 4.1 |
| Spanish | ordinary | The water tank by the house is leaking. My boss will look at it. | El tanque de agua junto a la casa tiene una fuga. Mi jefe lo revisará. | 2.97 |
| Spanish | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Reúnete con Aria en Tanaris a las 18:30. No vendas todavía las anguilas Stonescale. | 2.08 |
| Spanish | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Si la puerta está cerrada con llave, espera afuera. De lo contrario, entra. No la rompas. | 2.22 |
| Spanish | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Todavía no necesito curas, por favor espérame. ¿Podemos hacer la mazmorra después de la raid? | 1.37 |
| Swedish | negation | Do not attack yet. Wait until I am ready. | Attackera inte än. Vänta tills jag är redo. | 2.36 |
| Swedish | roles | Do not heal me. Heal the tank first. | Hela inte mig. Hela tanken först. | 1.59 |
| Swedish | numbers | I need fifty stones, not five, and twelve pieces of wood. | Jag behöver femtio stenar, inte fem, och tolv träbitar. | 2.42 |
| Swedish | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Min cooldown är inte redo. Vänta tio sekunder, inte två minuter. | 1.97 |
| Swedish | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healern har slut på mana. Dra inte fler mobs. Använd AoE på adds. | 1.34 |
| Swedish | kick | Interrupt the spell. Do not kick the healer from the group. | Avbryt besvärjelsen. Sparka inte ut helaren ur gruppen. | 2.52 |
| Swedish | ordinary | The water tank by the house is leaking. My boss will look at it. | Vattentanken vid huset läcker. Min chef ska titta på den. | 1.51 |
| Swedish | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Träffa Aria i Tanaris klockan 18:30. Sälj inte Stonescale Eels än. | 1.53 |
| Swedish | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Om dörren är låst, vänta utanför. Annars, kom in. Bryt inte upp den. | 1.53 |
| Swedish | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Jag behöver ingen healing än, vänta på mig, tack. Kan vi köra dungeonen efter raiden? | 1.44 |
| Thai | negation | Do not attack yet. Wait until I am ready. | อย่าเพิ่งโจมตี รอจนกว่าฉันจะพร้อม | 2.33 |
| Thai | roles | Do not heal me. Heal the tank first. | อย่าเพิ่งฮีลฉัน ฮีลแท็งก์ก่อน | 2.6 |
| Thai | numbers | I need fifty stones, not five, and twelve pieces of wood. | ฉันต้องการหินห้าสิบก้อน ไม่ใช่ห้าก้อน และไม้สิบสองชิ้น | 1.97 |
| Thai | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | คูลดาวน์ของฉันยังไม่พร้อม รอสิบวินาที ไม่ใช่สองนาที | 1.42 |
| Thai | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | ฮีลเลอร์มานาหมดแล้ว อย่าเพิ่งดึงม็อบเพิ่ม ใช้ AoE กับศัตรูที่เข้ามาเสริม | 1.68 |
| Thai | kick | Interrupt the spell. Do not kick the healer from the group. | ขัดจังหวะคาถานั้น อย่าเตะฮีลเลอร์ออกจากกลุ่ม | 2.54 |
| Thai | ordinary | The water tank by the house is leaking. My boss will look at it. | ถังเก็บน้ำข้างบ้านรั่ว เจ้านายของฉันจะไปดูให้ | 1.41 |
| Thai | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | ไปพบ Aria ที่ Tanaris เวลา 18:30 อย่าเพิ่งขาย Stonescale Eels | 1.54 |
| Thai | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | ถ้าประตูล็อกอยู่ ให้รอข้างนอก ไม่อย่างนั้นก็เข้ามาได้ อย่าพังประตู | 1.95 |
| Thai | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | ตอนนี้ฉันยังไม่ต้องการฮีล รอฉันก่อนนะ เราไปดันเจี้ยนหลังเรดได้ไหม | 1.83 |
| Turkish | negation | Do not attack yet. Wait until I am ready. | Henüz saldırmayın. Ben hazır olana kadar bekleyin. | 2.72 |
| Turkish | roles | Do not heal me. Heal the tank first. | Beni iyileştirme. Önce tankı iyileştir. | 1.99 |
| Turkish | numbers | I need fifty stones, not five, and twelve pieces of wood. | Beş değil, elli taşa ve on iki parça oduna ihtiyacım var. | 2.7 |
| Turkish | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Bekleme sürem hazır değil. İki dakika değil, on saniye bekleyin. | 1.47 |
| Turkish | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healer'ın manası bitti. Daha fazla mob çekmeyin. Ek düşmanlara AoE kullanın. | 1.71 |
| Turkish | kick | Interrupt the spell. Do not kick the healer from the group. | Büyüyü kes. Şifacıyı gruptan atma. | 2.46 |
| Turkish | ordinary | The water tank by the house is leaking. My boss will look at it. | Evin yanındaki su deposu sızdırıyor. Patronum ona bakacak. | 1.2 |
| Turkish | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | 18:30'da Tanaris'te Aria ile buluş. Stonescale Eel'leri henüz satma. | 1.37 |
| Turkish | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Kapı kilitliyse dışarıda bekle. Değilse içeri gir. Kırma. | 1.71 |
| Turkish | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Henüz heal gerekmiyor, lütfen beni bekle. Raid'den sonra dungeon yapabilir miyiz? | 1.52 |
| Ukrainian | negation | Do not attack yet. Wait until I am ready. | Поки що не атакуйте. Зачекайте, доки я буду готовий. | 2.77 |
| Ukrainian | roles | Do not heal me. Heal the tank first. | Не лікуй мене. Спочатку лікуй танка. | 2.14 |
| Ukrainian | numbers | I need fifty stones, not five, and twelve pieces of wood. | Мені потрібно п’ятдесят каменів, а не п’ять, і дванадцять шматків дерева. | 1.54 |
| Ukrainian | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Моя здатність ще на перезарядці. Зачекай десять секунд, а не дві хвилини. | 1.84 |
| Ukrainian | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Хілер без мани. Не пулльте більше мобів. Використовуйте AoE на додаткових мобах. | 1.54 |
| Ukrainian | kick | Interrupt the spell. Do not kick the healer from the group. | Перерви заклинання. Не виганяй хілера з групи. | 3.02 |
| Ukrainian | ordinary | The water tank by the house is leaking. My boss will look at it. | Бак із водою біля будинку протікає. Мій бос його огляне. | 1.67 |
| Ukrainian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Зустрінься з Арією в Танарісі о 18:30. Поки що не продавай Stonescale Eels. | 1.85 |
| Ukrainian | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Якщо двері замкнені, зачекай надворі. Інакше заходь. Не ламай їх. | 1.34 |
| Ukrainian | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Мені поки що не потрібне лікування, зачекайте на мене, будь ласка. Можемо пройти підземелля після рейду? | 1.45 |
| Vietnamese | negation | Do not attack yet. Wait until I am ready. | Đừng tấn công vội. Hãy chờ đến khi tôi sẵn sàng. | 2.75 |
| Vietnamese | roles | Do not heal me. Heal the tank first. | Đừng heal tôi. Hãy heal tank trước. | 1.15 |
| Vietnamese | numbers | I need fifty stones, not five, and twelve pieces of wood. | Tôi cần năm mươi viên đá, không phải năm viên, và mười hai mảnh gỗ. | 1.37 |
| Vietnamese | timing | My cooldown is not ready. Wait ten seconds, not two minutes. | Kỹ năng của tôi chưa hồi xong. Hãy chờ mười giây, không phải hai phút. | 1.39 |
| Vietnamese | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healer hết mana. Đừng kéo thêm mob. Dùng AoE lên các quái phụ. | 1.79 |
| Vietnamese | kick | Interrupt the spell. Do not kick the healer from the group. | Ngắt phép. Đừng đá healer khỏi nhóm. | 2.96 |
| Vietnamese | ordinary | The water tank by the house is leaking. My boss will look at it. | Bồn nước cạnh nhà đang bị rò rỉ. Sếp của tôi sẽ xem xét nó. | 2.24 |
| Vietnamese | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Gặp Aria ở Tanaris lúc 18:30. Đừng bán những con lươn Stonescale vội. | 1.61 |
| Vietnamese | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Nếu cửa bị khóa, hãy chờ bên ngoài. Nếu không, hãy vào đi. Đừng phá cửa. | 1.59 |
| Vietnamese | typos | i dont need healin yet, pls wait for me. can we do the dungeon after the raid? | Tôi chưa cần heal, làm ơn đợi tôi. Chúng ta đi dungeon sau raid được không? | 2.07 |

## Revised instructions: targeted and roleplay outputs

| Direction | Case | Input | Output | Seconds |
| --- | --- | --- | --- | --- |
| English → Arabic | roles | Do not heal me. Heal the tank first. | لا تشفني. عالج الـtank أولًا. | 2.3 |
| English → Arabic | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | قابل Aria في Tanaris الساعة 18:30. لا تبِع Stonescale Eels بعد. | 1.43 |
| English → Danish | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healeren er OOM. Træk ikke flere mobs. Brug AoE på adds. | 3.11 |
| English → Dutch | roles | Do not heal me. Heal the tank first. | Genees mij niet. Genees eerst de tank. | 2.61 |
| English → French | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Retrouve Aria à Tanaris à 18 h 30. Ne vends pas encore les Stonescale Eels. | 2.6 |
| English → Hindi | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | अगर दरवाज़ा बंद है, तो बाहर इंतज़ार करो। वरना, अंदर आ जाओ। उसे मत तोड़ना। | 2.35 |
| English → Italian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Incontra Aria a Tanaris alle 18:30. Non vendere ancora le Stonescale Eels. | 2.82 |
| English → Norwegian | gaming | The healer is OOM. Do not pull more mobs. Use AoE on the adds. | Healeren er OOM. Ikke trekk flere mobs. Bruk AoE på adds. | 2.81 |
| English → Polish | condition | If the door is locked, wait outside. Otherwise, come in. Do not break it. | Jeśli drzwi są zamknięte na klucz, poczekaj na zewnątrz. W przeciwnym razie wejdź. Nie wyważaj ich. | 5.1 |
| English → Russian | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Встреться с Арией в Танарисе в 18:30. Пока не продавай Stonescale Eels. | 2.98 |
| English → Spanish | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Encuéntrate con Aria en Tanaris a las 18:30. No vendas todavía las Stonescale Eels. | 2.48 |
| English → Vietnamese | names | Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet. | Gặp Aria ở Tanaris lúc 18:30. Đừng bán Stonescale Eels vội. | 2.49 |
| Norwegian → English | roleplay | *Senker stemmen og skjuler brevet i kappen.* Jeg lovet å vente til daggry, ikke å stole på deg. Hvis Aria ikke kommer tilbake, går vi uten henne. | *Lowers their voice and hides the letter in their cloak.* I promised to wait until dawn, not to trust you. If Aria does not return, we leave without her. | 2.65 |
| English → Norwegian | roleplay | "I may forgive you," she whispered, "but I will not forget." *She places three silver coins on the table, keeping the fourth.* | «Jeg kan kanskje tilgi deg», hvisket hun, «men jeg kommer ikke til å glemme.» *Hun legger tre sølvmynter på bordet og beholder den fjerde.* | 3.81 |
| English → German | roleplay | *The old healer studies the sealed door.* "It is closed, not locked. We could leave now, but I would rather hear your side of the story." | *Der alte Heiler mustert die versiegelte Tür.* „Sie ist geschlossen, nicht verschlossen. Wir könnten jetzt gehen, aber ich würde lieber deine Seite der Geschichte hören.“ | 2.79 |
| English → Spanish | roleplay | "Your Majesty, I seek neither gold nor pardon. I ask only that my brother be allowed to return home." *He bows, but does not kneel.* | «Vuestra Majestad, no busco ni oro ni perdón. Solo pido que se permita a mi hermano regresar a casa». *Hace una reverencia, pero no se arrodilla.* | 2.99 |
| English → French | roleplay | The lantern flickered above the empty chair. Perhaps Aria had already left; I could not tell. I put down the letter without opening it. | La lanterne vacillait au-dessus de la chaise vide. Aria était peut-être déjà partie ; je ne pouvais pas le savoir. J’ai posé la lettre sans l’ouvrir. | 2.72 |
| English → Japanese | roleplay | *Aria smiles faintly.* "I did not say the captain lied. I said I could not confirm the story." The footsteps outside stop, but nobody enters. | *アリアはかすかに微笑む。*「私は船長が嘘をついたとは言っていない。話の内容を確認できなかったと言ったのだ。」外の足音が止まるが、誰も入ってこない。 | 3.01 |

Reproduce the base suite with `.venv/Scripts/python.exe "norsk engelsk/tests/check_all_languages.py"`. This opt-in script consumes Codex allowance. It saves synthetic outputs locally; it does not read user messages.
