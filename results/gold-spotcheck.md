# Gold spot-check sample (72 items)

Stratified: all 4 Cantonese items, 3 per intent label, 3 per translate direction, rest random (seed 20261101).

## instruct (18)

### inst-010 `yue`
Prompt: 用廣東話口吻寫一句話形容今日好熱,要包含「好熱」同「冷氣」兩個詞。
Reference: {"must_include": ["好熱", "冷氣"], "max_sentences": 1}

### inst-043 `yue`
Prompt: 用廣東話寫一句話講今日好塞車,要包含「塞車」同「返工」。
Reference: {"must_include": ["塞車", "返工"], "max_sentences": 1}

### inst-044 `yue`
Prompt: 用廣東話寫一句鼓勵朋友嘅話,唔可以用「加油」,要包含「努力」。
Reference: {"must_include": ["努力"], "must_not_include": ["加油"], "max_sentences": 1}

### inst-071 `yue`
Prompt: 用廣東話寫一句話形容雲吞麵好食,要包含「雲吞麵」同「好食」。
Reference: {"must_include": ["雲吞麵", "好食"], "max_sentences": 1}

### inst-013 `en`
Prompt: Write a one-line weather update for Johor Bahru that starts with the word 'Today'. Keep it under 20 words.
Reference: {"starts_with": "Today", "max_words": 19}

### inst-016 `en`
Prompt: Explain in one English sentence why the MRT is useful. Include the word 'commute' and do not use the word 'train'.
Reference: {"must_include": ["commute"], "must_not_include": ["train"], "max_sentences": 1}

### inst-054 `en`
Prompt: Describe your favourite Malaysian dish in one English sentence without using the word 'delicious'. You must include the word 'taste'.
Reference: {"must_include": ["taste"], "must_not_include": ["delicious"], "max_sentences": 1}

### inst-008 `en,ms`
Prompt: Write a polite refusal to a meeting invite, mixing English and Bahasa Malaysia. It must contain 'maaf' and 'terima kasih' and use at most 40 words.
Reference: {"must_include": ["maaf", "terima kasih"], "max_words": 40}

### inst-006 `ms,en`
Prompt: Write a greeting that starts with 'Selamat pagi' and mentions the word 'meeting'. Use at most 20 words.
Reference: {"starts_with": "Selamat pagi", "must_include": ["meeting"], "max_words": 20}

### inst-007 `en,ms`
Prompt: Explain what the Malaysian slang 'lepak' means in no more than 25 words. Do not use the word 'relax'.
Reference: {"max_words": 25, "must_not_include": ["relax"]}

### inst-030 `ms`
Prompt: Tulis tagline pusat tuisyen dalam 10 patah perkataan atau kurang. Mesti ada perkataan 'cemerlang' dan tidak boleh ada perkataan 'murah'.
Reference: {"must_include": ["cemerlang"], "must_not_include": ["murah"], "max_words": 10}

### inst-037 `zh`
Prompt: 用中文写一句关于爱护环境的话,不超过25个字,不能用'污染',必须包含'地球'。
Reference: {"must_include": ["地球"], "must_not_include": ["污染"], "max_words": 25}

### inst-023 `ms`
Prompt: Tulis satu peringatan mesra dalam Bahasa Malaysia supaya membayar bil elektrik. Mesti ada perkataan 'bil' dan tidak lebih 30 patah perkataan.
Reference: {"must_include": ["bil"], "max_words": 30}

### inst-009 `ms`
Prompt: Tulis tagline kedai kopi dalam 8 patah perkataan atau kurang. Mesti ada perkataan 'kopi'.
Reference: {"must_include": ["kopi"], "max_words": 8}

### inst-011 `en`
Prompt: Write one sentence in English about durians. It must contain the word 'king'.
Reference: {"must_include": ["king"], "max_sentences": 1}

### inst-068 `en,ms`
Prompt: Write a one-sentence product review in English for a rice cooker. Include 'beras' and do not use the word 'good'.
Reference: {"must_include": ["beras"], "must_not_include": ["good"], "max_sentences": 1}

### inst-067 `zh`
Prompt: 用中文写两句关于槟城旅游的话,开头必须是'槟城',并包含'美食'。
Reference: {"starts_with": "槟城", "must_include": ["美食"], "max_sentences": 2}

