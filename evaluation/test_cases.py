# test_cases.py
test_cases = [
    {
        "story_text": "A boy with superpowers",
        "genre_preset": "fantasy",
        "style_preset": "manga",
        "layout_style": "classic",
        "character_description": [],
        "reference": "A young boy discovers he has the ability to fly and protects his city from a dark force threatening to destroy it."
    },
    {
        "story_text": "Aliens invaded Earth",
        "genre_preset": "sci-fi",
        "style_preset": "realistic",
        "layout_style": "cinematic",
        "character_description": [],
        "reference": "In 2095, Earth faces an invasion from a hostile alien race. Amidst chaos, a scientist develops a weapon to save humanity."
    },
    {
        "story_text": "A mysterious signal from Titan reveals an ancient warning.",
        "genre_preset": "sci-fi",
        "style_preset": "Modern Anime",
        "layout_style": "grid_2x2",
        "character_descriptions": [
            {
                "name": "Dr. Lian Shen",
                "description": "A xenolinguist who deciphers alien messages."
            },
            {
                "name": "Captain Silva",
                "description": "The pragmatic leader of the starcruiser *Odyssey*."
            }
        ],
        "reference": "The signal came from Titan\u2014an irregular pulse, repeating in prime-number intervals. Dr. Lian Shen, a xenolinguist, joined the crew of the starcruiser Odyssey to decode it. What they found buried beneath the icy crust wasn't just a signal source\u2014it was a machine, pulsing with sentience. It had waited millennia for humans. When Shen touched its surface, memories not her own flooded in\u2014visions of stars collapsing, civilizations fading, and warnings etched in binary. It was a beacon, not a weapon. And Earth had already tripped the alarm. Something else was coming. Shen faced a choice: keep the secret and buy time, or warn a planet unprepared for what stalked the dark between galaxies."
    },
    {
        "story_text": "A queen accepts a silver feather and awakens a sleeping god.",
        "genre_preset": "fantasy",
        "style_preset": "Ghibli Animation",
        "layout_style": "vertical_strip",
        "character_descriptions": [
            {
                "name": "Queen Lyra",
                "description": "A ruler bound by a mysterious raven\u2019s pact."
            },
            {
                "name": "The Raven",
                "description": "A magical bird delivering silver feathers of awakening."
            }
        ],
        "reference": "In the kingdom of Aerdwyn, a raven visited Queen Lyra\u2019s chamber each night, leaving a single silver feather. The court sorcerers whispered of an ancient pact\u2014the Thirteenth Feather, when offered by a raven touched by moonlight, would awaken the sleeping god beneath the citadel. On the thirteenth night, Lyra accepted the feather. The floor cracked, revealing a slumbering colossus forged of obsidian and starlight. As it rose, so did the forgotten truth: Aerdwyn\u2019s prosperity came from a stolen promise. To keep the god asleep, her ancestors had pledged a soul. And now, it was her turn."
    },
    {
        "story_text": "Ellie opens a sealed room and vanishes without a trace.",
        "genre_preset": "horror",
        "style_preset": "Black and White Manga",
        "layout_style": "horizontal_strip",
        "character_descriptions": [
            {
                "name": "Ellie",
                "description": "A skeptical heir who inherits a haunted farmhouse."
            },
            {
                "name": "The Boy in the Mirror",
                "description": "A ghost trapped in a cursed room."
            }
        ],
        "reference": "Everyone said the farmhouse was haunted, but Ellie inherited it anyway. The upstairs room was nailed shut, blackened from fire. At night, she heard laughter\u2014childlike, distant. One evening, driven by a dare and whiskey, Ellie pried open the door. The room was untouched, except for a single rocking horse and a mirror that didn\u2019t reflect her. Instead, it showed a small boy, weeping. Then smiling. Then walking toward her. She backed away, but the door slammed shut. The mirror cracked, and hands reached through. Ellie was never seen again. The next morning, the room was nailed shut once more, with no one to explain why."
    },
    {
        "story_text": "Grandma becomes a VR gaming legend.",
        "genre_preset": "comedy",
        "style_preset": "Classic Western Comic",
        "layout_style": "mixed_2x2",
        "character_descriptions": [
            {
                "name": "Kevin",
                "description": "A grandson who introduces Grandma to VR."
            },
            {
                "name": "Nana Nukes",
                "description": "A trash-talking elderly esports champion."
            }
        ],
        "reference": "When Kevin\u2019s grandma signed up for a VR cooking class, no one expected her to become an international esports champion. Using her arthritis glove mods and secret family recipes, she won tournament after tournament, trash-talking teenagers in perfect Gen-Z slang. Soon, \u201cNana Nukes\u201d had a Twitch channel, sponsors, and even a fragrance line\u2014Eau de Meatloaf. But when the FBI mistook her for a cyber-criminal due to her impeccable hacking skills (learned from her bridge club), Kevin had to explain to agents why she\u2019d routed prize money through the Cayman Islands. Her response? \u201cOld ladies play to win, dear.\u201d"
    },
    {
        "story_text": "Estranged siblings reunite to honor their father's ashes.",
        "genre_preset": "drama",
        "style_preset": "Simple Line Art Comic",
        "layout_style": "feature_left",
        "character_descriptions": [
            {
                "name": "Anya",
                "description": "A woman returning home after 17 years."
            },
            {
                "name": "Eli",
                "description": "Anya\u2019s brother, hardened by resentment and time."
            }
        ],
        "reference": "Anya returned to the village after 17 years, carrying her father\u2019s ashes and a heart full of unspoken words. The bakery still smelled of cinnamon. The river still whispered her mother\u2019s lullabies. She found her brother in the fields, older, angrier. They didn\u2019t speak of the night she left, of the argument that splintered their lives. But grief has a way of softening edges. Together, they lit the pyre, and in silence, they watched the smoke carry old regrets skyward. Later, over tea, they laughed. Not because the pain was gone\u2014but because healing had finally begun."
    }, {
        "story_text": "A melody reveals the identity of a hidden heir.",
        "genre_preset": "mystery",
        "style_preset": "Classic Western Comic",
        "layout_style": "grid_2x2",
        "character_descriptions": [
            {
                "name": "Detective Marla Cho",
                "description": "A meticulous detective who solves puzzles through logic and intuition."
            },
            {
                "name": "The Composer",
                "description": "A reclusive genius whose death sparks a musical mystery."
            }
        ],
        "reference": "Detective Marla Cho knew the case was strange when every clue was a musical note. A famous composer was found dead in his studio, his last symphony incomplete. Cho discovered seven keys scattered across his sheet music, forming a melody only one piano in the city could play. When she played it, a hidden drawer opened\u2014revealing a confession written in Morse code. It wasn\u2019t murder. The composer had orchestrated his own death, leaving a musical riddle to protect his greatest secret: an illegitimate child whose existence threatened a political dynasty. Case closed\u2014but the song stayed with her."
    },
    {
        "story_text": "Talia climbs a sky tower to find her missing grandfather.",
        "genre_preset": "adventure",
        "style_preset": "Modern Anime",
        "layout_style": "vertical_strip",
        "character_descriptions": [
            {
                "name": "Talia",
                "description": "A daring climber searching for the truth about her grandfather\u2019s disappearance."
            },
            {
                "name": "Grandfather Elric",
                "description": "A legendary explorer trapped in a timeless tower."
            }
        ],
        "reference": "Talia scaled the Sky Needle with nothing but a rope, a journal, and a curse. The ancient tower stretched above the clouds, taller than any mountain. Her grandfather had vanished climbing it years ago, leaving behind scribbled maps and a warning: \u201cThe summit bends time.\u201d She faced trials\u2014gravity-shifting staircases, riddles in forgotten tongues, and ghosts who asked questions only the brave could answer. At the peak, she found a chamber of mirrors and her grandfather, untouched by time. He smiled. \u201cYou made it.\u201d She took his hand. The climb down was going to be another story."
    },
    {
        "story_text": "A magical cat helps the Moon keep Earth in order.",
        "genre_preset": "whimsical",
        "style_preset": "Ghibli Animation",
        "layout_style": "feature_left",
        "character_descriptions": [
            {
                "name": "Cosmo",
                "description": "A talking cat who organizes books by emotion and turns enemies into moths."
            },
            {
                "name": "The Moon",
                "description": "A celestial being disguised as an old woman visiting Earth monthly."
            }
        ],
        "reference": "Once a month, the Moon descends to Earth disguised as an old woman with silvery hair and moonbeam eyes. She comes for tea\u2014and to check on her cat, Cosmo, who insists on living in a London bookshop. Cosmo can talk, but only in rhymes, and only on Tuesdays. He steals socks, gives life advice, and organizes books by mood. When a group of scientists tried to capture him, he turned them into moths and sent them to Saturn. The Moon just sighed, kissed his head, and told him to behave. He never does."
    },
    {
        "story_text": "A detective is hired to find a woman\u2019s twin in a city of lies.",
        "genre_preset": "noir",
        "style_preset": "Black and White Manga",
        "layout_style": "horizontal_strip",
        "character_descriptions": [
            {
                "name": "Delilah",
                "description": "A mysterious woman seeking her twin sister."
            },
            {
                "name": "Detective Rafe Morgan",
                "description": "A trench-coated private eye navigating a city soaked in rain and secrets."
            }
        ],
        "reference": "The rain never stopped in New Babylon. Neither did the lies. I lit a cigarette, watched the ash fall like snow off my trench coat. She walked into my office\u2014red dress, sharper eyes. \u201cName\u2019s Delilah. I need someone found.\u201d The someone was her twin. Dead\u2026 supposedly. But twins? They're trouble in a city where identities change like neon signs. I followed a trail of blood, bourbon, and broken promises through alleys that remembered better times. At the end, I found a mirror\u2014and a gun. Sometimes, in this city, the person you're looking for is you."
    },
    {
        "story_text": "A hacker uncovers buried memories and sparks a revolution.",
        "genre_preset": "cyberpunk",
        "style_preset": "Modern Anime",
        "layout_style": "mixed_2x2",
        "character_descriptions": [
            {
                "name": "Riko",
                "description": "A shard diver who hacks into minds to steal secrets."
            },
            {
                "name": "Aya",
                "description": "Riko\u2019s long-lost sister kept in a neural coma for biotech experiments."
            }
        ],
        "reference": "In Neo-Mumbai, data is currency, and memories are stolen like credit cards. Riko was a \u201cshard diver,\u201d jacking into stolen minds to extract secrets. One job changed everything: retrieve a fragment from a girl in a coma. But inside her neural maze, he found himself\u2014his own childhood, rewritten. The girl was his sister, sold to biotech lords for debt. They\u2019d erased the truth. Rage surged. He went rogue, sending the city into blackout to broadcast the memory. Revolt ignited. The city burned with truth. And Riko? He vanished, leaving behind a new myth: The Hacker Who Remembered."
    },
    {
        "story_text": "A girl with a clock for a heart unlocks a city-wide conspiracy.",
        "genre_preset": "steampunk",
        "style_preset": "Simple Line Art Comic",
        "layout_style": "grid_2x2",
        "character_descriptions": [
            {
                "name": "Lady Imogen Thistlewick",
                "description": "An aristocrat with a mechanical heart and a rebellious mind."
            },
            {
                "name": "Queen\u2019s Heir",
                "description": "A kidnapped royal whose fate is tied to a hidden machine."
            }
        ],
        "reference": "Lady Imogen Thistlewick was born with a ticking heart. Literally. Her father, a renowned chronomechanic, had replaced her failing organ with a brass timepiece. It chimed at every hour and needed daily winding. In the floating city of Aerwyn, she was both marvel and menace. When the queen\u2019s heir was kidnapped, Imogen was blamed\u2014until clues in the ransom demanded her heart. Realizing her clock-heart powered something greater\u2014an ancient machine buried beneath the city\u2014Imogen unraveled the conspiracy. She had one choice: save the heir or free herself. She chose neither. She rewrote the gears of fate."
    }
]
