import re
import logging
from typing import Dict, Any, List
from app.services.llm_service import llm_service
from app.services.source_ingest import source_ingest_service
from app.services.retrieval import retrieve_relevant_chunks
from app.services.language_router import detect_language_details
from app.services.prompts import (
    SYSTEM_PROMPT, QUIZ_PROMPT_TEMPLATE, LANGUAGE_INSTRUCTIONS,
    SOURCE_SYSTEM_PROMPT, SOURCE_QUIZ_PROMPT_TEMPLATE
)

logger = logging.getLogger(__name__)

def _get_mock_quiz(topic_lower: str, language_mode: str, topic: str, count: int) -> Dict[str, Any]:
    # Local Knowledge Base Fallback
    if "fraction" in topic_lower or "bhinn" in topic_lower:
        if language_mode == "english":
            title = f"Quick Check: {topic}"
            instructions = "Answer the following questions. Each question has 3 options."
            response_text = f"Alright children, let's take a short quiz of {count} questions on fractions. Listen carefully!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "What is 1 part of a bread slice divided equally into 4 parts?",
                    "options": ["1/2 (Half)", "1/4 (Quarter)", "3/4 (Three-quarters)"],
                    "correct_answer": "1/4 (Quarter)"
                },
                {
                    "id": 2,
                    "question": "In fraction 3/4, which number is the numerator?",
                    "options": ["3", "4", "7"],
                    "correct_answer": "3"
                },
                {
                    "id": 3,
                    "question": "What do you get by joining half (1/2) bread and half (1/2) bread?",
                    "options": ["Half", "One whole", "One and a half"],
                    "correct_answer": "One whole"
                },
                {
                    "id": 4,
                    "question": "If the numerator and denominator are equal (like 5/5), what is the fraction value?",
                    "options": ["0", "1", "5"],
                    "correct_answer": "1"
                },
                {
                    "id": 5,
                    "question": "What is the sum of 1/3 and 1/3?",
                    "options": ["2/3", "1/6", "2/6"],
                    "correct_answer": "2/3"
                }
            ]
        elif language_mode == "hindi":
            title = f"त्वरित जांच: {topic}"
            instructions = "नीचे दिए गए प्रश्नों के उत्तर दें। प्रत्येक प्रश्न के 3 विकल्प हैं।"
            response_text = f"चलो बच्चों, अब भिन्न पर एक छोटा सा {count} प्रश्नों का टेस्ट लेते हैं। ध्यान से सुनना!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "रोटी के 4 बराबर हिस्सों में से एक हिस्सा क्या कहलाएगा?",
                    "options": ["1/2 (आधा)", "1/4 (एक-चौथाई)", "3/4 (तीन-चौथाई)"],
                    "correct_answer": "1/4 (एक-चौथाई)"
                },
                {
                    "id": 2,
                    "question": "भिन्न 3/4 में अंश (numerator) कौन सी संख्या है?",
                    "options": ["3", "4", "7"],
                    "correct_answer": "3"
                },
                {
                    "id": 3,
                    "question": "आधी (1/2) रोटी और आधी (1/2) रोटी मिलकर कितनी रोटी बनती है?",
                    "options": ["आधा", "एक पूरी", "डेढ़ (1.5)"],
                    "correct_answer": "एक पूरी"
                },
                {
                    "id": 4,
                    "question": "यदि अंश और हर बराबर हों (जैसे 5/5), तो भिन्न का मान क्या होगा?",
                    "options": ["0", "1", "5"],
                    "correct_answer": "1"
                },
                {
                    "id": 5,
                    "question": "1/3 और 1/3 को जोड़ने पर क्या आएगा?",
                    "options": ["2/3", "1/6", "2/6"],
                    "correct_answer": "2/3"
                }
            ]
        else:
            title = f"Quick Check: {topic}"
            instructions = "Niche diye gaye sawalon ke jawab dein. Har sawal ke 3 options hain."
            response_text = f"Chalo bachon, ab {topic} par ek chota sa {count} sawal ka test lete hain. Dhyan se sunna!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "Roti ke 4 barabar hisson mein se ek hissa kya kehlayega?",
                    "options": ["1/2 (Aadha)", "1/4 (Ek-chouthai)", "3/4 (Teen-chouthai)"],
                    "correct_answer": "1/4 (Ek-chouthai)"
                },
                {
                    "id": 2,
                    "question": "Fraction 3/4 mein numerator (ansh) kaun sa number hai?",
                    "options": ["3", "4", "7"],
                    "correct_answer": "3"
                },
                {
                    "id": 3,
                    "question": "Aadhi (1/2) roti aur aadhi (1/2) roti milkar kitni roti banti hai?",
                    "options": ["Aadha", "Ek poori", "Dedh (1.5)"],
                    "correct_answer": "Ek poori"
                },
                {
                    "id": 4,
                    "question": "Agar numerator aur denominator barabar hon (jaise 5/5), toh fraction ki value kya hogi?",
                    "options": ["0", "1", "5"],
                    "correct_answer": "1"
                },
                {
                    "id": 5,
                    "question": "1/3 aur 1/3 ko jodne par kya aayega?",
                    "options": ["2/3", "1/6", "2/6"],
                    "correct_answer": "2/3"
                }
            ]
        
    elif "food chain" in topic_lower or "aahar" in topic_lower or "foodchain" in topic_lower:
        if language_mode == "english":
            title = f"Quick Check: {topic}"
            instructions = "Answer the following questions. Each question has 3 options."
            response_text = f"Alright children, let's take a short quiz of {count} questions on food chain. Listen carefully!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "Who comes first (producer) in a food chain?",
                    "options": ["Grass and Plants", "Lion", "Frog"],
                    "correct_answer": "Grass and Plants"
                },
                {
                    "id": 2,
                    "question": "If grass is eaten by an insect, and insect by a frog, what is the frog?",
                    "options": ["Producer", "Primary Consumer", "Secondary Consumer"],
                    "correct_answer": "Secondary Consumer"
                },
                {
                    "id": 3,
                    "question": "What is the job of decomposers (like worms and fungi)?",
                    "options": ["Making soil fertile", "Stealing food", "Blocking sunlight"],
                    "correct_answer": "Making soil fertile"
                },
                {
                    "id": 4,
                    "question": "Where do plants get their energy from to grow?",
                    "options": ["From sunlight", "From coal", "From air"],
                    "correct_answer": "From sunlight"
                },
                {
                    "id": 5,
                    "question": "If all plants are destroyed in a field, how will it affect herbivores?",
                    "options": ["They will die or migrate", "They will start eating meat", "Nothing will change"],
                    "correct_answer": "They will die or migrate"
                }
            ]
        elif language_mode == "hindi":
            title = f"त्वरित जांच: {topic}"
            instructions = "नीचे दिए गए प्रश्नों के उत्तर दें। प्रत्येक प्रश्न के 3 विकल्प हैं।"
            response_text = f"चलो बच्चों, अब खाद्य श्रृंखला पर एक छोटा सा {count} प्रश्नों का टेस्ट लेते हैं। ध्यान से सुनना!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "खाद्य श्रृंखला में सबसे पहले (उत्पादक) कौन आता है?",
                    "options": ["घास और पौधे", "शेर", "मेढक"],
                    "correct_answer": "घास और पौधे"
                },
                {
                    "id": 2,
                    "question": "यदि घास को कीड़ा खाए और कीड़े को मेढक, तो मेढक क्या है?",
                    "options": ["उत्पादक", "प्राथमिक उपभोक्ता", "द्वितीयक उपभोक्ता"],
                    "correct_answer": "द्वितीयक उपभोक्ता"
                },
                {
                    "id": 3,
                    "question": "अपघटक (जैसे केंचुआ और कवक) का क्या काम है?",
                    "options": ["मिट्टी को उपजाऊ बनाना", "भोजन चुराना", "धूप रोकना"],
                    "correct_answer": "मिट्टी को उपजाऊ बनाना"
                },
                {
                    "id": 4,
                    "question": "पेड़-पौधे बढ़ने के लिए अपनी ऊर्जा कहाँ से लेते हैं?",
                    "options": ["सूरज की धूप से", "कोयले से", "हवा से"],
                    "correct_answer": "सूरज की धूप से"
                },
                {
                    "id": 5,
                    "question": "यदि किसी खेत से सारे पौधे खत्म हो जाएं, तो शाकाहारी जानवरों पर क्या असर पड़ेगा?",
                    "options": ["वे मर जाएंगे या चले जाएंगे", "वे मांस खाने लगेंगे", "कुछ नहीं बदलेगा"],
                    "correct_answer": "वे मर जाएंगे या चले जाएंगे"
                }
            ]
        else:
            title = f"Quick Check: {topic}"
            instructions = "Niche diye gaye sawalon ke jawab dein. Har sawal ke 3 options hain."
            response_text = f"Chalo bachon, ab {topic} par ek chota sa {count} sawal ka test lete hain. Dhyan se sunna!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "Food chain mein sabse pehle (producer/utpadak) kaun aata hai?",
                    "options": ["Ghaas aur Paudhe", "Sher", "Mendhak"],
                    "correct_answer": "Ghaas aur Paudhe"
                },
                {
                    "id": 2,
                    "question": "Agar ghaas ko keeda khaye aur keede ko mendhak, toh mendhak kya hai?",
                    "options": ["Producer", "Primary Consumer", "Secondary Consumer"],
                    "correct_answer": "Secondary Consumer"
                },
                {
                    "id": 3,
                    "question": "Decomposers (jaise kachra saaf karne wale keede aur fungus) ka kya kaam hai?",
                    "options": ["Mitti ko upjau banana", "Khana churana", "Dhoop rokna"],
                    "correct_answer": "Mitti ko upjau banana"
                },
                {
                    "id": 4,
                    "question": "Ped-paudhe badhne ke liye apni energy kahan se lete hain?",
                    "options": ["Suraj ki dhoop se", "Koyle se", "Hawa se"],
                    "correct_answer": "Suraj ki dhoop se"
                },
                {
                    "id": 5,
                    "question": "Agar kisi khet se saare paudhe khatam ho jayein, toh shakahari janwaron par kya asar padega?",
                    "options": ["Woh mar jayenge ya chale jayenge", "Woh maans khane lagenge", "Kucch nahi badlega"],
                    "correct_answer": "Woh mar jayenge ya chale jayenge"
                }
            ]
        
    elif "photosynthesis" in topic_lower:
        if language_mode == "english":
            title = f"Quick Check: {topic}"
            instructions = "Answer the following questions. Each question has 3 options."
            response_text = f"Alright children, let's take a short quiz of {count} questions on photosynthesis. Listen carefully!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "Which gas do plants use to make their food?",
                    "options": ["Carbon Dioxide", "Oxygen", "Nitrogen"],
                    "correct_answer": "Carbon Dioxide"
                },
                {
                    "id": 2,
                    "question": "Which green pigment in leaves absorbs sunlight?",
                    "options": ["Chlorophyll", "Hemoglobin", "Melanin"],
                    "correct_answer": "Chlorophyll"
                },
                {
                    "id": 3,
                    "question": "Which gas do plants release during photosynthesis?",
                    "options": ["Oxygen", "Carbon Dioxide", "Hydrogen"],
                    "correct_answer": "Oxygen"
                },
                {
                    "id": 4,
                    "question": "If there is no sunlight, can plants make their food?",
                    "options": ["No", "Yes", "Only at night"],
                    "correct_answer": "No"
                },
                {
                    "id": 5,
                    "question": "Where do plants run their kitchen (food production)?",
                    "options": ["In leaves", "In roots", "In flowers"],
                    "correct_answer": "In leaves"
                }
            ]
        elif language_mode == "hindi":
            title = f"त्वरित जांच: {topic}"
            instructions = "नीचे दिए गए प्रश्नों के उत्तर दें। प्रत्येक प्रश्न के 3 विकल्प हैं।"
            response_text = f"चलो बच्चों, अब प्रकाश संश्लेषण पर एक छोटा सा {count} प्रश्नों का टेस्ट लेते हैं। ध्यान से सुनना!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "पेड़-पौधे भोजन बनाने के लिए किस गैस का उपयोग करते हैं?",
                    "options": ["कार्बन डाइऑक्साइड", "ऑक्सीजन", "नाइट्रोजन"],
                    "correct_answer": "कार्बन डाइऑक्साइड"
                },
                {
                    "id": 2,
                    "question": "पत्तियों में कौन सा हरा वर्णक (pigment) धूप सोखता है?",
                    "options": ["क्लोरोफिल", "हीमोग्लोबिन", "मेलेनिन"],
                    "correct_answer": "क्लोरोफिल"
                },
                {
                    "id": 3,
                    "question": "प्रकाश संश्लेषण के दौरान पौधे कौन सी गैस छोड़ते हैं?",
                    "options": ["ऑक्सीजन", "कार्बन डाइऑक्साइड", "हाइड्रोजन"],
                    "correct_answer": "ऑक्सीजन"
                },
                {
                    "id": 4,
                    "question": "अगर धूप न हो, तो क्या पौधे अपना भोजन बना पाएंगे?",
                    "options": ["नहीं", "हाँ", "सिर्फ रात को"],
                    "correct_answer": "नहीं"
                },
                {
                    "id": 5,
                    "question": "पौधे अपना भोजन मुख्य रूप से कहाँ बनाते हैं?",
                    "options": ["पत्तियों में", "जड़ों में", "फूलों में"],
                    "correct_answer": "पत्तियों में"
                }
            ]
        else:
            title = f"Quick Check: {topic}"
            instructions = "Niche diye gaye sawalon ke jawab dein. Har sawal ke 3 options hain."
            response_text = f"Chalo bachon, ab {topic} par ek chota sa {count} sawal ka test lete hain. Dhyan se sunna!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "Ped-paudhe khana banane ke liye kis gas ka use karte hain?",
                    "options": ["Carbon Dioxide", "Oxygen", "Nitrogen"],
                    "correct_answer": "Carbon Dioxide"
                },
                {
                    "id": 2,
                    "question": "Plants ke patton mein kaun sa green pigment dhoop sokhta hai?",
                    "options": ["Chlorophyll", "Hemoglobin", "Melanin"],
                    "correct_answer": "Chlorophyll"
                },
                {
                    "id": 3,
                    "question": "Photosynthesis process ke dauran plants kaun si gas chhodte hain?",
                    "options": ["Oxygen", "Carbon Dioxide", "Hydrogen"],
                    "correct_answer": "Oxygen"
                },
                {
                    "id": 4,
                    "question": "Agar dhoop na ho, toh kya ped apna khana bana payenge?",
                    "options": ["Nahi", "Haan", "Sirf raat ko"],
                    "correct_answer": "Nahi"
                },
                {
                    "id": 5,
                    "question": "Plants apni rasoi (food production) kahan chalate hain?",
                    "options": ["Patton (Leaves) mein", "Jadon (Roots) mein", "Phoolon (Flowers) mein"],
                    "correct_answer": "Patton (Leaves) mein"
                }
            ]
        
    elif "gravity" in topic_lower or "gurutva" in topic_lower:
        if language_mode == "english":
            title = f"Quick Check: {topic}"
            instructions = "Answer the following questions. Each question has 3 options."
            response_text = f"Alright children, let's take a short quiz of {count} questions on gravity. Listen carefully!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "Why does an apple fall to the ground when it falls from a tree?",
                    "options": ["Due to gravity", "Due to wind", "Due to the tree"],
                    "correct_answer": "Due to gravity"
                },
                {
                    "id": 2,
                    "question": "Is gravity on the moon the same as on the earth?",
                    "options": ["Less than the earth", "More than the earth", "Exactly the same"],
                    "correct_answer": "Less than the earth"
                },
                {
                    "id": 3,
                    "question": "What would happen if there was no gravity?",
                    "options": ["We and all objects would float in the air", "We would stick to the ground", "Nothing would change"],
                    "correct_answer": "We and all objects would float in the air"
                },
                {
                    "id": 4,
                    "question": "Which great scientist discovered gravity?",
                    "options": ["Isaac Newton", "Albert Einstein", "Galileo"],
                    "correct_answer": "Isaac Newton"
                },
                {
                    "id": 5,
                    "question": "If we drop a heavy stone and a light leaf without air resistance, what will happen?",
                    "options": ["Both will land at the same time", "Stone will fall first", "Leaf will fall first"],
                    "correct_answer": "Both will land at the same time"
                }
            ]
        elif language_mode == "hindi":
            title = f"त्वरित जांच: {topic}"
            instructions = "नीचे दिए गए प्रश्नों के उत्तर दें। प्रत्येक प्रश्न के 3 विकल्प हैं।"
            response_text = f"चलो बच्चों, अब गुरुत्वाकर्षण पर एक छोटा सा {count} प्रश्नों का टेस्ट लेते हैं। ध्यान से सुनना!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "पेड़ से टूटने पर सेब ज़मीन पर ही क्यों गिरता है?",
                    "options": ["गुरुत्वाकर्षण की वजह से", "हवा की वजह से", "पेड़ की वजह से"],
                    "correct_answer": "गुरुत्वाकर्षण की वजह से"
                },
                {
                    "id": 2,
                    "question": "क्या चाँद पर भी गुरुत्वाकर्षण पृथ्वी जितना ही होता है?",
                    "options": ["पृथ्वी से कम होता है", "पृथ्वी से ज़्यादा होता है", "बिल्कुल बराबर होता है"],
                    "correct_answer": "पृथ्वी से कम होता है"
                },
                {
                    "id": 3,
                    "question": "अगर गुरुत्वाकर्षण न हो, तो क्या होगा?",
                    "options": ["हम और सभी चीज़ें हवा में उड़ने लगेंगे", "हम ज़मीन पर चिपक जाएंगे", "कुछ नहीं बदलेगा"],
                    "correct_answer": "हम और सभी चीज़ें हवा में उड़ने लगेंगे"
                },
                {
                    "id": 4,
                    "question": "गुरुत्वाकर्षण की खोज किस महान वैज्ञानिक ने की थी?",
                    "options": ["आइज़क न्यूटन", "अल्बर्ट आइंस्टीन", "गैलिलियो"],
                    "correct_answer": "आइज़क न्यूटन"
                },
                {
                    "id": 5,
                    "question": "अगर हम एक भारी पत्थर और एक हल्के पत्ते को बिना हवा के प्रतिरोध के गिराएं, तो क्या होगा?",
                    "options": ["दोनों एक साथ ज़मीन पर गिरेंगे", "पत्थर पहले गिरेगा", "पत्ता पहले गिरेगा"],
                    "correct_answer": "दोनों एक साथ ज़मीन पर गिरेंगे"
                }
            ]
        else:
            title = f"Quick Check: {topic}"
            instructions = "Niche diye gaye sawalon ke jawab dein. Har sawal ke 3 options hain."
            response_text = f"Chalo bachon, ab {topic} par ek chota sa {count} sawal ka test lete hain. Dhyan se sunna!"
            questions_pool = [
                {
                    "id": 1,
                    "question": "Ped se tutne par seb zameen par hi kyu girta hai?",
                    "options": ["Gravity ki wajah se", "Hawa ki wajah se", "Ped ki wajah se"],
                    "correct_answer": "Gravity ki wajah se"
                },
                {
                    "id": 2,
                    "question": "Kya chaand (moon) par bhi gravity dharti jitni hi hoti hai?",
                    "options": ["Dharti se kam hoti hai", "Dharti se zyada hoti hai", "Bilkul barabar hoti hai"],
                    "correct_answer": "Dharti se kam hoti hai"
                },
                {
                    "id": 3,
                    "question": "Agar gravity na ho, toh kya hoga?",
                    "options": ["Hum aur sabhi cheezein hawa mein udne lagenge", "Hum zameen par chipak jayenge", "Kuch nahi badlega"],
                    "correct_answer": "Hum aur sabhi cheezein hawa mein udne lagenge"
                },
                {
                    "id": 4,
                    "question": "Gravity ki khoj kis mahan scientist ne ki thi?",
                    "options": ["Isaac Newton", "Albert Einstein", "Galileo"],
                    "correct_answer": "Isaac Newton"
                },
                {
                    "id": 5,
                    "question": "Agar hum ek bhari patthar aur ek halka patte ko bina air resistance ke girayein, toh kya hoga?",
                    "options": ["Dono ek saath zameen par girenge", "Patthar pehle girega", "Patta pehle girega"],
                    "correct_answer": "Dono ek saath zameen par girenge"
                }
            ]

    else:
        if language_mode == "english":
            title = f"Quick Check: {topic}"
            instructions = "Answer the following questions. Each question has 3 options."
            response_text = f"Alright children, let's take a short quiz of {count} questions on {topic}. Listen carefully!"
            questions_pool = [
                {
                    "id": 1,
                    "question": f"Is {topic} connected to our daily life?",
                    "options": ["Yes, everywhere", "No, only in books", "Do not know"],
                    "correct_answer": "Yes, everywhere"
                },
                {
                    "id": 2,
                    "question": f"What is the best way to understand {topic}?",
                    "options": ["By rote learning", "By understanding concepts and asking questions", "Doing nothing"],
                    "correct_answer": "By understanding concepts and asking questions"
                },
                {
                    "id": 3,
                    "question": f"Do we use {topic} in problem solving?",
                    "options": ["Yes", "No", "Only in exams"],
                    "correct_answer": "Yes"
                }
            ]
        elif language_mode == "hindi":
            title = f"त्वरित जांच: {topic}"
            instructions = f"नीचे दिए गए प्रश्नों के उत्तर दें। प्रत्येक प्रश्न के 3 विकल्प हैं।"
            response_text = f"चलो बच्चों, अब {topic} पर एक छोटा सा {count} प्रश्नों का टेस्ट लेते हैं। ध्यान से सुनना!"
            questions_pool = [
                {
                    "id": 1,
                    "question": f"क्या {topic} हमारे दैनिक जीवन से जुड़ा हुआ है?",
                    "options": ["हाँ, हर जगह", "नहीं, सिर्फ किताबों में", "पता नहीं"],
                    "correct_answer": "हाँ, हर जगह"
                },
                {
                    "id": 2,
                    "question": f"{topic} को समझने का सबसे अच्छा तरीका क्या है?",
                    "options": ["रट्टा मारना", "सिद्धांतों को समझना और सवाल पूछना", "कुछ न करना"],
                    "correct_answer": "सिद्धांतों को समझना और सवाल पूछना"
                },
                {
                    "id": 3,
                    "question": f"क्या हम समस्या सुलझाने में {topic} का उपयोग करते हैं?",
                    "options": ["हाँ", "नहीं", "सिर्फ परीक्षा में"],
                    "correct_answer": "हाँ"
                }
            ]
        else:
            title = f"Quick Check: {topic}"
            instructions = "Niche diye gaye sawalon ke jawab dein. Har sawal ke 3 options hain."
            response_text = f"Chalo bachon, ab {topic} par ek chota sa {count} sawal ka test lete hain. Dhyan se sunna!"
            questions_pool = [
                {
                    "id": 1,
                    "question": f"Kya {topic} hamare daily life se juda hua hai?",
                    "options": ["Haan, har jagah", "Nahi, sirf books mein", "Pata nahi"],
                    "correct_answer": "Haan, har jagah"
                },
                {
                    "id": 2,
                    "question": f"{topic} ko samajhne ka sabse accha tareeqa kya hai?",
                    "options": ["Ratta marna", "Concepts ko samajhna aur sawal poochna", "Kucch na karna"],
                    "correct_answer": "Concepts ko samajhna aur sawal poochna"
                },
                {
                    "id": 3,
                    "question": f"Kya hum {topic} ka use problem solving mein karte hain?",
                    "options": ["Haan", "Nahi", "Sirf exams mein"],
                    "correct_answer": "Haan"
                }
            ]
        
    questions = questions_pool[:count]
    answer_key = [f"{q['id']}: {q['correct_answer']}" for q in questions]
    
    return {
        "mode": "quiz",
        "title": title,
        "instructions": instructions,
        "questions": questions,
        "answer_key": answer_key,
        "response_text": response_text,
        "language_mode": language_mode
    }

