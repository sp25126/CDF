from typing import Optional, List, Dict, Any
import re
import logging
from app.services.llm_service import llm_service
from app.services.source_ingest import source_ingest_service
from app.services.retrieval import retrieve_relevant_chunks
from app.services.prompts import (
    SYSTEM_PROMPT, EXPLAIN_PROMPT_TEMPLATE, LANGUAGE_INSTRUCTIONS,
    SOURCE_SYSTEM_PROMPT, SOURCE_EXPLAIN_PROMPT_TEMPLATE
)

logger = logging.getLogger(__name__)

def _get_mock_explanation(topic_lower: str, language_mode: str, topic: str) -> Dict[str, Any]:
    # Local Knowledge Base Fallback
    if "photosynthesis" in topic_lower:
        if language_mode == "english":
            title = "Simplifying Photosynthesis"
            grade_level = 6
            bullets = [
                "Plants make their own food using sunlight.",
                "Leaves are the kitchen of the plants where food is prepared.",
                "Sunlight, water, and chlorophyll are essential for this process."
            ]
            example = "Just like you need a stove, utensils, and vegetables to cook food in a kitchen, leaves need sunlight and water."
            recap = "So remember, plants make their food using sunlight and water, which is called photosynthesis."
            response_text = "Children, today we will talk about Photosynthesis. Just like we cook food in our kitchen, plants prepare their food using sunlight and water."
        elif language_mode == "hindi":
            title = "प्रकाश संश्लेषण को समझना"
            grade_level = 6
            bullets = [
                "पौधे सूर्य के प्रकाश का उपयोग करके अपना भोजन स्वयं बनाते हैं।",
                "पत्तियां पौधों की रसोई होती हैं जहां भोजन तैयार किया जाता है।",
                "इस प्रक्रिया के लिए सूर्य का प्रकाश, पानी और क्लोरोफिल सबसे आवश्यक हैं।"
            ]
            example = "जैसे घर में रसोई में खाना बनाने के लिए चूल्हा, बर्तन और सब्जी चाहिए, वैसे ही पत्तों को धूप और पानी चाहिए।"
            recap = "तो याद रखिए, धूप और पानी से ही पौधे अपना भोजन बनाते हैं, इसी को प्रकाश संश्लेषण कहते हैं।"
            response_text = "बच्चों, आज हम प्रकाश संश्लेषण के बारे में बात करेंगे। जैसे हम घर की रसोई में खाना बनाते हैं, वैसे ही पेड़-पौधे भी धूप और पानी से अपना भोजन बनाते हैं।"
        else:
            title = "Simplifying Photosynthesis"
            grade_level = 6
            bullets = [
                "Plants apna khana khud banate hain.",
                "Patte (leaves) plants ki rasoi hote hain jo khana taiyar karte hain.",
                "Dhoop, paani aur chlorophyll iske liye sabse zaroori hain."
            ]
            example = "Jaise ghar mein rasoi mein khana banane ke liye chulha, bartan aur sabzi chahiye, waise hi patton ko dhoop aur paani chahiye."
            recap = "Toh yaad rakhiye, dhoop aur paani se hi plants apna khana banate hain, isi ko photosynthesis kehte hain."
            response_text = "Bachon, aaj hum Photosynthesis ke baare mein baat karenge. Jaise hum ghar ke kitchen mein khana banate hain, waise hi ped-paudhe bhi dhoop aur pani se apna khana banate hain."
    
    elif "gravity" in topic_lower or "gurutva" in topic_lower:
        if language_mode == "english":
            title = "Understanding Gravity"
            grade_level = 5
            bullets = [
                "Gravity is an invisible force that pulls objects toward each other.",
                "It pulls everything toward the Earth so nothing floats away into space.",
                "Because of this force, we are able to stand on the ground."
            ]
            example = "If you pluck an apple from a tree, it always falls down to the ground, never floats up."
            recap = "So remember, the Earth's force that pulls everything toward itself is called gravity."
            response_text = "Children, let's understand gravity simply. Imagine when a wrestler throws another down in a match, similarly our Earth pulls everything toward itself."
        elif language_mode == "hindi":
            title = "गुरुत्वाकर्षण को समझना"
            grade_level = 5
            bullets = [
                "गुरुत्वाकर्षण एक अदृश्य बल है जो वस्तुओं को एक-दूसरे की ओर खींचता है।",
                "यह पृथ्वी की ओर हर चीज़ को खींचकर रखता है ताकि कोई हवा में न उड़े।",
                "इसी बल की वजह से हम ज़मीन पर खड़े हो पाते हैं।"
            ]
            example = "जैसे अगर आप पेड़ से आम तोड़ेंगे, तो वह हमेशा नीचे ज़मीन पर ही गिरेगा, आसमान में नहीं उड़ेगा।"
            recap = "तो याद रखिए, पृथ्वी की हर चीज़ को अपनी तरफ खींचने की शक्ति को ही गुरुत्वाकर्षण कहते हैं।"
            response_text = "बच्चों, गुरुत्वाकर्षण को समझने के लिए एक सरल चीज़ सोचो। जैसे जब दंगल में एक पहलवान दूसरे को पकड़ कर ज़मीन पर गिराता है, वैसे ही हमारी पृथ्वी भी हर चीज़ को अपनी तरफ खींचती है।"
        else:
            title = "Understanding Gravity"
            grade_level = 5
            bullets = [
                "Gravity ek unseen force (taqat) hai jo har cheez ko apni taraf khinchti hai.",
                "Yeh earth ki taraf har cheez ko khinchkar rakhti hai taaki koi hawa mein na ude.",
                "Isi force ki wajah se hum zameen par khade ho paate hain."
            ]
            example = "Jaise agar aap khet mein aam ke ped se aam todenge, toh woh hamesha neeche zameen par hi girega, aasmaan mein nahi udega."
            recap = "Toh yaad rakhiye, dharti ki har cheez ko apni taraf khinchne ki taqat ko hi gravity kehte hain."
            response_text = "Bachon, gravity ko samajhne ke liye ek simple cheez socho. Jab dangal (wrestling) mein ek pehalwan dusre ko pakad kar zameen par girata hai, waise hi hamari dharti bhi har cheez ko apni taraf khinchti hai."
        
    elif "fraction" in topic_lower or "bhinn" in topic_lower:
        if language_mode == "english":
            title = "Learning Fractions"
            grade_level = 6
            bullets = [
                "Fractions represent equal parts of a whole object.",
                "It contains a numerator (top number) and a denominator (bottom number).",
                "Examples include half (1/2) or one-third (1/3)."
            ]
            example = "If you divide one bread slice equally among 4 friends, each gets one-quarter (1/4)."
            recap = "So remember, dividing a whole object into equal parts is called a fraction."
            response_text = "Children, fractions are not difficult. Just like when we divide paneer or bread into equal parts at home, that is what fractions are in math."
        elif language_mode == "hindi":
            title = "भिन्न को सीखना"
            grade_level = 6
            bullets = [
                "भिन्न का मतलब है किसी पूरी चीज़ का बराबर हिस्सा।",
                "इसमें एक अंश (ऊपर की संख्या) और एक हर (नीचे की संख्या) होती है।",
                "जैसे आधा (1/2) या एक-तिहाई (1/3)।"
            ]
            example = "जैसे अगर एक रोटी को 4 दोस्तों में बराबर बांटें, तो हर एक को एक-चौथाई (1/4) रोटी मिलेगी।"
            recap = "तो याद रखिए, एक पूरी चीज़ को बराबर हिस्सों में बांटना ही भिन्न कहलाता है।"
            response_text = "बच्चों, भिन्न कोई मुश्किल चीज़ नहीं है। जैसे जब हम घर में बराबर हिस्सों में पनीर या रोटी बांटते हैं, वही गणित में भिन्न है।"
        else:
            title = "Learning Fractions"
            grade_level = 6
            bullets = [
                "Fractions ka matlab hai kisi poori cheez ka barabar hissa.",
                "Ismein ek numerator (upar ka number) aur ek denominator (niche ka number) hota hai.",
                "Jaise aadha (1/2) ya ek-tihai (1/3)."
            ]
            example = "Jaise agar ek roti ko 4 doston mein barabar baantein, toh har ek ko ek-chouthai (1/4) roti milegi."
            recap = "Toh yaad rakhiye, ek poori cheez ko barabar hisson mein baatna hi fraction kehlata hai."
            response_text = "Bachon, fractions koi mushkil cheez nahi hai. Jaise jab hum ghar mein barabar hisson mein paneer ya roti baante hain, wahi maths mein fractions hai."
        
    elif "food chain" in topic_lower or "aahar" in topic_lower or "foodchain" in topic_lower:
        if language_mode == "english":
            title = "Exploring the Food Chain"
            grade_level = 6
            bullets = [
                "Every living organism depends on another organism for its food.",
                "Plants are eaten by insects, insects by frogs, and frogs by snakes.",
                "This runs like a chain to maintain nature's balance."
            ]
            example = "In a farm, crop is eaten by small insects, insect by bird, and bird by hawk."
            recap = "So remember, one organism eating another and becoming food for someone else is a food chain."
            response_text = "Children, today we will read about the Food Chain. It's like a cycle in a farm—plants grow from sunlight, then animals eat them."
        elif language_mode == "hindi":
            title = "खाद्य श्रृंखला की खोज"
            grade_level = 6
            bullets = [
                "हर जीव अपने भोजन के लिए दूसरे जीव पर निर्भर है।",
                "पौधों को टिड्डी खाती है, टिड्डी को मेढक और मेढक को सांप खाता है।",
                "यह एक श्रृंखला की तरह चलता रहता है जो प्रकृति का संतुलन बनाता है।"
            ]
            example = "जैसे खेत में फसल को छोटा कीड़ा खाता है, कीड़े को पक्षी खाता है, और पक्षी को बाज।"
            recap = "तो याद रखिए, एक जीव का दूसरे को खाना और खुद किसी का खाना बनना ही खाद्य श्रृंखला है।"
            response_text = "बच्चों, आज हम खाद्य श्रृंखला के बारे में पढ़ेंगे। यह खेत के चक्कर जैसा है—पौधे धूप से बढ़ते हैं, फिर उन्हें जानवर खाते हैं।"
        else:
            title = "Exploring the Food Chain"
            grade_level = 6
            bullets = [
                "Har jeev apne khane ke liye doosre jeev par nirbhar hai.",
                "Paudhon ko tiddi khati hai, tiddi ko mendhak aur mendhak ko saanp khata hai.",
                "Yeh ek chain ki tarah chalta rehta hai jo nature ka balance banata hai."
            ]
            example = "Jaise khet mein fasal ko chhota keeda khata hai, keede ko pakshi khata hai, aur pakshi ko baaz."
            recap = "Toh yaad rakhiye, ek jeev ka doosre ko khana aur khud kisi ka khana banna hi food chain hai."
            response_text = "Bachon, aaj hum Food Chain ke baare mein padhenge. Yeh khet ke chakkar jaisa hai—paudhe dhoop se badhte hain, fir unhe janwar khate hain."

    else:
        if language_mode == "english":
            title = f"Simplifying {topic}"
            grade_level = 6
            bullets = [
                f"{topic} is an important concept in science and math.",
                "We understand it by connecting it with the world around us.",
                "It involves a balance between different components."
            ]
            example = f"Just like you need different tools for different jobs in a farm, there are different rules to understand {topic}."
            recap = f"So remember, {topic} runs an important part of our life."
            response_text = f"Children, today we will talk about {topic}. This topic is very important for your studies and daily life."
        elif language_mode == "hindi":
            title = f"{topic} को समझना"
            grade_level = 6
            bullets = [
                f"{topic} विज्ञान और गणित का एक बहुत ही महत्वपूर्ण सिद्धांत है।",
                "इसे हम अपने आस-पास की दुनिया से जोड़ कर समझते हैं।",
                "इसमें अलग-अलग घटकों का आपस में संतुलन होता है।"
            ]
            example = f"जैसे खेत में अलग-अलग काम के लिए अलग-अलग उपकरण चाहिए, वैसे ही {topic} को समझने के लिए अलग नियम होते हैं।"
            recap = f"तो याद रखिए, {topic} हमारे जीवन के किसी न किसी महत्वपूर्ण हिस्से को चलाता है।"
            response_text = f"बच्चों, आज हम {topic} के बारे में बात करेंगे। यह विषय आपकी पढ़ाई और दैनिक जीवन के लिए बहुत ज़रूरी है।"
        else:
            title = f"Simplifying {topic}"
            grade_level = 6
            bullets = [
                f"{topic} science aur maths ka ek bahut hi important concept hai.",
                "Isko hum apne aas-paas ki duniya se jod kar samajhte hain.",
                "Ismein alag-alag components ka aapas mein balance hota hai."
            ]
            example = f"Jaise khet mein alag-alag kaam ke liye alag-alag tools chahiye, waise hi {topic} ko samajhne ke liye alag rules hote hain."
            recap = f"Toh yaad rakhiye, {topic} hamare jeevan ke kisi na kisi important hisse ko chalata hai."
            response_text = f"Bachon, aaj hum {topic} ke baare karenge. Yeh topic aapki padhai aur daily life ke liye bahut zaroori hai."

    return {
        "mode": "explain",
        "title": title,
        "grade_level": grade_level,
        "bullets": bullets,
        "example": example,
        "recap": recap,
        "response_text": response_text,
        "language_mode": language_mode
    }

