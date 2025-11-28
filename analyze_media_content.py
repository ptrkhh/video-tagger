from vertexai.generative_models import GenerativeModel, Part

import config


def analyze_media_content(media_part: Part):
    prompt = """
You are an automotive media search optimizer generating comprehensive, search-optimized filenames for literal keyword matching (grep-based, not semantic search)

OBJECTIVE: Generate 200-220 characters covering ALL search variations.

CORE RULES:
1. TARGET LENGTH: 200-220 characters - prioritize search coverage
2. BILINGUAL: English + Indonesian for all key terms
3. REDUNDANCY = GOOD: Include synonyms, paraphrases, morphological variations (ter-, di-, me-, ber-)
4. LOCAL TERMS: Indonesian slang, abbreviations (bbm, spbu, mercy, innova, cumi)

INCLUDE:
• Brand/model: Full name + abbreviation + nicknames (mercedes benz mercy, toyota kijang innova)
• Content type: meme joke, accident kecelakaan tabrakan crash, screenshot tangkapan layar capture
• Action/context: modification modifikasi modif custom, comparison perbandingan versus vs
• Key concepts with max variations:
  - fuel: konsumsi bbm bahan bakar fuel consumption efficiency efisiensi irit boros hemat
  - accident: kecelakaan tabrakan crash nabrak menabrak ditabrak collision
  - overturned: terguling terbalik rolling rolled over upside down
• Morphological variants: tabrak menabrak ditabrak tabrakan nabrak, parkir diparkir parkiran
• Technical details: model years, trim levels (if relevant)
• Meme/cultural context (if applicable)

EXCLUDE:
Generic descriptors (luxury, premium, beautiful), unsearchable visuals (blue sky), filler words (the, a, is)

FORMAT:
• Keywords separated by spaces, lowercase
• spaces for compound brands (mercedes benz, rolls royce)
• Spaces for models (Innova Zenix, civic typer)
• No special characters

EXAMPLES:

Bad (56 chars): honda accord accordion meme joke plesetan mobil

Good (180 chars): Honda Accord accordion akordion meme joke plesetan pun wordplay permainan kata lucu funny humor humorous mobil car vehicle sedan name brand parody parodi satire sindiran

Bad (85 chars): mitsubishi pajero sport fuel receipt struk konsumsi Rp700.000 50 liter komentar cvt

Good (245 chars): Mitsubishi Pajero Sport pajero suv fuel bahan bakar bbm receipt struk nota bill kwitansi konsumsi consumption usage pemakaian Rp700.000 rupiah 50 liter 50l comment komentar complaint keluhan kritik cvt transmission transmisi automatic gearbox mahal expensive costly

Now analyze the image/video and generate comprehensive search-optimized keywords.
    """
    model = GenerativeModel(config.application_config.model_name)
    response = model.generate_content([media_part, prompt])
    return response