def normalize_quiz_question(q: dict) -> dict:
    options = q.get("options", [])
    
    # If correct_index is already there, use it
    if "correct_index" in q and isinstance(q["correct_index"], int):
        correct_index = q["correct_index"]
    else:
        # Try to find correct_answer in options
        correct_answer = q.get("correct_answer") or q.get("answer") or ""
        correct_index = 0
        for idx, opt in enumerate(options):
            if str(opt).lower() == str(correct_answer).lower() or str(correct_answer).lower() in str(opt).lower():
                correct_index = idx
                break
                
    explanation = q.get("explanation") or f"The correct option is: {options[correct_index] if correct_index < len(options) else ''}"
    
    return {
        "question": q.get("question", ""),
        "options": options,
        "correct_index": correct_index,
        "explanation": explanation
    }

async def generate_quiz(session_id: str, text: str, language_mode: str = "hinglish", source_mode: bool = False):
    """
    Generate quiz using the live LLM, falling back to a structured mock database if the LLM fails.
    """
    # Extract number of questions if present (default to 7, range 5–10)
    match = re.search(r'\b(\d+)\b', text)
    count = int(match.group(1)) if match else 7
    if count < 5:
        count = 5
    elif count > 10:
        count = 10
        
    # Extract a rough topic (mock logic using word boundaries)
    clean_text = text.lower()
    for char in [".", ",", "?", "!", "\"", "'"]:
        clean_text = clean_text.replace(char, " ")
        
    stop_words = [
        "create", "generate", "start", "quiz", "test", "mcq", "question", "questions", "on", "of", "about",
        "for class 6", "for class 7", "for class 8", "for class 5", "a", "an", "the", "make",
        "in english", "english mein", "english me", "in hindi", "hindi mein", "hindi me", "pure hindi"
    ]
    for word in stop_words:
        clean_text = re.sub(rf'\b{re.escape(word)}\b', ' ', clean_text)
        
    clean_text = re.sub(r'\b\d+\b', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    topic = clean_text.title() or "Fractions"
    topic_lower = topic.lower()

    _, is_explicit = detect_language_details(text)
    actual_lang = "hinglish_explicit" if (language_mode == "hinglish" and is_explicit) else language_mode
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(actual_lang, LANGUAGE_INSTRUCTIONS["hinglish"])


    if source_mode:
        all_sources = source_ingest_service.list_sources()
        if not all_sources:
            return {
                "mode": "quiz",
                "title": "No Source Uploaded",
                "response_text": "Please upload some classroom materials first in the sources panel.",
                "questions": [],
                "citations": []
            }

        chunks = retrieve_relevant_chunks(text, limit=3)
        chunks = [c.model_dump() for c in chunks]
        if not chunks:
            return {
                "mode": "quiz",
                "title": "Not Found",
                "response_text": "I cannot find the answer to this question in the provided source material.",
                "questions": [],
                "citations": []
            }

        snippets_str = "\n---\n".join([f"Source: {c['source_title']} (Page {c['page_number']}):\n{c['text']}" for c in chunks])
        sys_prompt = SOURCE_SYSTEM_PROMPT.format(LANGUAGE_MODE=lang_instruction)
        user_prompt = SOURCE_QUIZ_PROMPT_TEMPLATE.format(
            topic=topic,
            count=count,
            language_instruction=lang_instruction,
            snippets=snippets_str
        )

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
            response_json = await llm_service.get_chat_completion([
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ], response_format={"type": "json_object"}, task_type="quiz")
            
            raw_questions = response_json.get("questions", [])
            normalized_questions = [normalize_quiz_question(q) for q in raw_questions]
            
            ans_text = response_json.get("response_text") or response_json.get("answer_text")
            if "provided source material" in str(ans_text).lower() or response_json.get("title") == "Not Found":
                cits = []
            else:
                cits = citations
                
            return {
                "title": response_json.get("title", f"Quiz on {topic}"),
                "response_text": ans_text,
                "questions": normalized_questions,
                "citations": cits
            }
        except Exception as e:
            logger.error(f"Source quiz generation failed: {e}")
            top_chunk = chunks[0]
            q_text = f"According to the source document '{top_chunk['source_title']}', what is the main concept discussed in the following text: '{top_chunk['text'][:80]}...'?"
            return {
                "title": f"Quiz from {top_chunk['source_title']}",
                "response_text": "I compiled a short quiz from your source document. Let's see how much we understand!",
                "questions": [
                    {
                        "question": q_text,
                        "options": ["A key classroom concept", "An unrelated topic", "I don't know"],
                        "correct_index": 0,
                        "explanation": f"The main concept is discussed at the start of the source document: {top_chunk['text'][:50]}..."
                    }
                ],
                "citations": [citations[0]]
            }

    # Standard Quiz Mode
    sys_prompt = SYSTEM_PROMPT.format(LANGUAGE_MODE=lang_instruction)
    user_prompt = QUIZ_PROMPT_TEMPLATE.format(
        topic=topic,
        count=count,
        language_instruction=lang_instruction
    )

    try:
        response_json = await llm_service.get_chat_completion([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ], response_format={"type": "json_object"}, task_type="quiz")
        
        raw_questions = response_json.get("questions", [])
        normalized_questions = [normalize_quiz_question(q) for q in raw_questions]

        # If LLM returned an empty questions list (soft rate-limit or model refusal)
        # fall through to the mock database rather than returning an empty quiz.
        if not normalized_questions:
            raise ValueError("LLM returned 0 questions — triggering mock fallback")

        return {
            "title": response_json.get("title", f"Quiz on {topic}"),
            "response_text": response_json.get("response_text") or response_json.get("answer_text"),
            "questions": normalized_questions
        }
    except Exception as e:
        logger.error(f"LLM quiz generation failed: {e}")
        mock_lang = "english" if language_mode == "english" else ("hindi" if language_mode == "hindi" else "hinglish")
        
        # Merge English written content with Hinglish spoken if default (which maps to hinglish/default here)
        if language_mode == "default" or language_mode == "hinglish":
            eng = _get_mock_quiz(topic_lower, "english", topic, count)
            hing = _get_mock_quiz(topic_lower, "hinglish", topic, count)
            questions = [normalize_quiz_question(q) for q in eng["questions"]]
            return {
                "title": eng["title"],
                "response_text": hing["response_text"],
                "questions": questions
            }
        else:
            mock_data = _get_mock_quiz(topic_lower, mock_lang, topic, count)
            questions = [normalize_quiz_question(q) for q in mock_data["questions"]]
            return {
                "title": mock_data["title"],
                "response_text": mock_data["response_text"],
                "questions": questions
            }