### inst-057 `ms`
Prompt: Tulis satu ayat dalam Bahasa Malaysia tentang sukan badminton. Mesti ada perkataan 'raket' dan jangan ada perkataan 'bola'.
Reference: {"must_include": ["raket"], "must_not_include": ["bola"], "max_sentences": 1}

## intent (18)

### intent-026 `en,ms`
Prompt: The toilet here kotor gila, no tissue, no soap. How to use?!
Reference: complaint

### intent-027 `zh`
Prompt: 邻居每天晚上装修到半夜,实在太过分了!
Reference: complaint

### intent-020 `en,ms`
Prompt: Waiter forgot our order, dah tunggu 45 minit. Service teruk betul.
Reference: complaint

### intent-005 `en,ms,zh`
Prompt: 你们几点关门啊? Got parking tak?
Reference: inquiry

### intent-009 `en`
Prompt: How much is the delivery fee to Subang Jaya ah?
Reference: inquiry

### intent-033 `en`
Prompt: Do you provide delivery to Sabah and Sarawak?
Reference: inquiry

### intent-003 `en,ms`
Prompt: Wah the staff here very friendly, terbaik!
Reference: praise

### intent-041 `en,ms`
Prompt: Five stars! Bilik bersih, staff friendly, location pun best.
Reference: praise

### intent-050 `en,ms`
Prompt: App senang guna, payment smooth je. Good job developers!
Reference: praise

### intent-055 `en`
Prompt: Please extend my checkout to 2pm if possible.
Reference: request

### intent-054 `zh`
Prompt: 麻烦帮我拿一份菜单,谢谢!
Reference: request

### intent-008 `en`
Prompt: Please reset my password, I can't log in.
Reference: request

### intent-068 `en,ms`
Prompt: Okay can, I update you later ya.
Reference: other

### intent-011 `en`
Prompt: Okay noted, thanks.
Reference: other

### intent-063 `en`
Prompt: Haha okay lor, see you tomorrow.
Reference: other

### intent-057 `en`
Prompt: Kindly cancel my appointment this Friday and reschedule to next week.
Reference: request

### intent-065 `ms`
Prompt: Hari ni cuaca panas gila kat luar.
Reference: other

### intent-072 `en,ms`
Prompt: Alamak I forgot to bring my wallet lah.
Reference: other

## normalize (18)

### norm-014 `en,ms,zh`
Prompt: 他说 tomorrow 要 cuti, so I need to cover his shift.
Reference: He said he's taking leave tomorrow, so I need to cover his shift.

### norm-043 `ms,en`
Prompt: Budak-budak sekarang manja sangat, sikit-sikit complain kat parents.
Reference: Kids nowadays are so spoiled. They complain to their parents over the smallest things.

### norm-032 `en,ms`
Prompt: That lecturer garang gila, last time I lewat five minutes kena marah.
Reference: That lecturer is really fierce. Last time I was five minutes late and got scolded.

### norm-024 `en,ms`
Prompt: Eh you heard or not? Ali kena promoted, now he big shot already.
Reference: Hey, did you hear? Ali got promoted, and now he's a big shot.

### norm-040 `zh`
Prompt: 你的华语讲得很好咧,在哪里学的?
Reference: You speak Mandarin very well. Where did you learn it?

### norm-042 `en,ms`
Prompt: That shop tipu one, cakap original but actually fake goods je.
Reference: That shop is dishonest. They claim the goods are original, but they're actually fake.

### norm-004 `en,ms`
Prompt: Wah, today jam teruk gila, I reach office pun lambat.
Reference: Wow, the traffic was terrible today, and I was late to the office.

### norm-021 `en,ms`
Prompt: Dia cakap dia busy, tapi I nampak dia lepak kat Starbucks je.
Reference: He said he's busy, but I saw him just hanging out at Starbucks.

### norm-031 `zh`
Prompt: 今晚我不能去,你跟他们讲一声,下次我请喝茶。
Reference: I can't go tonight. Please tell them for me, and I'll treat everyone to drinks next time.

### norm-053 `en,ms`
Prompt: This kopi o here kaw gila, one sip terus awake already.
Reference: The black coffee here is incredibly strong. One sip and I'm wide awake.

### norm-039 `ms,en`
Prompt: Malam ni ada bola, Jom tengok kat mamak, I belanja teh o ais.
Reference: There's football tonight. Let's watch it at the mamak. I'll treat you to iced tea.

### norm-044 `zh`
Prompt: 我妈煮的咖喱鸡最好吃,外面卖的根本不能比。
Reference: My mum's curry chicken is the most delicious. What's sold outside can't compare at all.

