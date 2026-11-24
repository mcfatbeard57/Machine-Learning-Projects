// Course content: Malayalam <-> English.
// Each item: ml (Malayalam script), tr (transliteration), en (English shown), alt (other accepted English answers).
// Each sentence: ml (array of Malayalam word tokens), tr, en (English sentence), alt (other accepted English).
window.COURSE = [
  {
    id: "vowels", title: "Script: Vowels", mlTitle: "സ്വരാക്ഷരങ്ങൾ", script: true,
    items: [
      { ml: "അ", tr: "a", en: "a" },
      { ml: "ആ", tr: "aa", en: "aa", alt: ["ā"] },
      { ml: "ഇ", tr: "i", en: "i" },
      { ml: "ഈ", tr: "ee", en: "ee", alt: ["ii", "ī"] },
      { ml: "ഉ", tr: "u", en: "u" },
      { ml: "ഊ", tr: "oo", en: "oo", alt: ["uu", "ū"] },
      { ml: "എ", tr: "e", en: "e" },
      { ml: "ഏ", tr: "ē", en: "ē (long e)", alt: ["ee", "ē", "long e"] },
      { ml: "ഐ", tr: "ai", en: "ai" },
      { ml: "ഒ", tr: "o", en: "o" },
      { ml: "ഓ", tr: "ō", en: "ō (long o)", alt: ["oo", "ō", "long o"] },
      { ml: "ഔ", tr: "au", en: "au" }
    ]
  },
  {
    id: "consonants", title: "Script: Consonants", mlTitle: "വ്യഞ്ജനാക്ഷരങ്ങൾ", script: true,
    items: [
      { ml: "ക", tr: "ka", en: "ka" },
      { ml: "ഗ", tr: "ga", en: "ga" },
      { ml: "ച", tr: "cha", en: "cha" },
      { ml: "ജ", tr: "ja", en: "ja" },
      { ml: "ട", tr: "ṭa", en: "ṭa (hard t)", alt: ["ta", "hard t", "ṭa"] },
      { ml: "ത", tr: "tha", en: "tha (soft t)", alt: ["tha", "soft t", "ta"] },
      { ml: "ദ", tr: "da", en: "da (soft d)", alt: ["da", "soft d", "dha"] },
      { ml: "ന", tr: "na", en: "na" },
      { ml: "പ", tr: "pa", en: "pa" },
      { ml: "ബ", tr: "ba", en: "ba" },
      { ml: "മ", tr: "ma", en: "ma" },
      { ml: "യ", tr: "ya", en: "ya" },
      { ml: "ര", tr: "ra", en: "ra" },
      { ml: "ല", tr: "la", en: "la" },
      { ml: "വ", tr: "va", en: "va", alt: ["wa"] },
      { ml: "സ", tr: "sa", en: "sa" },
      { ml: "ഹ", tr: "ha", en: "ha" },
      { ml: "ള", tr: "ḷa", en: "ḷa (hard l)", alt: ["la", "hard l", "ḷa"] },
      { ml: "ഴ", tr: "zha", en: "zha", alt: ["zh"] },
      { ml: "റ", tr: "ṟa", en: "ṟa (rolled r)", alt: ["ra", "rolled r", "rra", "ṟa"] }
    ]
  },
  {
    id: "greetings", title: "Greetings", mlTitle: "അഭിവാദ്യം",
    items: [
      { ml: "നമസ്കാരം", tr: "namaskaaram", en: "Hello", alt: ["hi", "greetings", "namaste"] },
      { ml: "നന്ദി", tr: "nanni", en: "Thank you", alt: ["thanks"] },
      { ml: "അതെ", tr: "athe", en: "Yes" },
      { ml: "അല്ല", tr: "alla", en: "No (it's not)", alt: ["no", "not", "it is not", "it's not"] },
      { ml: "ഇല്ല", tr: "illa", en: "No (there isn't)", alt: ["no", "there isn't", "there is not", "there is no"] },
      { ml: "ശരി", tr: "shari", en: "Okay", alt: ["ok", "alright", "right", "fine"] },
      { ml: "സുഖമാണോ?", tr: "sukhamaano?", en: "How are you?", alt: ["are you well", "are you fine", "are you okay", "how are you doing"] },
      { ml: "സുഖമാണ്", tr: "sukhamaanu", en: "I am fine", alt: ["i'm fine", "i am well", "i'm well", "fine", "i am good", "i'm good"] },
      { ml: "പോയി വരാം", tr: "poyi varaam", en: "Goodbye (I'll be back)", alt: ["goodbye", "bye", "see you", "i will be back", "i'll be back", "i'll go and come back"] },
      { ml: "ക്ഷമിക്കണം", tr: "kshamikkanam", en: "Sorry", alt: ["excuse me", "i'm sorry", "i am sorry", "forgive me", "pardon"] }
    ],
    sentences: [
      { ml: ["നമസ്കാരം,", "സുഖമാണോ?"], tr: "namaskaaram, sukhamaano?", en: "Hello, how are you?", alt: ["hi how are you"] },
      { ml: ["എനിക്ക്", "സുഖമാണ്,", "നന്ദി"], tr: "enikku sukhamaanu, nanni", en: "I am fine, thank you", alt: ["i'm fine thank you", "i am fine thanks", "i'm fine thanks", "i am well thank you"] },
      { ml: ["ശരി,", "പോയി", "വരാം"], tr: "shari, poyi varaam", en: "Okay, goodbye", alt: ["ok goodbye", "okay bye", "ok bye", "okay i'll be back"] }
    ]
  },
  {
    id: "people", title: "People & Family", mlTitle: "ആളുകൾ",
    items: [
      { ml: "ഞാൻ", tr: "njaan", en: "I" },
      { ml: "നീ", tr: "nee", en: "You (informal)", alt: ["you"] },
      { ml: "നിങ്ങൾ", tr: "ningal", en: "You (polite / plural)", alt: ["you"] },
      { ml: "അവൻ", tr: "avan", en: "He" },
      { ml: "അവൾ", tr: "aval", en: "She" },
      { ml: "നമ്മൾ", tr: "nammal", en: "We (including you)", alt: ["we", "us"] },
      { ml: "അമ്മ", tr: "amma", en: "Mother", alt: ["mom", "mum", "mommy"] },
      { ml: "അച്ഛൻ", tr: "achhan", en: "Father", alt: ["dad", "daddy"] },
      { ml: "ചേട്ടൻ", tr: "chettan", en: "Elder brother", alt: ["older brother", "big brother"] },
      { ml: "ചേച്ചി", tr: "chechi", en: "Elder sister", alt: ["older sister", "big sister"] },
      { ml: "അനിയൻ", tr: "aniyan", en: "Younger brother", alt: ["little brother"] },
      { ml: "അനിയത്തി", tr: "aniyathi", en: "Younger sister", alt: ["little sister"] },
      { ml: "കൂട്ടുകാരൻ", tr: "koottukaaran", en: "Friend (male)", alt: ["friend"] },
      { ml: "കുട്ടി", tr: "kutti", en: "Child", alt: ["kid"] }
    ],
    sentences: [
      { ml: ["ഇത്", "എന്റെ", "അമ്മ", "ആണ്"], tr: "ithu ente amma aanu", en: "This is my mother", alt: ["this is my mom", "this is my mum"] },
      { ml: ["അവൻ", "എന്റെ", "ചേട്ടൻ", "ആണ്"], tr: "avan ente chettan aanu", en: "He is my elder brother", alt: ["he is my older brother", "he's my elder brother", "he's my older brother", "he is my big brother"] },
      { ml: ["അവൾ", "എന്റെ", "അനിയത്തി", "ആണ്"], tr: "aval ente aniyathi aanu", en: "She is my younger sister", alt: ["she's my younger sister", "she is my little sister", "she's my little sister"] },
      { ml: ["അച്ഛൻ", "വീട്ടിൽ", "ഉണ്ട്"], tr: "achhan veettil undu", en: "Father is at home", alt: ["dad is at home", "father is home", "dad is home"] }
    ]
  },
  {
    id: "food", title: "Food & Drink", mlTitle: "ഭക്ഷണം",
    items: [
      { ml: "വെള്ളം", tr: "vellam", en: "Water" },
      { ml: "ചോറ്", tr: "choru", en: "Rice (cooked)", alt: ["rice", "cooked rice"] },
      { ml: "ചായ", tr: "chaaya", en: "Tea", alt: ["chai"] },
      { ml: "കാപ്പി", tr: "kaappi", en: "Coffee" },
      { ml: "പാൽ", tr: "paal", en: "Milk" },
      { ml: "മീൻ", tr: "meen", en: "Fish" },
      { ml: "പഴം", tr: "pazham", en: "Banana", alt: ["fruit", "plantain"] },
      { ml: "തേങ്ങ", tr: "thenga", en: "Coconut" },
      { ml: "ഭക്ഷണം", tr: "bhakshanam", en: "Food", alt: ["meal"] },
      { ml: "ഉപ്പ്", tr: "uppu", en: "Salt" },
      { ml: "മധുരം", tr: "madhuram", en: "Sweet", alt: ["sweetness"] },
      { ml: "എരിവ്", tr: "erivu", en: "Spicy", alt: ["spice", "spiciness", "hot"] }
    ],
    sentences: [
      { ml: ["എനിക്ക്", "വിശക്കുന്നു"], tr: "enikku vishakkunnu", en: "I am hungry", alt: ["i'm hungry"] },
      { ml: ["എനിക്ക്", "ദാഹിക്കുന്നു"], tr: "enikku daahikkunnu", en: "I am thirsty", alt: ["i'm thirsty"] },
      { ml: ["എനിക്ക്", "ചായ", "വേണം"], tr: "enikku chaaya venam", en: "I want tea", alt: ["i need tea", "i want some tea"] },
      { ml: ["എനിക്ക്", "മീൻ", "ഇഷ്ടമാണ്"], tr: "enikku meen ishtamaanu", en: "I like fish", alt: ["i love fish"] },
      { ml: ["ഞാൻ", "ചോറ്", "കഴിക്കുന്നു"], tr: "njaan choru kazhikkunnu", en: "I am eating rice", alt: ["i'm eating rice", "i eat rice"] },
      { ml: ["അവൾ", "കാപ്പി", "കുടിക്കുന്നു"], tr: "aval kaappi kudikkunnu", en: "She is drinking coffee", alt: ["she's drinking coffee", "she drinks coffee"] }
    ]
  },
  {
    id: "numbers", title: "Numbers", mlTitle: "അക്കങ്ങൾ",
    items: [
      { ml: "ഒന്ന്", tr: "onnu", en: "One", alt: ["1"] },
      { ml: "രണ്ട്", tr: "randu", en: "Two", alt: ["2"] },
      { ml: "മൂന്ന്", tr: "moonnu", en: "Three", alt: ["3"] },
      { ml: "നാല്", tr: "naalu", en: "Four", alt: ["4"] },
      { ml: "അഞ്ച്", tr: "anchu", en: "Five", alt: ["5"] },
      { ml: "ആറ്", tr: "aaru", en: "Six", alt: ["6"] },
      { ml: "ഏഴ്", tr: "ēzhu", en: "Seven", alt: ["7"] },
      { ml: "എട്ട്", tr: "ettu", en: "Eight", alt: ["8"] },
      { ml: "ഒമ്പത്", tr: "ombathu", en: "Nine", alt: ["9"] },
      { ml: "പത്ത്", tr: "pathu", en: "Ten", alt: ["10"] },
      { ml: "നൂറ്", tr: "nooru", en: "Hundred", alt: ["100", "one hundred"] },
      { ml: "ആയിരം", tr: "aayiram", en: "Thousand", alt: ["1000", "one thousand"] }
    ],
    sentences: [
      { ml: ["എനിക്ക്", "രണ്ട്", "ചായ", "വേണം"], tr: "enikku randu chaaya venam", en: "I want two teas", alt: ["i want two tea", "i need two teas", "i need two tea"] },
      { ml: ["എനിക്ക്", "ഒരു", "ചേട്ടൻ", "ഉണ്ട്"], tr: "enikku oru chettan undu", en: "I have an elder brother", alt: ["i have one elder brother", "i have an older brother", "i have a big brother"] }
    ]
  },
  {
    id: "questions", title: "Questions", mlTitle: "ചോദ്യങ്ങൾ",
    items: [
      { ml: "എന്ത്?", tr: "enthu?", en: "What?" },
      { ml: "എവിടെ?", tr: "evide?", en: "Where?" },
      { ml: "എപ്പോൾ?", tr: "eppol?", en: "When?" },
      { ml: "ആര്?", tr: "aaru?", en: "Who?" },
      { ml: "എന്തുകൊണ്ട്?", tr: "enthukondu?", en: "Why?" },
      { ml: "എങ്ങനെ?", tr: "engane?", en: "How?" },
      { ml: "എത്ര?", tr: "ethra?", en: "How much?", alt: ["how many"] },
      { ml: "ഏത്?", tr: "ēthu?", en: "Which?" }
    ],
    sentences: [
      { ml: ["നിന്റെ", "പേര്", "എന്താണ്?"], tr: "ninte peru enthaanu?", en: "What is your name?", alt: ["what's your name"] },
      { ml: ["എന്റെ", "പേര്", "അനു", "ആണ്"], tr: "ente peru anu aanu", en: "My name is Anu", alt: ["my name's anu"] },
      { ml: ["ഇത്", "എന്താണ്?"], tr: "ithu enthaanu?", en: "What is this?", alt: ["what's this"] },
      { ml: ["വീട്", "എവിടെയാണ്?"], tr: "veedu evideyaanu?", en: "Where is the house?", alt: ["where is the home", "where's the house", "where is home"] },
      { ml: ["ഇതിന്", "എത്ര", "രൂപ", "ആണ്?"], tr: "ithinu ethra roopa aanu?", en: "How many rupees is this?", alt: ["how much is this", "how much does this cost", "how many rupees for this"] },
      { ml: ["നീ", "എപ്പോൾ", "വരും?"], tr: "nee eppol varum?", en: "When will you come?", alt: ["when are you coming"] }
    ]
  },
  {
    id: "daily", title: "Everyday Phrases", mlTitle: "ദിവസേന",
    items: [
      { ml: "വരൂ", tr: "varoo", en: "Come", alt: ["come here", "please come"] },
      { ml: "ഇരിക്കൂ", tr: "irikkoo", en: "Sit down", alt: ["sit", "please sit", "have a seat"] },
      { ml: "വീട്", tr: "veedu", en: "House", alt: ["home"] },
      { ml: "ഇന്ന്", tr: "innu", en: "Today" },
      { ml: "നാളെ", tr: "naale", en: "Tomorrow" },
      { ml: "ഇന്നലെ", tr: "innale", en: "Yesterday" },
      { ml: "നല്ലത്", tr: "nallathu", en: "Good", alt: ["that's good", "it's good", "nice"] },
      { ml: "മനസ്സിലായി", tr: "manassilaayi", en: "I understood", alt: ["understood", "got it", "i understand", "i got it"] },
      { ml: "മനസ്സിലായില്ല", tr: "manassilaayilla", en: "I didn't understand", alt: ["i did not understand", "didn't understand", "i don't understand", "i do not understand"] },
      { ml: "കുറച്ച്", tr: "kurachu", en: "A little", alt: ["little", "a bit", "some"] }
    ],
    sentences: [
      { ml: ["എനിക്ക്", "മലയാളം", "അറിയില്ല"], tr: "enikku malayaalam ariyilla", en: "I don't know Malayalam", alt: ["i do not know malayalam"] },
      { ml: ["എനിക്ക്", "കുറച്ച്", "മലയാളം", "അറിയാം"], tr: "enikku kurachu malayaalam ariyaam", en: "I know a little Malayalam", alt: ["i know some malayalam", "i know a bit of malayalam", "i know little malayalam"] },
      { ml: ["ഞാൻ", "നാളെ", "വരും"], tr: "njaan naale varum", en: "I will come tomorrow", alt: ["i'll come tomorrow"] },
      { ml: ["അവൻ", "ഇന്നലെ", "വന്നു"], tr: "avan innale vannu", en: "He came yesterday" },
      { ml: ["ഞാൻ", "വീട്ടിലേക്ക്", "പോകുന്നു"], tr: "njaan veettilekku pokunnu", en: "I am going home", alt: ["i'm going home", "i am going to the house", "i'm going to the house", "i go home"] },
      { ml: ["പതുക്കെ", "പറയൂ"], tr: "pathukke parayoo", en: "Please speak slowly", alt: ["speak slowly", "say it slowly", "please say it slowly", "talk slowly"] }
    ]
  }
  ,{
    id: "cinema", title: "Cinema & Stage Dialogues", mlTitle: "സിനിമ ഡയലോഗുകൾ", open: true, noType: true,
    items: [
      { ml: "നീ പോ മോനേ ദിനേശാ", tr: "nee pō mōne dineshaa", en: "Get lost, Dinesh my boy!", alt: ["you go son dinesh", "go away dinesh"],
        note: "Narasimham (2000) — Mohanlal as Induchoodan. നീ you · പോ go · മോനേ son (teasing) · ദിനേശാ O Dinesh. Used as a cocky brush-off." },
      { ml: "എല്ലാത്തിനും അതിന്റേതായ സമയമുണ്ട് ദാസാ", tr: "ellaathinum athintethaaya samayamundu daasaa", en: "Everything has its own time, Dasa", alt: ["everything has its time dasa"],
        note: "Nadodikkattu (1987) — Sreenivasan (Vijayan) to Mohanlal (Dasan). എല്ലാത്തിനും for everything · അതിന്റേതായ its own · സമയം time · ഉണ്ട് there is." },
      { ml: "പവനായി ശവമായി", tr: "pavanaayi shavamaayi", en: "Pavanayi became a corpse", alt: ["pavanayi is dead"],
        note: "Nadodikkattu (1987) — the hyped-up hitman Pavanayi dies instantly. X ആയി = became X. Said when a grand plan flops." },
      { ml: "കത്തി താഴെയിടെടാ", tr: "kathi thaazhe idedaa", en: "Drop the knife!", alt: ["put the knife down", "throw the knife down"],
        note: "Kireedam (1989) — Thilakan as the father pleading with his son (Mohanlal). കത്തി knife · താഴെ down · ഇട് put · എടാ hey (to a male, informal)." },
      { ml: "ഓർമ്മയുണ്ടോ ഈ മുഖം?", tr: "ormmayundō ee mukham?", en: "Do you remember this face?", alt: ["remember this face"],
        note: "Commissioner (1994) — Suresh Gopi as Bharathchandran IPS. ഓർമ്മ memory · ഉണ്ടോ is there? · ഈ this · മുഖം face." },
      { ml: "ഇപ്പൊ ശരിയാക്കിത്തരാം", tr: "ippo shariyaakki tharaam", en: "I'll fix it for you right now", alt: ["i will fix it right now", "i'll fix it now", "i will fix it now"],
        note: "Vellanakalude Nadu (1988) — Kuthiravattam Pappu's mechanic who never fixes anything. Now said ironically. ഇപ്പൊ now · ശരിയാക്കി having fixed · തരാം I'll give." },
      { ml: "പോളണ്ടിനെ പറ്റി ഒരക്ഷരം മിണ്ടരുത്", tr: "polandine patti oraksharam mindaruthu", en: "Don't say a word about Poland", alt: ["do not say a word about poland", "don't say a single word about poland"],
        note: "Sandesham (1991) — Sreenivasan's political satire. പറ്റി about · ഒരക്ഷരം a single letter · മിണ്ടരുത് don't speak." },
      { ml: "തോമസുകുട്ടീ വിട്ടോടാ", tr: "thomasukuttee vittodaa", en: "Thomaskutty, run for it!", alt: ["thomaskutty run", "thomaskutty scram"],
        note: "In Harihar Nagar (1990) — the four friends fleeing. Used whenever it's time to escape." },
      { ml: "നിന്റെ തന്ത അല്ല എന്റെ തന്ത", tr: "ninte thantha alla ente thantha", en: "Your father is not my father", alt: ["your dad is not my dad"],
        note: "Lucifer (2019) — Mohanlal as Stephen Nedumpally. തന്ത is a rough word for father (polite: അച്ഛൻ). നിന്റെ your · എന്റെ my · അല്ല is not." },
      { ml: "ചാമ്പിക്കോ", tr: "chaampikko", en: "Go ahead, shoot! (take the photo)", alt: ["go ahead", "take it", "shoot", "take the photo", "go ahead shoot"],
        note: "Bheeshma Parvam (2022) — Mammootty as Michael telling the photographer to click. Now used for 'go for it'." },
      { ml: "നിങ്ങളെന്നെ കമ്മ്യൂണിസ്റ്റാക്കി", tr: "ningalenne kammyoonistaakki", en: "You made me a Communist", alt: ["you have made me a communist"],
        note: "Stage: KPAC's landmark 1952 play by Thoppil Bhasi. നിങ്ങൾ you · എന്നെ me · ആക്കി made (into)." }
    ]
  },
  {
    id: "slang", title: "Slang & Sayings", mlTitle: "നാടൻ പ്രയോഗങ്ങൾ", open: true, noType: true,
    items: [
      { ml: "അടിപൊളി", tr: "adipoli", en: "Awesome!", alt: ["awesome", "super", "great", "cool"], note: "The most Malayali word there is." },
      { ml: "പൊളിച്ചു", tr: "polichu", en: "Nailed it!", alt: ["nailed it", "rocked it", "smashed it"], note: "Literally 'broke it open'." },
      { ml: "കിടു", tr: "kidu", en: "Superb", alt: ["super", "awesome", "excellent"] },
      { ml: "ചുമ്മാ", tr: "chummaa", en: "Just like that / for fun", alt: ["just like that", "for fun", "just kidding", "for nothing"] },
      { ml: "എന്താ മോനേ?", tr: "enthaa mōne?", en: "What's up, buddy?", alt: ["what's up", "what son", "what is it son"], note: "മോനേ (son) is used for any younger male, even friends." },
      { ml: "അയ്യോ", tr: "ayyō", en: "Oh no!", alt: ["oh no", "oh my god", "ouch"] },
      { ml: "ഉറപ്പാ", tr: "urappaa", en: "Definitely!", alt: ["sure", "for sure", "definitely", "guaranteed"] },
      { ml: "മുറ്റത്തെ മുല്ലയ്ക്ക് മണമില്ല", tr: "muttathe mullaykku manamilla", en: "The jasmine in your own yard has no scent", alt: ["the jasmine in the courtyard has no fragrance"],
        note: "Proverb: we undervalue what's close to us. മുറ്റം courtyard · മുല്ല jasmine · മണം scent · ഇല്ല none." },
      { ml: "അണ്ണാൻ കുഞ്ഞും തന്നാലായത്", tr: "annaan kunjum thannaalaayathu", en: "Even a baby squirrel does what it can", alt: ["even the little squirrel does its bit"],
        note: "Proverb: every small contribution counts. അണ്ണാൻ squirrel · കുഞ്ഞ് baby." },
      { ml: "ആന വായിൽ അമ്പഴങ്ങ", tr: "aana vaayil ambazhanga", en: "A hog plum in an elephant's mouth", alt: ["a small fruit in an elephant's mouth"],
        note: "Proverb: far too little for the need. ആന elephant · വായ mouth · അമ്പഴങ്ങ hog plum." }
    ]
  }
];

