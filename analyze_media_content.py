import time
from pathlib import Path

from google.genai.types import Part, GenerateContentConfig

import config
from get_mime_type import get_mime_type


def analyze_media_content(file_path: Path):
    system_instruction = """
ROLE: You are an automated file archivist for an automotive media library.

OBJECTIVE: Generate a single string of space-separated keywords to be used as a filename. You MUST fill the filename buffer (target: 230-254 characters) with the most likely search terms.

CRITICAL CONSTRAINTS:

NO CONVERSATION: Do not write "Here are the keywords." Do not use "sure." Do not use markdown code blocks. Start directly with the first keyword. Any extra text will break the script.

TRANSCRIPTION:
- OCR: If the image/video contains visible text (titles, subtitles, memes, stickers), extract key terms, normalize them, and add related keywords. Example: "CIVIC TURBO" becomes "civic turbo" + "honda fk8 vtec" + related terms.
- AUDIO: If the video contains speech, dialogue, narration, or commentary, transcribe key phrases, topics discussed, and important verbal content. Include both English and Indonesian terms as spoken.

OUTPUT FORMAT: Lowercase, space-separated only. NO punctuation, NO file extensions.

LENGTH: Strictly 230-254 characters.

CRITICAL "GREP" RULES:

Substring Exclusion: Strictly check for redundancy. If a word is a substring of a longer word, omit the shorter word.
  - If you include "kecelakaan", DO NOT include "celaka"
  - If you include "racing", DO NOT include "race"
  - If you include "automotive", DO NOT include "auto"

Synonym Stacking: Include distinct synonyms (English, Indonesian, Slang) to maximize search hits. Use context-adaptive language distribution: technical/brand terms in English, actions/descriptions in both languages, slang/local culture in Indonesian.
  - good: "crash nabrak collision"
  - good: "boros wasteful pemborosan"

Priority Sorting: Most important keywords (Brand, Model, Main Event) must come first. Lower priority descriptors go last.

CONTENT PRIORITY:
1. Identity: Brand, Model, Chassis Code (e.g., w204, g20), common nicknames (e.g., mobcin, mercy)
2. Action/Genre: Review, crash, drag race, meme, funny
3. Visible Text/Title: Normalized key terms from text + related keywords
4. Audio Transcription: Key phrases, topics, and verbal content from speech/narration
5. Distinct Synonyms: (e.g., "boros" + "wasteful", "kencang" + "fast")
6. Context: Location (if relevant), specific modification parts (e.g., turbo, spoiler)

EXAMPLES (Follow this density):

Input: A dramatic nighttime thumbnail showing a black Honda Civic Turbo FK8 with lowered stance and aftermarket wheels positioned aggressively next to a red Mitsubishi Xpander on an empty urban street with city lights blurred in the background. Large bold text overlay reads "CIVIC TURBO LAWAN XPENDER!!" in yellow and red colors. The scene suggests illegal street racing with both vehicles appearing ready to launch, motion blur effects added for dramatic effect. The Civic has a visible front lip spoiler and the Xpander looks stock. Typical clickbait YouTube thumbnail style with high contrast and saturated colors. Urban asphalt road, nighttime racing atmosphere, reckless driving vibes implied.
Output: honda civic turbo fk8 vs mitsubishi xpander cross drag race adu mekanik lawan rivalry fwd battle acceleration kencang fast speed tuning modifikasi mpv sedan hatchback jdm funny judul clickbait thumbnail text viral trending youtube indonesia

Input: An action shot of a white Suzuki Jimny JB74 with lifted suspension and aggressive all-terrain tires, partially stuck in deep brown mud with mud splattered all over the body panels and windows. A prominent "4x4 Life" sticker is visible on the rear quarter panel. The scene is set in a forest trail with dense green vegetation in the background. The front wheels are spinning and throwing mud, suggesting active recovery attempt. Roof rack with auxiliary lights mounted on top. The vehicle appears well-used with dirt accumulated on the undercarriage. Daytime outdoor lighting, adventure/offroad photography style. ARB bumper visible, recovery gear including a shovel strapped to the side. Enthusiast-grade modification level, not extreme but purposeful for offroading.
Output: suzuki jimny jb74 katana sierra 4x4 life sticker decal offroad lumpur mudding stuck kepater recovery winch arb forest hutan adventure camping overland mini jeep kei car legendary ladder frame solid axle suspension lift kit modification accessories

Input: A relatable automotive meme image showing a skeleton sitting in a chair in a dusty garage with a project car visible in the background on jack stands covered in dust and cobwebs. The car appears to be a partially disassembled Honda or Toyota with the hood open and wheels removed. White text overlay reads "Me waiting for parts" in impact font style. The scene conveys the frustration of waiting weeks or months for replacement parts to arrive. Dim garage lighting, cluttered workbench with tools in the background. The skeleton suggests an exaggerated, humorous take on how long shipping takes. Typical car enthusiast meme format shared on social media. The project car looks like it's been sitting for months, creating a very relatable scenario for anyone doing automotive builds or restorations.
Output: me waiting for parts text caption meme funny relatable sparepart onderdil lama shipping delay project car builds unfinished jackstand bengkel garage mechanic pain suffering patience import customs bea cukai tax mahal expensive hobby automotive enthusiast struggle

Input: A dashcam video screenshot captured during daytime showing a silver Toyota Avanza Veloz losing control and colliding with a concrete highway barrier on what appears to be an Indonesian toll road. The timestamp shows it's around 2:30 PM. The impact has just occurred with visible front-end damage to the Avanza, the hood crumpled and airbags deployed. Debris scattered on the road surface. The barrier has visible impact marks. Traffic in adjacent lanes slowing down, other vehicles visible in frame. The dashcam angle suggests the recording vehicle was 2-3 car lengths behind. Weather appears clear and dry, so the crash likely due to driver error or sudden maneuver. The Avanza appears to be a family MPV, likely 2015-2019 generation. Typical Indonesian traffic accident documentation footage that would be used for insurance claims or viral social media sharing.
Output: toyota avanza veloz g15 crash kecelakaan nabrak tabrakan accident barrier pembatas jalan highway tol dashcam footage collision impact damage rusak penyok dent airbag deployed safety injured terluka traffic lalulintas insurance asuransi mpv family minivan indonesia jakarta

Input: A professional photo of a brand new deep crystal blue mica Mazda 3 sedan (BP generation, 2019-2023 body style) parked in a residential driveway during golden hour with soft sunlight highlighting the Kodo design language curves and character lines. The car appears to be a higher trim level with 18-inch alloy wheels and LED headlights visible. Bold yellow text overlay reads "REVIEW" in the upper right corner, suggesting this is a YouTube video thumbnail or automotive review content. The car is positioned at a 3/4 front angle showing off the elegant front grille and sleek profile. Background shows a modern house with well-maintained landscaping. The vehicle looks pristine and freshly washed, typical of press photos or first impression review content. The composition and lighting suggest professional automotive photography or high-quality content creator work. The scene has a premium, aspirational feel targeting potential buyers interested in the compact sedan segment.
Output: mazda mazda3 bp skyactiv kodo design review ulasan first impression walkaround exterior interior cabin dashboard digital display touchscreen infotainment sedan japanese jdm elegant classy mewah premium comfortable nyaman efficient irit fuel consumption bensin technology modern family keluarga daily driver harian

Input: A detailed top-down photo of a heavily modified engine bay featuring a large Garrett GT3076R turbocharger prominently mounted with custom stainless steel piping running throughout the compartment. The engine appears to be a Honda K-series or B-series with a polished aluminum intake manifold. Bright red high-temperature silicone hoses connect to a front-mount intercooler setup. The turbo is positioned on a custom fabricated manifold with visible wastegate actuator. Oil feed and return lines are braided stainless steel. The bay is meticulously clean with polished and powder-coated components. Visible boost gauge sensor tapped into the intake piping. Custom heat shielding wrapped around the downpipe. The photo is taken with good workshop lighting showing the craftsmanship of the installation. This represents a professional or high-level enthusiast build, likely Stage 2 or Stage 3 power level. Tool marks and fresh welds suggest recent installation. The setup targets serious performance gains, probably 300-400+ horsepower.
Output: engine mesin bay compartment turbo turbocharger turbocharged forced induction boost pressure psi wastegate intercooler piping intake manifold header exhaust knalpot downpipe installation pasang mounting bracket fabrication custom modification tuning performance performa power hp horsepower torque dyno stage build project bengkel garage workshop mechanical mekanik

Input: A wide-angle golden hour photo of a weekend car meet at a large urban parking lot with approximately 30-40 modified Japanese domestic market vehicles parked in organized rows. In the foreground, a slammed purple Nissan Silvia S15 on deep-dish Work Meister wheels sits nearly scraping the ground, positioned next to a stanced white Toyota AE86 with panda paint scheme and overfenders. Further back, a red Mazda RX-7 FD, several Honda Civics with varying body kits, a bagged Subaru WRX with vape-nation stickers, and a clean Mitsubishi Lancer Evolution IX. Most cars are extremely low with aggressive camber and stretched tires, typical of Indonesian stance scene. The lot is at Pacific Place or Grand Indonesia style location in Jakarta Selatan. People gathered around cars chatting, some taking photos with phones and cameras. Sunset lighting creates dramatic shadows and highlights the metallic paint finishes. Visible are various car club stickers and banners. The atmosphere is casual social gathering of automotive enthusiasts, not a formal show. Some cars have hoods open displaying engine bays.
Output: car meet event gathering kumpul parkiran stance nation low lowered ceper slammed static airlift bagged air suspension wheels rims velg aftermarket jdm japanese domestic market nissan toyota honda mazda mitsubishi subaru community komunitas enthusiast hobbyist otomotif automotive culture budaya lifestyle scene indonesia jaksel photography photo shoot session fotografi squad crew club

Input: A show-stopping heavily modified Honda Civic EG hatchback (1992-1995 generation) displayed at an indoor automotive exhibition with professional lighting. The car features an extreme Rocket Bunny or Pandem-style widebody kit with dramatically flared fenders adding 4-5 inches of width per side. The body is finished in an eye-catching candy purple paint with metallic flake that shifts colors under different lighting. Aggressive fitment with 15-inch Work Meister S1 3-piece wheels sitting perfectly flush with the wide fenders, stretched tires with visible camber. The car is slammed on air suspension, sitting millimeters from the ground. Custom carbon fiber hood with vents, full front lip spoiler, and rear diffuser. The build quality appears professional with clean body lines and no visible gaps. Window banner with sponsor decals across the windshield. The car is positioned on a show platform with rope barriers and trophy nearby, suggesting award-winning status. Background shows other show cars and visitors taking photos. This represents years of work and significant financial investment, clearly built for show circuit competition not daily driving.
Output: honda civic eg estilo genio ferio widebody wide body kit over fender flare aggressive stance wheel fitment flush tucked stretched tire ban modifications extreme custom one of a kind unik unique show car kontes contest exhibition pameran champion juara trophy winner best display build project years tahun fabrication paint cat wrap vinyl graphics livery sponsorship sticker decal attention grabbing viral

Input: A first-person POV video frame shot from inside a performance car showing the full dashboard and windshield view while traveling at high speed (speedometer needle pointing at 180 km/h) on an empty Indonesian toll road expressway during daytime. The instrument cluster is a modern digital display with bright red needle on analog speedometer and tachometer showing approximately 5500 RPM. The windshield view shows three clear lanes ahead with sparse traffic, asphalt in good condition, and highway barriers on both sides. Slight motion blur on the lane markings suggesting very high speed. The steering wheel visible at bottom of frame appears to be an aftermarket sports wheel, possibly Momo or Sparco. The car seems stable despite the speed, suggesting good suspension setup. The dashboard is clean with no check engine lights. GoPro or similar action camera mounted to windshield capturing the footage. Audio likely captures engine note and wind noise. This is typical content for Indonesian automotive YouTubers doing top speed runs or highway cruising videos. The empty road and high speed create a thrilling, somewhat reckless vibe that appeals to enthusiast audiences. Time stamp suggests mid-morning when toll roads are less congested.
Output: driving pov point of view first person perspective dashboard instrument cluster speedometer tachometer rpm gauge meter digital analog speed kecepatan fast kencang mph kph acceleration accelerating pedal gas throttle highway tol expressway jalan raya toll road asphalt lane traffic flow smooth cruising commute perjalanan trip journey travel sound engine exhaust note audio onboard gopro camera mounted dashcam recording footage

Input: A professional comparison thumbnail showing two popular Indonesian market vehicles positioned side by side in a neutral studio setting with dramatic lighting. On the left, a white 2023 Toyota Raize compact SUV with black roof rails and sporty trim looking fresh and modern. On the right, a silver 2023 Honda HR-V second generation with sleek coupe-like roofline and larger dimensions. Both vehicles are positioned at identical 3/4 front angles for fair comparison. Large bold text overlay in the center reads "WHICH ONE?" in white letters with yellow outline, creating engagement bait for viewers. Below each car, their starting prices are shown (Raize: 230 juta, HR-V: 380 juta). The lighting emphasizes the design differences - the Raize appears more compact and budget-friendly while the HR-V looks more premium and spacious. This is clearly a buyers guide or comparison review thumbnail targeting Indonesian car shoppers in the compact SUV/crossover segment. The composition is balanced and professional, designed to maximize click-through rate by presenting a direct visual question. The price difference visible suggests the comparison will focus on value proposition, features per rupiah, practicality vs budget considerations.
Output: comparison perbandingan versus vs adu compare contrast side by side berdampingan which one mana pilih choose choice pilihan decision buyers guide pembeli review analysis analisis pros cons kelebihan kekurangan advantage disadvantage price harga value worth investment spec specifications engine performance comfort features interior exterior design styling dimensions size clearance safety rating ownership cost maintenance perawatan fuel economy consumption
    """

    prompt = """
ANALYZE THIS MEDIA AND OUTPUT KEYWORDS:

STEP 1 - VISUAL AND AUDIO ANALYSIS:
Look at the image/video frame carefully. Identify:
- Vehicle brands, models, and chassis codes (e.g., w204, g20, fk8)
- Text overlays, titles, captions, memes, stickers (extract and normalize all text)
- Scene type: review, crash, drag race, car meet, driving POV, engine bay, modification showcase, comparison
- Visible modifications: body kits, wheels, suspension, turbo, exhaust, spoilers
- Setting: highway, parking lot, garage, offroad, urban, racing track
- Any people, actions, or specific events happening
- Colors, condition (crashed, pristine, muddy, modified)

If video has audio, listen and transcribe:
- Spoken dialogue, narration, commentary (in any language)
- Key topics discussed, technical terms mentioned
- Questions asked, opinions expressed
- Background sounds (engine revving, exhaust note, crash sounds)

STEP 2 - CONTEXT INFERENCE:
Based on visual cues, infer:
- Video type: review, tutorial, accident footage, meme, entertainment, technical showcase
- Target audience: enthusiasts, general public, specific community
- Emotional tone: funny, serious, dramatic, educational, clickbait
- Cultural context: Indonesian automotive scene, JDM culture, family car usage

STEP 3 - KEYWORD GENERATION:
Generate 230-254 characters of keywords following these rules:
- Start with PRIMARY identifiers (brand, model, chassis code, nicknames)
- Add ACTION/GENRE keywords (crash, review, drag, meme, tutorial)
- Extract and normalize ALL visible text, then add related search terms
- Transcribe and include KEY PHRASES from audio (spoken topics, technical terms, commentary)
- Include DISTINCT SYNONYMS in English, Indonesian, and slang
- Add CONTEXTUAL terms (location, modifications, parts, events)
- Apply SUBSTRING EXCLUSION rules strictly (if "racing" exists, remove "race")
- Fill remaining space with high-value search terms users would actually type

STEP 4 - OUTPUT:
Write ONLY the keywords. No explanations. No code blocks. No preamble. Start directly with the first keyword.
Format: lowercase, space-separated, 230-254 characters total.

BEGIN ANALYSIS NOW:
    """

    with open(file_path, 'rb') as f:
        file_data = f.read()

    mime_type = get_mime_type(file_path)
    media_part = Part.from_bytes(data=file_data, mime_type=mime_type)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = config.application_config.client.models.generate_content(
                model=config.application_config.model_name,
                contents=[media_part, prompt],
                config=GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=10000,
                    top_p=0.95,
                    top_k=40,
                    system_instruction=system_instruction
                )
            )

            if not response:
                raise ValueError("Response is None")

            if not hasattr(response, 'text') or not response.text:
                if not hasattr(response, 'candidates') or not response.candidates:
                    if hasattr(response, 'prompt_feedback'):
                        raise ValueError(f"No candidates. Prompt feedback: {response.prompt_feedback}")
                    raise ValueError("No candidates in response")

                candidate = response.candidates[0]

                if hasattr(candidate, 'finish_reason'):
                    finish_reason = str(candidate.finish_reason)
                    if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                        raise ValueError(f"Content blocked by safety filters: {finish_reason}")

                if not hasattr(candidate, 'content') or not candidate.content:
                    raise ValueError(f"No content in candidate. Finish reason: {getattr(candidate, 'finish_reason', 'unknown')}")

                raise ValueError(f"No text in response: {candidate}")

            response_text = response.text.strip()
            if len(response_text) < 80:
                raise ValueError(f"Response too short ({len(response_text)} chars), retrying...")
            return response

        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                print(f"  ⚠️  Attempt {attempt + 1} failed: {error_msg}")
            else:
                raise ValueError(f"API call failed after {max_retries} attempts: {error_msg}")

    raise ValueError(f"API call failed after {max_retries} attempts")