async def generate_explanation(session_id: str, text: str, language_mode: str = "default", source_mode: bool = False):
    """
    Generate explanation using the live LLM, falling back to a structured mock database if the LLM fails.
    """
    # Extract a rough topic (mock logic using word boundaries)
    clean_text = text.lower()
    # Remove punctuation first
    for char in [".", ",", "?", "!", "\"", "'"]:
        clean_text = clean_text.replace(char, " ")
        
    stop_words = [
        "explain", "samjhao", "batao", "kya hai", "meaning", "how", "why", "about",
        "for class 6", "for class 7", "for class 8", "for class 5", "in hinglish", 
        "haryana", "a", "an", "the", "make", "in english", "english mein", "english me",
        "in hindi", "hindi mein", "hindi me", "pure hindi"
    ]
    for word in stop_words:
        clean_text = re.sub(rf'\b{re.escape(word)}\b', ' ', clean_text)
        
    # Remove extra spaces
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    topic = clean_text.title() or "Photosynthesis"
    topic_lower = topic.lower()

    # Get language specific instructions
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language_mode, LANGUAGE_INSTRUCTIONS["default"])

    if source_mode:
        # Check if we have any documents uploaded
        all_sources = source_ingest_service.list_sources()
        if not all_sources:
            return {
                "mode": "explain",
                "title": "No Source Uploaded",
                "grade_level": 6,
                "bullets": ["Please upload classroom materials first in the sources panel."],
                "example": "No active files found.",
                "recap": "Upload files, text, or links to query documents.",
                "response_text": "Please upload some classroom materials first in the sources panel.",
                "language_mode": language_mode,
                "source_mode": True,
                "citations": []
            }

        # Retrieve relevant chunks
        chunks = retrieve_relevant_chunks(text, limit=3)
        chunks = [c.model_dump() for c in chunks]
        if not chunks:
            # Source mode refusal
            return {
                "mode": "explain",
                "title": "Not Found",
                "grade_level": 6,
                "bullets": [],
                "example": "",
                "recap": "",
                "response_text": "I cannot find the answer to this question in the provided source material.",
                "language_mode": language_mode,
                "source_mode": True,
                "citations": []
            }

        snippets_str = "\n---\n".join([f"Source: {c['source_title']} (Page {c['page_number']}):\n{c['text']}" for c in chunks])
        sys_prompt = SOURCE_SYSTEM_PROMPT.format(LANGUAGE_MODE=lang_instruction)
        user_prompt = SOURCE_EXPLAIN_PROMPT_TEMPLATE.format(
            topic=topic,
            grade=6,
            language_instruction=lang_instruction,
            snippets=snippets_str
        )

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]

        citations = [
            {
                "source_title": c["source_title"],
                "snippet": c["text"][:150] + "...",
                "page_number": c["page_number"],
                "section_label": c["section_label"]
            }
            for c in chunks
        ]

        try:
            response_json = await llm_service.get_chat_completion(messages, response_format={"type": "json_object"})
            response_json["mode"] = "explain"
            response_json["language_mode"] = language_mode
            response_json["source_mode"] = True
            if "provided source material" in response_json.get("response_text", "").lower() or response_json.get("title") == "Not Found":
                response_json["citations"] = []
            else:
                response_json["citations"] = citations
            return response_json
        except Exception as e:
            logger.error(f"Fallback inside source mode due to LLM error: {e}")
            top_chunk = chunks[0]
            bullets = [top_chunk["text"][:120] + "..."]
            if len(top_chunk["text"]) > 120:
                bullets.append(top_chunk["text"][120:240] + "...")
            return {
                "mode": "explain",
                "title": f"From: {top_chunk['source_title']}",
                "grade_level": 6,
                "bullets": bullets,
                "example": f"Verified from page {top_chunk['page_number']}.",
                "recap": "Grounded direct source chunk fallback.",
                "response_text": top_chunk["text"][:300] + "...",
                "language_mode": language_mode,
                "source_mode": True,
                "citations": [citations[0]]
            }

    sys_prompt = SYSTEM_PROMPT.format(LANGUAGE_MODE=lang_instruction)
    user_prompt = EXPLAIN_PROMPT_TEMPLATE.format(
        topic=topic,
        grade=6,
        language_instruction=lang_instruction
    )

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response_json = await llm_service.get_chat_completion(messages, response_format={"type": "json_object"})
        response_json["mode"] = "explain"
        response_json["language_mode"] = language_mode
        response_json["source_mode"] = False
        return response_json
    except Exception as e:
        logger.error(f"Fallback to mock database for topic '{topic}' due to LLM error: {e}")
        if language_mode == "default":
            eng = _get_mock_explanation(topic_lower, "english", topic)
            hing = _get_mock_explanation(topic_lower, "hinglish", topic)
            return {
                "mode": "explain",
                "title": eng["title"],
                "grade_level": eng["grade_level"],
                "bullets": eng["bullets"],
                "example": eng["example"],
                "recap": eng["recap"],
                "response_text": hing["response_text"],
                "language_mode": "default"
            }
        else:
            return _get_mock_explanation(topic_lower, language_mode, topic)