### norm-016 `en,zh`
Prompt: Tomorrow I got exam, tonight must chiong already, cannot sleep early.
Reference: I have an exam tomorrow, so I have to study hard tonight and can't sleep early.

### norm-030 `ms,en`
Prompt: Hujan lebat sangat tadi, my shoes basah kuyup, sejuk gila now.
Reference: It rained very heavily just now. My shoes are soaked through, and I'm freezing now.

### norm-056 `ms,en`
Prompt: Makcik tu baik hati, selalu bagi extra kuah without charge.
Reference: That aunty is kind-hearted. She always gives extra gravy without charging.

### norm-027 `zh,en`
Prompt: 我跟你讲,这个地方很难找,你最好用Waze,不然confirm迷路。
Reference: Let me tell you, this place is hard to find. You'd better use Waze, or you'll definitely get lost.

### norm-034 `en,ms`
Prompt: Aiyo this queue panjang gila, wait already half hour still not my turn.
Reference: Oh no, this queue is incredibly long. I've waited half an hour and it's still not my turn.

### norm-069 `ms,en`
Prompt: Cuti sekolah next week, mana-mana pun jam, better stay home je.
Reference: It's the school holidays next week. Everywhere will be jammed, so it's better to just stay home.

## translate (18)

### trans-017 `ms,en`
Prompt: Translate into English: Pihak sekolah menganjurkan gotong-royong hujung minggu ini.
Reference: The school is organizing a gotong-royong this weekend.

### trans-001 `ms,en`
Prompt: Translate into English: Boleh tolong hantar barang ni ke pejabat saya sebelum pukul 5?
Reference: Can you please deliver this item to my office before 5 o'clock?

### trans-015 `ms,en`
Prompt: Translate into English: Kuih tradisional ini dibuat segar setiap pagi.
Reference: These traditional kuih are made fresh every morning.

### trans-026 `en,ms`
Prompt: Translate into Bahasa Malaysia: The baby is sleeping, please be quiet.
Reference: Bayi sedang tidur, tolong senyap.

### trans-021 `en,ms`
Prompt: Translate into Bahasa Malaysia: The train will arrive in ten minutes.
Reference: Keretapi akan tiba dalam masa sepuluh minit.

### trans-024 `en,ms`
Prompt: Translate into Bahasa Malaysia: Our house is near the primary school.
Reference: Rumah kami berhampiran dengan sekolah rendah.

### trans-039 `zh,en`
Prompt: Translate into English: 火车误点了,大概要等半个小时。
Reference: The train is delayed. We'll probably have to wait half an hour.

### trans-036 `zh,en`
Prompt: Translate into English: 我们下个星期去马六甲一日游。
Reference: We're going on a day trip to Malacca next week.

### trans-031 `zh,en`
Prompt: Translate into English: 这本书很有意思,我一口气读完了。
Reference: This book is very interesting. I finished it in one sitting.

### trans-048 `en,zh`
Prompt: Translate into Mandarin (Simplified): She is learning to play the piano.
Reference: 她正在学弹钢琴。

### trans-052 `en,zh`
Prompt: Translate into Mandarin (Simplified): This medicine must be taken after meals.
Reference: 这个药必须饭后吃。

### trans-053 `en,zh`
Prompt: Translate into Mandarin (Simplified): Congratulations on your promotion!
Reference: 恭喜你升职!

### trans-054 `ms,zh`
Prompt: Translate into Mandarin (Simplified): Selamat pagi, apa khabar hari ini?
Reference: 早安,你今天好吗?

### trans-059 `ms,zh`
Prompt: Translate into Mandarin (Simplified): Adik saya belajar di universiti.
Reference: 我弟弟在大学读书。

### trans-055 `ms,zh`
Prompt: Translate into Mandarin (Simplified): Tolong beri saya segelas air.
Reference: 请给我一杯水。

### trans-074 `zh,ms`
Prompt: Translate into Bahasa Malaysia: 请帮我开门。
Reference: Tolong bukakan pintu untuk saya.

### trans-072 `zh,ms`
Prompt: Translate into Bahasa Malaysia: 他每天坐巴士上学。
Reference: Dia naik bas ke sekolah setiap hari.

### trans-071 `zh,ms`
Prompt: Translate into Bahasa Malaysia: 医院离这里很远吗?
Reference: Hospital jauh tak dari sini?
