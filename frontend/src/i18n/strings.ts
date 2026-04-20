export type Lang = "en" | "hi";

export const STRINGS: Record<
  Lang,
  Record<string, string>
> = {
  en: {
    appTitle: "Ai legal assistant",
    tagline: "AI-assisted incident intake",
    disclaimerShort:
      "Outputs may be incomplete and should be reviewed before taking action.",
    startNow: "Start now",
    chooseLang: "Language",
    chooseCity: "Location context (optional)",
    acceptDisclaimer: "I understand the assistant may be incomplete and requires review.",
    landingHint: "Describe the incident in your preferred language and add optional context if useful.",
    chatPlaceholder: "Describe what happened…",
    send: "Send",
    buildPlan: "Build action plan",
    actionPlan: "Action plan",
    confidence: "Confidence",
    whyAdvice: "Why this advice?",
    whyStep: "Why this step?",
    evidenceTitle: "Evidence checklist",
    cityLinks: "City & portals",
    clarifyTitle: "We need a bit more detail",
    continueChat: "Reply in chat with details, then tap Build action plan.",
    urgencyHigh: "High urgency — prioritize safety and quick reporting.",
    urgencyCritical: "Critical — secure funds/accounts immediately.",
    lawyerCta: "Prepared for provider-backed AI workflows",
    thumbsHelpful: "Was this helpful?",
    thanksFeedback: "Thanks for the feedback.",
    loading: "Working…",
    stepOptionalDocs: "Documents",
  },
  hi: {
    appTitle: "एआई साइबर अपराध शिकायत मार्गदर्शन",
    tagline: "एआई-सहायित घटना इनटेक",
    disclaimerShort:
      "उत्पन्न आउटपुट अपूर्ण हो सकता है और कार्रवाई से पहले उसकी समीक्षा करनी चाहिए।",
    startNow: "अभी शुरू करें",
    chooseLang: "भाषा",
    chooseCity: "स्थान संदर्भ (वैकल्पिक)",
    acceptDisclaimer: "मैं समझता/समझती हूँ कि सहायक का आउटपुट अपूर्ण हो सकता है और उसकी समीक्षा आवश्यक है।",
    landingHint: "अपनी पसंदीदा भाषा में घटना लिखें और जरूरत हो तो अतिरिक्त संदर्भ जोड़ें।",
    chatPlaceholder: "क्या हुआ, लिखें…",
    send: "भेजें",
    buildPlan: "कार्य योजना बनाएं",
    actionPlan: "कार्य योजना",
    confidence: "विश्वास स्तर",
    whyAdvice: "यह सलाह क्यों?",
    whyStep: "यह कदम क्यों?",
    evidenceTitle: "साक्ष्य सूची",
    cityLinks: "शहर व पोर्टल",
    clarifyTitle: "थोड़ी और जानकारी चाहिए",
    continueChat: "चैट में विवरण दें, फिर कार्य योजना बनाएं दबाएं।",
    urgencyHigh: "उच्च तात्कालिकता — सुरक्षा और त्वरित रिपोर्टिंग प्राथमिक।",
    urgencyCritical: "गंभीर — तुरंत खाता/धन सुरक्षित करें।",
    lawyerCta: "प्रदाता-आधारित एआई वर्कफ़्लो के लिए तैयार",
    thumbsHelpful: "क्या यह उपयोगी था?",
    thanksFeedback: "प्रतिक्रिया के लिए धन्यवाद।",
    loading: "काम जारी…",
    stepOptionalDocs: "दस्तावेज़",
  },
};

export function t(lang: Lang, key: keyof typeof STRINGS.en): string {
  return STRINGS[lang][key as string] ?? STRINGS.en[key as string] ?? key;
}
