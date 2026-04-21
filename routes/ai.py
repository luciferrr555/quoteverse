import random
import os
import json
import traceback
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import current_user

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

# ─── Gemini AI Setup ──────────────────────────────────────────────────────────
_gemini_client = None


def get_gemini_client():
    """Lazy-init Gemini client using the new google.genai SDK."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    api_key = (current_app.config.get('GEMINI_API_KEY')
               or os.environ.get('GEMINI_API_KEY'))
    if not api_key:
        return None

    try:
        from google import genai
        _gemini_client = genai.Client(api_key=api_key)
        return _gemini_client
    except Exception as e:
        print(f'[AI] Failed to init Gemini client: {e}')
        return None


def ask_gemini(prompt, fallback=None):
    """Send a prompt to Gemini and return text response. Falls back on error."""
    client = get_gemini_client()
    if client is None:
        return fallback  # no API key — use template fallback

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'temperature': 0.9,
                'max_output_tokens': 1024,
            }
        )
        return response.text.strip()
    except Exception as e:
        print(f'[AI] Gemini call failed: {e}')
        traceback.print_exc()
        return fallback


def parse_json_from_ai(text):
    """Try to extract a JSON array from Gemini's response text."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith('```'):
        lines = text.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        text = '\n'.join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find a JSON array in the text
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    return None


# ─── Template Fallbacks (used when API key is missing or call fails) ──────────
MOOD_QUOTES = {
    'sad': [
        "Pain is temporary. It may last a minute, or an hour, or a day — but eventually it will subside.",
        "Every storm runs out of rain. Every dark night turns into day. Your sadness is not permanent.",
        "You are allowed to be both a masterpiece and a work in progress simultaneously.",
        "Crying doesn't indicate weakness. Since birth, it has always been a sign that you are alive.",
        "Even the darkest night will end, and the sun will rise again.",
        "The wound is the place where the light enters you.",
        "Tough times never last, but tough people do.",
        "Your current situation is not your final destination. The best is yet to come.",
        "Stars can't shine without darkness.",
    ],
    'gym': [
        "Your body can stand almost anything. It's your mind you have to convince.",
        "The only bad workout is the one that didn't happen.",
        "Push harder than yesterday if you want a different tomorrow.",
        "Sweat is just fat crying. Keep going.",
        "No pain, no gain. Shut up and train.",
        "The body achieves what the mind believes.",
        "Discipline is doing it even when you don't feel like it.",
        "Fall in love with the process. The results will follow.",
    ],
    'success': [
        "Success is not final, failure is not fatal. It is the courage to continue that counts.",
        "The secret of getting ahead is getting started.",
        "Don't watch the clock. Do what it does — keep going.",
        "Opportunities don't happen. You create them.",
        "Dream big. Start small. Act now.",
        "Winners are not people who never fail, but people who never quit.",
        "Hustle in silence and let your success make the noise.",
    ],
    'heartbreak': [
        "You survived everything before this. You will survive this too.",
        "Sometimes good things fall apart so better things can fall together.",
        "Never allow someone to be your priority while allowing yourself to be their option.",
        "Your value doesn't decrease based on someone's inability to see your worth.",
        "Stop looking for happiness in the same place you lost it.",
    ],
    'motivation': [
        "Act as if what you do makes a difference. It does.",
        "Believe you can and you're halfway there.",
        "It does not matter how slowly you go as long as you do not stop.",
        "You miss 100% of the shots you don't take.",
        "The only way to do great work is to love what you do.",
        "Start where you are. Use what you have. Do what you can.",
    ],
    'study': [
        "Education is the most powerful weapon which you can use to change the world.",
        "An investment in knowledge pays the best interest.",
        "The beautiful thing about learning is that no one can take it away from you.",
        "The expert in anything was once a beginner.",
        "Learn as if you will live forever, live like you will die tomorrow.",
    ],
    'money': [
        "Don't work for money. Make money work for you.",
        "Financial freedom is not about being rich, it's about having choices.",
        "The goal is not more money. The goal is living life on your terms.",
        "Every rupee you save is a soldier fighting for your freedom.",
        "Build assets that work while you sleep.",
    ],
    'discipline': [
        "Discipline is the bridge between goals and accomplishment.",
        "We must all suffer from one of two pains: the pain of discipline or the pain of regret.",
        "Self-discipline is the magic power that makes you virtually unstoppable.",
        "Motivation gets you going. Discipline keeps you growing.",
        "Without self-discipline, success is impossible, period.",
    ],
    'hinglish': [
        "Sapne dekh nahi, sapne mein jee. Tab jaake zindagi badlegi.",
        "Kal ki chinta mat kar bhai, aaj ka kaam aaj kar.",
        "Log kya kahenge yeh soch ke apni life mat rok.",
        "Thoda aur ruk. Kamiyabi door nahi.",
        "Apni mehnat pe trust kar, baaki sab time pe chhod.",
    ]
}

DAILY_MOOD_PERSONALIZED = {
    'happy': 'success',
    'productive': 'discipline',
    'sad': 'sad',
    'heartbroken': 'heartbreak',
    'tired': 'gym',
    'broke': 'money',
    'studying': 'study',
    'default': 'motivation'
}


# ─── Routes ───────────────────────────────────────────────────────────────────

@ai_bp.route('/')
def ai_tools():
    has_ai = bool(current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY'))
    return render_template('ai_tools.html', has_real_ai=has_ai)


@ai_bp.route('/generate', methods=['POST'])
def generate_quote():
    """Generate quotes using Gemini AI. Falls back to templates if unavailable."""
    data = request.json or {}
    mood = data.get('mood', 'motivation').lower().strip()
    count = min(int(data.get('count', 5)), 10)

    # ── Try Gemini AI first ──
    prompt = (
        f"Generate exactly {count} unique, original motivational quotes about '{mood}'. "
        f"Each quote should be 1-2 sentences, powerful, and shareable on social media. "
        f"Return ONLY a JSON array of strings, no other text. Example: [\"quote 1\", \"quote 2\"]"
    )

    # Template fallback
    pool = MOOD_QUOTES.get(mood) or MOOD_QUOTES.get('motivation')
    fallback_quotes = random.sample(pool, min(count, len(pool)))

    ai_response = ask_gemini(prompt, fallback=None)
    if ai_response:
        parsed = parse_json_from_ai(ai_response)
        if parsed and isinstance(parsed, list) and len(parsed) > 0:
            return jsonify({'quotes': parsed[:count], 'mood': mood, 'source': 'gemini'})

    # Fallback
    return jsonify({'quotes': fallback_quotes, 'mood': mood, 'source': 'template'})


@ai_bp.route('/rewrite', methods=['POST'])
def rewrite_quote():
    """Rewrite a quote in a specific style using Gemini AI."""
    data = request.json or {}
    original = data.get('quote', '').strip()
    style = data.get('style', 'deep').lower()

    if not original:
        return jsonify({'error': 'No quote provided'}), 400

    style_descriptions = {
        'funny': 'in a humorous, witty, Gen-Z meme-style way with emojis. Make it relatable and funny.',
        'savage': 'in a savage, brutally honest, no-nonsense alpha tone. Be direct and hard-hitting.',
        'romantic': 'in a deeply romantic, poetic, heartfelt way. Make it sound like a love letter.',
        'deep': 'in a profound, philosophical, thought-provoking way. Make the reader stop and reflect.'
    }

    style_desc = style_descriptions.get(style, style_descriptions['deep'])

    prompt = (
        f"Rewrite the following quote {style_desc}\n\n"
        f"Original quote: \"{original}\"\n\n"
        f"Return ONLY the rewritten quote as plain text, nothing else. No quotes around it."
    )

    ai_response = ask_gemini(prompt)
    if ai_response:
        # Clean up any wrapping quotes the AI might add
        rewritten = ai_response.strip().strip('"').strip("'")
        return jsonify({
            'rewritten': rewritten,
            'style': style,
            'original': original,
            'source': 'gemini'
        })

    # Template fallback
    TEMPLATES = {
        'funny': [
            "Okay but imagine if '{quote}' was actually true for once",
            "Me at 3am: '{quote}' also me at 3am: *reaches for phone again*",
        ],
        'savage': [
            "While you scrolled past this, someone lived by it: '{quote}'. Stay average.",
            "Either you're about it or you're not. '{quote}'. Pick a lane.",
        ],
        'romantic': [
            "Every love story starts with a spark. Mine started when I realized: '{quote}'",
            "If love had a language, it would sound like this: '{quote}'",
        ],
        'deep': [
            "Between who you are and who you're becoming lies this truth: '{quote}'",
            "The universe doesn't speak in words. It speaks in moments that feel like: '{quote}'",
        ]
    }

    templates = TEMPLATES.get(style, TEMPLATES['deep'])
    display_quote = original if len(original) <= 80 else original[:77] + '...'
    rewritten = random.choice(templates).replace('{quote}', display_quote)

    return jsonify({
        'rewritten': rewritten,
        'style': style,
        'original': original,
        'source': 'template'
    })


@ai_bp.route('/caption', methods=['POST'])
def generate_caption():
    """Generate an Instagram caption using Gemini AI."""
    data = request.json or {}
    quote = data.get('quote', '').strip()
    if not quote:
        return jsonify({'error': 'No quote provided'}), 400

    prompt = (
        f"Create a viral Instagram caption for the following motivational quote:\n\n"
        f"\"{quote}\"\n\n"
        f"The caption should include:\n"
        f"- The quote formatted beautifully with emojis\n"
        f"- A call-to-action (tag someone, double tap, save, etc.)\n"
        f"- 10-15 relevant hashtags at the end\n"
        f"- Total length: 150-300 characters\n\n"
        f"Return ONLY the caption as plain text."
    )

    ai_response = ask_gemini(prompt)
    if ai_response:
        return jsonify({'caption': ai_response, 'source': 'gemini'})

    # Template fallback
    CAPTION_TEMPLATES = [
        f"✨ {quote} ✨\n\n📌 Save this for the days you need it most.\n💬 Tag someone who needs to see this!\n.\n.\n#motivation #quotes #inspiration #mindset #growth #success #viral",
        f"💡 '{quote}'\n\n🔥 Double tap if this hit different!\n👇 What does this mean to you?\n.\n.\n#quotesoftheday #dailyquotes #motivationalquotes #instaquote #quotestagram",
        f"🌟 {quote}\n\n→ Read that again.\n→ Now go do the thing.\n\n✅ Follow @quoteverse for daily doses of truth.\n.\n.\n#quoteverse #mindsetshift #growthmindset #successmindset #hustle",
    ]

    return jsonify({'caption': random.choice(CAPTION_TEMPLATES), 'source': 'template'})


@ai_bp.route('/daily', methods=['GET'])
def daily_quote():
    """Generate a personalized daily quote using Gemini AI."""
    mood = request.args.get('mood', 'default').lower()
    category = DAILY_MOOD_PERSONALIZED.get(mood, 'motivation')

    prompt = (
        f"Generate a single original motivational quote for someone who is feeling '{mood}' today. "
        f"The quote should be about {category}, 1-2 sentences, powerful and uplifting. "
        f"Return ONLY the quote as plain text, nothing else."
    )

    ai_response = ask_gemini(prompt)
    if ai_response:
        quote = ai_response.strip().strip('"').strip("'")
        return jsonify({
            'quote': quote,
            'category': category.upper(),
            'mood': mood,
            'source': 'gemini'
        })

    # Template fallback — use day-of-year seed for daily consistency
    pool = MOOD_QUOTES.get(category, MOOD_QUOTES['motivation'])
    import datetime
    day_seed = datetime.date.today().timetuple().tm_yday
    random.seed(day_seed)
    quote = random.choice(pool)
    random.seed()

    return jsonify({
        'quote': quote,
        'category': category.upper(),
        'mood': mood,
        'source': 'template'
    })


@ai_bp.route('/explain', methods=['POST'])
def explain_quote():
    """NEW: Use Gemini to explain a quote's meaning and context."""
    data = request.json or {}
    quote = data.get('quote', '').strip()
    author = data.get('author', 'Unknown').strip()

    if not quote:
        return jsonify({'error': 'No quote provided'}), 400

    prompt = (
        f"Explain the following quote in a simple, engaging way that a teenager would understand. "
        f"Include: (1) what it means, (2) how to apply it in daily life, "
        f"(3) a real-life example. Keep it under 150 words.\n\n"
        f"Quote: \"{quote}\" — {author}"
    )

    ai_response = ask_gemini(prompt)
    if ai_response:
        return jsonify({
            'explanation': ai_response,
            'quote': quote,
            'author': author,
            'source': 'gemini'
        })

    return jsonify({
        'explanation': 'AI explanation requires a Gemini API key. Add GEMINI_API_KEY to your .env file.',
        'quote': quote,
        'author': author,
        'source': 'unavailable'
    })


@ai_bp.route('/hashtags', methods=['POST'])
def generate_hashtags():
    """NEW: Generate trending hashtags for a quote using Gemini AI."""
    data = request.json or {}
    quote = data.get('quote', '').strip()
    category = data.get('category', '').strip()

    if not quote:
        return jsonify({'error': 'No quote provided'}), 400

    prompt = (
        f"Generate 20 trending Instagram/Twitter hashtags for this motivational quote "
        f"in the '{category}' category:\n\n\"{quote}\"\n\n"
        f"Return ONLY a JSON array of hashtag strings (with #). Example: [\"#motivation\", \"#success\"]"
    )

    ai_response = ask_gemini(prompt)
    if ai_response:
        parsed = parse_json_from_ai(ai_response)
        if parsed and isinstance(parsed, list):
            return jsonify({'hashtags': parsed, 'source': 'gemini'})

    # Fallback
    fallback = [
        '#motivation', '#quotes', '#inspiration', '#mindset', '#success',
        '#growth', '#hustle', '#grindset', '#quoteoftheday', '#motivationalquotes',
        '#dailymotivation', '#positivevibes', '#selfimprovement', '#nevergiveup',
        '#believeinyourself', '#quotestagram', '#instaquote', '#viral', '#trending',
        f'#{category.lower()}' if category else '#life',
    ]
    return jsonify({'hashtags': fallback, 'source': 'template'})
