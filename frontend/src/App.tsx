import { useState } from "react";
import { AssistantPage } from "./app/AssistantPage";
import { LandingPage } from "./app/LandingPage";
import type { Lang } from "./i18n/strings";

export default function App() {
  const [screen, setScreen] = useState<"landing" | "assistant">("landing");
  const [lang, setLang] = useState<Lang>("en");
  const [city, setCity] = useState("");
  const [disclaimerOk, setDisclaimerOk] = useState(false);

  if (screen === "landing") {
    return (
      <LandingPage
        lang={lang}
        setLang={setLang}
        city={city}
        setCity={setCity}
        disclaimerOk={disclaimerOk}
        setDisclaimerOk={setDisclaimerOk}
        onStart={() => setScreen("assistant")}
      />
    );
  }

  return (
    <AssistantPage
      lang={lang}
      setLang={setLang}
      city={city}
      onBack={() => setScreen("landing")}
    />
  );
}
