from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CityAuthority, LegalReference, PathwayTemplate, Rule


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(Rule).limit(1)):
        return

    refs = [
        LegalReference(
            act_name="Information Technology Act, 2000",
            section_code="Sec. 66",
            short_text_en="Computer-related offences including dishonest or fraudulent conduct.",
            short_text_hi="कंप्यूटर से जुड़े अपराध — बेईमानी या धोखाधड़ी संबंधी आचरण।",
            source_url="https://indiankanoon.org/",
            active=True,
        ),
        LegalReference(
            act_name="Information Technology Act, 2000",
            section_code="Sec. 66C",
            short_text_en="Identity theft — fraudulent use of electronic signature, password, etc.",
            short_text_hi="पहचान चोरी — इलेक्ट्रॉनिक हस्ताक्षर/पासवर्ड का धोखाधड़ीपूर्ण उपयोग।",
            source_url="https://indiankanoon.org/",
            active=True,
        ),
        LegalReference(
            act_name="Information Technology Act, 2000",
            section_code="Sec. 66D",
            short_text_en="Cheating by personation using computer resource.",
            short_text_hi="कंप्यूटर संसाधन का उपयोग कर किसी की छवि बनाकर धोखाधड़ी।",
            source_url="https://indiankanoon.org/",
            active=True,
        ),
        LegalReference(
            act_name="IPC (as applicable)",
            section_code="Cheating / Criminal breach",
            short_text_en="General penal provisions for cheating or criminal breach of trust.",
            short_text_hi="धोखाधड़ी या विश्वासघात से संबंधित दंड प्रावधान (जहाँ लागू)।",
            source_url="https://indiankanoon.org/",
            active=True,
        ),
    ]
    for r in refs:
        db.add(r)
    db.flush()

    rules = [
        Rule(
            issue_type="account_hacking",
            conditions_json={},
            priority=100,
            actions_json={"urgency": "high", "prepend_steps": []},
            legal_ref_ids=[1, 2, 3],
            active=True,
        ),
        Rule(
            issue_type="payment_fraud",
            conditions_json={"time_since_incident_hours": {"lte": 24}},
            priority=110,
            actions_json={
                "urgency": "critical",
                "prepend_steps": [
                    "en:Immediately contact your bank and block or secure the affected account/payment instrument.",
                    "en:Report on the National Cyber Crime Reporting Portal under Financial Fraud / online cheating.",
                    "hi:तुरंत अपने बैंक से संपर्क करें और प्रभावित खाता/भुगतान साधन सुरक्षित करें।",
                    "hi:राष्ट्रीय साइबर अपराध पोर्टल पर वित्तीय धोखाधड़ी श्रेणी में रिपोर्ट दर्ज करें।",
                ],
            },
            legal_ref_ids=[1, 3, 4],
            active=True,
        ),
        Rule(
            issue_type="impersonation",
            conditions_json={},
            priority=95,
            actions_json={"urgency": "normal", "prepend_steps": []},
            legal_ref_ids=[2, 3],
            active=True,
        ),
        Rule(
            issue_type="cyber_stalking_harassment",
            conditions_json={},
            priority=90,
            actions_json={"urgency": "high", "prepend_steps": []},
            legal_ref_ids=[1, 3, 4],
            active=True,
        ),
    ]
    for ru in rules:
        db.add(ru)

    cities = [
        CityAuthority(
            city="mumbai",
            state="Maharashtra",
            cyber_portal_url="https://www.cybercrime.gov.in/",
            police_portal_url="https://mahapolice.gov.in/",
            helpline_numbers=["1930", "100"],
            notes_en="Use the national portal first; follow up with local police / cyber cell for FIR.",
            notes_hi="पहले राष्ट्रीय पोर्टल का उपयोग करें; एफआईआर के लिए स्थानीय पुलिस/साइबर सेल से संपर्क करें।",
        ),
        CityAuthority(
            city="delhi",
            state="Delhi",
            cyber_portal_url="https://www.cybercrime.gov.in/",
            police_portal_url="https://delhipolice.gov.in/",
            helpline_numbers=["1930", "100", "1091"],
            notes_en="National portal reporting with Delhi Police cyber coordination.",
            notes_hi="दिल्ली पुलिस साइबर समन्वय के साथ राष्ट्रीय पोर्टल पर रिपोर्टिंग।",
        ),
        CityAuthority(
            city="bengaluru",
            state="Karnataka",
            cyber_portal_url="https://www.cybercrime.gov.in/",
            police_portal_url="https://ksp.karnataka.gov.in/",
            helpline_numbers=["1930", "100"],
            notes_en="National portal; Karnataka Police for local escalation in Bengaluru.",
            notes_hi="राष्ट्रीय पोर्टल; बेंगलुरु में स्थानीय स्तर पर कर्नातक पुलिस।",
        ),
    ]
    for c in cities:
        db.add(c)

    # pathway_templates: steps use keys title_en/title_hi or unified — generator will pick by lang
    def steps_account(lang: str) -> list:
        if lang == "en":
            return [
                {
                    "title": "National Cybercrime Reporting Portal",
                    "action": "File a complaint at https://www.cybercrime.gov.in/ under social media / account compromise.",
                    "expected_time": "Same day",
                    "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                    "docs_required": ["Screenshots", "Login alerts", "Email/SMS from platform"],
                },
                {
                    "title": "Preserve evidence",
                    "action": "Export chat logs, save metadata where possible; do not delete extortion messages.",
                    "expected_time": "Before filing",
                    "links": [],
                    "docs_required": ["Original screenshots (un-cropped if safe)", "Timeline of events"],
                },
                {
                    "title": "Platform recovery",
                    "action": "Use official in-app account recovery; enable 2FA after regaining access.",
                    "expected_time": "Parallel to police report",
                    "links": [],
                    "docs_required": ["Government ID for verification"],
                },
            ]
        return [
            {
                "title": "राष्ट्रीय साइबर अपराध पोर्टल",
                "action": "https://www.cybercrime.gov.in/ पर सोशल मीडिया / अकाउंट समझौता श्रेणी में शिकायत दर्ज करें।",
                "expected_time": "उसी दिन",
                "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                "docs_required": ["स्क्रीनशॉट", "लॉगिन अलर्ट", "प्लेटफ़ॉर्म से ईमेल/एसएमएस"],
            },
            {
                "title": "साक्ष्य सुरक्षित रखें",
                "action": "चैट लॉग निर्यात करें; संभव हो तो मेटाडेटा सहेजें; रंगदम या धमकी वाले संदेश न हटाएं।",
                "expected_time": "शिकायत से पहले",
                "links": [],
                "docs_required": ["मूल स्क्रीनशॉट", "घटनाओं का क्रम"],
            },
            {
                "title": "प्लेटफ़ॉर्म रिकवरी",
                "action": "आधिकारिक इन-ऐप रिकवरी का उपयोग करें; एक्सेस मिलने के बाद 2FA सक्षम करें।",
                "expected_time": "पुलिस रिपोर्ट के साथ",
                "links": [],
                "docs_required": ["सत्यापन हेतु सरकारी आईडी"],
            },
        ]

    def evidence_for(issue: str, lang: str) -> list:
        m = {
            "account_hacking": (
                ["Screenshots", "Platform emails", "Device logs"]
                if lang == "en"
                else ["स्क्रीनशॉट", "प्लेटफ़ॉर्म ईमेल", "डिवाइस लॉग"]
            ),
            "payment_fraud": (
                ["Transaction reference IDs", "Bank SMS", "Beneficiary details"]
                if lang == "en"
                else ["लेनदेन संदर्भ आईडी", "बैंक एसएमएस", "लाभार्थी विवरण"]
            ),
            "impersonation": (
                ["Profile URLs", "Impersonation messages", "Friend list evidence"]
                if lang == "en"
                else ["प्रोफ़ाइल यूआरएल", "प्रतिरूप संदेश", "प्रमाण के स्क्रीनशॉट"]
            ),
            "cyber_stalking_harassment": (
                ["Chronology", "Threat screenshots", "Caller IDs"]
                if lang == "en"
                else ["घटनाक्रम", "धमकी के स्क्रीनशॉट", "कॉलर आईडी"]
            ),
        }
        return m.get(issue, m["account_hacking"])

    issues = ["account_hacking", "payment_fraud", "impersonation", "cyber_stalking_harassment"]
    for issue in issues:
        for lang in ("en", "hi"):
            st = steps_account(lang) if issue == "account_hacking" else None
            if issue == "payment_fraud":
                st = (
                    [
                        {
                            "title": "Bank / PSP first",
                            "action": "Block instrument, report fraudulent debit via app helpline; save reference number.",
                            "expected_time": "Immediately",
                            "links": [],
                            "docs_required": ["Transaction ID", "Timestamp"],
                        },
                        {
                            "title": "National Cybercrime Reporting Portal",
                            "action": "File under financial fraud with full timeline.",
                            "expected_time": "Within 24 hours",
                            "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                            "docs_required": ["Bank acknowledgment"],
                        },
                    ]
                    if lang == "en"
                    else [
                        {
                            "title": "बैंक / पीएसपी पहले",
                            "action": "साधन ब्लॉक करें, ऐप हेल्पलाइन से धोखाधड़ी रिपोर्ट करें; संदर्भ संख्या सहेजें।",
                            "expected_time": "तुरंत",
                            "links": [],
                            "docs_required": ["लेनदेन आईडी", "समय"],
                        },
                        {
                            "title": "राष्ट्रीय साइबर अपराध पोर्टल",
                            "action": "पूर्ण समयरेखा के साथ वित्तीय धोखाधड़ी में शिकायत दर्ज करें।",
                            "expected_time": "24 घंटे में",
                            "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                            "docs_required": ["बैंक पावती"],
                        },
                    ]
                )
            if issue == "impersonation":
                st = (
                    [
                        {
                            "title": "Report impersonation",
                            "action": "NCRP + platform report fake profile; collect URLs and archives.",
                            "expected_time": "Same day",
                            "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                            "docs_required": ["URLs", "Screenshots", "Victim impact note"],
                        },
                        {
                            "title": "Police follow-up",
                            "action": "If funds solicited or reputational harm, visit police with ID and evidence.",
                            "expected_time": "As needed",
                            "links": [],
                            "docs_required": ["ID proof", "Printed evidence bundle"],
                        },
                    ]
                    if lang == "en"
                    else [
                        {
                            "title": "प्रतिरूपण रिपोर्ट",
                            "action": "एनसीआरपी + प्लेटफ़ॉर्म पर नकली प्रोफ़ाइल रिपोर्ट; यूआरएल व संग्रह।",
                            "expected_time": "उसी दिन",
                            "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                            "docs_required": ["यूआरएल", "स्क्रीनशॉट"],
                        },
                        {
                            "title": "पुलिस फॉलो-अप",
                            "action": "यदि धन मांगा गया या नुकसान हुआ, पहचान व साक्ष्य साथ लेकर पुलिस जाएं।",
                            "expected_time": "आवश्यकतानुसार",
                            "links": [],
                            "docs_required": ["पहचान पत्र", "प्रिंटेड साक्ष्य"],
                        },
                    ]
                )
            if issue == "cyber_stalking_harassment":
                st = (
                    [
                        {
                            "title": "Safety first",
                            "action": "If immediate physical risk, call 112/100; document every incident.",
                            "expected_time": "Immediate",
                            "links": [],
                            "docs_required": [],
                        },
                        {
                            "title": "NCRP + platform blocks",
                            "action": "File cyber complaint with timeline; block and report on platform.",
                            "expected_time": "Same day",
                            "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                            "docs_required": ["Screenshot trail", "Dates and times"],
                        },
                    ]
                    if lang == "en"
                    else [
                        {
                            "title": "सुरक्षा पहले",
                            "action": "यदि शारीरिक जोखिम हो, 112/100 पर कॉल करें; हर घटना दर्ज करें।",
                            "expected_time": "तुरंत",
                            "links": [],
                            "docs_required": [],
                        },
                        {
                            "title": "एनसीआरपी + ब्लॉक",
                            "action": "समयरेखा के साथ ऑनलाइन शिकायत; प्लेटफ़ॉर्म पर ब्लॉक व रिपोर्ट।",
                            "expected_time": "उसी दिन",
                            "links": [{"label": "NCRP", "url": "https://www.cybercrime.gov.in/"}],
                            "docs_required": ["स्क्रीनशॉट श्रृंखला", "तारीख/समय"],
                        },
                    ]
                )

            db.add(
                PathwayTemplate(
                    issue_type=issue,
                    lang=lang,
                    steps_json=st,
                    evidence_json=evidence_for(issue, lang),
                    escalation_json={"helpline": "1930"},
                )
            )

    db.flush()