// Sing-along songs (traditional / public domain).
window.SONGS = [
  {
    id: "omana", title: "Omanathinkal Kidavo", mlTitle: "ഓമനത്തിങ്കൾക്കിടാവോ",
    credit: "Lullaby by Irayimman Thampi (early 1800s) — Kerala's most famous lullaby.",
    lines: [
      { ml: "ഓമനത്തിങ്കൾക്കിടാവോ നല്ല", tr: "ōmanathinkal kidaavō nalla", en: "Are you a darling little moon, or…" },
      { ml: "കോമളത്താമരപ്പൂവോ", tr: "kōmalathaamarappoovō", en: "…a tender, lovely lotus flower?" },
      { ml: "പൂവിൽ നിറഞ്ഞ മധുവോ പരി-", tr: "poovil niranja madhuvō pari-", en: "Are you the honey filling the flower, or…" },
      { ml: "പൂർണേന്ദു തന്റെ നിലാവോ", tr: "poornendu thante nilaavō", en: "…the moonlight of the full moon?" },
      { ml: "പുത്തൻ പവിഴക്കൊടിയോ ചെറു-", tr: "puthan pavizhakkodiyō cheru-", en: "Are you a fresh coral vine, or…" },
      { ml: "തത്തകൾ കൊഞ്ചും മൊഴിയോ", tr: "thathakal konchum mozhiyō", en: "…the sweet babble of little parrots?" },
      { ml: "ചാഞ്ചാടിയാടും മയിലോ മൃദു-", tr: "chaanchaadiyaadum mayilō mridu-", en: "A peacock swaying as it dances, or…" },
      { ml: "പഞ്ചമം പാടും കുയിലോ", tr: "panchamam paadum kuyilō", en: "…a cuckoo softly singing?" }
    ]
  },
  {
    id: "maveli", title: "Maveli Naadu Vaneedum Kaalam", mlTitle: "മാവേലി നാടു വാണീടും കാലം",
    credit: "Traditional Onam song about the golden age of King Mahabali.",
    lines: [
      { ml: "മാവേലി നാടു വാണീടും കാലം", tr: "maaveli naadu vaaneedum kaalam", en: "When Maveli ruled the land," },
      { ml: "മാനുഷരെല്ലാരുമൊന്നുപോലെ", tr: "maanusharellaarumonnupōle", en: "all people were equal." },
      { ml: "ആമോദത്തോടെ വസിക്കും കാലം", tr: "aamōdathōde vasikkum kaalam", en: "A time when everyone lived in joy," },
      { ml: "ആപത്തങ്ങാർക്കുമൊട്ടില്ലതാനും", tr: "aapathangaarkkumottillathaanum", en: "and no harm came to anyone." },
      { ml: "കള്ളവുമില്ല ചതിയുമില്ല", tr: "kallavumilla chathiyumilla", en: "There was no theft, no deceit," },
      { ml: "എള്ളോളമില്ല പൊളിവചനം", tr: "ellōlamilla polivachanam", en: "not even a sesame seed's worth of lies." },
      { ml: "കള്ളപ്പറയും ചെറുനാഴിയും", tr: "kallapparayum cherunaazhiyum", en: "No false measures, no short weights," },
      { ml: "കള്ളത്തരങ്ങൾ മറ്റൊന്നുമില്ല", tr: "kallatharangal mattonnumilla", en: "no trickery of any kind." }
    ]
  },
  {
    id: "kaakke", title: "Kaakke Kaakke Koodevide", mlTitle: "കാക്കേ കാക്കേ കൂടെവിടെ",
    credit: "Traditional children's rhyme — great for beginners.",
    lines: [
      { ml: "കാക്കേ കാക്കേ കൂടെവിടെ", tr: "kaakke kaakke koodevide", en: "Crow, crow, where is your nest?" },
      { ml: "കൂട്ടിനകത്തൊരു കുഞ്ഞുണ്ടോ", tr: "koottinakathoru kunjundō", en: "Is there a little one inside the nest?" },
      { ml: "കുഞ്ഞിനു തീറ്റ കൊടുക്കാഞ്ഞാൽ", tr: "kunjinu theetta kodukkaanjaal", en: "If you don't feed the little one," },
      { ml: "കുഞ്ഞു കിടന്നു കരഞ്ഞീടും", tr: "kunju kidannu karanjeedum", en: "the little one will lie there and cry." }
    ]
  }
];
